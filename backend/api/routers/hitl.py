"""
Human-in-the-Loop (HITL) approval router
EU AI Act compliance - mandatory human review for high-risk AI decisions
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import httpx

from ..models import (
    HITLApprovalRequest, HITLApprovalResponse, HITLApprovalDecision,
    ApprovalStage, ApprovalStatus
)
from ..database import get_db, HITLApproval, create_audit_log
from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/create-approval-request", response_model=HITLApprovalResponse)
async def create_approval_request(
    request: HITLApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    Create a Human-in-the-Loop approval request

    This pauses the n8n workflow until a human reviews and approves/rejects.
    Required for EU AI Act compliance (high-risk AI decision).
    """
    try:
        logger.info(f"Creating HITL approval for {request.stage} (execution: {request.execution_id})")

        # Calculate expiration
        if request.stage == ApprovalStage.JD_REVIEW:
            expires_at = datetime.utcnow() + timedelta(minutes=settings.HITL_APPROVAL_TIMEOUT_MINUTES)
        else:  # FINAL_REVIEW
            expires_at = datetime.utcnow() + timedelta(hours=settings.HITL_FINAL_APPROVAL_TIMEOUT_HOURS)

        # Generate n8n webhook resume URL
        # This is the webhook URL that will resume the n8n workflow
        resume_webhook_url = f"{settings.N8N_WEBHOOK_URL}/{request.stage.value}-approval/{request.execution_id}"

        # Create approval record
        approval = HITLApproval(
            workflow_id=request.workflow_id,
            execution_id=request.execution_id,
            stage=request.stage.value,
            status=ApprovalStatus.PENDING.value,
            data=request.data,
            reviewer_email=request.reviewer_email,
            expires_at=expires_at,
            resume_webhook_url=resume_webhook_url
        )

        db.add(approval)
        db.commit()
        db.refresh(approval)

        # Generate review URL (frontend)
        review_url = f"{settings.FRONTEND_URL}/review/{approval.id}"

        # TODO: Send email notification to reviewer
        # await send_email_notification(
        #     to=request.reviewer_email,
        #     subject=f"Review Required: {request.stage}",
        #     review_url=review_url,
        #     expires_at=expires_at
        # )

        # Audit log
        create_audit_log(
            db=db,
            execution_id=request.execution_id,
            event_type="hitl",
            action="approval_request_created",
            resource_type="approval",
            resource_id=approval.id,
            details={
                "stage": request.stage.value,
                "reviewer": request.reviewer_email,
                "expires_at": expires_at.isoformat()
            }
        )

        logger.info(f"HITL approval created: {approval.id}, expires at {expires_at}")

        return HITLApprovalResponse(
            approval_id=approval.id,
            review_url=review_url,
            expires_at=expires_at,
            webhook_resume_url=resume_webhook_url
        )

    except Exception as e:
        logger.error(f"Failed to create HITL approval: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-decision/{approval_id}")
async def submit_approval_decision(
    approval_id: str,
    decision: HITLApprovalDecision,
    db: Session = Depends(get_db)
):
    """
    Submit human approval decision

    Called by frontend when human reviews and approves/rejects.
    This resumes the n8n workflow via webhook.
    """
    try:
        logger.info(f"Submitting HITL decision for approval {approval_id}: {decision.status}")

        # Get approval record
        approval = db.query(HITLApproval).filter(HITLApproval.id == approval_id).first()
        if not approval:
            raise HTTPException(status_code=404, detail="Approval request not found")

        # Check if already reviewed
        if approval.status != ApprovalStatus.PENDING.value:
            raise HTTPException(status_code=400, detail=f"Approval already {approval.status}")

        # Check if expired
        if datetime.utcnow() > approval.expires_at:
            approval.status = ApprovalStatus.EXPIRED.value
            db.commit()
            raise HTTPException(status_code=400, detail="Approval request expired")

        # Update approval
        approval.status = decision.status.value
        approval.approved_data = decision.approved_data
        approval.rejection_reason = decision.rejection_reason
        approval.reviewer_notes = decision.reviewer_notes
        approval.reviewed_at = datetime.utcnow()

        db.commit()

        # Audit log
        create_audit_log(
            db=db,
            execution_id=approval.execution_id,
            event_type="hitl",
            action=f"approval_{decision.status.value}",
            resource_type="approval",
            resource_id=approval_id,
            actor="human",
            details={
                "stage": approval.stage,
                "reviewer_notes": decision.reviewer_notes
            }
        )

        # Resume n8n workflow by calling webhook
        try:
            async with httpx.AsyncClient() as client:
                webhook_payload = {
                    "approval_status": decision.status.value,
                    "approved_data": decision.approved_data or approval.data,
                    "rejection_reason": decision.rejection_reason,
                    "approval_id": approval_id
                }

                response = await client.post(
                    approval.resume_webhook_url,
                    json=webhook_payload,
                    timeout=10.0
                )
                response.raise_for_status()

            logger.info(f"n8n workflow resumed for execution {approval.execution_id}")

        except Exception as e:
            logger.error(f"Failed to resume n8n workflow: {e}")
            # Don't fail the approval - it's recorded, just log the error

        return {
            "status": "success",
            "approval_id": approval_id,
            "decision": decision.status.value,
            "workflow_resumed": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit HITL decision: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approval/{approval_id}")
async def get_approval(approval_id: str, db: Session = Depends(get_db)):
    """Get approval request details for review UI"""
    approval = db.query(HITLApproval).filter(HITLApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    return {
        "approval_id": approval.id,
        "stage": approval.stage,
        "status": approval.status,
        "data": approval.data,
        "approved_data": approval.approved_data,
        "created_at": approval.created_at,
        "expires_at": approval.expires_at,
        "reviewed_at": approval.reviewed_at,
        "rejection_reason": approval.rejection_reason,
        "reviewer_notes": approval.reviewer_notes
    }

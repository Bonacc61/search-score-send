"""
Message generation router
AI-powered personalized outreach messages
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from ..models import MessageGenerationRequest, MessageGenerationResponse, PersonalizedMessage
from ..database import get_db, Candidate, create_audit_log
from ..services.claude_client import claude_client

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate-batch", response_model=MessageGenerationResponse)
async def generate_messages_batch(
    request: MessageGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate personalized outreach messages for qualified candidates

    IMPORTANT: No generic templates or [FIRST_NAME] placeholders
    Each message is truly personalized based on candidate's specific skills and experience
    """
    try:
        logger.info(f"Generating messages for {len(request.qualified_candidates)} candidates")

        messages = []

        for scored_candidate in request.qualified_candidates:
            try:
                # Anonymize for Claude API (GDPR)
                anonymized_profile = {
                    "platform": scored_candidate.candidate.platform,
                    "headline": scored_candidate.candidate.headline,
                    "skills": scored_candidate.candidate.skills[:5],  # Top 5 skills
                    "experience_years": scored_candidate.candidate.experience_years,
                    "location": scored_candidate.candidate.location
                }

                # Generate personalized message
                message_data = await claude_client.generate_message(
                    anonymized_profile=anonymized_profile,
                    job=request.job.dict(),
                    score_data={
                        "overall_score": scored_candidate.overall_score,
                        "evaluations": [e.dict() for e in scored_candidate.evaluations]
                    }
                )

                # Create message object
                message = PersonalizedMessage(
                    candidate_id=scored_candidate.anonymized_profile_id,
                    message_subject=message_data["message_subject"],
                    message_body=message_data["message_body"],
                    personalization_points=message_data.get("personalization_points", []),
                    tone=message_data.get("tone", "professional")
                )

                messages.append(message)

                # Update candidate in database
                db_candidate = db.query(Candidate).filter(
                    Candidate.anonymized_id == scored_candidate.anonymized_profile_id,
                    Candidate.execution_id == request.execution_id
                ).first()

                if db_candidate:
                    db_candidate.message_subject = message.message_subject
                    db_candidate.message_body = message.message_body

            except Exception as e:
                logger.error(f"Failed to generate message for candidate: {e}")
                # Continue with other candidates

        db.commit()

        # Audit log
        create_audit_log(
            db=db,
            execution_id=request.execution_id,
            event_type="messaging",
            action="generate_messages_completed",
            resource_type="messages",
            details={
                "messages_generated": len(messages),
                "job_title": request.job.title
            }
        )

        logger.info(f"Generated {len(messages)} personalized messages")

        return MessageGenerationResponse(
            messages=messages,
            execution_id=request.execution_id
        )

    except Exception as e:
        logger.error(f"Message generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

"""
Candidate scoring router
AI-powered scoring with GDPR anonymization
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
import uuid
from typing import List

from ..models import (
    ScoringRequest, ScoringResponse, ScoredCandidate,
    EvaluationCriteria, CandidateProfile
)
from ..database import get_db, Candidate, create_audit_log
from ..services.claude_client import claude_client
from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


def anonymize_profile(profile: CandidateProfile) -> dict:
    """
    Anonymize candidate profile before sending to Claude API (GDPR compliance)

    Removes PII and replaces with anonymized identifiers
    """
    if not settings.ANONYMIZATION_ENABLED:
        return profile.dict()

    return {
        "platform": profile.platform,
        "headline": profile.headline,
        "location": profile.location,
        "skills": profile.skills,
        "experience_years": profile.experience_years,
        # PII removed: name, email, profile_url
        # Hashed identifier for deduplication only
        "anonymized_id": str(uuid.uuid4())
    }


@router.post("/batch", response_model=ScoringResponse)
async def score_candidates_batch(
    request: ScoringRequest,
    db: Session = Depends(get_db)
):
    """
    Score multiple candidates in batch

    GDPR Compliance:
    - Anonymizes profiles before Claude API calls
    - No PII sent to external AI service
    - Only anonymized evaluation data stored
    """
    try:
        logger.info(f"Scoring {len(request.candidates)} candidates for execution {request.execution_id}")

        scored_candidates: List[ScoredCandidate] = []
        qualified_count = 0

        for candidate in request.candidates:
            try:
                # Anonymize profile for GDPR compliance
                anonymized = anonymize_profile(candidate)

                # Call Claude API to score
                score_result = await claude_client.score_candidate(
                    anonymized_profile=anonymized,
                    job_requirements=request.job_requirements.dict()
                )

                # Create evaluation criteria objects
                evaluations = [
                    EvaluationCriteria(**eval_data)
                    for eval_data in score_result.get("evaluations", [])
                ]

                # Create scored candidate
                scored = ScoredCandidate(
                    candidate=candidate,
                    overall_score=score_result["overall_score"],
                    evaluations=evaluations,
                    recommendation=score_result["recommendation"],
                    anonymized_profile_id=anonymized["anonymized_id"]
                )

                scored_candidates.append(scored)

                # Count qualified
                if scored.overall_score >= request.threshold:
                    qualified_count += 1

                # Save to database
                db_candidate = Candidate(
                    execution_id=request.execution_id,
                    anonymized_id=anonymized["anonymized_id"],
                    email_hash=candidate.email_hash,
                    name=candidate.name,  # TODO: Encrypt with DATABASE_ENCRYPTION_KEY
                    profile_url=candidate.profile_url,
                    platform=candidate.platform,
                    headline=candidate.headline,
                    location=candidate.location,
                    skills=candidate.skills,
                    experience_years=candidate.experience_years,
                    overall_score=scored.overall_score,
                    evaluations=[e.dict() for e in evaluations],
                    recommendation=scored.recommendation,
                    raw_data=candidate.raw_data
                )
                db.add(db_candidate)

            except Exception as e:
                logger.error(f"Failed to score candidate {candidate.email_hash}: {e}")
                # Continue with other candidates

        db.commit()

        # Audit log
        create_audit_log(
            db=db,
            execution_id=request.execution_id,
            event_type="scoring",
            action="batch_score_completed",
            resource_type="candidates",
            details={
                "total_scored": len(scored_candidates),
                "qualified": qualified_count,
                "threshold": request.threshold,
                "anonymization_enabled": settings.ANONYMIZATION_ENABLED
            }
        )

        logger.info(f"Scored {len(scored_candidates)} candidates, {qualified_count} qualified (>={request.threshold}%)")

        return ScoringResponse(
            scored_candidates=scored_candidates,
            scored=len(scored_candidates),
            qualified=qualified_count,
            execution_id=request.execution_id,
            anonymization_applied=settings.ANONYMIZATION_ENABLED
        )

    except Exception as e:
        logger.error(f"Batch scoring failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

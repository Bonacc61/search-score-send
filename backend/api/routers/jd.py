"""
Job Description extraction router
Extracts structured requirements from raw JD text using Claude API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
import json

from ..models import JDExtractionRequest, JDExtractionResponse, SearchBoolean
from ..database import get_db, create_audit_log
from ..services.claude_client import claude_client

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/extract", response_model=JDExtractionResponse)
async def extract_jd(
    request: JDExtractionRequest,
    db: Session = Depends(get_db)
):
    """
    Extract structured job requirements from raw job description text

    Uses Claude Sonnet 4 to:
    - Identify role title and seniority
    - Extract must-have vs nice-to-have skills
    - Determine experience requirements
    - Generate Boolean search queries for LinkedIn, GitHub, Stack Overflow

    Returns structured JD data ready for search phase
    """
    try:
        logger.info(f"Extracting JD (length: {len(request.raw_text)} chars)")

        # Prepare Claude prompt
        prompt = f"""You are an expert technical recruiter and sourcing specialist.
Analyze this job description and extract structured hiring requirements.

Job Description:
{request.raw_text}

Extract the following information and return as JSON:
{{
  "title": "Job title",
  "seniority": "junior|mid|senior|lead|principal",
  "must_have_skills": ["skill1", "skill2", ...],
  "nice_to_have": ["skill1", "skill2", ...],
  "years_experience": 5,
  "location": "City, Country or Remote",
  "remote_policy": "remote|hybrid|onsite",
  "salary_range": "€XX,XXX - €XX,XXX or null if not specified",
  "search_boolean": {{
    "linkedin": "Boolean query optimized for LinkedIn Recruiter",
    "github": "Boolean query for GitHub search",
    "stackoverflow": "Boolean query for Stack Overflow search"
  }},
  "extraction_confidence": 0.95
}}

IMPORTANT for search_boolean:
- LinkedIn: Use parentheses for OR groups, AND for required terms
- GitHub: Use language:X, location:Y, followers:>N syntax
- Stack Overflow: Use [tag1] OR [tag2] syntax
- Focus on the MUST-HAVE skills for search queries
- Be specific but not overly restrictive

Return ONLY the JSON, no markdown formatting."""

        # Call Claude API
        response = await claude_client.extract_jd(prompt)

        # Parse response
        try:
            extracted_data = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response: {e}")
            logger.debug(f"Claude response: {response}")
            raise HTTPException(
                status_code=500,
                detail="Failed to parse AI response. Please try again."
            )

        # Validate and create response
        jd_response = JDExtractionResponse(
            title=extracted_data.get("title", "Unknown Role"),
            seniority=extracted_data.get("seniority", "mid"),
            must_have_skills=extracted_data.get("must_have_skills", []),
            nice_to_have=extracted_data.get("nice_to_have", []),
            years_experience=extracted_data.get("years_experience", 0),
            location=extracted_data.get("location"),
            remote_policy=extracted_data.get("remote_policy"),
            salary_range=extracted_data.get("salary_range"),
            search_boolean=SearchBoolean(**extracted_data.get("search_boolean", {
                "linkedin": "",
                "github": "",
                "stackoverflow": ""
            })),
            extraction_confidence=extracted_data.get("extraction_confidence", 0.9),
            raw_claude_response=response
        )

        logger.info(f"Extracted JD: {jd_response.title} ({jd_response.seniority})")
        logger.info(f"Must-have skills: {', '.join(jd_response.must_have_skills[:5])}...")

        return jd_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JD extraction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract job requirements: {str(e)}"
        )

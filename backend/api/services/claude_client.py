"""
Claude API client for AI-powered operations
Handles JD extraction, candidate scoring, and message generation
"""
import anthropic
from typing import List, Dict, Any
import logging
import json
from ..config import settings

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Wrapper around Anthropic Claude API"""

    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        self.max_tokens = settings.CLAUDE_MAX_TOKENS

    async def _call_claude(self, prompt: str, system: str = None) -> str:
        """
        Call Claude API with prompt

        Args:
            prompt: User prompt
            system: Optional system prompt

        Returns:
            Claude's text response
        """
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            }

            if system:
                kwargs["system"] = system

            response = await self.client.messages.create(**kwargs)

            return response.content[0].text

        except Exception as e:
            logger.error(f"Claude API call failed: {e}", exc_info=True)
            raise

    async def extract_jd(self, prompt: str) -> str:
        """Extract structured JD from raw text"""
        return await self._call_claude(
            prompt=prompt,
            system="You are an expert technical recruiter. Return only valid JSON, no markdown."
        )

    async def score_candidate(
        self,
        anonymized_profile: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score a single candidate against job requirements

        IMPORTANT: Profile is already anonymized by caller for GDPR compliance
        """
        prompt = f"""You are an expert technical recruiter scoring a candidate against job requirements.

Job Requirements:
- Title: {job_requirements['title']}
- Seniority: {job_requirements['seniority']}
- Must-Have Skills: {', '.join(job_requirements['must_have_skills'])}
- Nice-to-Have: {', '.join(job_requirements.get('nice_to_have', []))}
- Experience: {job_requirements['years_experience']}+ years

Candidate Profile (anonymized):
- Platform: {anonymized_profile['platform']}
- Headline: {anonymized_profile.get('headline', 'N/A')}
- Skills: {', '.join(anonymized_profile.get('skills', []))}
- Experience: {anonymized_profile.get('experience_years', 'Unknown')} years
- Location: {anonymized_profile.get('location', 'Unknown')}

Score this candidate on the following criteria (0-100 for each):
1. Technical Skills Match
2. Experience Level Match
3. Seniority Alignment
4. Location/Remote Compatibility

Return JSON:
{{
  "overall_score": 85.0,
  "evaluations": [
    {{
      "criterion": "Technical Skills Match",
      "score": 90.0,
      "reasoning": "Strong match for X, Y, Z skills",
      "evidence": ["skill evidence 1", "skill evidence 2"]
    }},
    ...
  ],
  "recommendation": "Strong fit|Good fit|Moderate fit|Weak fit|No fit"
}}

Be honest and critical. Score based on actual evidence, not potential."""

        response = await self._call_claude(
            prompt=prompt,
            system="You are an expert recruiter. Return only valid JSON."
        )

        return json.loads(response)

    async def generate_message(
        self,
        anonymized_profile: Dict[str, Any],
        job: Dict[str, Any],
        score_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate personalized outreach message

        IMPORTANT: Profile is anonymized - do not request or use PII
        """
        prompt = f"""You are writing a LinkedIn outreach message for a {job['title']} role.

DO NOT use generic templates or [FIRST_NAME] placeholders.
DO personalize based on specific skills and experience.

Candidate Context (anonymized):
- Platform: {anonymized_profile['platform']}
- Headline: {anonymized_profile.get('headline', '')}
- Key Skills: {', '.join(anonymized_profile.get('skills', [])[:5])}
- Match Score: {score_data['overall_score']:.0f}%
- Top Strengths: {', '.join([e['criterion'] for e in score_data['evaluations'][:2]])}

Job:
- Title: {job['title']}
- Seniority: {job['seniority']}
- Must-Have: {', '.join(job['must_have_skills'][:3])}
- Location: {job.get('location', 'Remote')}

Write a professional LinkedIn message (300-400 chars) that:
1. Mentions 1-2 SPECIFIC skills/experience from their profile
2. Explains why they're a strong fit (use scoring evidence)
3. Includes clear call-to-action
4. NO [FIRST_NAME] or template placeholders
5. Tone: professional but warm

Return JSON:
{{
  "message_subject": "Subject line",
  "message_body": "Message text...",
  "personalization_points": ["Mentioned X skill", "Referenced Y experience"],
  "tone": "professional"
}}"""

        response = await self._call_claude(
            prompt=prompt,
            system="You are a talent acquisition specialist. Return only valid JSON."
        )

        return json.loads(response)


# Global client instance
claude_client = ClaudeClient()

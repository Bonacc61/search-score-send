"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== Job Description ====================

class JDExtractionRequest(BaseModel):
    """Request to extract structured data from raw job description"""
    raw_text: str = Field(..., description="Raw job description text")


class SearchBoolean(BaseModel):
    """Platform-specific Boolean search queries"""
    linkedin: str
    github: str
    stackoverflow: str


class JDExtractionResponse(BaseModel):
    """Extracted job requirements"""
    title: str
    seniority: str
    must_have_skills: List[str]
    nice_to_have: List[str]
    years_experience: int
    location: Optional[str] = None
    remote_policy: Optional[str] = None
    salary_range: Optional[str] = None
    search_boolean: SearchBoolean
    extraction_confidence: float = Field(..., ge=0, le=1)
    raw_claude_response: Optional[str] = None


# ==================== Search ====================

class SearchRequest(BaseModel):
    """Request to search a platform"""
    query: str = Field(..., description="Boolean search query")
    limit: int = Field(default=20, ge=1, le=100)
    execution_id: str = Field(..., description="n8n execution ID for tracking")


class CandidateProfile(BaseModel):
    """Candidate profile from search"""
    name: str
    email_hash: str = Field(..., description="HMAC hash of email for deduplication")
    profile_url: str
    platform: str = Field(..., description="linkedin|github|stackoverflow")
    headline: Optional[str] = None
    location: Optional[str] = None
    skills: List[str] = []
    experience_years: Optional[int] = None
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Platform-specific data")


class SearchResponse(BaseModel):
    """Search results"""
    candidates: List[CandidateProfile]
    total_found: int
    platform: str
    query_used: str
    execution_id: str


# ==================== Scoring ====================

class ScoringRequest(BaseModel):
    """Request to score candidates"""
    candidates: List[CandidateProfile]
    job_requirements: JDExtractionResponse
    threshold: float = Field(default=80.0, ge=0, le=100)
    execution_id: str


class EvaluationCriteria(BaseModel):
    """Individual scoring criterion"""
    criterion: str
    score: float = Field(..., ge=0, le=100)
    reasoning: str
    evidence: List[str] = []


class ScoredCandidate(BaseModel):
    """Candidate with AI scoring"""
    candidate: CandidateProfile
    overall_score: float = Field(..., ge=0, le=100)
    evaluations: List[EvaluationCriteria]
    recommendation: str
    anonymized_profile_id: str = Field(..., description="Anonymized ID for GDPR compliance")
    scored_at: datetime = Field(default_factory=datetime.utcnow)


class ScoringResponse(BaseModel):
    """Batch scoring results"""
    scored_candidates: List[ScoredCandidate]
    scored: int
    qualified: int = Field(..., description="Number meeting threshold")
    execution_id: str
    anonymization_applied: bool = True


# ==================== Messages ====================

class MessageGenerationRequest(BaseModel):
    """Request to generate personalized messages"""
    qualified_candidates: List[ScoredCandidate]
    job: JDExtractionResponse
    execution_id: str


class PersonalizedMessage(BaseModel):
    """Generated outreach message"""
    candidate_id: str
    message_subject: str
    message_body: str
    personalization_points: List[str] = Field(..., description="What was personalized")
    tone: str = "professional"
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class MessageGenerationResponse(BaseModel):
    """Batch message generation results"""
    messages: List[PersonalizedMessage]
    execution_id: str


# ==================== HITL ====================

class ApprovalStage(str, Enum):
    """HITL approval stages"""
    JD_REVIEW = "jd_review"
    FINAL_REVIEW = "final_review"


class ApprovalStatus(str, Enum):
    """Approval request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class HITLApprovalRequest(BaseModel):
    """Create HITL approval request"""
    workflow_id: str
    execution_id: str
    stage: ApprovalStage
    data: Dict[str, Any]
    reviewer_email: EmailStr
    candidates_count: Optional[int] = None


class HITLApprovalResponse(BaseModel):
    """HITL approval request created"""
    approval_id: str
    review_url: str
    expires_at: datetime
    webhook_resume_url: str = Field(..., description="URL to resume n8n workflow")


class HITLApprovalDecision(BaseModel):
    """Human approval decision"""
    approval_id: str
    status: ApprovalStatus
    approved_data: Optional[Dict[str, Any]] = None
    rejection_reason: Optional[str] = None
    reviewer_notes: Optional[str] = None


# ==================== Progress ====================

class ProgressStage(str, Enum):
    """Workflow execution stages"""
    STARTED = "started"
    JD_EXTRACTING = "jd_extracting"
    JD_REVIEW = "jd_review"
    SEARCHING = "searching"
    SCORING = "scoring"
    GENERATING_MESSAGES = "generating_messages"
    FINAL_REVIEW = "final_review"
    COMPLETED = "completed"
    FAILED = "failed"


class ProgressUpdate(BaseModel):
    """Progress update for SSE"""
    execution_id: str
    stage: ProgressStage
    message: str
    progress_percent: Optional[float] = Field(None, ge=0, le=100)
    candidates_found: Optional[int] = None
    candidates_qualified: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==================== Outreach ====================

class SendMode(str, Enum):
    """Message sending mode"""
    QUEUE = "queue"  # Add to send queue for manual triggering
    IMMEDIATE = "immediate"  # Send immediately


class OutreachPrepareRequest(BaseModel):
    """Prepare messages for sending"""
    approved_candidates: List[Dict[str, Any]]
    execution_id: str
    send_mode: SendMode = SendMode.QUEUE


class OutreachPrepareResponse(BaseModel):
    """Outreach preparation result"""
    queued: int
    send_mode: SendMode
    queue_url: Optional[str] = None
    execution_id: str

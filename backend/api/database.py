"""
SQLAlchemy database models and session management
"""
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid

from .config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# ==================== Database Models ====================

class WorkflowExecution(Base):
    """Track workflow executions"""
    __tablename__ = "workflow_executions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, nullable=False, index=True)
    execution_id = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, nullable=False, default="running")  # running|completed|failed|rejected
    stage = Column(String, nullable=False, default="started")
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Metrics
    candidates_found = Column(Integer, default=0)
    candidates_scored = Column(Integer, default=0)
    candidates_qualified = Column(Integer, default=0)
    candidates_approved = Column(Integer, default=0)

    # Data
    job_description = Column(Text, nullable=True)
    extracted_jd = Column(JSON, nullable=True)
    metadata = Column(JSON, default=dict)

    # GDPR
    expires_at = Column(DateTime, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=settings.DATA_RETENTION_DAYS)


class Candidate(Base):
    """Candidate profiles (anonymized)"""
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, nullable=False, index=True)

    # Anonymized identifiers
    anonymized_id = Column(String, unique=True, nullable=False, index=True)
    email_hash = Column(String, nullable=False, index=True)

    # Profile data (anonymized)
    name = Column(String, nullable=True)  # Encrypted
    profile_url = Column(String, nullable=True)
    platform = Column(String, nullable=False)
    headline = Column(String, nullable=True)
    location = Column(String, nullable=True)
    skills = Column(JSON, default=list)
    experience_years = Column(Integer, nullable=True)

    # Scoring
    overall_score = Column(Float, nullable=True)
    evaluations = Column(JSON, default=list)
    recommendation = Column(String, nullable=True)

    # Outreach
    message_subject = Column(String, nullable=True)
    message_body = Column(Text, nullable=True)
    message_sent = Column(Boolean, default=False)
    message_sent_at = Column(DateTime, nullable=True)

    # Metadata
    raw_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # GDPR
    expires_at = Column(DateTime, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=settings.DATA_RETENTION_DAYS)


class HITLApproval(Base):
    """Human-in-the-loop approval requests"""
    __tablename__ = "hitl_approvals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, nullable=False, index=True)
    execution_id = Column(String, nullable=False, index=True)

    # Approval details
    stage = Column(String, nullable=False)  # jd_review|final_review
    status = Column(String, nullable=False, default="pending")  # pending|approved|rejected|expired

    # Data
    data = Column(JSON, nullable=False)
    approved_data = Column(JSON, nullable=True)

    # Reviewer
    reviewer_email = Column(String, nullable=False)
    reviewer_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)

    # n8n webhook to resume workflow
    resume_webhook_url = Column(String, nullable=False)


class AuditLog(Base):
    """Audit trail for compliance"""
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, nullable=False, index=True)

    # Event details
    event_type = Column(String, nullable=False, index=True)
    actor = Column(String, nullable=True)  # system|human|api
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)

    # Data
    details = Column(JSON, default=dict)

    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # GDPR
    expires_at = Column(DateTime, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=settings.DATA_RETENTION_DAYS)


# ==================== Helper Functions ====================

def get_db():
    """Dependency for FastAPI routes to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_audit_log(
    db,
    execution_id: str,
    event_type: str,
    action: str,
    resource_type: str,
    actor: str = "system",
    resource_id: str = None,
    details: dict = None
):
    """Create audit log entry"""
    if not settings.ENABLE_AUDIT_LOGGING:
        return

    log = AuditLog(
        execution_id=execution_id,
        event_type=event_type,
        actor=actor,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {}
    )
    db.add(log)
    db.commit()

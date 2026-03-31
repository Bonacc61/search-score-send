"""
Billing database models
SQLAlchemy models for subscriptions, usage tracking, and invoices
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

from .database import Base
from .models_billing import SubscriptionTier, BillingCycle, SubscriptionStatus, InvoiceStatus


class User(Base):
    """User/Organization account"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    organization_name = Column(String, nullable=True)

    # Stripe
    stripe_customer_id = Column(String, unique=True, nullable=True, index=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription = relationship("SubscriptionDB", back_populates="user", uselist=False)
    usage_records = relationship("UsageRecordDB", back_populates="user")
    invoices = relationship("InvoiceDB", back_populates="user")


class SubscriptionDB(Base):
    """User subscription"""
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # Plan
    tier = Column(String, nullable=False, default=SubscriptionTier.FREE.value, index=True)
    billing_cycle = Column(String, nullable=False, default=BillingCycle.MONTHLY.value)
    status = Column(String, nullable=False, default=SubscriptionStatus.TRIAL.value, index=True)

    # Dates
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    trial_ends_at = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)

    # Stripe
    stripe_subscription_id = Column(String, unique=True, nullable=True, index=True)
    last_payment_at = Column(DateTime, nullable=True)
    next_payment_at = Column(DateTime, nullable=True)

    # Metadata
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscription")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.current_period_start:
            self.current_period_start = datetime.utcnow()
        if not self.current_period_end:
            # Default to 30 days for monthly
            self.current_period_end = self.current_period_start + timedelta(days=30)


class UsageRecordDB(Base):
    """Individual usage record for metering"""
    __tablename__ = "usage_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Metric
    metric_type = Column(String, nullable=False, index=True)  # workflow_execution, jd_extraction, etc.
    quantity = Column(Integer, nullable=False, default=1)
    execution_id = Column(String, nullable=True, index=True)

    # Billing
    billable = Column(Boolean, default=True, nullable=False)
    billed = Column(Boolean, default=False, nullable=False, index=True)
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=True)

    # Metadata
    metadata = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="usage_records")
    invoice = relationship("InvoiceDB", back_populates="usage_records")

    # Composite indexes for efficient querying
    __table_args__ = (
        Index('ix_usage_user_time', 'user_id', 'timestamp'),
        Index('ix_usage_user_metric', 'user_id', 'metric_type'),
        Index('ix_usage_unbilled', 'user_id', 'billed', 'billable'),
    )


class InvoiceDB(Base):
    """Customer invoice"""
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Status
    status = Column(String, nullable=False, default=InvoiceStatus.DRAFT.value, index=True)

    # Billing period
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)

    # Amounts
    subtotal_eur = Column(Float, nullable=False, default=0)
    tax_eur = Column(Float, nullable=False, default=0)
    total_eur = Column(Float, nullable=False, default=0)

    # Line items (stored as JSON)
    line_items = Column(JSON, default=list)

    # Stripe
    stripe_invoice_id = Column(String, unique=True, nullable=True, index=True)
    payment_url = Column(String, nullable=True)

    # Dates
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=False)
    paid_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="invoices")
    usage_records = relationship("UsageRecordDB", back_populates="invoice")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.due_date:
            self.due_date = datetime.utcnow() + timedelta(days=14)


class QuotaUsageDB(Base):
    """Current billing period usage summary (cached for performance)"""
    __tablename__ = "quota_usage"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Billing period
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)

    # Usage counts
    executions = Column(Integer, default=0, nullable=False)
    jd_extractions = Column(Integer, default=0, nullable=False)
    candidates_searched = Column(Integer, default=0, nullable=False)
    candidates_scored = Column(Integer, default=0, nullable=False)
    messages_generated = Column(Integer, default=0, nullable=False)
    hitl_approvals = Column(Integer, default=0, nullable=False)
    api_calls = Column(Integer, default=0, nullable=False)

    # Overage counts
    executions_overage = Column(Integer, default=0, nullable=False)
    candidates_overage = Column(Integer, default=0, nullable=False)
    scorings_overage = Column(Integer, default=0, nullable=False)

    # Overage costs
    overage_cost_eur = Column(Float, default=0, nullable=False)

    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite index
    __table_args__ = (
        Index('ix_quota_user_period', 'user_id', 'period_start', unique=True),
    )


class RateLimitDB(Base):
    """Rate limit tracking (Redis alternative for simple cases)"""
    __tablename__ = "rate_limits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Window
    window_start = Column(DateTime, nullable=False, index=True)
    window_type = Column(String, nullable=False)  # minute|hour|day

    # Counts
    request_count = Column(Integer, default=0, nullable=False)

    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite index
    __table_args__ = (
        Index('ix_ratelimit_user_window', 'user_id', 'window_type', 'window_start'),
    )

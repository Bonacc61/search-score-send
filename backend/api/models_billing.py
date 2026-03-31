"""
Billing and monetization models
Usage-based pricing with subscription tiers
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== Subscription Plans ====================

class SubscriptionTier(str, Enum):
    """Subscription tiers with different limits"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class PlanLimits(BaseModel):
    """Usage limits per plan"""
    # Workflow executions
    executions_per_month: int = Field(..., description="Max workflow executions per month")

    # Candidate limits
    candidates_per_execution: int = Field(..., description="Max candidates per workflow")
    total_candidates_per_month: int = Field(..., description="Total candidates processed per month")

    # AI operations
    jd_extractions_per_month: int = Field(..., description="Max JD extractions")
    scorings_per_month: int = Field(..., description="Max candidate scorings")
    messages_per_month: int = Field(..., description="Max message generations")

    # Features
    hitl_enabled: bool = Field(default=False, description="Human-in-the-loop approval gates")
    multi_user: bool = Field(default=False, description="Multiple team members")
    api_access: bool = Field(default=False, description="API access for integrations")
    custom_branding: bool = Field(default=False, description="Custom branding")
    priority_support: bool = Field(default=False, description="Priority support")

    # Advanced features
    audit_logs_retention_days: int = Field(default=30, description="Audit log retention")
    data_export: bool = Field(default=False, description="Full data export capability")
    sla_guarantee: bool = Field(default=False, description="SLA guarantee")


# Predefined plans
PLAN_LIMITS = {
    SubscriptionTier.FREE: PlanLimits(
        executions_per_month=5,
        candidates_per_execution=10,
        total_candidates_per_month=50,
        jd_extractions_per_month=5,
        scorings_per_month=50,
        messages_per_month=20,
        hitl_enabled=False,
        multi_user=False,
        api_access=False,
        custom_branding=False,
        priority_support=False,
        audit_logs_retention_days=7,
        data_export=False,
        sla_guarantee=False
    ),
    SubscriptionTier.STARTER: PlanLimits(
        executions_per_month=50,
        candidates_per_execution=50,
        total_candidates_per_month=500,
        jd_extractions_per_month=50,
        scorings_per_month=500,
        messages_per_month=200,
        hitl_enabled=True,
        multi_user=False,
        api_access=True,
        custom_branding=False,
        priority_support=False,
        audit_logs_retention_days=30,
        data_export=True,
        sla_guarantee=False
    ),
    SubscriptionTier.PROFESSIONAL: PlanLimits(
        executions_per_month=200,
        candidates_per_execution=100,
        total_candidates_per_month=2000,
        jd_extractions_per_month=200,
        scorings_per_month=2000,
        messages_per_month=1000,
        hitl_enabled=True,
        multi_user=True,
        api_access=True,
        custom_branding=True,
        priority_support=True,
        audit_logs_retention_days=90,
        data_export=True,
        sla_guarantee=False
    ),
    SubscriptionTier.ENTERPRISE: PlanLimits(
        executions_per_month=999999,  # Unlimited
        candidates_per_execution=500,
        total_candidates_per_month=999999,
        jd_extractions_per_month=999999,
        scorings_per_month=999999,
        messages_per_month=999999,
        hitl_enabled=True,
        multi_user=True,
        api_access=True,
        custom_branding=True,
        priority_support=True,
        audit_logs_retention_days=365,
        data_export=True,
        sla_guarantee=True
    )
}


class PricingModel(BaseModel):
    """Pricing structure per plan"""
    tier: SubscriptionTier
    monthly_price_eur: float
    annual_price_eur: float = Field(..., description="Annual price (usually 20% discount)")

    # Overage pricing (pay-as-you-go above limits)
    overage_per_execution_eur: float = Field(default=0, description="Cost per execution over limit")
    overage_per_candidate_eur: float = Field(default=0, description="Cost per candidate over limit")
    overage_per_scoring_eur: float = Field(default=0, description="Cost per AI scoring over limit")

    # Features included
    limits: PlanLimits


# Predefined pricing
PRICING = {
    SubscriptionTier.FREE: PricingModel(
        tier=SubscriptionTier.FREE,
        monthly_price_eur=0,
        annual_price_eur=0,
        overage_per_execution_eur=0,  # No overage on free plan
        overage_per_candidate_eur=0,
        overage_per_scoring_eur=0,
        limits=PLAN_LIMITS[SubscriptionTier.FREE]
    ),
    SubscriptionTier.STARTER: PricingModel(
        tier=SubscriptionTier.STARTER,
        monthly_price_eur=99,
        annual_price_eur=950,  # ~20% discount
        overage_per_execution_eur=2.50,
        overage_per_candidate_eur=0.50,
        overage_per_scoring_eur=0.10,
        limits=PLAN_LIMITS[SubscriptionTier.STARTER]
    ),
    SubscriptionTier.PROFESSIONAL: PricingModel(
        tier=SubscriptionTier.PROFESSIONAL,
        monthly_price_eur=299,
        annual_price_eur=2870,  # ~20% discount
        overage_per_execution_eur=2.00,
        overage_per_candidate_eur=0.40,
        overage_per_scoring_eur=0.08,
        limits=PLAN_LIMITS[SubscriptionTier.PROFESSIONAL]
    ),
    SubscriptionTier.ENTERPRISE: PricingModel(
        tier=SubscriptionTier.ENTERPRISE,
        monthly_price_eur=999,
        annual_price_eur=9590,  # ~20% discount
        overage_per_execution_eur=0,  # No overage on enterprise
        overage_per_candidate_eur=0,
        overage_per_scoring_eur=0,
        limits=PLAN_LIMITS[SubscriptionTier.ENTERPRISE]
    )
}


# ==================== Usage Tracking ====================

class UsageMetricType(str, Enum):
    """Types of billable usage metrics"""
    WORKFLOW_EXECUTION = "workflow_execution"
    JD_EXTRACTION = "jd_extraction"
    CANDIDATE_SEARCH = "candidate_search"
    CANDIDATE_SCORING = "candidate_scoring"
    MESSAGE_GENERATION = "message_generation"
    HITL_APPROVAL = "hitl_approval"
    API_CALL = "api_call"


class UsageRecord(BaseModel):
    """Individual usage record for billing"""
    user_id: str
    metric_type: UsageMetricType
    quantity: int = Field(default=1, description="Number of units consumed")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_id: Optional[str] = None
    billable: bool = Field(default=True, description="Whether this counts toward quota")


class UsageSummary(BaseModel):
    """Monthly usage summary for a user"""
    user_id: str
    billing_period_start: datetime
    billing_period_end: datetime

    # Counts
    executions: int = 0
    jd_extractions: int = 0
    candidates_searched: int = 0
    candidates_scored: int = 0
    messages_generated: int = 0
    hitl_approvals: int = 0
    api_calls: int = 0

    # Plan limits
    plan_tier: SubscriptionTier
    plan_limits: PlanLimits

    # Overage
    executions_overage: int = 0
    candidates_overage: int = 0
    scorings_overage: int = 0

    # Costs
    overage_cost_eur: float = 0


# ==================== Subscription Management ====================

class BillingCycle(str, Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    ANNUAL = "annual"


class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    SUSPENDED = "suspended"


class Subscription(BaseModel):
    """User subscription record"""
    user_id: str
    tier: SubscriptionTier
    billing_cycle: BillingCycle
    status: SubscriptionStatus

    # Dates
    started_at: datetime
    current_period_start: datetime
    current_period_end: datetime
    trial_ends_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None

    # Billing
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    last_payment_at: Optional[datetime] = None
    next_payment_at: Optional[datetime] = None

    # Usage tracking
    current_usage: UsageSummary


class SubscriptionCreateRequest(BaseModel):
    """Request to create new subscription"""
    user_id: str
    email: EmailStr
    tier: SubscriptionTier
    billing_cycle: BillingCycle
    payment_method_id: Optional[str] = None  # Stripe payment method ID
    start_trial: bool = Field(default=False)


class SubscriptionUpdateRequest(BaseModel):
    """Request to update subscription"""
    tier: Optional[SubscriptionTier] = None
    billing_cycle: Optional[BillingCycle] = None
    cancel: bool = Field(default=False)


# ==================== Billing & Invoices ====================

class InvoiceStatus(str, Enum):
    """Invoice status"""
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class InvoiceLineItem(BaseModel):
    """Individual line item on invoice"""
    description: str
    quantity: int
    unit_price_eur: float
    total_eur: float
    metric_type: Optional[UsageMetricType] = None


class Invoice(BaseModel):
    """Customer invoice"""
    invoice_id: str
    user_id: str
    status: InvoiceStatus

    # Dates
    created_at: datetime
    due_date: datetime
    paid_at: Optional[datetime] = None

    # Billing period
    period_start: datetime
    period_end: datetime

    # Line items
    line_items: List[InvoiceLineItem]

    # Totals
    subtotal_eur: float
    tax_eur: float = 0
    total_eur: float

    # Payment
    stripe_invoice_id: Optional[str] = None
    payment_url: Optional[str] = None


# ==================== API Rate Limiting ====================

class RateLimitConfig(BaseModel):
    """Rate limit configuration based on plan"""
    tier: SubscriptionTier
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int = Field(..., description="Max requests in 1 second")


RATE_LIMITS = {
    SubscriptionTier.FREE: RateLimitConfig(
        tier=SubscriptionTier.FREE,
        requests_per_minute=10,
        requests_per_hour=100,
        requests_per_day=500,
        burst_limit=3
    ),
    SubscriptionTier.STARTER: RateLimitConfig(
        tier=SubscriptionTier.STARTER,
        requests_per_minute=30,
        requests_per_hour=500,
        requests_per_day=5000,
        burst_limit=10
    ),
    SubscriptionTier.PROFESSIONAL: RateLimitConfig(
        tier=SubscriptionTier.PROFESSIONAL,
        requests_per_minute=60,
        requests_per_hour=2000,
        requests_per_day=20000,
        burst_limit=20
    ),
    SubscriptionTier.ENTERPRISE: RateLimitConfig(
        tier=SubscriptionTier.ENTERPRISE,
        requests_per_minute=300,
        requests_per_hour=10000,
        requests_per_day=100000,
        burst_limit=100
    )
}


class RateLimitStatus(BaseModel):
    """Current rate limit status for user"""
    user_id: str
    tier: SubscriptionTier
    requests_remaining_minute: int
    requests_remaining_hour: int
    requests_remaining_day: int
    reset_at: datetime

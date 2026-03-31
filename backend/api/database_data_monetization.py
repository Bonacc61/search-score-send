"""
Database models for pattern learning and data monetization
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, Text, Index
from datetime import datetime
import uuid

from .database import Base


class SearchPatternDB(Base):
    """Learned search patterns"""
    __tablename__ = "search_patterns"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pattern_type = Column(String, nullable=False, index=True)

    # Job context (anonymized)
    job_title = Column(String, nullable=False)
    job_category = Column(String, nullable=False, index=True)
    seniority = Column(String, nullable=False, index=True)
    required_skills = Column(JSON, nullable=False)

    # Query that worked
    successful_query = Column(Text, nullable=False)
    query_platform = Column(String, nullable=False, index=True)

    # Success metrics
    candidates_found = Column(Integer, nullable=False)
    candidates_qualified = Column(Integer, nullable=False)
    average_score = Column(Float, nullable=False)
    time_to_fill_estimate_days = Column(Integer, nullable=True)

    # Pattern strength
    confidence_score = Column(Float, nullable=False, index=True)
    usage_count = Column(Integer, default=1, nullable=False)

    # Geographic context
    geographic_region = Column(String, nullable=True, index=True)

    # Timestamps
    learned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_pattern_category_seniority', 'job_category', 'seniority'),
        Index('ix_pattern_confidence', 'confidence_score'),
    )


class SemanticEmbeddingDB(Base):
    """Semantic embeddings of JD → Query mappings"""
    __tablename__ = "semantic_embeddings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Input
    jd_text_anonymized = Column(Text, nullable=False)
    jd_embedding = Column(JSON, nullable=False)  # List of floats

    # Output
    successful_queries = Column(JSON, nullable=False)  # Dict[platform, query]
    query_embeddings = Column(JSON, nullable=False)  # Dict[platform, embedding]

    # Success metrics
    retrieval_precision = Column(Float, nullable=False)
    retrieval_recall_estimate = Column(Float, nullable=True)

    # Context
    industry = Column(String, nullable=True, index=True)
    company_size = Column(String, nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class SkillPatternDB(Base):
    """Skill combination patterns"""
    __tablename__ = "skill_patterns"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Primary skill
    anchor_skill = Column(String, nullable=False, index=True)

    # Combinations
    high_value_combinations = Column(JSON, nullable=False)
    low_value_combinations = Column(JSON, default=list)

    # Context
    job_category = Column(String, nullable=False, index=True)
    seniority_level = Column(String, nullable=False, index=True)

    # Statistics
    sample_size = Column(Integer, nullable=False)
    confidence_interval = Column(Float, nullable=False)

    # Timestamps
    learned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_skill_anchor_category', 'anchor_skill', 'job_category'),
    )


class PlatformStrategyDB(Base):
    """Platform sourcing strategies"""
    __tablename__ = "platform_strategies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Role context
    job_category = Column(String, nullable=False, index=True)
    seniority = Column(String, nullable=False, index=True)
    key_skills = Column(JSON, nullable=False)

    # Strategy
    platform_allocation = Column(JSON, nullable=False)  # Dict[platform, percentage]
    platform_tactics = Column(JSON, nullable=False)  # Dict[platform, tactics]

    # Success metrics
    average_time_to_fill_days = Column(Float, nullable=False)
    quality_score = Column(Float, nullable=False)

    # Statistics
    sample_size = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScoringPatternDB(Base):
    """Candidate scoring patterns"""
    __tablename__ = "scoring_patterns"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Feature importance
    feature_importance = Column(JSON, nullable=False)  # Dict[feature, weight]

    # Context
    job_category = Column(String, nullable=False, index=True)
    seniority = Column(String, nullable=False, index=True)

    # Model performance
    model_accuracy = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)

    # Timestamps
    learned_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MessagePatternDB(Base):
    """Message personalization patterns"""
    __tablename__ = "message_patterns"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Message characteristics
    personalization_elements = Column(JSON, nullable=False)
    message_tone = Column(String, nullable=False)
    message_length_chars = Column(Integer, nullable=False)

    # Effectiveness
    response_rate = Column(Float, nullable=True)
    engagement_score = Column(Float, nullable=False)

    # Context
    job_category = Column(String, nullable=False, index=True)
    seniority = Column(String, nullable=False)
    platform = Column(String, nullable=False, index=True)

    # Template (anonymized)
    anonymized_template = Column(Text, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DatasetExportDB(Base):
    """Exported datasets for sale"""
    __tablename__ = "dataset_exports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_type = Column(String, nullable=False, index=True)
    version = Column(String, nullable=False)

    # Content
    record_count = Column(Integer, nullable=False)
    records_json = Column(Text, nullable=False)  # JSONL or compressed JSON

    # Quality
    average_confidence = Column(Float, nullable=False)
    validation_coverage = Column(Float, nullable=False)

    # Commercial
    price_per_record_usd = Column(Float, nullable=False)
    total_value_usd = Column(Float, nullable=False)
    license_type = Column(String, nullable=False, default="single_use")

    # Description
    description = Column(Text, nullable=False)
    use_cases = Column(JSON, nullable=False)

    # Statistics
    metadata_distribution = Column(JSON, nullable=False)

    # Export details
    exported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    format = Column(String, nullable=False, default="jsonl")
    size_mb = Column(Float, nullable=False)

    # Sales tracking
    times_sold = Column(Integer, default=0, nullable=False)
    revenue_generated_usd = Column(Float, default=0, nullable=False)


class DataPurchaseDB(Base):
    """Data purchases"""
    __tablename__ = "data_purchases"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_export_id = Column(String, nullable=False, index=True)

    # Buyer
    buyer_email = Column(String, nullable=False, index=True)
    buyer_organization = Column(String, nullable=False)

    # Purchase details
    records_purchased = Column(Integer, nullable=False)
    filters_applied = Column(JSON, default=dict)

    # Commercial
    unit_price_usd = Column(Float, nullable=False)
    discount_applied_percent = Column(Float, default=0, nullable=False)
    total_price_usd = Column(Float, nullable=False)

    # Fulfillment
    download_url = Column(String, nullable=False)
    download_expires_at = Column(DateTime, nullable=False)
    download_count = Column(Integer, default=0, nullable=False)

    # Payment
    stripe_payment_intent_id = Column(String, nullable=True, index=True)
    paid_at = Column(DateTime, nullable=True)

    # Timestamps
    purchased_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    license_type = Column(String, nullable=False)
    use_case = Column(Text, nullable=False)


class PatternLearningJobDB(Base):
    """Background jobs for pattern learning"""
    __tablename__ = "pattern_learning_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Job type
    job_type = Column(String, nullable=False, index=True)  # learn_search|learn_skills|etc.

    # Status
    status = Column(String, nullable=False, default="pending", index=True)  # pending|running|completed|failed

    # Input data range
    data_from_date = Column(DateTime, nullable=False)
    data_to_date = Column(DateTime, nullable=False)

    # Results
    patterns_created = Column(Integer, default=0)
    patterns_updated = Column(Integer, default=0)
    records_processed = Column(Integer, default=0)

    # Error tracking
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('ix_job_status_created', 'status', 'created_at'),
    )

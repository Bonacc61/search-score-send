"""
Data Monetization Layer - Pattern Learning & Data Accrual

This layer learns from sourcing patterns and semantic search behavior to create
valuable datasets that can be sold to:
- AI training companies (Scale AI, Scale AI, Labelbox)
- Recruitment platforms needing training data
- HR tech companies building AI products
- Research institutions studying hiring patterns

Data is anonymized and structured for maximum value while maintaining privacy.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== Search Pattern Learning ====================

class SearchPatternType(str, Enum):
    """Types of search patterns we learn from"""
    BOOLEAN_QUERY = "boolean_query"
    SEMANTIC_EMBEDDING = "semantic_embedding"
    SKILL_COMBINATION = "skill_combination"
    LOCATION_PREFERENCE = "location_preference"
    SENIORITY_MAPPING = "seniority_mapping"
    PLATFORM_STRATEGY = "platform_strategy"


class SearchPattern(BaseModel):
    """
    Learned search pattern from successful candidate sourcing

    This captures "what queries work" for specific role types
    """
    pattern_id: str
    pattern_type: SearchPatternType

    # Input (job requirements)
    job_title: str = Field(..., description="Anonymized job title")
    job_category: str = Field(..., description="Engineering|Product|Sales|etc")
    seniority: str
    required_skills: List[str]

    # Learned query strategy
    successful_query: str = Field(..., description="The query that found good candidates")
    query_platform: str = Field(..., description="linkedin|github|stackoverflow")

    # Success metrics
    candidates_found: int
    candidates_qualified: int = Field(..., description="How many scored 80%+")
    average_score: float
    time_to_fill_estimate_days: Optional[int] = None

    # Pattern strength
    confidence_score: float = Field(..., ge=0, le=1, description="How confident we are in this pattern")
    usage_count: int = Field(default=1, description="How many times this pattern was successful")

    # Metadata
    learned_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: datetime = Field(default_factory=datetime.utcnow)
    geographic_region: Optional[str] = None  # For location-specific patterns


class SemanticQueryEmbedding(BaseModel):
    """
    Semantic embedding of successful job description → search query mappings

    Valuable for training retrieval models
    """
    embedding_id: str

    # Input
    jd_text_anonymized: str = Field(..., description="Job description (PII removed)")
    jd_embedding: List[float] = Field(..., description="Vector embedding of JD")

    # Output
    successful_queries: Dict[str, str] = Field(
        ...,
        description="Platform → query mapping that worked"
    )
    query_embeddings: Dict[str, List[float]] = Field(
        ...,
        description="Platform → query embedding"
    )

    # Success metrics
    retrieval_precision: float = Field(..., description="% of results that were qualified")
    retrieval_recall_estimate: float = Field(..., description="Estimated % of market covered")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    industry: Optional[str] = None
    company_size: Optional[str] = None  # startup|scaleup|enterprise


class SkillCombinationPattern(BaseModel):
    """
    Learned patterns about which skill combinations predict success

    Example: "Python + Django + PostgreSQL" candidates score higher than "Python + Flask + MongoDB"
    """
    pattern_id: str

    # Primary skill
    anchor_skill: str = Field(..., description="The main skill (e.g., 'Python')")

    # Combinations that work well together
    high_value_combinations: List[Dict[str, Any]] = Field(
        ...,
        description="Skill sets that produce high-scoring candidates"
    )
    # Example: [{"skills": ["Django", "PostgreSQL", "AWS"], "avg_score": 92.5, "count": 15}]

    # Combinations that don't work
    low_value_combinations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Skill sets that produce low-scoring candidates"
    )

    # Context
    job_category: str
    seniority_level: str

    # Statistical confidence
    sample_size: int
    confidence_interval: float

    # Metadata
    learned_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PlatformSourcingStrategy(BaseModel):
    """
    Learned strategies for which platforms work best for which roles

    Example: "Backend engineers: 60% GitHub, 30% LinkedIn, 10% StackOverflow"
    """
    strategy_id: str

    # Role context
    job_category: str
    seniority: str
    key_skills: List[str]

    # Platform distribution (where to search)
    platform_allocation: Dict[str, float] = Field(
        ...,
        description="Platform → % of search effort. Should sum to 1.0"
    )
    # Example: {"linkedin": 0.6, "github": 0.3, "stackoverflow": 0.1}

    # Platform-specific tactics
    platform_tactics: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Best practices per platform"
    )
    # Example: {
    #   "github": {
    #     "focus_on": "public_repos",
    #     "languages": ["Python", "Go"],
    #     "min_followers": 50
    #   }
    # }

    # Success metrics
    average_time_to_fill_days: float
    quality_score: float = Field(..., ge=0, le=100)

    # Metadata
    sample_size: int
    confidence: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== Candidate Quality Patterns ====================

class ScoringPattern(BaseModel):
    """
    Patterns about what predicts candidate quality

    This is valuable for training AI scoring models
    """
    pattern_id: str

    # Feature → Impact mapping
    feature_importance: Dict[str, float] = Field(
        ...,
        description="Which profile features predict high scores"
    )
    # Example: {
    #   "years_experience": 0.35,
    #   "github_contributions": 0.25,
    #   "open_source_projects": 0.20,
    #   "stackoverflow_reputation": 0.10,
    #   "linkedin_endorsements": 0.10
    # }

    # Role context
    job_category: str
    seniority: str

    # Statistical validation
    model_accuracy: float
    sample_size: int

    # Metadata
    learned_at: datetime = Field(default_factory=datetime.utcnow)


class MessagePersonalizationPattern(BaseModel):
    """
    Patterns about what makes outreach messages effective

    Valuable for training message generation models
    """
    pattern_id: str

    # Message characteristics
    personalization_elements: List[str] = Field(
        ...,
        description="What elements were personalized"
    )
    # Example: ["specific_project_mention", "skill_recognition", "company_culture_fit"]

    message_tone: str = Field(..., description="professional|casual|technical")
    message_length_chars: int

    # Effectiveness
    response_rate: Optional[float] = None  # If we have this data
    engagement_score: float = Field(..., description="Proxy metric for effectiveness")

    # Context
    job_category: str
    seniority: str
    platform: str

    # Example message (anonymized)
    anonymized_template: str = Field(
        ...,
        description="Message template with [PLACEHOLDERS] for learning"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== Structured Data Export (Scale AI Format) ====================

class DatasetType(str, Enum):
    """Types of datasets we can export for sale"""
    SEARCH_QUERY_PAIRS = "search_query_pairs"  # JD → Boolean query mappings
    SEMANTIC_EMBEDDINGS = "semantic_embeddings"  # Vector embeddings
    SKILL_TAXONOMY = "skill_taxonomy"  # Skill relationship graph
    SCORING_TRAINING_DATA = "scoring_training_data"  # Candidate profiles → scores
    MESSAGE_EFFECTIVENESS = "message_effectiveness"  # Messages → response rates
    MARKET_INTELLIGENCE = "market_intelligence"  # Hiring trends and patterns


class Scale AIDataRecord(BaseModel):
    """
    Single training data record formatted for Scale AI/Scale AI/similar platforms

    This is the format data buyers expect
    """
    record_id: str
    dataset_type: DatasetType

    # Input (X)
    input_data: Dict[str, Any] = Field(
        ...,
        description="The input features for training"
    )

    # Output (Y)
    ground_truth: Dict[str, Any] = Field(
        ...,
        description="The labeled output/target"
    )

    # Metadata for filtering/segmentation
    metadata: Dict[str, Any] = Field(
        ...,
        description="Industry, region, seniority, etc."
    )

    # Quality assurance
    confidence: float = Field(..., ge=0, le=1)
    validation_status: str = Field(default="validated")

    # Privacy
    anonymized: bool = Field(default=True)
    pii_removed: bool = Field(default=True)

    # Provenance
    created_at: datetime
    source: str = Field(default="search_score_send")


class DatasetExport(BaseModel):
    """
    Complete dataset export ready for sale
    """
    dataset_id: str
    dataset_type: DatasetType
    version: str = Field(..., description="Semantic versioning e.g. '1.2.0'")

    # Records
    records: List[Scale AIDataRecord]
    record_count: int

    # Quality metrics
    average_confidence: float
    validation_coverage: float = Field(..., description="% of records that are validated")

    # Commercial metadata
    price_per_record_usd: float
    total_value_usd: float
    license_type: str = Field(default="single_use")  # single_use|unlimited|subscription

    # Description for buyers
    description: str
    use_cases: List[str]

    # Statistics
    metadata_distribution: Dict[str, Dict[str, int]] = Field(
        ...,
        description="Breakdown by industry, region, etc."
    )

    # Export details
    exported_at: datetime = Field(default_factory=datetime.utcnow)
    format: str = Field(default="jsonl")
    size_mb: float


# ==================== Learning Pipeline Configuration ====================

class PatternLearningConfig(BaseModel):
    """Configuration for pattern learning pipeline"""

    # What to learn
    learn_search_patterns: bool = Field(default=True)
    learn_semantic_embeddings: bool = Field(default=True)
    learn_skill_combinations: bool = Field(default=True)
    learn_platform_strategies: bool = Field(default=True)
    learn_scoring_patterns: bool = Field(default=True)
    learn_message_patterns: bool = Field(default=True)

    # When to update patterns
    min_sample_size: int = Field(default=10, description="Minimum data points before creating pattern")
    update_frequency_days: int = Field(default=7, description="How often to retrain patterns")

    # Quality thresholds
    min_confidence: float = Field(default=0.7, ge=0, le=1)
    min_success_rate: float = Field(default=0.6, description="Min % of qualified candidates")

    # Privacy
    anonymize_before_learning: bool = Field(default=True)
    remove_company_names: bool = Field(default=True)
    remove_personal_identifiers: bool = Field(default=True)

    # Data export
    enable_data_export: bool = Field(default=True)
    export_format: str = Field(default="scalai_jsonl")


class DataMonetizationMetrics(BaseModel):
    """Metrics tracking the value of accrued data"""

    # Volume
    total_search_patterns: int
    total_semantic_embeddings: int
    total_skill_patterns: int
    total_scoring_patterns: int
    total_message_patterns: int

    # Quality
    average_pattern_confidence: float
    validation_coverage: float

    # Commercial value
    estimated_value_usd: float = Field(
        ...,
        description="Estimated market value of accrued data"
    )
    records_sold: int = Field(default=0)
    revenue_generated_usd: float = Field(default=0)

    # Growth
    patterns_learned_last_30_days: int
    growth_rate_percent: float

    # Updated
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# ==================== Data Marketplace API ====================

class DataProductListing(BaseModel):
    """A data product for sale on marketplace"""
    product_id: str
    name: str
    description: str

    # Product details
    dataset_type: DatasetType
    record_count: int
    quality_score: float = Field(..., ge=0, le=1)

    # Filtering capabilities
    available_filters: Dict[str, List[str]] = Field(
        ...,
        description="What filters buyers can apply"
    )
    # Example: {
    #   "industry": ["tech", "finance", "healthcare"],
    #   "region": ["US", "EU", "APAC"],
    #   "seniority": ["junior", "mid", "senior"]
    # }

    # Pricing
    price_per_record_usd: float
    min_purchase_records: int = Field(default=100)
    bulk_discounts: Dict[int, float] = Field(
        default_factory=dict,
        description="Quantity → discount % mapping"
    )

    # Sample
    sample_records: List[Scale AIDataRecord] = Field(
        default_factory=list,
        description="Free sample for buyers to evaluate"
    )

    # Metadata
    created_at: datetime
    updated_at: datetime
    total_sold: int = Field(default=0)


class DataPurchaseRequest(BaseModel):
    """Request to purchase dataset"""
    product_id: str
    buyer_email: str
    buyer_organization: str

    # Purchase details
    record_count: int
    filters: Dict[str, List[str]] = Field(default_factory=dict)

    # Licensing
    license_type: str = Field(default="single_use")
    use_case: str = Field(..., description="What will you use this data for?")

    # Payment (to be integrated with Stripe)
    payment_method_id: Optional[str] = None


class DataPurchase(BaseModel):
    """Completed data purchase"""
    purchase_id: str
    product_id: str
    buyer_email: str

    # Purchase details
    records_purchased: int
    filters_applied: Dict[str, List[str]]

    # Commercial
    unit_price_usd: float
    discount_applied_percent: float
    total_price_usd: float

    # Fulfillment
    download_url: str
    download_expires_at: datetime

    # Metadata
    purchased_at: datetime
    license_type: str

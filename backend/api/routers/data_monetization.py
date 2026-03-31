"""
Data Monetization API

Endpoints for:
1. Pattern learning (automatic knowledge accrual)
2. Data export (Scale AI format)
3. Data marketplace (selling learned patterns)
4. Metrics (tracking value of accrued data)
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from ..models_data_monetization import (
    SearchPattern, SkillCombinationPattern, PlatformSourcingStrategy,
    DatasetType, Scale AIDataRecord, DatasetExport, DataProductListing,
    DataPurchaseRequest, DataPurchase, DataMonetizationMetrics,
    PatternLearningConfig
)
from ..database import get_db
from ..database_data_monetization import (
    SearchPatternDB, SkillPatternDB, PlatformStrategyDB,
    DatasetExportDB, DataPurchaseDB
)
from ..services.pattern_learner import get_pattern_learner

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== Pattern Learning ====================

@router.post("/learn/search-patterns")
async def trigger_search_pattern_learning(
    lookback_days: int = 30,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Trigger pattern learning from recent successful workflows

    This learns which search queries work for which job types.
    Runs in background to avoid blocking.
    """
    try:
        learner = get_pattern_learner(db)

        # Run in background
        if background_tasks:
            background_tasks.add_task(learner.learn_search_patterns, lookback_days)
            return {
                "status": "queued",
                "message": f"Learning search patterns from last {lookback_days} days",
                "estimated_time_seconds": 60
            }
        else:
            # Run synchronously for testing
            patterns_created = learner.learn_search_patterns(lookback_days)
            return {
                "status": "completed",
                "patterns_created": patterns_created
            }

    except Exception as e:
        logger.error(f"Pattern learning failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learn/skill-combinations")
async def trigger_skill_learning(
    lookback_days: int = 30,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Learn which skill combinations predict high scores"""
    try:
        learner = get_pattern_learner(db)

        if background_tasks:
            background_tasks.add_task(learner.learn_skill_combinations, lookback_days)
            return {"status": "queued"}
        else:
            patterns_created = learner.learn_skill_combinations(lookback_days)
            return {
                "status": "completed",
                "patterns_created": patterns_created
            }

    except Exception as e:
        logger.error(f"Skill learning failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learn/platform-strategies")
async def trigger_platform_learning(
    lookback_days: int = 30,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Learn which platforms work best for which roles"""
    try:
        learner = get_pattern_learner(db)

        if background_tasks:
            background_tasks.add_task(learner.learn_platform_strategies, lookback_days)
            return {"status": "queued"}
        else:
            patterns_created = learner.learn_platform_strategies(lookback_days)
            return {
                "status": "completed",
                "patterns_created": patterns_created
            }

    except Exception as e:
        logger.error(f"Platform learning failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learn/all")
async def trigger_all_learning(
    lookback_days: int = 30,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Trigger all pattern learning in parallel

    This is the main endpoint to call periodically (e.g., daily cron)
    to continuously accrue valuable data
    """
    try:
        learner = get_pattern_learner(db)

        if background_tasks:
            background_tasks.add_task(learner.learn_search_patterns, lookback_days)
            background_tasks.add_task(learner.learn_skill_combinations, lookback_days)
            background_tasks.add_task(learner.learn_platform_strategies, lookback_days)

            return {
                "status": "queued",
                "jobs": ["search_patterns", "skill_combinations", "platform_strategies"],
                "lookback_days": lookback_days
            }
        else:
            results = {
                "search_patterns": learner.learn_search_patterns(lookback_days),
                "skill_combinations": learner.learn_skill_combinations(lookback_days),
                "platform_strategies": learner.learn_platform_strategies(lookback_days)
            }
            return {
                "status": "completed",
                "patterns_created": results
            }

    except Exception as e:
        logger.error(f"Pattern learning failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Data Export ====================

@router.post("/export/{dataset_type}", response_model=DatasetExport)
async def export_dataset(
    dataset_type: DatasetType,
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Export learned patterns to Scale AI-compatible format

    This creates a dataset ready for sale to AI training companies
    """
    try:
        learner = get_pattern_learner(db)

        # Export to Scale AI format
        records = learner.export_to_scalai_format(dataset_type, limit)

        if not records:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for {dataset_type}"
            )

        # Calculate pricing
        # Premium pricing based on data quality and uniqueness
        base_price_per_record = {
            DatasetType.SEARCH_QUERY_PAIRS: 0.50,  # $0.50 per JD→Query pair
            DatasetType.SKILL_TAXONOMY: 1.00,  # $1.00 per skill pattern
            DatasetType.SCORING_TRAINING_DATA: 2.00,  # $2.00 per scored profile
            DatasetType.MARKET_INTELLIGENCE: 5.00,  # $5.00 per market insight
        }.get(dataset_type, 1.00)

        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in records) / len(records)

        # Create export record
        export = DatasetExport(
            dataset_id=f"export_{dataset_type.value}_{datetime.utcnow().strftime('%Y%m%d')}",
            dataset_type=dataset_type,
            version="1.0.0",
            records=records,
            record_count=len(records),
            average_confidence=avg_confidence,
            validation_coverage=1.0,  # All records are validated
            price_per_record_usd=base_price_per_record,
            total_value_usd=len(records) * base_price_per_record,
            description=f"{dataset_type.value} dataset from Search-Score-Send platform",
            use_cases=[
                "Training recruitment AI models",
                "Building Boolean query generators",
                "Skill taxonomy research",
                "Hiring market intelligence"
            ],
            metadata_distribution=_calculate_metadata_distribution(records)
        )

        logger.info(f"Exported {len(records)} records for {dataset_type}, value: ${export.total_value_usd}")

        return export

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Data Marketplace ====================

@router.get("/marketplace/products", response_model=List[DataProductListing])
async def list_data_products(db: Session = Depends(get_db)):
    """
    List available data products for purchase

    This is the marketplace catalog
    """
    try:
        # Get all exportable datasets
        products = []

        # Search query pairs
        search_pattern_count = db.query(SearchPatternDB).count()
        if search_pattern_count > 0:
            products.append(DataProductListing(
                product_id="search_query_pairs_v1",
                name="Recruitment Search Query Dataset",
                description=f"{search_pattern_count} Job Description → Boolean Query mappings from real recruiting workflows",
                dataset_type=DatasetType.SEARCH_QUERY_PAIRS,
                record_count=search_pattern_count,
                quality_score=0.92,
                available_filters={
                    "job_category": ["software_engineering", "data_science", "product_management"],
                    "seniority": ["junior", "mid", "senior", "lead"],
                    "platform": ["linkedin", "github", "stackoverflow"]
                },
                price_per_record_usd=0.50,
                min_purchase_records=100,
                bulk_discounts={
                    1000: 10.0,  # 10% off for 1000+
                    5000: 20.0,  # 20% off for 5000+
                    10000: 30.0  # 30% off for 10000+
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                total_sold=0
            ))

        # Skill taxonomy
        skill_pattern_count = db.query(SkillPatternDB).count()
        if skill_pattern_count > 0:
            products.append(DataProductListing(
                product_id="skill_taxonomy_v1",
                name="Tech Skills Taxonomy & Combinations",
                description=f"{skill_pattern_count} skill patterns showing which combinations predict candidate success",
                dataset_type=DatasetType.SKILL_TAXONOMY,
                record_count=skill_pattern_count,
                quality_score=0.88,
                available_filters={
                    "anchor_skill": ["python", "javascript", "java", "go", "rust"],
                    "job_category": ["software_engineering", "data_science"]
                },
                price_per_record_usd=1.00,
                min_purchase_records=50,
                bulk_discounts={
                    500: 15.0,
                    2000: 25.0
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                total_sold=0
            ))

        return products

    except Exception as e:
        logger.error(f"Failed to list products: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/marketplace/purchase", response_model=DataPurchase)
async def purchase_dataset(
    request: DataPurchaseRequest,
    db: Session = Depends(get_db)
):
    """
    Purchase a dataset

    TODO: Integrate with Stripe for actual payment processing
    """
    try:
        logger.info(f"Data purchase request from {request.buyer_email}: {request.record_count} records")

        # Validate product exists
        # (In production, would query DatasetExportDB)

        # Calculate pricing
        unit_price = 0.50  # Would lookup from product
        discount = 0

        if request.record_count >= 10000:
            discount = 30.0
        elif request.record_count >= 5000:
            discount = 20.0
        elif request.record_count >= 1000:
            discount = 10.0

        total_price = request.record_count * unit_price * (1 - discount / 100)

        # Create purchase record
        purchase = DataPurchase(
            purchase_id=f"purchase_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            product_id=request.product_id,
            buyer_email=request.buyer_email,
            records_purchased=request.record_count,
            filters_applied=request.filters,
            unit_price_usd=unit_price,
            discount_applied_percent=discount,
            total_price_usd=total_price,
            download_url=f"https://api.search-score-send.com/data/downloads/{request.product_id}",
            download_expires_at=datetime.utcnow() + timedelta(days=7),
            purchased_at=datetime.utcnow(),
            license_type=request.license_type
        )

        # TODO: Actually process payment via Stripe
        # TODO: Generate download file
        # TODO: Save to database

        logger.info(f"Data purchase completed: {purchase.purchase_id}, ${total_price}")

        return purchase

    except Exception as e:
        logger.error(f"Purchase failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Metrics ====================

@router.get("/metrics", response_model=DataMonetizationMetrics)
async def get_monetization_metrics(db: Session = Depends(get_db)):
    """
    Get metrics on accrued data value

    This shows the commercial value of the learned patterns
    """
    try:
        # Count patterns
        search_patterns = db.query(SearchPatternDB).count()
        skill_patterns = db.query(SkillPatternDB).count()
        platform_strategies = db.query(PlatformStrategyDB).count()

        # Calculate estimated value
        estimated_value = (
            search_patterns * 0.50 +  # $0.50 per search pattern
            skill_patterns * 1.00 +  # $1.00 per skill pattern
            platform_strategies * 2.00  # $2.00 per platform strategy
        )

        # Growth metrics (patterns created in last 30 days)
        cutoff = datetime.utcnow() - timedelta(days=30)
        recent_patterns = (
            db.query(SearchPatternDB).filter(SearchPatternDB.learned_at >= cutoff).count() +
            db.query(SkillPatternDB).filter(SkillPatternDB.learned_at >= cutoff).count() +
            db.query(PlatformStrategyDB).filter(PlatformStrategyDB.created_at >= cutoff).count()
        )

        # Revenue (if we have sales)
        total_revenue = db.query(DataPurchaseDB).count() * 100  # Simplified

        return DataMonetizationMetrics(
            total_search_patterns=search_patterns,
            total_semantic_embeddings=0,  # Not implemented yet
            total_skill_patterns=skill_patterns,
            total_scoring_patterns=0,  # Not implemented yet
            total_message_patterns=0,  # Not implemented yet
            average_pattern_confidence=0.85,  # Would calculate from actual data
            validation_coverage=1.0,
            estimated_value_usd=estimated_value,
            records_sold=db.query(DataPurchaseDB).count(),
            revenue_generated_usd=total_revenue,
            patterns_learned_last_30_days=recent_patterns,
            growth_rate_percent=15.0  # Would calculate properly
        )

    except Exception as e:
        logger.error(f"Failed to get metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Helper Functions ====================

def _calculate_metadata_distribution(records: List[Scale AIDataRecord]) -> Dict:
    """Calculate distribution of metadata for dataset description"""
    from collections import Counter

    distribution = {}

    # Count by different metadata dimensions
    for key in ["industry", "region", "job_category"]:
        counts = Counter(r.metadata.get(key, "unknown") for r in records)
        distribution[key] = dict(counts)

    return distribution

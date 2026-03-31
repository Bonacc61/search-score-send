"""
Pattern Learning Service

Learns from successful sourcing workflows to create valuable, sellable datasets.
This is the core monetization layer - it accrues knowledge that can be sold to:
- AI training companies (ScalAI, Scale AI)
- Recruitment platforms
- HR tech companies
- Research institutions
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from collections import defaultdict, Counter
import statistics

from ..database import Candidate, WorkflowExecution
from ..database_data_monetization import (
    SearchPatternDB, SemanticEmbeddingDB, SkillPatternDB,
    PlatformStrategyDB, ScoringPatternDB, MessagePatternDB
)
from ..models_data_monetization import (
    SearchPattern, SearchPatternType,
    SkillCombinationPattern, PlatformSourcingStrategy,
    ScoringPattern, MessagePersonalizationPattern,
    ScalAIDataRecord, DatasetType
)

logger = logging.getLogger(__name__)


class PatternLearner:
    """
    Learns patterns from successful workflows

    This class analyzes completed workflows to extract:
    1. Search patterns (which queries work for which roles)
    2. Skill combinations (which skills together predict success)
    3. Platform strategies (which platforms work best)
    4. Scoring patterns (what predicts candidate quality)
    5. Message patterns (what makes outreach effective)
    """

    def __init__(self, db: Session, config: Dict[str, Any] = None):
        self.db = db
        self.config = config or {
            "min_sample_size": 10,
            "min_confidence": 0.7,
            "min_success_rate": 0.6,
            "anonymize": True
        }

    # ==================== Search Pattern Learning ====================

    def learn_search_patterns(self, lookback_days: int = 30) -> int:
        """
        Learn which search queries work for which job types

        Returns: Number of patterns created/updated
        """
        logger.info(f"Learning search patterns from last {lookback_days} days")

        # Get completed workflows with qualified candidates
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)

        workflows = self.db.query(WorkflowExecution).filter(
            WorkflowExecution.status == "completed",
            WorkflowExecution.completed_at >= cutoff_date,
            WorkflowExecution.candidates_qualified > 0
        ).all()

        logger.info(f"Found {len(workflows)} successful workflows to learn from")

        patterns_created = 0

        # Group by job category + seniority + platform
        grouped = defaultdict(list)

        for workflow in workflows:
            if not workflow.extracted_jd:
                continue

            jd = workflow.extracted_jd
            job_category = self._categorize_job(jd.get("title", ""))
            seniority = jd.get("seniority", "mid")

            # Get candidates from this workflow
            candidates = self.db.query(Candidate).filter(
                Candidate.execution_id == workflow.execution_id
            ).all()

            if not candidates:
                continue

            # Analyze by platform
            by_platform = defaultdict(list)
            for candidate in candidates:
                by_platform[candidate.platform].append(candidate)

            # Create pattern for each platform
            for platform, platform_candidates in by_platform.items():
                if len(platform_candidates) < self.config["min_sample_size"]:
                    continue

                qualified = [c for c in platform_candidates if c.overall_score and c.overall_score >= 80]
                success_rate = len(qualified) / len(platform_candidates) if platform_candidates else 0

                if success_rate < self.config["min_success_rate"]:
                    continue

                key = (job_category, seniority, platform)
                grouped[key].append({
                    "workflow": workflow,
                    "jd": jd,
                    "candidates": platform_candidates,
                    "qualified": qualified,
                    "success_rate": success_rate,
                    "avg_score": statistics.mean([c.overall_score for c in qualified if c.overall_score])
                })

        # Create patterns from grouped data
        for (job_category, seniority, platform), instances in grouped.items():
            if len(instances) < self.config["min_sample_size"]:
                continue

            # Find common successful query pattern
            # (In production, this would use more sophisticated NLP/pattern extraction)
            successful_query = self._extract_common_query(instances, platform)

            # Calculate aggregate metrics
            total_candidates = sum(len(inst["candidates"]) for inst in instances)
            total_qualified = sum(len(inst["qualified"]) for inst in instances)
            avg_score = statistics.mean([inst["avg_score"] for inst in instances])

            # Extract common skills
            all_skills = []
            for inst in instances:
                all_skills.extend(inst["jd"].get("must_have_skills", []))
            common_skills = [skill for skill, count in Counter(all_skills).most_common(5)]

            # Create or update pattern
            pattern = SearchPatternDB(
                pattern_type=SearchPatternType.BOOLEAN_QUERY.value,
                job_title=f"{seniority} {job_category}",  # Anonymized
                job_category=job_category,
                seniority=seniority,
                required_skills=common_skills,
                successful_query=successful_query,
                query_platform=platform,
                candidates_found=total_candidates,
                candidates_qualified=total_qualified,
                average_score=avg_score,
                confidence_score=min(len(instances) / 50, 1.0),  # More data = higher confidence
                usage_count=len(instances)
            )

            self.db.add(pattern)
            patterns_created += 1

        self.db.commit()
        logger.info(f"Created {patterns_created} search patterns")
        return patterns_created

    # ==================== Skill Combination Learning ====================

    def learn_skill_combinations(self, lookback_days: int = 30) -> int:
        """
        Learn which skill combinations predict high scores

        Example: "Python + Django + PostgreSQL" scores better than "Python + Flask + MySQL"
        """
        logger.info(f"Learning skill combinations from last {lookback_days} days")

        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)

        # Get all scored candidates
        candidates = self.db.query(Candidate).filter(
            Candidate.created_at >= cutoff_date,
            Candidate.overall_score.isnot(None)
        ).all()

        logger.info(f"Analyzing {len(candidates)} scored candidates")

        # Group by anchor skill
        by_anchor_skill = defaultdict(list)

        for candidate in candidates:
            if not candidate.skills or len(candidate.skills) < 2:
                continue

            # Each skill can be an anchor
            for skill in candidate.skills[:3]:  # Focus on top 3 skills
                by_anchor_skill[skill.lower()].append({
                    "skills": [s.lower() for s in candidate.skills],
                    "score": candidate.overall_score,
                    "platform": candidate.platform
                })

        patterns_created = 0

        # Analyze each anchor skill
        for anchor_skill, skill_sets in by_anchor_skill.items():
            if len(skill_sets) < self.config["min_sample_size"]:
                continue

            # Find high-value combinations
            combinations = defaultdict(list)

            for item in skill_sets:
                # Get other skills (excluding anchor)
                other_skills = tuple(sorted([s for s in item["skills"] if s != anchor_skill][:3]))
                if other_skills:
                    combinations[other_skills].append(item["score"])

            # Calculate averages
            combination_scores = {
                combo: {
                    "avg_score": statistics.mean(scores),
                    "count": len(scores),
                    "skills": list(combo)
                }
                for combo, scores in combinations.items()
                if len(scores) >= 3  # Need at least 3 examples
            }

            if not combination_scores:
                continue

            # Sort by average score
            sorted_combos = sorted(
                combination_scores.items(),
                key=lambda x: x[1]["avg_score"],
                reverse=True
            )

            # Top combinations = high value
            high_value = [
                {
                    "skills": combo_data["skills"],
                    "avg_score": combo_data["avg_score"],
                    "count": combo_data["count"]
                }
                for combo, combo_data in sorted_combos[:5]
                if combo_data["avg_score"] >= 80
            ]

            # Bottom combinations = low value
            low_value = [
                {
                    "skills": combo_data["skills"],
                    "avg_score": combo_data["avg_score"],
                    "count": combo_data["count"]
                }
                for combo, combo_data in sorted_combos[-3:]
                if combo_data["avg_score"] < 70
            ]

            if not high_value:
                continue

            # Create pattern
            pattern = SkillPatternDB(
                anchor_skill=anchor_skill,
                high_value_combinations=high_value,
                low_value_combinations=low_value,
                job_category="software_engineering",  # Could be inferred from workflow
                seniority_level="mid",  # Could be inferred
                sample_size=len(skill_sets),
                confidence_interval=0.85  # Simplified - would calculate properly in production
            )

            self.db.add(pattern)
            patterns_created += 1

        self.db.commit()
        logger.info(f"Created {patterns_created} skill combination patterns")
        return patterns_created

    # ==================== Platform Strategy Learning ====================

    def learn_platform_strategies(self, lookback_days: int = 30) -> int:
        """
        Learn which platforms work best for which role types
        """
        logger.info(f"Learning platform strategies from last {lookback_days} days")

        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)

        # Get completed workflows
        workflows = self.db.query(WorkflowExecution).filter(
            WorkflowExecution.status == "completed",
            WorkflowExecution.completed_at >= cutoff_date,
            WorkflowExecution.candidates_qualified > 0
        ).all()

        # Group by job category
        by_category = defaultdict(list)

        for workflow in workflows:
            if not workflow.extracted_jd:
                continue

            category = self._categorize_job(workflow.extracted_jd.get("title", ""))
            seniority = workflow.extracted_jd.get("seniority", "mid")

            # Get platform distribution for this workflow
            candidates = self.db.query(Candidate).filter(
                Candidate.execution_id == workflow.execution_id
            ).all()

            platform_stats = defaultdict(lambda: {"found": 0, "qualified": 0})

            for candidate in candidates:
                platform_stats[candidate.platform]["found"] += 1
                if candidate.overall_score and candidate.overall_score >= 80:
                    platform_stats[candidate.platform]["qualified"] += 1

            by_category[(category, seniority)].append({
                "workflow": workflow,
                "platform_stats": dict(platform_stats),
                "total_candidates": len(candidates)
            })

        patterns_created = 0

        # Create strategies
        for (category, seniority), instances in by_category.items():
            if len(instances) < self.config["min_sample_size"]:
                continue

            # Aggregate platform performance
            platform_totals = defaultdict(lambda: {"found": 0, "qualified": 0})

            for inst in instances:
                for platform, stats in inst["platform_stats"].items():
                    platform_totals[platform]["found"] += stats["found"]
                    platform_totals[platform]["qualified"] += stats["qualified"]

            total_found = sum(p["found"] for p in platform_totals.values())

            if total_found == 0:
                continue

            # Calculate allocation (as percentage of effort)
            platform_allocation = {
                platform: stats["found"] / total_found
                for platform, stats in platform_totals.items()
            }

            # Calculate quality per platform
            platform_quality = {
                platform: (stats["qualified"] / stats["found"] * 100 if stats["found"] > 0 else 0)
                for platform, stats in platform_totals.items()
            }

            # Create strategy
            pattern = PlatformStrategyDB(
                job_category=category,
                seniority=seniority,
                key_skills=[],  # Would extract from workflows
                platform_allocation=platform_allocation,
                platform_tactics={
                    platform: {
                        "quality_score": platform_quality[platform],
                        "total_found": stats["found"],
                        "success_rate": stats["qualified"] / stats["found"] if stats["found"] > 0 else 0
                    }
                    for platform, stats in platform_totals.items()
                },
                average_time_to_fill_days=30.0,  # Would calculate from actual data
                quality_score=statistics.mean(platform_quality.values()) if platform_quality else 0,
                sample_size=len(instances),
                confidence=min(len(instances) / 50, 1.0)
            )

            self.db.add(pattern)
            patterns_created += 1

        self.db.commit()
        logger.info(f"Created {patterns_created} platform strategies")
        return patterns_created

    # ==================== Helper Methods ====================

    def _categorize_job(self, title: str) -> str:
        """Categorize job title into broad category"""
        title_lower = title.lower()

        if any(term in title_lower for term in ["engineer", "developer", "programmer"]):
            return "software_engineering"
        elif any(term in title_lower for term in ["data", "scientist", "analyst"]):
            return "data_science"
        elif any(term in title_lower for term in ["product", "manager"]):
            return "product_management"
        elif any(term in title_lower for term in ["designer", "ux", "ui"]):
            return "design"
        elif any(term in title_lower for term in ["sales", "account"]):
            return "sales"
        else:
            return "other"

    def _extract_common_query(self, instances: List[Dict], platform: str) -> str:
        """
        Extract common query pattern from successful instances

        In production, this would use NLP to find common Boolean query structures
        For now, simplified version
        """
        # This is a placeholder - in production would analyze actual queries
        # and extract common patterns using NLP

        if not instances:
            return ""

        # Get the first successful query as representative
        first_instance = instances[0]
        jd = first_instance["jd"]

        # Construct representative query
        skills = jd.get("must_have_skills", [])[:3]
        query = " AND ".join(skills)

        return query

    # ==================== Export to ScalAI Format ====================

    def export_to_scalai_format(
        self,
        dataset_type: DatasetType,
        limit: Optional[int] = None
    ) -> List[ScalAIDataRecord]:
        """
        Export learned patterns to ScalAI-compatible format for sale

        Args:
            dataset_type: Type of dataset to export
            limit: Max number of records to export

        Returns:
            List of ScalAI-formatted records ready for sale
        """
        records = []

        if dataset_type == DatasetType.SEARCH_QUERY_PAIRS:
            # Export search patterns as JD → Query pairs
            patterns = self.db.query(SearchPatternDB).order_by(
                SearchPatternDB.confidence_score.desc()
            ).limit(limit or 10000).all()

            for pattern in patterns:
                record = ScalAIDataRecord(
                    record_id=pattern.id,
                    dataset_type=dataset_type,
                    input_data={
                        "job_title": pattern.job_title,
                        "job_category": pattern.job_category,
                        "seniority": pattern.seniority,
                        "required_skills": pattern.required_skills
                    },
                    ground_truth={
                        "query": pattern.successful_query,
                        "platform": pattern.query_platform,
                        "expected_success_rate": pattern.candidates_qualified / pattern.candidates_found if pattern.candidates_found > 0 else 0
                    },
                    metadata={
                        "industry": "technology",  # Would be actual industry
                        "region": pattern.geographic_region or "global",
                        "confidence": pattern.confidence_score
                    },
                    confidence=pattern.confidence_score,
                    created_at=pattern.learned_at
                )
                records.append(record)

        elif dataset_type == DatasetType.SKILL_TAXONOMY:
            # Export skill combination patterns
            patterns = self.db.query(SkillPatternDB).limit(limit or 10000).all()

            for pattern in patterns:
                record = ScalAIDataRecord(
                    record_id=pattern.id,
                    dataset_type=dataset_type,
                    input_data={
                        "anchor_skill": pattern.anchor_skill,
                        "job_category": pattern.job_category,
                        "seniority": pattern.seniority_level
                    },
                    ground_truth={
                        "high_value_combinations": pattern.high_value_combinations,
                        "low_value_combinations": pattern.low_value_combinations
                    },
                    metadata={
                        "sample_size": pattern.sample_size,
                        "confidence_interval": pattern.confidence_interval
                    },
                    confidence=min(pattern.sample_size / 100, 1.0),
                    created_at=pattern.learned_at
                )
                records.append(record)

        logger.info(f"Exported {len(records)} records in ScalAI format for {dataset_type}")
        return records


# Global instance
pattern_learner: Optional[PatternLearner] = None


def get_pattern_learner(db: Session) -> PatternLearner:
    """Get or create pattern learner instance"""
    return PatternLearner(db)

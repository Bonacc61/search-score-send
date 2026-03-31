"""
Scale AI Data Exporter

Exports learned patterns in Scale AI's required formats:
1. LLM Fine-tuning: CSV with prompt/response columns
2. Annotation/Labeling: JSON with task structure
3. General Training Data: JSONL with metadata

Based on Scale AI documentation:
- LLM Engine: CSV with "prompt" and "response" columns (max 100K rows)
- Rapid API: JSON annotation format with task_id, annotations, attributes
- Recommended: Minimum 200 rows for effective fine-tuning
"""
import csv
import json
import logging
from typing import List, Dict, Any, Optional
from io import StringIO
from datetime import datetime

from ..models_data_monetization import (
    SearchPattern, SkillCombinationPattern,
    ScaleAIDataRecord, DatasetType
)

logger = logging.getLogger(__name__)


class ScaleAIExporter:
    """
    Export training data in Scale AI's required formats

    Supports multiple export formats based on use case:
    - CSV: For LLM fine-tuning (Scale LLM Engine)
    - JSON: For annotation tasks (Scale Rapid API)
    - JSONL: For general ML training data
    """

    # ==================== CSV Format (LLM Fine-tuning) ====================

    @staticmethod
    def export_search_patterns_to_csv(patterns: List[SearchPattern]) -> str:
        """
        Export search patterns as CSV for Scale AI LLM Engine fine-tuning

        Format: prompt,response
        - Prompt: Job description requirements
        - Response: Boolean search query

        Use case: Training an LLM to generate Boolean queries from JDs
        """
        output = StringIO()
        writer = csv.writer(output)

        # Header row (required by Scale AI)
        writer.writerow(["prompt", "response"])

        for pattern in patterns:
            # Construct prompt (input to LLM)
            prompt = f"""Generate a Boolean search query for this job:
Title: {pattern.job_title}
Seniority: {pattern.seniority}
Required Skills: {', '.join(pattern.required_skills)}
Platform: {pattern.query_platform}"""

            # Response (expected output from LLM)
            response = pattern.successful_query

            writer.writerow([prompt, response])

        csv_content = output.getvalue()
        output.close()

        logger.info(f"Exported {len(patterns)} search patterns to Scale AI CSV format")
        return csv_content

    @staticmethod
    def export_skill_patterns_to_csv(patterns: List[SkillCombinationPattern]) -> str:
        """
        Export skill combination insights as CSV for LLM training

        Use case: Training an LLM to recommend skill combinations
        """
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(["prompt", "response"])

        for pattern in patterns:
            # Prompt: Ask for skill recommendations
            prompt = f"""What skills pair well with {pattern.anchor_skill} for a {pattern.job_category} role at {pattern.seniority_level} level?"""

            # Response: Structured recommendations
            high_value = pattern.high_value_combinations[:3]  # Top 3
            response_parts = []

            for combo in high_value:
                skills_str = ", ".join(combo["skills"])
                score = combo["avg_score"]
                response_parts.append(f"{skills_str} (average score: {score:.1f}%)")

            response = "Top skill combinations:\n" + "\n".join(response_parts)

            writer.writerow([prompt, response])

        csv_content = output.getvalue()
        output.close()

        logger.info(f"Exported {len(patterns)} skill patterns to Scale AI CSV format")
        return csv_content

    # ==================== JSON Format (Annotation Tasks) ====================

    @staticmethod
    def export_to_annotation_json(
        patterns: List[Any],
        task_type: str = "text_classification"
    ) -> Dict[str, Any]:
        """
        Export as Scale AI Rapid API annotation format

        Use case: Creating labeled datasets for supervised learning
        Format: Scale AI JSON annotation structure
        """
        tasks = []

        for idx, pattern in enumerate(patterns):
            task = {
                "task_id": f"task_{idx:06d}",
                "type": task_type,
                "status": "completed",
                "params": {},
                "response": {
                    "annotations": []
                },
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "dataset_type": "recruitment_patterns",
                    "quality_score": getattr(pattern, "confidence_score", 1.0)
                }
            }

            # Add pattern-specific data
            if hasattr(pattern, "job_category"):
                task["params"]["text"] = str(pattern.__dict__)
                task["response"]["annotations"].append({
                    "label": pattern.job_category,
                    "confidence": getattr(pattern, "confidence_score", 1.0),
                    "attributes": {
                        "seniority": getattr(pattern, "seniority", "unknown"),
                        "platform": getattr(pattern, "query_platform", "unknown")
                    }
                })

            tasks.append(task)

        output = {
            "version": "1.0",
            "format": "scale_ai_annotation",
            "task_count": len(tasks),
            "tasks": tasks,
            "exported_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Exported {len(tasks)} tasks to Scale AI annotation JSON format")
        return output

    # ==================== JSONL Format (General ML Training) ====================

    @staticmethod
    def export_to_jsonl(records: List[ScaleAIDataRecord]) -> str:
        """
        Export as JSONL (JSON Lines) for general ML training

        Industry standard format:
        - Each line is a complete JSON object
        - UTF-8 encoded
        - Newline-delimited

        Compatible with:
        - Scale AI Data Engine
        - OpenAI fine-tuning
        - HuggingFace datasets
        - AWS SageMaker
        - Google Vertex AI
        """
        lines = []

        for record in records:
            # Each record becomes one line
            line_data = {
                "id": record.record_id,
                "input": record.input_data,
                "output": record.ground_truth,
                "metadata": {
                    **record.metadata,
                    "confidence": record.confidence,
                    "validation_status": record.validation_status,
                    "anonymized": record.anonymized,
                    "pii_removed": record.pii_removed,
                    "created_at": record.created_at.isoformat(),
                    "source": record.source
                }
            }

            # Convert to JSON string (no pretty printing)
            json_str = json.dumps(line_data, ensure_ascii=False)
            lines.append(json_str)

        # Join with newlines (JSONL format)
        jsonl_content = "\n".join(lines)

        logger.info(f"Exported {len(records)} records to JSONL format ({len(jsonl_content)} bytes)")
        return jsonl_content

    # ==================== Alpaca Format (Instruction Tuning) ====================

    @staticmethod
    def export_to_alpaca_format(patterns: List[SearchPattern]) -> str:
        """
        Export in Alpaca instruction-tuning format

        Format: {"instruction": "...", "input": "...", "output": "..."}

        Popular for LLM fine-tuning:
        - Stanford Alpaca
        - Vicuna
        - LLaMA fine-tuning
        """
        lines = []

        for pattern in patterns:
            record = {
                "instruction": f"Generate a {pattern.query_platform} Boolean search query for recruiting.",
                "input": f"Job: {pattern.job_title}\nSkills: {', '.join(pattern.required_skills)}\nSeniority: {pattern.seniority}",
                "output": pattern.successful_query
            }

            lines.append(json.dumps(record, ensure_ascii=False))

        jsonl_content = "\n".join(lines)

        logger.info(f"Exported {len(patterns)} patterns to Alpaca JSONL format")
        return jsonl_content

    # ==================== OpenAI Chat Format ====================

    @staticmethod
    def export_to_openai_chat_format(patterns: List[SearchPattern]) -> str:
        """
        Export in OpenAI fine-tuning chat format

        Format: {"messages": [{"role": "...", "content": "..."}]}

        Use case: Fine-tuning GPT-3.5/GPT-4 models
        """
        lines = []

        for pattern in patterns:
            record = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a recruitment sourcing expert. Generate Boolean search queries for finding candidates."
                    },
                    {
                        "role": "user",
                        "content": f"Create a {pattern.query_platform} search query for: {pattern.job_title}, requiring {', '.join(pattern.required_skills[:3])}"
                    },
                    {
                        "role": "assistant",
                        "content": pattern.successful_query
                    }
                ]
            }

            lines.append(json.dumps(record, ensure_ascii=False))

        jsonl_content = "\n".join(lines)

        logger.info(f"Exported {len(patterns)} patterns to OpenAI chat JSONL format")
        return jsonl_content

    # ==================== Quality Validation ====================

    @staticmethod
    def validate_csv_for_scale_ai(csv_content: str) -> Dict[str, Any]:
        """
        Validate CSV meets Scale AI LLM Engine requirements

        Requirements:
        - Has "prompt" and "response" columns
        - Between 200 and 100,000 rows
        - No empty cells
        - UTF-8 encoded
        """
        lines = csv_content.strip().split("\n")
        row_count = len(lines) - 1  # Exclude header

        issues = []

        # Check header
        header = lines[0].split(",")
        if header != ["prompt", "response"]:
            issues.append(f"Invalid header. Expected ['prompt', 'response'], got {header}")

        # Check row count
        if row_count < 200:
            issues.append(f"Too few rows ({row_count}). Scale AI recommends minimum 200 rows.")
        elif row_count > 100000:
            issues.append(f"Too many rows ({row_count}). Scale AI supports maximum 100,000 rows.")

        # Sample check for empty cells
        for i, line in enumerate(lines[1:11], 1):  # Check first 10 rows
            parts = line.split(",")
            if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
                issues.append(f"Row {i} has empty cells")

        return {
            "valid": len(issues) == 0,
            "row_count": row_count,
            "issues": issues,
            "recommendation": "Ready for Scale AI LLM Engine" if len(issues) == 0 else "Fix issues before uploading"
        }

    # ==================== Format Detection ====================

    @staticmethod
    def get_recommended_format(dataset_type: DatasetType, use_case: str = "llm_training") -> str:
        """
        Recommend export format based on dataset type and use case

        Args:
            dataset_type: Type of data being exported
            use_case: What the buyer will use it for

        Returns:
            Recommended format name
        """
        recommendations = {
            ("search_query_pairs", "llm_training"): "csv_scale_ai",
            ("search_query_pairs", "instruction_tuning"): "alpaca_jsonl",
            ("skill_taxonomy", "llm_training"): "csv_scale_ai",
            ("scoring_training_data", "supervised_learning"): "annotation_json",
            ("market_intelligence", "analytics"): "jsonl",
        }

        key = (dataset_type.value if hasattr(dataset_type, "value") else dataset_type, use_case)
        return recommendations.get(key, "jsonl")


# Global instance
scale_ai_exporter = ScaleAIExporter()

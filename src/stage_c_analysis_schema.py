"""Stage C Analysis Schema.

Defines schemas and templates for evaluation result artifacts.
Enforces that empty result placeholders explicitly state NO_EMPIRICAL_RESULTS_PRESENT.
"""

from typing import Any, Dict


RESULTS_ARTIFACT_JSON_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "StageCEvaluationResult",
    "type": "object",
    "required": [
        "schema_version",
        "benchmark_stage",
        "evaluation_status",
        "total_tasks_registered",
        "tasks_evaluated"
    ],
    "properties": {
        "schema_version": {"type": "string"},
        "benchmark_stage": {"type": "string", "enum": ["STAGE_C"]},
        "evaluation_status": {
            "type": "string",
            "enum": ["NO_EMPIRICAL_RESULTS_PRESENT", "COMPLETED", "PARTIAL"]
        },
        "reason": {"type": "string"},
        "total_tasks_registered": {"type": "integer", "minimum": 0},
        "tasks_evaluated": {"type": "integer", "minimum": 0},
        "metrics": {"type": "object"},
        "epistemic_notice": {"type": "string"}
    },
    "additionalProperties": False
}


def get_empty_results_template() -> Dict[str, Any]:
    """Generates the canonical empty results artifact declaring zero empirical scores."""
    return {
        "schema_version": "1.0.0",
        "benchmark_stage": "STAGE_C",
        "evaluation_status": "NO_EMPIRICAL_RESULTS_PRESENT",
        "reason": "Pre-registered benchmark foundation; model evaluations not executed.",
        "total_tasks_registered": 300,
        "tasks_evaluated": 0,
        "metrics": {},
        "epistemic_notice": (
            "This artifact preserves scientific integrity by recording benchmark infrastructure "
            "readiness without fabricated model performance numbers, accuracy claims, or p-values."
        )
    }

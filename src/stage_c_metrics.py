"""Stage C Metrics Engine.

Computes primary, secondary, and stratified metrics across benchmark task instances.
"""

from typing import Any, Dict, List, Optional
import math


class StageCMetrics:
    """Calculates evaluation metrics and stratified breakdowns."""

    @classmethod
    def compute_evaluation_metrics(cls, evaluated_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates individual task evaluations into comprehensive benchmark metrics."""
        if not evaluated_tasks:
            return {
                "status": "NO_EMPIRICAL_RESULTS_PRESENT",
                "total_tasks": 0,
                "summary": {}
            }

        total = len(evaluated_tasks)
        successes = sum(1 for t in evaluated_tasks if t.get("is_success", False))
        tool_correct_count = sum(1 for t in evaluated_tasks if t.get("tool_correct", False))
        schema_valid_count = sum(1 for t in evaluated_tasks if t.get("schema_valid", False))

        slot_precisions = [t.get("slot_precision", 0.0) for t in evaluated_tasks if not t.get("is_abstention_task", False)]
        slot_recalls = [t.get("slot_recall", 0.0) for t in evaluated_tasks if not t.get("is_abstention_task", False)]
        slot_f1s = [t.get("slot_f1", 0.0) for t in evaluated_tasks if not t.get("is_abstention_task", False)]

        mean_prec = (sum(slot_precisions) / len(slot_precisions)) if slot_precisions else 0.0
        mean_rec = (sum(slot_recalls) / len(slot_recalls)) if slot_recalls else 0.0
        mean_f1 = (sum(slot_f1s) / len(slot_f1s)) if slot_f1s else 0.0

        # Classification counts
        classification_counts: Dict[str, int] = {}
        for t in evaluated_tasks:
            clf = t.get("classification", "UNKNOWN")
            classification_counts[clf] = classification_counts.get(clf, 0) + 1

        summary = {
            "total_tasks": total,
            "successful_tasks": successes,
            "execution_success_rate": round(successes / total, 4) if total > 0 else 0.0,
            "tool_selection_accuracy": round(tool_correct_count / total, 4) if total > 0 else 0.0,
            "schema_compliance_rate": round(schema_valid_count / total, 4) if total > 0 else 0.0,
            "mean_slot_precision": round(mean_prec, 4),
            "mean_slot_recall": round(mean_rec, 4),
            "mean_slot_f1": round(mean_f1, 4),
            "classifications": classification_counts
        }

        # Breakdown by category
        by_category = cls._stratify_by_key(evaluated_tasks, "category")
        # Breakdown by mutation family
        by_family = cls._stratify_by_key(evaluated_tasks, "mutation_family")
        # Breakdown by domain
        by_domain = cls._stratify_by_key(evaluated_tasks, "domain")

        return {
            "status": "EVALUATED",
            "summary": summary,
            "by_category": by_category,
            "by_mutation_family": by_family,
            "by_domain": by_domain
        }

    @classmethod
    def _stratify_by_key(cls, tasks: List[Dict[str, Any]], key: str) -> Dict[str, Any]:
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for t in tasks:
            val = t.get(key, "unspecified")
            grouped.setdefault(val, []).append(t)

        stratified = {}
        for group_name, group_tasks in grouped.items():
            grp_total = len(group_tasks)
            grp_success = sum(1 for t in group_tasks if t.get("is_success", False))
            grp_schema = sum(1 for t in group_tasks if t.get("schema_valid", False))
            grp_tool = sum(1 for t in group_tasks if t.get("tool_correct", False))

            f1s = [t.get("slot_f1", 0.0) for t in group_tasks if not t.get("is_abstention_task", False)]
            grp_f1 = (sum(f1s) / len(f1s)) if f1s else 0.0

            stratified[group_name] = {
                "total_tasks": grp_total,
                "successful_tasks": grp_success,
                "success_rate": round(grp_success / grp_total, 4) if grp_total > 0 else 0.0,
                "schema_compliance_rate": round(grp_schema / grp_total, 4) if grp_total > 0 else 0.0,
                "tool_selection_accuracy": round(grp_tool / grp_total, 4) if grp_total > 0 else 0.0,
                "mean_slot_f1": round(grp_f1, 4)
            }
        return stratified

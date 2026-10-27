"""Stage C Human Review Adjudication Engine.

Generates adjudication queues for discordant reviews, clusters disagreement types,
and applies reviewer quality exclusion criteria.
"""

from typing import Any, Dict, List, Optional
import copy


class StageCReviewAdjudication:
    """Detects inter-reviewer discordances and prepares adjudication queues."""

    DISCORDANCE_TYPES = [
        "DISAGREE_TOOL_CHOICE",
        "DISAGREE_ABSTENTION",
        "DISAGREE_ARGUMENT_VALUES",
        "DISAGREE_AMBIGUITY_ASSESSMENT"
    ]

    @classmethod
    def generate_adjudication_queue(
        cls,
        submission_a: Dict[str, Any],
        submission_b: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identifies discordant task evaluations between two reviewers."""
        map_a = {r["blind_task_id"]: r for r in submission_a.get("reviews", [])}
        map_b = {r["blind_task_id"]: r for r in submission_b.get("reviews", [])}

        queue = []
        common_ids = sorted(list(set(map_a.keys()).intersection(set(map_b.keys()))))

        for tid in common_ids:
            item_a = map_a[tid]
            item_b = map_b[tid]

            abstain_a = item_a.get("abstain_from_invocation", False)
            abstain_b = item_b.get("abstain_from_invocation", False)
            tool_a = item_a.get("selected_tool_name")
            tool_b = item_b.get("selected_tool_name")
            ambig_a = item_a.get("is_ambiguous", False)
            ambig_b = item_b.get("is_ambiguous", False)

            discordances = []

            # 1. Abstention conflict
            if abstain_a != abstain_b:
                discordances.append("DISAGREE_ABSTENTION")

            # 2. Tool choice conflict
            elif not abstain_a and tool_a != tool_b:
                discordances.append("DISAGREE_TOOL_CHOICE")

            # 3. Argument values conflict
            elif not abstain_a and item_a.get("submitted_arguments") != item_b.get("submitted_arguments"):
                discordances.append("DISAGREE_ARGUMENT_VALUES")

            # 4. Ambiguity flag divergence
            if ambig_a != ambig_b:
                discordances.append("DISAGREE_AMBIGUITY_ASSESSMENT")

            if discordances:
                queue.append({
                    "adjudication_id": f"ADJ_{tid}",
                    "blind_task_id": tid,
                    "reviewer_a_id": submission_a.get("reviewer_pseudonym"),
                    "reviewer_b_id": submission_b.get("reviewer_pseudonym"),
                    "reviewer_a_response": item_a,
                    "reviewer_b_response": item_b,
                    "discordance_types": discordances,
                    "adjudication_status": "PENDING_THIRD_REVIEW",
                    "requires_third_reviewer": True
                })

        return queue

    @classmethod
    def apply_reviewer_exclusion_rules(
        cls,
        submission: Dict[str, Any],
        minimum_required_items: int = 25
    ) -> Dict[str, Any]:
        """Evaluates whether a submission satisfies quality thresholds or must be excluded."""
        reviews = submission.get("reviews", [])
        total = len(reviews)
        exclusions = []

        if total < minimum_required_items:
            exclusions.append(f"Incomplete submission: completed {total} items (minimum {minimum_required_items}).")

        confidences = [r.get("confidence_score", 0) for r in reviews if r.get("confidence_score") is not None]
        avg_conf = (sum(confidences) / len(confidences)) if confidences else 0.0

        if avg_conf < 2.0:
            exclusions.append(f"Abnormally low mean confidence score ({avg_conf:.2f} < 2.0).")

        return {
            "reviewer_pseudonym": submission.get("reviewer_pseudonym"),
            "is_excluded": len(exclusions) > 0,
            "exclusion_reasons": exclusions,
            "items_reviewed": total,
            "mean_confidence": round(avg_conf, 2)
        }

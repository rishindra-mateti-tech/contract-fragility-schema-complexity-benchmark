"""Stage C Human Review Agreement Analytics Engine.

Calculates inter-rater reliability metrics between independent reviewer pairs:
- Exact-match tool selection agreement
- Cohen's kappa for categorical selection / abstention decisions
- Field-level argument precision, recall, and F1
- Ambiguity flag rates
- Stratified agreement breakdowns
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import math


class StageCReviewAgreement:
    """Inter-rater reliability analysis routines."""

    @staticmethod
    def compute_cohens_kappa(labels_a: List[str], labels_b: List[str]) -> float:
        """Computes Cohen's kappa coefficient between two raters.
        
        kappa = (p_o - p_e) / (1 - p_e)
        """
        if len(labels_a) != len(labels_b) or len(labels_a) == 0:
            return 0.0

        n = len(labels_a)
        # Observed agreement
        observed_matches = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
        p_o = observed_matches / n

        # Marginal category frequencies
        cats = sorted(list(set(labels_a).union(set(labels_b))))
        count_a = {c: 0 for c in cats}
        count_b = {c: 0 for c in cats}

        for a, b in zip(labels_a, labels_b):
            count_a[a] += 1
            count_b[b] += 1

        # Expected chance agreement
        p_e = sum((count_a[c] / n) * (count_b[c] / n) for c in cats)

        if p_e >= 1.0:
            return 1.0 if p_o == 1.0 else 0.0

        kappa = (p_o - p_e) / (1.0 - p_e)
        return round(kappa, 4)

    @staticmethod
    def compute_field_level_agreement(
        args_a: Optional[Dict[str, Any]],
        args_b: Optional[Dict[str, Any]]
    ) -> Tuple[float, float, float]:
        """Computes precision, recall, and F1 between two argument dictionaries."""
        if args_a is None and args_b is None:
            return 1.0, 1.0, 1.0
        if args_a is None or args_b is None:
            return 0.0, 0.0, 0.0

        keys_a = set(args_a.keys())
        keys_b = set(args_b.keys())

        matched_keys = 0
        for k in keys_a.intersection(keys_b):
            val_a = args_a[k]
            val_b = args_b[k]
            if val_a == val_b:
                matched_keys += 1

        prec = (matched_keys / len(keys_b)) if keys_b else 0.0
        rec = (matched_keys / len(keys_a)) if keys_a else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

        return round(prec, 4), round(rec, 4), round(f1, 4)

    @classmethod
    def compute_pairwise_agreement(
        cls,
        submission_a: Dict[str, Any],
        submission_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compares two complete reviewer submissions on matching blind task IDs."""
        map_a = {r["blind_task_id"]: r for r in submission_a.get("reviews", [])}
        map_b = {r["blind_task_id"]: r for r in submission_b.get("reviews", [])}

        common_ids = sorted(list(set(map_a.keys()).intersection(set(map_b.keys()))))
        if not common_ids:
            return {
                "common_items_count": 0,
                "tool_selection_exact_match": 0.0,
                "abstention_exact_match": 0.0,
                "cohens_kappa": 0.0,
                "mean_field_f1": 0.0,
                "ambiguity_rate_a": 0.0,
                "ambiguity_rate_b": 0.0
            }

        actions_a = []
        actions_b = []
        field_f1_scores = []
        ambig_count_a = 0
        ambig_count_b = 0

        for tid in common_ids:
            item_a = map_a[tid]
            item_b = map_b[tid]

            # Represent decision label: tool name or 'ABSTAIN'
            label_a = "ABSTAIN" if item_a.get("abstain_from_invocation") else (item_a.get("selected_tool_name") or "NO_TOOL")
            label_b = "ABSTAIN" if item_b.get("abstain_from_invocation") else (item_b.get("selected_tool_name") or "NO_TOOL")

            actions_a.append(label_a)
            actions_b.append(label_b)

            if item_a.get("is_ambiguous"):
                ambig_count_a += 1
            if item_b.get("is_ambiguous"):
                ambig_count_b += 1

            if not item_a.get("abstain_from_invocation") and not item_b.get("abstain_from_invocation"):
                _, _, f1 = cls.compute_field_level_agreement(
                    item_a.get("submitted_arguments"),
                    item_b.get("submitted_arguments")
                )
                field_f1_scores.append(f1)

        total = len(common_ids)
        exact_matches = sum(1 for a, b in zip(actions_a, actions_b) if a == b)
        exact_rate = round(exact_matches / total, 4) if total else 0.0
        kappa = cls.compute_cohens_kappa(actions_a, actions_b)
        mean_f1 = round(sum(field_f1_scores) / len(field_f1_scores), 4) if field_f1_scores else 0.0

        return {
            "reviewer_a": submission_a.get("reviewer_pseudonym"),
            "reviewer_b": submission_b.get("reviewer_pseudonym"),
            "common_items_count": total,
            "overall_decision_exact_match_rate": exact_rate,
            "cohens_kappa": kappa,
            "mean_argument_field_f1": mean_f1,
            "ambiguity_rate_a": round(ambig_count_a / total, 4),
            "ambiguity_rate_b": round(ambig_count_b / total, 4)
        }

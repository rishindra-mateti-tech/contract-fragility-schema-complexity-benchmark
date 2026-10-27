"""Stage C Human Review Submission Validator.

Validates schema compliance, integrity hashing, blind task ID validity,
and author-side reconciliation for reviewer submissions.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import hashlib
import json
from pathlib import Path


class StageCHumanReviewSubmissionValidator:
    """Validates structure and cryptographic integrity of reviewer submission bundles."""

    VALID_CONFIDENCE_SCORES = {1, 2, 3, 4, 5}

    @classmethod
    def compute_submission_hash(cls, reviews: List[Dict[str, Any]]) -> str:
        """Computes deterministic SHA-256 integrity hash over sorted review items."""
        serialized = json.dumps(reviews, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @classmethod
    def validate_submission_bundle(
        cls,
        submission: Dict[str, Any],
        valid_blind_task_ids: Optional[Set[str]] = None
    ) -> Tuple[bool, List[str]]:
        """Validates all fields, confidence ranges, and integrity hashes of a submission."""
        errors: List[str] = []

        # 1. Root structure checks
        required_root = [
            "submission_version",
            "reviewer_pseudonym",
            "submission_timestamp",
            "total_items_reviewed",
            "reviews",
            "integrity_hash"
        ]
        for field in required_root:
            if field not in submission:
                errors.append(f"Missing required root field: '{field}'")

        pseudonym = submission.get("reviewer_pseudonym", "").strip()
        if not pseudonym:
            errors.append("reviewer_pseudonym must be a non-empty string.")

        reviews = submission.get("reviews", [])
        if not isinstance(reviews, list) or len(reviews) == 0:
            errors.append("Submission contains zero review items.")
            return False, errors

        # 2. Check declared vs actual items
        declared_total = submission.get("total_items_reviewed")
        if declared_total != len(reviews):
            errors.append(f"Declared items count ({declared_total}) does not match reviews array length ({len(reviews)}).")

        # 3. Verify integrity hash
        expected_hash = cls.compute_submission_hash(reviews)
        actual_hash = submission.get("integrity_hash", "")
        if actual_hash != expected_hash:
            errors.append(f"Integrity hash mismatch: expected {expected_hash}, got {actual_hash}")

        # 4. Validate each review item
        seen_ids = set()
        for idx, item in enumerate(reviews):
            tid = item.get("blind_task_id")
            if not tid:
                errors.append(f"Review item at index {idx} missing 'blind_task_id'.")
                continue

            if tid in seen_ids:
                errors.append(f"Duplicate review for blind task '{tid}' at index {idx}.")
            seen_ids.add(tid)

            if valid_blind_task_ids and tid not in valid_blind_task_ids:
                errors.append(f"Unknown blind task ID '{tid}' not present in registered sample.")

            confidence = item.get("confidence_score")
            if confidence not in cls.VALID_CONFIDENCE_SCORES:
                errors.append(f"Task '{tid}' has invalid confidence_score {confidence}. Must be 1 to 5.")

            abstain = item.get("abstain_from_invocation")
            if not isinstance(abstain, bool):
                errors.append(f"Task '{tid}' has invalid 'abstain_from_invocation' (must be bool).")

            arguments = item.get("submitted_arguments")
            if arguments is not None and not isinstance(arguments, dict):
                errors.append(f"Task '{tid}' has invalid 'submitted_arguments' (must be dict or null).")

        return (len(errors) == 0), errors

    @classmethod
    def reconcile_with_author_key(
        cls,
        submission: Dict[str, Any],
        author_key: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Maps blinded submissions to original task metadata for author-side analysis."""
        key_map = {entry["blind_task_id"]: entry for entry in author_key}
        reconciled = []

        for rev in submission.get("reviews", []):
            btid = rev.get("blind_task_id")
            orig = key_map.get(btid, {})

            reconciled.append({
                "blind_task_id": btid,
                "original_task_id": orig.get("original_task_id"),
                "original_category": orig.get("original_category"),
                "base_contract_id": orig.get("base_contract_id"),
                "mutation_family": orig.get("mutation_family"),
                "reviewer_selected_tool": rev.get("selected_tool_name"),
                "reviewer_arguments": rev.get("submitted_arguments"),
                "reviewer_abstained": rev.get("abstain_from_invocation"),
                "reviewer_confidence": rev.get("confidence_score"),
                "reviewer_flagged_ambiguous": rev.get("is_ambiguous"),
                "reviewer_notes": rev.get("reviewer_notes", ""),
                "gold_tool_name": orig.get("gold_tool_name"),
                "gold_arguments": orig.get("gold_arguments"),
                "is_gold_abstention": orig.get("is_gold_abstention")
            })

        return {
            "reviewer_pseudonym": submission.get("reviewer_pseudonym"),
            "submission_timestamp": submission.get("submission_timestamp"),
            "reconciled_items_count": len(reconciled),
            "reconciled_items": reconciled
        }

"""Tests for Stage C Human Review Submission Validator (Track 5).

Verifies submission bundle validation, cryptographic integrity hash checking,
rejection of malformed reviews, and author reconciliation mapping.
"""

from typing import Any, Dict
import json
from pathlib import Path
import pytest

from src.validate_stage_c_human_review_submission import StageCHumanReviewSubmissionValidator

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGES_DIR = REPO_ROOT / "data_stage_c" / "reviewer_packages"


@pytest.fixture
def sample_valid_submission():
    reviews = [
        {
            "blind_task_id": "BLIND_TASK_001",
            "selected_tool_name": "set_cache_entry",
            "submitted_arguments": {"key": "usr_10", "value": "active"},
            "abstain_from_invocation": False,
            "confidence_score": 5,
            "is_ambiguous": False,
            "reviewer_notes": "Clear instruction.",
            "item_timestamp": "2026-10-27T00:00:00Z"
        },
        {
            "blind_task_id": "BLIND_TASK_002",
            "selected_tool_name": None,
            "submitted_arguments": None,
            "abstain_from_invocation": True,
            "confidence_score": 4,
            "is_ambiguous": False,
            "reviewer_notes": "Required key omitted in prompt.",
            "item_timestamp": "2026-10-27T00:02:00Z"
        }
    ]
    integrity_hash = StageCHumanReviewSubmissionValidator.compute_submission_hash(reviews)
    return {
        "submission_version": "1.0.0",
        "reviewer_pseudonym": "evaluator_alpha",
        "submission_timestamp": "2026-10-27T00:05:00Z",
        "total_items_reviewed": 2,
        "reviews": reviews,
        "integrity_hash": integrity_hash
    }


def test_valid_submission_bundle_passes(sample_valid_submission):
    is_valid, errors = StageCHumanReviewSubmissionValidator.validate_submission_bundle(
        sample_valid_submission,
        valid_blind_task_ids={"BLIND_TASK_001", "BLIND_TASK_002"}
    )
    assert is_valid is True, f"Validation failed: {errors}"
    assert len(errors) == 0


def test_tampered_hash_fails(sample_valid_submission):
    tampered = dict(sample_valid_submission)
    tampered["integrity_hash"] = "0000000000000000000000000000000000000000000000000000000000000000"
    is_valid, errors = StageCHumanReviewSubmissionValidator.validate_submission_bundle(tampered)
    assert is_valid is False
    assert any("Integrity hash mismatch" in e for e in errors)


def test_invalid_confidence_score_fails(sample_valid_submission):
    tampered = dict(sample_valid_submission)
    # Shallow copy reviews list to avoid mutating fixture
    bad_reviews = [dict(r) for r in sample_valid_submission["reviews"]]
    bad_reviews[0]["confidence_score"] = 99  # Invalid score
    tampered["reviews"] = bad_reviews
    tampered["integrity_hash"] = StageCHumanReviewSubmissionValidator.compute_submission_hash(bad_reviews)

    is_valid, errors = StageCHumanReviewSubmissionValidator.validate_submission_bundle(tampered)
    assert is_valid is False
    assert any("invalid confidence_score" in e for e in errors)


def test_author_reconciliation_mapping(sample_valid_submission):
    author_key = [
        {
            "blind_task_id": "BLIND_TASK_001",
            "original_task_id": "TASK_SYNTH_AC_001",
            "original_category": "ARGUMENT_CONSTRUCTION",
            "base_contract_id": "BASE_SYNTH_001",
            "mutation_family": "CANONICAL",
            "gold_tool_name": "set_cache_entry",
            "gold_arguments": {"key": "usr_10", "value": "active"},
            "is_gold_abstention": False
        },
        {
            "blind_task_id": "BLIND_TASK_002",
            "original_task_id": "TASK_SYNTH_AB_001",
            "original_category": "ABSTENTION",
            "base_contract_id": "BASE_SYNTH_001",
            "mutation_family": "CANONICAL",
            "gold_tool_name": None,
            "gold_arguments": None,
            "is_gold_abstention": True
        }
    ]

    reconciled = StageCHumanReviewSubmissionValidator.reconcile_with_author_key(
        sample_valid_submission,
        author_key
    )

    assert reconciled["reviewer_pseudonym"] == "evaluator_alpha"
    assert reconciled["reconciled_items_count"] == 2

    item0 = reconciled["reconciled_items"][0]
    assert item0["blind_task_id"] == "BLIND_TASK_001"
    assert item0["original_task_id"] == "TASK_SYNTH_AC_001"
    assert item0["reviewer_selected_tool"] == "set_cache_entry"
    assert item0["gold_tool_name"] == "set_cache_entry"

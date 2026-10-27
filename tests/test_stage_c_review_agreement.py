"""Tests for Stage C Human Review Agreement Engine (Track 6).

Verifies Cohen's kappa calculations, exact match ratios, field-level F1,
and edge case handling for perfect and chance agreement.
"""

import pytest
from src.stage_c_review_agreement import StageCReviewAgreement


def test_cohens_kappa_perfect_agreement():
    labels_a = ["tool_1", "tool_2", "ABSTAIN", "tool_1"]
    labels_b = ["tool_1", "tool_2", "ABSTAIN", "tool_1"]
    kappa = StageCReviewAgreement.compute_cohens_kappa(labels_a, labels_b)
    assert kappa == 1.0


def test_cohens_kappa_zero_or_negative_agreement():
    # Complete disagreement
    labels_a = ["tool_1", "tool_1", "tool_1", "tool_1"]
    labels_b = ["tool_2", "tool_2", "tool_2", "tool_2"]
    kappa = StageCReviewAgreement.compute_cohens_kappa(labels_a, labels_b)
    assert kappa <= 0.0


def test_field_level_agreement():
    args_a = {"user_id": "usr_10", "ttl": 3600, "flag": True}
    args_b = {"user_id": "usr_10", "ttl": 3600, "flag": False}

    prec, rec, f1 = StageCReviewAgreement.compute_field_level_agreement(args_a, args_b)
    # 2 out of 3 matched exactly
    assert 0.65 < prec < 0.68
    assert 0.65 < rec < 0.68
    assert 0.65 < f1 < 0.68


def test_pairwise_agreement_with_mock_submissions():
    sub_a = {
        "reviewer_pseudonym": "rev_a",
        "reviews": [
            {"blind_task_id": "BLIND_TASK_001", "selected_tool_name": "t1", "submitted_arguments": {"k": "v"}, "abstain_from_invocation": False, "is_ambiguous": False},
            {"blind_task_id": "BLIND_TASK_002", "selected_tool_name": None, "submitted_arguments": None, "abstain_from_invocation": True, "is_ambiguous": True}
        ]
    }
    sub_b = {
        "reviewer_pseudonym": "rev_b",
        "reviews": [
            {"blind_task_id": "BLIND_TASK_001", "selected_tool_name": "t1", "submitted_arguments": {"k": "v"}, "abstain_from_invocation": False, "is_ambiguous": False},
            {"blind_task_id": "BLIND_TASK_002", "selected_tool_name": None, "submitted_arguments": None, "abstain_from_invocation": True, "is_ambiguous": False}
        ]
    }

    res = StageCReviewAgreement.compute_pairwise_agreement(sub_a, sub_b)
    assert res["common_items_count"] == 2
    assert res["overall_decision_exact_match_rate"] == 1.0
    assert res["cohens_kappa"] == 1.0
    assert res["mean_argument_field_f1"] == 1.0
    assert res["ambiguity_rate_a"] == 0.5
    assert res["ambiguity_rate_b"] == 0.0

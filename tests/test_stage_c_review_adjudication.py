"""Tests for Stage C Review Adjudication Engine (Track 6).

Verifies adjudication queue generation, discordance classification,
reviewer exclusion rules, and zero-results state reporting.
"""

import pytest
from src.stage_c_review_adjudication import StageCReviewAdjudication
from src.analyze_stage_c_human_reviews import StageCHumanReviewAnalyzer


def test_adjudication_queue_detects_tool_discordance():
    sub_a = {
        "reviewer_pseudonym": "rev_1",
        "reviews": [
            {"blind_task_id": "BLIND_TASK_001", "selected_tool_name": "tool_x", "submitted_arguments": {}, "abstain_from_invocation": False, "is_ambiguous": False}
        ]
    }
    sub_b = {
        "reviewer_pseudonym": "rev_2",
        "reviews": [
            {"blind_task_id": "BLIND_TASK_001", "selected_tool_name": "tool_y", "submitted_arguments": {}, "abstain_from_invocation": False, "is_ambiguous": False}
        ]
    }

    queue = StageCReviewAdjudication.generate_adjudication_queue(sub_a, sub_b)
    assert len(queue) == 1
    assert queue[0]["blind_task_id"] == "BLIND_TASK_001"
    assert "DISAGREE_TOOL_CHOICE" in queue[0]["discordance_types"]
    assert queue[0]["requires_third_reviewer"] is True


def test_adjudication_queue_detects_abstention_discordance():
    sub_a = {
        "reviewer_pseudonym": "rev_1",
        "reviews": [
            {"blind_task_id": "BLIND_TASK_002", "selected_tool_name": "tool_x", "submitted_arguments": {}, "abstain_from_invocation": False, "is_ambiguous": False}
        ]
    }
    sub_b = {
        "reviewer_pseudonym": "rev_2",
        "reviews": [
            {"blind_task_id": "BLIND_TASK_002", "selected_tool_name": None, "submitted_arguments": None, "abstain_from_invocation": True, "is_ambiguous": False}
        ]
    }

    queue = StageCReviewAdjudication.generate_adjudication_queue(sub_a, sub_b)
    assert len(queue) == 1
    assert "DISAGREE_ABSTENTION" in queue[0]["discordance_types"]


def test_reviewer_exclusion_rules():
    # Low confidence submission
    sub_low_conf = {
        "reviewer_pseudonym": "rev_low",
        "reviews": [{"confidence_score": 1} for _ in range(30)]
    }
    res_low = StageCReviewAdjudication.apply_reviewer_exclusion_rules(sub_low_conf)
    assert res_low["is_excluded"] is True
    assert any("low mean confidence" in r for r in res_low["exclusion_reasons"])

    # Incomplete submission (< 25 items)
    sub_incomplete = {
        "reviewer_pseudonym": "rev_short",
        "reviews": [{"confidence_score": 5} for _ in range(10)]
    }
    res_short = StageCReviewAdjudication.apply_reviewer_exclusion_rules(sub_incomplete)
    assert res_short["is_excluded"] is True
    assert any("Incomplete submission" in r for r in res_short["exclusion_reasons"])


def test_analyzer_with_no_submissions_returns_no_human_review_results():
    analyzer = StageCHumanReviewAnalyzer()
    res = analyzer.analyze_submissions([])
    assert res["validation_status"] == "NO_HUMAN_REVIEW_RESULTS_PRESENT"
    assert res["total_submissions_loaded"] == 0
    assert "Independent human validation is pending" in res["reason"]

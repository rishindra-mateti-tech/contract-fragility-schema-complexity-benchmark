"""Tests for Stage C Metrics Engine (Track 5).

Verifies metric aggregations, rate computations, and stratified groupings.
"""

from src.stage_c_metrics import StageCMetrics


def test_metrics_empty_tasks():
    res = StageCMetrics.compute_evaluation_metrics([])
    assert res["status"] == "NO_EMPIRICAL_RESULTS_PRESENT"
    assert res["total_tasks"] == 0


def test_metrics_aggregation_with_mock_evaluations():
    mock_evals = [
        {
            "task_id": "T1",
            "category": "ARGUMENT_CONSTRUCTION",
            "mutation_family": "CANONICAL",
            "domain": "data_management",
            "is_success": True,
            "tool_correct": True,
            "schema_valid": True,
            "slot_precision": 1.0,
            "slot_recall": 1.0,
            "slot_f1": 1.0,
            "classification": "EXACT_MATCH",
            "is_abstention_task": False
        },
        {
            "task_id": "T2",
            "category": "ARGUMENT_CONSTRUCTION",
            "mutation_family": "NESTED_HIERARCHY",
            "domain": "data_management",
            "is_success": False,
            "tool_correct": True,
            "schema_valid": False,
            "slot_precision": 0.5,
            "slot_recall": 0.5,
            "slot_f1": 0.5,
            "classification": "SCHEMA_VIOLATION",
            "is_abstention_task": False
        },
        {
            "task_id": "T3",
            "category": "ABSTENTION",
            "mutation_family": "CANONICAL",
            "domain": "communications",
            "is_success": True,
            "tool_correct": True,
            "schema_valid": True,
            "slot_precision": 1.0,
            "slot_recall": 1.0,
            "slot_f1": 1.0,
            "classification": "CORRECT_ABSTENTION",
            "is_abstention_task": True
        }
    ]

    res = StageCMetrics.compute_evaluation_metrics(mock_evals)
    assert res["status"] == "EVALUATED"
    summary = res["summary"]

    assert summary["total_tasks"] == 3
    assert summary["successful_tasks"] == 2
    assert summary["execution_success_rate"] == round(2 / 3, 4)
    assert summary["schema_compliance_rate"] == round(2 / 3, 4)

    # Category breakdown
    by_cat = res["by_category"]
    assert "ARGUMENT_CONSTRUCTION" in by_cat
    assert by_cat["ARGUMENT_CONSTRUCTION"]["total_tasks"] == 2
    assert by_cat["ARGUMENT_CONSTRUCTION"]["success_rate"] == 0.5

    assert "ABSTENTION" in by_cat
    assert by_cat["ABSTENTION"]["total_tasks"] == 1
    assert by_cat["ABSTENTION"]["success_rate"] == 1.0

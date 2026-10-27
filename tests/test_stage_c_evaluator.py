"""Tests for Stage C Offline Evaluator (Track 5).

Verifies single-task evaluation, batch evaluation without responses,
and execution with synthetic response fixtures.
"""

import json
from pathlib import Path
import pytest

from src.stage_c_evaluator import StageCEvaluator


REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = REPO_ROOT / "data_stage_c" / "task_instances"


def test_evaluator_empty_batch_returns_no_empirical_results():
    evaluator = StageCEvaluator()
    task_files = sorted(TASKS_DIR.glob("TASK_SYNTH_*.json"))[:10]
    tasks = []
    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            tasks.append(json.load(f))

    # Evaluate batch with no responses provided
    result = evaluator.evaluate_batch(tasks, responses_by_task_id=None)
    assert result["evaluation_status"] == "NO_EMPIRICAL_RESULTS_PRESENT"
    assert result["total_tasks_registered"] == len(tasks)
    assert result["tasks_evaluated"] == 0
    assert result["metrics"] == {}


def test_evaluator_with_synthetic_responses():
    evaluator = StageCEvaluator()

    # Load 1 AC task and 1 Abstention task
    ac_task_file = TASKS_DIR / "TASK_SYNTH_AC_001.json"
    ab_task_file = TASKS_DIR / "TASK_SYNTH_AB_001.json"

    with open(ac_task_file, "r", encoding="utf-8") as f:
        ac_task = json.load(f)
    with open(ab_task_file, "r", encoding="utf-8") as f:
        ab_task = json.load(f)

    # Synthetic responses: perfect responses
    responses = {
        ac_task["task_id"]: {
            "tool_calls": [{
                "function": {
                    "name": ac_task["expected_tool_name"],
                    "arguments": json.dumps(ac_task["expected_arguments"])
                }
            }]
        },
        ab_task["task_id"]: "ABSTAIN: The request lacks mandatory parameters."
    }

    batch_res = evaluator.evaluate_batch([ac_task, ab_task], responses_by_task_id=responses)
    assert batch_res["evaluation_status"] == "COMPLETED"
    assert batch_res["tasks_evaluated"] == 2

    metrics = batch_res["metrics"]
    summary = metrics["summary"]
    assert summary["execution_success_rate"] == 1.0
    assert summary["successful_tasks"] == 2

"""Tests for Stage C Model Execution Readiness Gates (Track 7).

Verifies the 12-gate evaluation harness, enforcement of the blocking state,
and prevention of unauthorized model execution.
"""

from pathlib import Path
import json
import pytest

from src.check_stage_c_execution_readiness import StageCExecutionReadinessEnforcer


REPO_ROOT = Path(__file__).resolve().parent.parent
STATUS_JSON = REPO_ROOT / "results_stage_c" / "STAGE_C_EXECUTION_READINESS_STATUS.json"
GATES_MD = REPO_ROOT / "results_stage_c" / "STAGE_C_EXECUTION_READINESS_GATES.md"


def test_gate_evaluator_evaluates_all_12_gates():
    enforcer = StageCExecutionReadinessEnforcer()
    manifest = enforcer.evaluate_all_gates()

    assert manifest["total_gates"] == 12
    assert len(manifest["gates"]) == 12
    assert manifest["operational_state"] == "MODEL_EXECUTION_BLOCKED_PENDING_INDEPENDENT_HUMAN_VALIDATION"
    assert manifest["model_execution_permitted"] is False

    # Check reproducibility gates pass
    assert manifest["gates"]["GATE_01_BASE_CORPUS_REPRODUCIBILITY"]["status"] == "PASS"
    assert manifest["gates"]["GATE_02_MUTATION_REPRODUCIBILITY"]["status"] == "PASS"
    assert manifest["gates"]["GATE_03_TASK_SUITE_REPRODUCIBILITY"]["status"] == "PASS"

    # Check human review and release 2 blocker gates are blocked
    assert manifest["gates"]["GATE_07_ZERO_UNRESOLVED_INVALID_TASKS"]["status"] == "BLOCKED_PENDING_RELEASE_2_REMEDIATION"
    assert manifest["gates"]["GATE_09_DUAL_HUMAN_REVIEWS_COMPLETED"]["status"] == "BLOCKED_PENDING_INDEPENDENT_HUMAN_REVIEW"


def test_assert_execution_permitted_raises_permission_error():
    enforcer = StageCExecutionReadinessEnforcer()
    with pytest.raises(PermissionError) as exc_info:
        enforcer.assert_execution_permitted()
    assert "MODEL_EXECUTION_BLOCKED_PENDING_INDEPENDENT_HUMAN_VALIDATION" in str(exc_info.value)


def test_readiness_artifacts_exist_and_match():
    assert STATUS_JSON.is_file(), f"Missing status JSON at {STATUS_JSON}"
    assert GATES_MD.is_file(), f"Missing gates MD at {GATES_MD}"

    with open(STATUS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["operational_state"] == "MODEL_EXECUTION_BLOCKED_PENDING_INDEPENDENT_HUMAN_VALIDATION"
    assert data["gates_passed"] == 7
    assert data["gates_blocked"] == 5


def test_strict_punctuation_in_gates_report():
    with open(GATES_MD, "r", encoding="utf-8") as f:
        content = f.read()
    assert "\u2014" not in content, f"Em dash found in {GATES_MD.name}"
    assert "\u2013" not in content, f"En dash found in {GATES_MD.name}"

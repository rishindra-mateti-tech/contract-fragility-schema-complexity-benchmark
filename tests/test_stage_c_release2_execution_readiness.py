"""Tests for Stage C Release 2 Model Execution Readiness and Release Gate Enforcer (Track 5).

Verifies that all 11 Release 2 gates are evaluated correctly, model execution is
strictly blocked with PermissionError, and operational state invariants are preserved.
"""

from pathlib import Path
import json
import pytest

from src.check_stage_c_release2_execution_readiness import (
    StageCRelease2ExecutionReadinessEnforcer,
    GATES_JSON,
    GATES_MD
)


def test_release2_execution_readiness_evaluation():
    enforcer = StageCRelease2ExecutionReadinessEnforcer()
    status = enforcer.evaluate_all_gates()

    assert status["total_gates_evaluated"] == 11
    assert status["passed_gates_count"] == 7
    assert status["blocked_gates_count"] == 4
    assert status["operational_state"] == "MODEL_EXECUTION_BLOCKED_PENDING_RELEASE2_INDEPENDENT_HUMAN_VALIDATION"
    assert status["model_execution_permitted"] is False
    assert GATES_JSON.is_file()
    assert GATES_MD.is_file()


def test_permission_error_on_unauthorized_execution():
    enforcer = StageCRelease2ExecutionReadinessEnforcer()
    with pytest.raises(PermissionError) as exc_info:
        enforcer.assert_model_execution_permitted()

    assert "MODEL EXECUTION FORBIDDEN" in str(exc_info.value)
    assert "MODEL_EXECUTION_BLOCKED_PENDING_RELEASE2_INDEPENDENT_HUMAN_VALIDATION" in str(exc_info.value)


def test_individual_gate_states():
    enforcer = StageCRelease2ExecutionReadinessEnforcer()
    status = enforcer.evaluate_all_gates()
    gates = status["gates"]

    # Gates that must PASS
    assert gates["GATE_01_RELEASE2_REPRODUCIBILITY"]["status"] == "PASS"
    assert gates["GATE_02_ZERO_INVALID_TASKS"]["status"] == "PASS"
    assert gates["GATE_03_ZERO_UNRESOLVED_AMBIGUITY"]["status"] == "PASS"
    assert gates["GATE_04_LEAKAGE_AUDIT_PASSES"]["status"] == "PASS"
    assert gates["GATE_05_DISTRACTOR_AUDIT_PASSES"]["status"] == "PASS"
    assert gates["GATE_06_CORPUS_BALANCE_AUDIT_PASSES"]["status"] == "PASS"
    assert gates["GATE_07_BLIND_REVIEW_PACKAGE_EXISTS"]["status"] == "PASS"

    # Gates that must be BLOCKED pending human validation
    assert gates["GATE_08_INDEPENDENT_REVIEW_SUBMISSIONS_REQUIRED"]["status"] == "BLOCKED"
    assert gates["GATE_09_INTER_RATER_AGREEMENT_REQUIRED"]["status"] == "BLOCKED"
    assert gates["GATE_10_ADJUDICATION_LOG_REQUIRED"]["status"] == "BLOCKED"
    assert gates["GATE_11_FINAL_MANIFEST_FROZEN_AND_HASHED"]["status"] == "BLOCKED"

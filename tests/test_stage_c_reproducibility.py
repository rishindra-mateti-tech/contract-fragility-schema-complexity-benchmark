"""Tests for Stage C Reproducibility Verification (Track 7).

Verifies that the reproducibility script succeeds and all Stage C components
regenerate deterministically with zero Stage B mutations.
"""

from scripts.verify_stage_c_reproducibility import (
    verify_base_contracts_determinism,
    verify_mutations_determinism,
    verify_tasks_determinism,
    verify_stage_b_immutability,
)


def test_base_contracts_reproducibility():
    ok, errors = verify_base_contracts_determinism()
    assert ok is True, f"Base contracts reproducibility failed: {errors}"


def test_mutations_reproducibility():
    ok, errors = verify_mutations_determinism()
    assert ok is True, f"Mutations reproducibility failed: {errors}"


def test_tasks_reproducibility():
    ok, errors = verify_tasks_determinism()
    assert ok is True, f"Tasks reproducibility failed: {errors}"


def test_stage_b_immutability_check():
    ok, errors = verify_stage_b_immutability()
    assert ok is True, f"Stage B immutability check failed: {errors}"

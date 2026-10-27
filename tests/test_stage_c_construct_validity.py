"""Tests for Stage C Construct Validity and Human Review Verifier (Track 8).

Verifies that the construct validity verifier runs cleanly and all checks pass.
"""

from scripts.verify_stage_c_construct_validity import (
    verify_track0_scope_freeze,
    verify_track1_leakage_audit,
    verify_track2_distractor_audit,
    verify_track3_balance_and_diversity,
    verify_track4_blind_packages,
    verify_track5_review_app,
    verify_track6_human_review_tooling,
    verify_track7_execution_gates,
    verify_release1_tasks_immutability,
)


def test_track0_scope_freeze_verification():
    ok, errors = verify_track0_scope_freeze()
    assert ok is True, f"Track 0 verification failed: {errors}"


def test_track1_leakage_audit_verification():
    ok, errors = verify_track1_leakage_audit()
    assert ok is True, f"Track 1 verification failed: {errors}"


def test_track2_distractor_audit_verification():
    ok, errors = verify_track2_distractor_audit()
    assert ok is True, f"Track 2 verification failed: {errors}"


def test_track3_balance_and_diversity_verification():
    ok, errors = verify_track3_balance_and_diversity()
    assert ok is True, f"Track 3 verification failed: {errors}"


def test_track4_blind_packages_verification():
    ok, errors = verify_track4_blind_packages()
    assert ok is True, f"Track 4 verification failed: {errors}"


def test_track5_review_app_verification():
    ok, errors = verify_track5_review_app()
    assert ok is True, f"Track 5 verification failed: {errors}"


def test_track6_human_review_tooling_verification():
    ok, errors = verify_track6_human_review_tooling()
    assert ok is True, f"Track 6 verification failed: {errors}"


def test_track7_execution_gates_verification():
    ok, errors = verify_track7_execution_gates()
    assert ok is True, f"Track 7 verification failed: {errors}"


def test_release1_tasks_immutability_verification():
    ok, errors = verify_release1_tasks_immutability()
    assert ok is True, f"Release 1 immutability verification failed: {errors}"

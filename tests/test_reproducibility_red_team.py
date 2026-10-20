"""
test_reproducibility_red_team.py - Regression Tests for Adversarial Red-Team Scenarios.

Verifies:
1. SCENARIO_TAMPERED_RAW_HASH triggers cryptographic detection.
2. SCENARIO_MUTATED_CANONICAL_CONTRACT triggers closed wrapper rejection.
3. SCENARIO_LINEAGE_POINTER_TAMPERING fails closed on broken pointers.
4. SCENARIO_UNAUTHORIZED_PROMOTION blocks CANONICAL_FAITHFUL without independent review.
5. SCENARIO_UNSCOPED_RESEARCH_CLAIM is caught by epistemic claim linter.
6. SCENARIO_DROPPED_REQUIRED_FIELD is caught as POTENTIAL_LOSS.
7. Full runner executes all 6 scenarios cleanly and saves report.
"""

import pytest
from scripts.red_team_reproducibility import (
    scenario_tampered_raw_hash,
    scenario_mutated_canonical_contract,
    scenario_lineage_pointer_tampering,
    scenario_unauthorized_promotion,
    scenario_unscoped_research_claim,
    scenario_dropped_required_field,
    run_all_red_team_scenarios,
    REPO_ROOT,
)


def test_tampered_raw_hash_scenario():
    passed, msg = scenario_tampered_raw_hash()
    assert passed, msg


def test_mutated_canonical_contract_scenario():
    passed, msg = scenario_mutated_canonical_contract()
    assert passed, msg


def test_lineage_pointer_tampering_scenario():
    passed, msg = scenario_lineage_pointer_tampering()
    assert passed, msg


def test_unauthorized_promotion_scenario():
    passed, msg = scenario_unauthorized_promotion()
    assert passed, msg


def test_unscoped_research_claim_scenario():
    passed, msg = scenario_unscoped_research_claim()
    assert passed, msg


def test_dropped_required_field_scenario():
    passed, msg = scenario_dropped_required_field()
    assert passed, msg


def test_full_red_team_runner():
    data = run_all_red_team_scenarios()
    assert data["all_scenarios_passed"] is True
    assert data["total_scenarios_evaluated"] == 6
    assert data["total_scenarios_passed"] == 6

    report_path = REPO_ROOT / "results_stage_b" / "REPRODUCIBILITY_RED_TEAM_AUDIT.md"
    assert report_path.exists(), "Missing REPRODUCIBILITY_RED_TEAM_AUDIT.md"

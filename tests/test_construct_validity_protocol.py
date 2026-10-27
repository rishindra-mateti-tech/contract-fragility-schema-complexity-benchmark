"""Tests for Stage C Construct Validity Protocol and Scope Freeze (Track 0).

Verifies the construct definition, intentionally measured vs excluded traits,
audit dimensions, preregistered sampling plan, and gating states.
"""

from pathlib import Path
import json
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "results_stage_c"
SCOPE_FREEZE_PATH = RESULTS_DIR / "CONSTRUCT_VALIDITY_SCOPE_FREEZE.md"
PROTOCOL_PATH = RESULTS_DIR / "CONSTRUCT_VALIDITY_PROTOCOL_001.md"
PREREG_PATH = RESULTS_DIR / "CONSTRUCT_VALIDITY_PREREGISTRATION.json"


def test_files_exist():
    assert SCOPE_FREEZE_PATH.is_file(), f"Missing scope freeze file at {SCOPE_FREEZE_PATH}"
    assert PROTOCOL_PATH.is_file(), f"Missing protocol file at {PROTOCOL_PATH}"
    assert PREREG_PATH.is_file(), f"Missing preregistration file at {PREREG_PATH}"


def test_preregistration_structure_and_construct():
    with open(PREREG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_construct = (
        "Ability to map a natural-language request to an appropriate structured "
        "tool invocation under controlled schema-surface transformations."
    )
    assert data["target_construct"] == expected_construct
    assert data["operational_state"] == "MODEL_EXECUTION_BLOCKED_PENDING_INDEPENDENT_HUMAN_VALIDATION"
    assert data["empirical_results_state"] == "NO_EMPIRICAL_RESULTS_PRESENT"

    measured = data["intentionally_measured"]
    assert "argument construction" in measured
    assert "tool selection" in measured
    assert "abstention" in measured
    assert "structural schema sensitivity" in measured

    excluded = data["excluded_non_constructs"]
    assert "real API competence" in excluded
    assert "endpoint execution" in excluded
    assert "software engineering ability" in excluded
    assert "factual knowledge" in excluded
    assert "tool usefulness" in excluded
    assert "production readiness" in excluded
    assert "human preference" in excluded


def test_human_review_preregistration_parameters():
    with open(PREREG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    hr_plan = data["human_review_plan"]
    assert hr_plan["sample_size_target"] >= 90
    assert hr_plan["minimum_reviewers_per_item"] >= 2
    assert hr_plan["inter_rater_agreement_threshold_kappa"] >= 0.70
    assert hr_plan["independent_review_state"] == "NO_HUMAN_REVIEW_RESULTS_PRESENT"


def test_strict_punctuation_in_track_0():
    for p in [SCOPE_FREEZE_PATH, PROTOCOL_PATH]:
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        assert "\u2014" not in content, f"Em dash found in {p.name}"
        assert "\u2013" not in content, f"En dash found in {p.name}"

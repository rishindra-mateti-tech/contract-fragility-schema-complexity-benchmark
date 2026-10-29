"""Tests for Stage C Release 2 Design Specification (Track 1).

Verifies that the Release 2 specification, preregistration, and changelog artifacts
are complete, consistent, and adhere to preregistered invariants.
"""

from pathlib import Path
import json

ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results_stage_c"

SPEC_MD = RESULTS_DIR / "RELEASE2_DESIGN_SPECIFICATION.md"
PREREG_JSON = RESULTS_DIR / "RELEASE2_PREREGISTRATION.json"
CHANGELOG_MD = RESULTS_DIR / "RELEASE2_CHANGELOG_FROM_RELEASE1.md"


def test_specification_files_exist():
    assert SPEC_MD.is_file(), f"Missing {SPEC_MD}"
    assert PREREG_JSON.is_file(), f"Missing {PREREG_JSON}"
    assert CHANGELOG_MD.is_file(), f"Missing {CHANGELOG_MD}"


def test_preregistration_invariants():
    with open(PREREG_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("benchmark_release") == "RELEASE_2"
    assert data.get("preregistration_version") == "2.0.0"
    assert data.get("operational_state") == "MODEL_EXECUTION_BLOCKED_PENDING_RELEASE2_INDEPENDENT_HUMAN_VALIDATION"
    assert data.get("empirical_results_state") == "NO_EMPIRICAL_RESULTS_PRESENT"
    assert data.get("human_review_state") == "NO_INDEPENDENT_HUMAN_REVIEW_RESULTS_PRESENT"

    # Paired group design
    pg = data.get("paired_group_design", {})
    assert "paired_group_id" in pg.get("description", "")
    assert pg.get("max_intra_cell_prompt_duplicates") == 0

    # Quality thresholds
    thresh = data.get("required_quality_thresholds", {})
    assert thresh.get("unresolved_invalid_tasks_permitted") == 0
    assert thresh.get("unadjudicated_ambiguity_count_permitted") == 0
    assert thresh.get("minimum_independent_reviewers") == 2
    assert thresh.get("inter_rater_agreement_threshold_kappa") == 0.7


def test_task_category_invariants():
    with open(PREREG_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    invariants = data.get("task_category_invariants", {})
    assert "ARGUMENT_CONSTRUCTION" in invariants
    assert "TOOL_SELECTION" in invariants
    assert "ABSTENTION" in invariants

    ac = invariants["ARGUMENT_CONSTRUCTION"]
    assert ac.get("tool_name_in_user_prompt_permitted") is False
    assert ac.get("verbatim_snake_case_keys_in_prompt_permitted") is False
    assert ac.get("all_non_inferable_gold_values_in_prompt") is True

    ts = invariants["TOOL_SELECTION"]
    assert ts.get("target_tool_in_user_prompt_permitted") is False
    assert ts.get("target_position_balanced") is True

    ab = invariants["ABSTENTION"]
    assert ab.get("candidate_tools_match_intent") is False
    assert ab.get("explicit_abstention_hints_permitted") is False


def test_changelog_content():
    content = CHANGELOG_MD.read_text(encoding="utf-8")
    assert "Paired Experimental Design" in content
    assert "paired_group_id" in content
    assert "Immutable historical diagnostic evidence" in content or "immutable historical diagnostic evidence" in content
    assert "RELEASE_2_PENDING_HUMAN_VALIDATION" in content

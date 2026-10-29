"""Tests for Stage C Release 2 Blind Review Packages and App Integration (Track 4).

Verifies that the blinded reviewer packages adhere to strict blinding invariants,
the sampling plan and assignment templates exist, and the review app supports
explicit release selection.
"""

from pathlib import Path
import json
import pytest
from fastapi.testclient import TestClient

from review_app.app import app
from src.build_stage_c_release2_blind_review_package import (
    StageCRelease2BlindReviewBuilder,
    R2_PACKAGES_DIR,
    R2_TASKS_DIR,
    BASE_DIR
)

SAMPLING_PLAN_MD = Path(__file__).resolve().parent.parent / "results_stage_c" / "RELEASE2_HUMAN_REVIEW_SAMPLING_PLAN.md"
ASSIGNMENT_CSV = Path(__file__).resolve().parent.parent / "results_stage_c" / "RELEASE2_HUMAN_REVIEW_ASSIGNMENT_TEMPLATE.csv"
READINESS_MD = Path(__file__).resolve().parent.parent / "results_stage_c" / "RELEASE2_HUMAN_REVIEW_READINESS.md"


def test_blind_manifest_structure_and_counts():
    manifest_file = R2_PACKAGES_DIR / "blind_sample_manifest.json"
    assert manifest_file.is_file(), f"Missing {manifest_file}"

    with open(manifest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("benchmark_release") == "RELEASE_2"
    assert data.get("total_blinded_tasks") == 90

    breakdown = data.get("category_breakdown", {})
    assert breakdown.get("ARGUMENT_CONSTRUCTION") == 30
    assert breakdown.get("TOOL_SELECTION") == 30
    assert breakdown.get("ABSTENTION") == 30


def test_strict_blinding_invariants():
    manifest_file = R2_PACKAGES_DIR / "blind_sample_manifest.json"
    with open(manifest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data.get("tasks", []):
        assert "expected_tool_name" not in item
        assert "expected_arguments" not in item
        assert "expected_latent_intent" not in item
        assert "mutation_family" not in item
        assert "paired_group_id" not in item
        assert "base_contract_id" not in item
        assert "prompt_seed" not in item
        assert "target_position" not in item

        # Verify candidate tools are sanitized
        for tool in item.get("candidate_tools", []):
            assert "tool_name" in tool
            assert "schema" in tool
            assert "mapping_spec" not in tool
            assert "gold_examples" not in tool


def test_author_reconciliation_map():
    map_file = R2_PACKAGES_DIR / "author_reconciliation_map.json"
    assert map_file.is_file(), f"Missing {map_file}"

    with open(map_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    key_list = data.get("author_reconciliation_key", [])
    assert len(key_list) == 90

    for entry in key_list:
        assert entry["release_2_task_id"].startswith("TASK_R2_")
        assert entry["blind_task_id"].startswith("BLIND_R2_TASK_")
        assert entry["category"] in ["ARGUMENT_CONSTRUCTION", "TOOL_SELECTION", "ABSTENTION"]


def test_documentation_and_csv_artifacts():
    assert SAMPLING_PLAN_MD.is_file()
    assert ASSIGNMENT_CSV.is_file()
    assert READINESS_MD.is_file()

    plan_text = SAMPLING_PLAN_MD.read_text(encoding="utf-8")
    assert "NO_INDEPENDENT_HUMAN_REVIEW_RESULTS_PRESENT" in plan_text
    assert "90" in plan_text

    readiness_text = READINESS_MD.read_text(encoding="utf-8")
    assert "NO_INDEPENDENT_HUMAN_REVIEW_RESULTS_PRESENT" in readiness_text
    assert "MODEL_EXECUTION_BLOCKED_PENDING_RELEASE2_INDEPENDENT_HUMAN_VALIDATION" in readiness_text

    # Verify CSV has headers only
    lines = ASSIGNMENT_CSV.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert "blind_task_id" in lines[0]


def test_review_app_release_selection():
    client = TestClient(app)

    # 1. Login with Release 2
    resp = client.post("/login", data={"pseudonym": "test_r2_reviewer", "release": "release2"}, follow_redirects=False)
    assert resp.status_code == 303
    cookies = resp.cookies

    # 2. Get task list
    tasks_resp = client.get("/tasks", cookies=cookies)
    assert tasks_resp.status_code == 200
    assert "BLIND_R2_TASK_" in tasks_resp.text

    # 3. View task detail
    detail_resp = client.get("/task/BLIND_R2_TASK_001", cookies=cookies)
    assert detail_resp.status_code == 200
    assert "BLIND_R2_TASK_001" in detail_resp.text
    # Verify no gold leaked
    assert "expected_tool_name" not in detail_resp.text

"""Tests for Stage C Blind Human-Review Data Package (Track 4).

Verifies sample size (90 tasks + 5 qual), stratification balance (30/30/30),
strict blinding compliance, blank assignment template, and reconciliation mapping.
"""

from pathlib import Path
import csv
import json
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGES_DIR = REPO_ROOT / "data_stage_c" / "reviewer_packages"
ASSIGNMENT_CSV = REPO_ROOT / "results_stage_c" / "HUMAN_REVIEW_ASSIGNMENT_TEMPLATE.csv"


def test_package_files_exist():
    expected_files = [
        PACKAGES_DIR / "blind_sample_manifest.json",
        PACKAGES_DIR / "construction_review_packet.json",
        PACKAGES_DIR / "selection_review_packet.json",
        PACKAGES_DIR / "abstention_review_packet.json",
        PACKAGES_DIR / "qualification_review_packet.json",
        PACKAGES_DIR / "author_reconciliation_map.json",
        ASSIGNMENT_CSV,
    ]
    for p in expected_files:
        assert p.is_file(), f"Missing package file at {p}"


def test_blind_sample_counts_and_stratification():
    with open(PACKAGES_DIR / "blind_sample_manifest.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    manifest = data["manifest"]
    assert manifest["total_blind_tasks"] == 90
    assert manifest["qualification_tasks"] == 5

    strat = manifest["stratification"]
    assert strat["CONSTRUCTION_REVIEW"] == 30
    assert strat["SELECTION_REVIEW"] == 30
    assert strat["ABSTENTION_REVIEW"] == 30

    tasks = data["tasks"]
    assert len(tasks) == 90


def test_blinding_invariants():
    with open(PACKAGES_DIR / "blind_sample_manifest.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data["tasks"]:
        assert item["blinding_verification"] == "BLINDED_NO_GOLD_LABELS_PRESENT"
        # Must not contain gold answers or mutation family
        assert "expected_tool_name" not in item
        assert "expected_arguments" not in item
        assert "expected_latent_intent" not in item
        assert "mutation_family" not in item
        assert "base_contract_id" not in item

        # Form template must be unpopulated
        form = item["response_form_template"]
        assert form["selected_tool_name"] is None
        assert form["submitted_arguments"] == {}
        assert form["abstain_from_invocation"] is False


def test_assignment_csv_blank_reviewers():
    with open(ASSIGNMENT_CSV, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) == 90
    for row in reader:
        assert row["assigned_reviewer_id"] == ""
        assert row["review_status"] == "UNASSIGNED"
        assert row["submission_timestamp"] == ""


def test_author_reconciliation_key_integrity():
    with open(PACKAGES_DIR / "author_reconciliation_map.json", "r", encoding="utf-8") as f:
        key_data = json.load(f)

    assert len(key_data) == 90
    blind_ids = {entry["blind_task_id"] for entry in key_data}
    assert len(blind_ids) == 90

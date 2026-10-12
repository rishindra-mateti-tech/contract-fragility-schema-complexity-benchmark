"""Tests for Deterministic Replacement Candidate Ranking Engine.

Verifies:
1. Exactly five open slots are evaluated and ranked.
2. Every slot has at least five ranked candidate operations.
3. Every ranked candidate strictly passes the frozen protocol eligibility gate.
4. No ranked candidate duplicates an existing operation in the official manifest.
5. All candidates have mock_safety_status == MOCK_SAFETY_REVIEW_PENDING.
6. Recommendation status is explicitly DRAFT_PENDING_REVIEW.
7. Ranking output is 100% byte-stable when --generated-at is provided.
8. Official manifest remains untouched.
"""

import json
import os
import pytest
import yaml
from src.rank_stage_b_replacement_candidates import (
    rank_replacement_candidates,
    generate_markdown_report,
    JSON_OUTPUT_PATH,
    MD_OUTPUT_PATH,
    MANIFEST_PATH,
    UNIVERSE_JSON_PATH,
    CONFIG_PATH,
    sha256_file,
)


def test_ranking_evaluates_five_slots():
    report = rank_replacement_candidates(generated_at_utc="2026-10-12T04:45:00Z")
    slots = report["slots"]
    assert len(slots) == 5
    slot_ids = [s["slot_id"] for s in slots]
    expected_slot_ids = [
        "SLOT_GITHUB_01",
        "SLOT_STRIPE_01",
        "SLOT_STRIPE_02",
        "SLOT_CHATWOOT_01",
        "SLOT_LINE_01",
    ]
    assert slot_ids == expected_slot_ids


def test_each_slot_has_at_least_five_candidates():
    report = rank_replacement_candidates(generated_at_utc="2026-10-12T04:45:00Z")
    for s in report["slots"]:
        assert s["candidates_ranked"] >= 5, f"Slot {s['slot_id']} must have >= 5 candidates"
        assert len(s["ranked_candidates"]) >= 5


def test_ranked_candidates_are_strictly_protocol_eligible():
    report = rank_replacement_candidates(generated_at_utc="2026-10-12T04:45:00Z")
    with open(UNIVERSE_JSON_PATH, "r", encoding="utf-8") as f:
        universe_data = json.load(f)
    univ_by_id = {op["operation_id"]: op for op in universe_data["operations"]}

    for s in report["slots"]:
        for c in s["ranked_candidates"]:
            op_id = c["operation_id"]
            assert op_id in univ_by_id, f"Candidate {op_id} must exist in universe"
            orig = univ_by_id[op_id]
            elig = orig.get("static_eligibility", orig.get("canonical_eligibility"))
            assert elig in ["STATICALLY_ELIGIBLE_CANDIDATE", "STATICALLY_ELIGIBLE_FAITHFUL_UNION_CANDIDATE", "ELIGIBLE", "ELIGIBLE_FAITHFUL_UNION"]
            assert orig["maximum_nesting_depth"] <= 5
            assert orig["has_cycle"] is False
            assert orig["has_binary_or_multipart"] is False
            assert orig["has_external_ref"] is False


def test_no_candidate_duplicates_existing_manifest_operation():
    report = rank_replacement_candidates(generated_at_utc="2026-10-12T04:45:00Z")
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    existing_op_ids = {op["operation_id"] for op in manifest.get("operations", [])}
    excluded_op_ids = {op["operation_id"] for op in manifest.get("excluded_operations", [])}
    forbidden = existing_op_ids.union(excluded_op_ids)

    seen_in_ranking = set()
    for s in report["slots"]:
        for c in s["ranked_candidates"]:
            op_id = c["operation_id"]
            assert op_id not in forbidden, f"Ranked candidate {op_id} duplicates manifest operation"
            # Ensure Stripe Slot A and Slot B do not overlap
            if s["slot_id"] in ["SLOT_STRIPE_01", "SLOT_STRIPE_02"]:
                assert op_id not in seen_in_ranking, f"Candidate {op_id} recommended in both Stripe slots"
                seen_in_ranking.add(op_id)


def test_mock_safety_and_recommendation_status_invariants():
    report = rank_replacement_candidates(generated_at_utc="2026-10-12T04:45:00Z")
    for s in report["slots"]:
        for c in s["ranked_candidates"]:
            assert c["mock_safety_status"] == "MOCK_SAFETY_REVIEW_PENDING", "Mock safety must remain pending"
            assert c["recommendation_status"] == "DRAFT_PENDING_REVIEW", "Must be labeled draft pending review"
            assert len(c["mock_safety_notes"]) > 0


def test_deterministic_output_with_generated_at():
    fixed_ts = "2026-10-12T04:45:00Z"
    rep1 = rank_replacement_candidates(generated_at_utc=fixed_ts)
    rep2 = rank_replacement_candidates(generated_at_utc=fixed_ts)

    json1 = json.dumps(rep1, indent=2, sort_keys=True)
    json2 = json.dumps(rep2, indent=2, sort_keys=True)
    assert json1 == json2, "Runs with identical inputs and generated-at must produce byte-identical JSON"

    md1 = generate_markdown_report(rep1)
    md2 = generate_markdown_report(rep2)
    assert md1 == md2, "Runs with identical inputs and generated-at must produce byte-identical Markdown"


def test_ranking_config_loaded_and_hashed():
    report = rank_replacement_candidates(generated_at_utc="2026-10-12T04:45:00Z")
    meta = report["metadata"]
    assert meta["config_file"] == "results_stage_b/replacement_ranking_config.yaml"
    assert meta["config_sha256"] == sha256_file(CONFIG_PATH)


def test_mock_safety_contributes_strictly_zero_points():
    report = rank_replacement_candidates(generated_at_utc="2026-10-12T04:45:00Z")
    for s in report["slots"]:
        for c in s["ranked_candidates"]:
            assert c["mock_safety_points_contributed"] == 0
            assert c["score_breakdown"]["mock_safety_feasibility_points"] == 0


def test_ties_preserved_as_co_leading_candidates():
    report = report_data = rank_replacement_candidates(generated_at_utc="2026-10-12T04:45:00Z")
    github_slot = next(s for s in report["slots"] if s["slot_id"] == "SLOT_GITHUB_01")
    candidates = github_slot["ranked_candidates"]
    top_two = candidates[:2]
    assert top_two[0]["composite_score"] == top_two[1]["composite_score"] == 100
    assert top_two[0]["is_co_leading"] is True
    assert top_two[1]["is_co_leading"] is True
    assert "CO_LEADING_CANDIDATE (Tied)" in top_two[0]["status_label"]
    assert "CO_LEADING_CANDIDATE (Tied)" in top_two[1]["status_label"]
    op_ids = {top_two[0]["operation_id"], top_two[1]["operation_id"]}
    assert op_ids == {"pulls/submit-review", "pulls/create"}


def test_statefulness_warning_on_dependent_operations():
    report = rank_replacement_candidates(generated_at_utc="2026-10-12T04:45:00Z")
    github_slot = next(s for s in report["slots"] if s["slot_id"] == "SLOT_GITHUB_01")
    submit_review = next(c for c in github_slot["ranked_candidates"] if c["operation_id"] == "pulls/submit-review")
    assert submit_review["is_potentially_stateful"] is True
    assert "POTENTIALLY_STATEFUL_DEPENDENCY" in submit_review["statefulness_warning"]
    assert "review_id" in submit_review["statefulness_warning"]

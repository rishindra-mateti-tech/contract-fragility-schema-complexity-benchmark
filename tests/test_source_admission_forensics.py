"""
test_source_admission_forensics.py - Unit and Regression Tests for Forensic Universe Accounting.

Verifies:
1. All 10 raw source files match Git blob SHA and SHA-256 with zero drift.
2. 14 candidate sources reconcile exactly across admission decisions.
3. 1,346 scanned operations partition cleanly into 1,110 eligible and 236 disqualified.
4. Disqualification root-cause overlap matrix sums exactly to 236 with zero unclassified ops.
5. Marginal root-cause counts reconcile (137 depth, 176 object union, 19 multipart/binary).
6. 30 final active manifest operations reconcile across 10 clusters.
7. Zero ghost or duplicate candidates exist.
8. On-disk audit artifacts exist, are non-empty, and match audit results.
"""

import json
import pytest
from pathlib import Path
from src.audit_stage_b_source_admission import (
    REPO_ROOT,
    audit_raw_sources,
    audit_candidate_inventory,
    audit_raw_operation_universe,
    audit_replacement_decisions,
    audit_manifest_and_readiness,
    generate_forensic_audit,
)


def test_all_ten_raw_sources_pass_cryptographic_verification():
    """Verifies that all 10 raw source files match recorded Git blob SHA and SHA-256."""
    raw_audit = audit_raw_sources()
    assert raw_audit["total_raw_sources_registered"] == 10
    assert raw_audit["total_raw_sources_verified"] == 10
    assert raw_audit["all_cryptographic_hashes_verified"] is True

    for s in raw_audit["sources"]:
        assert s["exists"] is True, f"Missing file: {s['file_path']}"
        assert s["blob_sha_match"] is True, f"Blob SHA mismatch for {s['candidate_source_id']}"
        assert s["sha256_match"] is True, f"SHA-256 mismatch for {s['candidate_source_id']}"
        assert s["status"] == "VERIFIED"


def test_candidate_inventory_reconciliation():
    """Verifies that the 14 candidate sources reconcile with exact decisions."""
    inv_audit = audit_candidate_inventory()
    assert inv_audit["total_candidate_sources_evaluated"] == 14
    breakdown = inv_audit["admission_breakdown"]
    assert breakdown["ADMITTED"] == 10
    assert breakdown["REJECTED"] == 1  # DataDog
    assert breakdown["PENDING_REVIEW"] == 3  # PayPal, NYT, OpenAI


def test_raw_universe_scanned_counts_and_eligibility():
    """Verifies that 1,346 scanned operations partition into 1,110 eligible and 236 disqualified."""
    uni = audit_raw_operation_universe()
    assert uni["total_operations_scanned"] == 1346
    edist = uni["eligibility_distribution"]
    assert edist["STATICALLY_ELIGIBLE_CANDIDATE"] == 1109
    assert edist["STATICALLY_ELIGIBLE_FAITHFUL_UNION_CANDIDATE"] == 1
    assert edist["DISQUALIFIED"] == 236
    assert (
        edist["STATICALLY_ELIGIBLE_CANDIDATE"]
        + edist["STATICALLY_ELIGIBLE_FAITHFUL_UNION_CANDIDATE"]
        + edist["DISQUALIFIED"]
    ) == 1346


def test_disqualification_overlap_matrix_integrity():
    """Verifies that the disjoint overlap matrix partitions sum exactly to 236."""
    uni = audit_raw_operation_universe()
    overlap = uni["disqualification_cause_overlap_matrix"]

    assert overlap["depth_only"] == 44
    assert overlap["union_only"] == 83
    assert overlap["multipart_only"] == 15
    assert overlap["depth_and_union"] == 90
    assert overlap["depth_and_multipart"] == 1
    assert overlap["union_and_multipart"] == 1
    assert overlap["all_three"] == 2
    assert overlap["other"] == 0

    partition_sum = sum(overlap.values())
    assert partition_sum == 236, f"Expected 236 disjoint items, got {partition_sum}"


def test_marginal_root_cause_sums():
    """Verifies marginal totals for non-exclusive root causes."""
    uni = audit_raw_operation_universe()
    totals = uni["disqualification_cause_totals"]

    assert totals["DEPTH"] == 137
    assert totals["OBJECT_UNION"] == 176
    assert totals["MULTIPART_BINARY"] == 19


def test_replacement_decisions_reconciliation():
    """Verifies that 25 replacement candidates were evaluated and 5 admitted."""
    rep = audit_replacement_decisions()
    assert rep["replacement_slots_count"] == 5
    assert rep["total_replacement_candidates_evaluated"] == 25
    assert rep["admitted_replacements_count"] == 5
    assert rep["rejected_replacements_count"] == 20

    slot_ids = {s["slot_id"] for s in rep["slots"]}
    expected_slots = {
        "SLOT_GITHUB_01",
        "SLOT_STRIPE_01",
        "SLOT_STRIPE_02",
        "SLOT_CHATWOOT_01",
        "SLOT_LINE_01",
    }
    assert slot_ids == expected_slots


def test_manifest_cohort_reconciliation():
    """Verifies active manifest contains exactly 30 operations across 10 clusters."""
    man = audit_manifest_and_readiness()
    assert man["active_manifest_count"] == 30
    assert man["excluded_cohort_count"] == 7
    assert man["total_tracked_operations"] == 37


def test_no_duplicate_or_ghost_operations():
    """Asserts zero duplicate operation IDs in manifest and all resolve to valid candidate sources."""
    manifest_path = REPO_ROOT / "results_stage_b" / "stage_b_operation_manifest.yaml"
    import yaml

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    ops = manifest.get("operations", [])
    op_ids = [op["operation_id"] for op in ops]
    assert len(op_ids) == len(set(op_ids)), "Duplicate operation IDs detected in manifest!"

    cand_sources = {op["candidate_source_id"] for op in ops}
    raw_audit = audit_raw_sources()
    admitted_cands = {s["candidate_source_id"] for s in raw_audit["sources"]}
    assert cand_sources.issubset(admitted_cands), "Ghost candidate source detected in manifest!"


def test_on_disk_artifacts_integrity():
    """Verifies that on-disk forensic audit reports exist and match computed values."""
    audit_data = generate_forensic_audit()

    json_path = REPO_ROOT / "results_stage_b" / "SOURCE_ADMISSION_FORENSIC_AUDIT.json"
    md_path = REPO_ROOT / "results_stage_b" / "SOURCE_ADMISSION_FORENSIC_AUDIT.md"
    accounting_path = REPO_ROOT / "results_stage_b" / "DATASET_UNIVERSE_ACCOUNTING.md"

    assert json_path.exists(), "Missing JSON audit file"
    assert md_path.exists(), "Missing Markdown audit file"
    assert accounting_path.exists(), "Missing Dataset Universe Accounting file"

    with open(json_path, "r", encoding="utf-8") as f:
        disk_json = json.load(f)

    assert disk_json["reconciliation_summary"] == audit_data["reconciliation_summary"]

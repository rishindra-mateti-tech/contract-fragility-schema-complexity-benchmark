"""Tests for Stage B Full-Cohort Extraction Readiness Audit.

Validates:
1. Complete audit coverage: exactly 30 active operations and 7 excluded operations (37 total).
2. Pinned source cryptographic continuity: blob SHA and file SHA-256 match pinned records.
3. Strict taxonomy verification:
   - Exactly 6 operations classified READY_WITH_EXPLICIT_WRAPPER_POLICY.
   - Exactly 1 operation classified REQUIRES_PROTOCOL_AMENDMENT (PostRefunds).
   - Exactly 23 operations classified REQUIRES_EXTRACTOR_CAPABILITY.
   - Exactly 7 operations classified EXCLUDED.
4. Non-empty blockers for all non-ready operations.
5. Presence and consistency of emitted audit artifacts:
   - results_stage_b/EXTRACTION_READINESS_MATRIX.json
   - results_stage_b/EXTRACTION_READINESS_MATRIX.md
   - results_stage_b/EXTRACTION_READINESS_AUDIT.md
"""

import json
import os
import pytest

from src.audit_stage_b_extraction_readiness import (
    JSON_MATRIX_PATH,
    MD_MATRIX_PATH,
    MD_AUDIT_PATH,
    run_extraction_readiness_audit,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_extraction_readiness_audit_execution():
    """Verify that the readiness audit executes cleanly and returns valid structured output."""
    res = run_extraction_readiness_audit()
    assert "summary" in res
    assert "operations" in res

    summary = res["summary"]
    assert summary["total_operations_audited"] == 37
    assert summary["active_cohort_size"] == 30
    assert summary["excluded_cohort_size"] == 7

    dist = summary["readiness_distribution"]
    assert dist["READY_WITH_EXPLICIT_WRAPPER_POLICY"] == 6
    assert dist["REQUIRES_PROTOCOL_AMENDMENT"] == 1
    assert dist["REQUIRES_EXTRACTOR_CAPABILITY"] == 23
    assert dist["EXCLUDED"] == 7


def test_provenance_cryptographic_verification():
    """Verify that all audited operations have verified Git blob SHAs matching disk bytes."""
    res = run_extraction_readiness_audit()
    for op in res["operations"]:
        assert op["blob_sha_verified"] is True, f"Blob SHA mismatch for {op['operation_id']} ({op['slot_id']})"
        assert len(op["raw_source_sha256"]) == 64
        assert len(op["raw_source_blob_sha"]) == 40
        assert os.path.exists(os.path.join(ROOT_DIR, op["raw_source_file_path"]))


def test_readiness_taxonomy_invariants():
    """Verify that operations are honestly classified and non-ready operations have explicit blockers."""
    res = run_extraction_readiness_audit()
    ready_ops = [op for op in res["operations"] if op["readiness_state"] == "READY_WITH_EXPLICIT_WRAPPER_POLICY"]
    ready_op_ids = {op["operation_id"] for op in ready_ops}

    # Only operations supported by the current generic extractor are marked ready
    expected_ready = {
        "pulls/create",
        "PostShippingRates",
        "PostPayouts",
        "repos/create-commit-status",
        "repos/create-for-authenticated-user",
        "create-a-webhook",
    }
    assert ready_op_ids == expected_ready

    # PostRefunds requires protocol amendment for faithful unions
    refund_op = next(op for op in res["operations"] if op["operation_id"] == "PostRefunds")
    assert refund_op["readiness_state"] == "REQUIRES_PROTOCOL_AMENDMENT"
    assert any("faithful union" in b.lower() for b in refund_op["blockers"])

    # Non-ready operations must possess explicit blockers
    for op in res["operations"]:
        if op["readiness_state"] != "READY_WITH_EXPLICIT_WRAPPER_POLICY":
            assert len(op["blockers"]) > 0, f"Missing blockers for non-ready operation: {op['operation_id']}"


def test_on_disk_artifacts_integrity():
    """Verify that all Track 1 artifacts exist on disk and agree with audit results."""
    assert os.path.exists(JSON_MATRIX_PATH)
    assert os.path.exists(MD_MATRIX_PATH)
    assert os.path.exists(MD_AUDIT_PATH)

    with open(JSON_MATRIX_PATH, "r", encoding="utf-8") as f:
        disk_data = json.load(f)

    assert disk_data["summary"]["total_operations_audited"] == 37
    assert len(disk_data["operations"]) == 37

    with open(MD_MATRIX_PATH, "r", encoding="utf-8") as f:
        md_matrix = f.read()
    assert "Stage B Full-Cohort Extraction Readiness Matrix" in md_matrix
    assert "Active Operations Readiness Ledger (30 Operations)" in md_matrix

    with open(MD_AUDIT_PATH, "r", encoding="utf-8") as f:
        md_audit = f.read()
    assert "Stage B Full-Cohort Extraction Readiness Audit Report" in md_audit
    assert "Extractor Capability Gap Analysis" in md_audit

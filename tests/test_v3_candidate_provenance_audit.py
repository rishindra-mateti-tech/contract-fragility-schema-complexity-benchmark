#!/usr/bin/env python3
"""Tests for V3 Candidate Provenance and Difference Audit."""

import json
import os
import pytest

from src.audit_v3_candidate_provenance import (
    execute_v3_provenance_audit,
    AUDIT_JSON,
    AUDIT_MD,
    REJECTION_MD,
    COVERAGE_MATRIX_JSON,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_provenance_audit_executes_with_zero_failures():
    """Verify that execute_v3_provenance_audit completes with 0 failures."""
    rep = execute_v3_provenance_audit()
    assert rep["total_failures"] == 0
    assert rep["total_candidates_audited"] == 18
    assert os.path.exists(AUDIT_JSON)
    assert os.path.exists(AUDIT_MD)
    assert os.path.exists(REJECTION_MD)
    assert os.path.exists(COVERAGE_MATRIX_JSON)


def test_full_30_manifest_operation_reconciliation():
    """Assert complete mathematical reconciliation across all 30 manifest operations."""
    with open(AUDIT_JSON, "r", encoding="utf-8") as f:
        rep = json.load(f)

    audited_count = len(rep["candidate_results"])
    rejected_count = len(rep["rejection_register"])
    pilots_count = 2  # SLOT_GITHUB_01 and SLOT_STRIPE_02

    assert audited_count == 18
    assert rejected_count == 10
    assert audited_count + rejected_count + pilots_count == 30


def test_coverage_matrix_accurately_records_adapters():
    """Verify adapter coverage matrix attributes adapters correctly."""
    with open(COVERAGE_MATRIX_JSON, "r", encoding="utf-8") as f:
        mat = json.load(f)

    assert len(mat) == 18

    # Slack slots
    for sid in ["SLOT_SLACK_01", "SLOT_SLACK_02", "SLOT_SLACK_03"]:
        assert "OpenAPI2FormDataAdapter" in mat[sid]["adapters_used"]
        assert "form" in mat[sid]["surfaces"]
        assert "body" not in mat[sid]["surfaces"]

    # Chatwoot slots
    for sid in ["SLOT_CHATWOOT_02", "SLOT_CHATWOOT_03"]:
        assert "ParameterInheritanceAdapter" in mat[sid]["adapters_used"]
        assert "path" in mat[sid]["surfaces"]

    # Unadapted slots
    for sid in ["SLOT_TWILIO_01", "SLOT_BOX_01", "SLOT_LINE_01"]:
        assert mat[sid]["adapters_used"] == []


def test_audit_detects_prohibited_nullable():
    """Test that check_for_raw_nullable flags bare nullable keyword."""
    from src.audit_v3_candidate_provenance import check_for_raw_nullable
    bad_schema = {
        "type": "string",
        "nullable": True
    }
    errs = check_for_raw_nullable(bad_schema, "#")
    assert len(errs) == 1
    assert "Prohibited 'nullable'" in errs[0]

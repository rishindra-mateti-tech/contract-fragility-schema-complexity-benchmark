#!/usr/bin/env python3
"""Tests for Stage B Candidate Extraction Pipeline V4."""

import json
import os
import sys
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.extract_stage_b_batch_candidates_v4 import (
    V4_OUTPUT_BASE,
    RESULTS_JSON,
    RESULTS_MD,
)
from src.validate_stage_b_intermediate_representation import IntermediateRepresentationValidator


def test_batch_v4_execution_produces_exact_counts():
    """Verify Batch V4 produces exactly 22 candidates, 6 rejections, and 2 skipped pilots."""
    assert os.path.exists(RESULTS_JSON)
    assert os.path.exists(RESULTS_MD)

    with open(RESULTS_JSON, "r", encoding="utf-8") as f:
        res = json.load(f)

    summary = res["summary"]
    assert summary["manifest_total"] == 30
    assert summary["pilots_skipped"] == 2
    assert summary["candidates_generated"] == 22
    assert summary["candidates_rejected"] == 6
    assert summary["candidates_generated"] + summary["candidates_rejected"] + summary["pilots_skipped"] == 30


def test_v4_adapter_attribution():
    """Verify adapter attribution across all adapted families in V4."""
    # Slack candidates must record OpenAPI2FormDataAdapter
    for slot_id in ["SLOT_SLACK_01", "SLOT_SLACK_02", "SLOT_SLACK_03"]:
        meta_p = os.path.join(V4_OUTPUT_BASE, slot_id, "extraction_metadata.json")
        with open(meta_p, "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert "OpenAPI2FormDataAdapter" in meta["adapters_used"]

    # Chatwoot 02 and 03 must record ParameterInheritanceAdapter
    for slot_id in ["SLOT_CHATWOOT_02", "SLOT_CHATWOOT_03"]:
        meta_p = os.path.join(V4_OUTPUT_BASE, slot_id, "extraction_metadata.json")
        with open(meta_p, "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert "ParameterInheritanceAdapter" in meta["adapters_used"]

    # DigitalOcean 01 must record LocalReferenceResolver
    meta_p = os.path.join(V4_OUTPUT_BASE, "SLOT_DO_01", "extraction_metadata.json")
    with open(meta_p, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert "LocalReferenceResolver" in meta["adapters_used"]

    # SQLite MCP tools must record PythonAstToolExtractor
    for slot_id in ["SLOT_MCP_SQLITE_01", "SLOT_MCP_SQLITE_02", "SLOT_MCP_SQLITE_03"]:
        meta_p = os.path.join(V4_OUTPUT_BASE, slot_id, "extraction_metadata.json")
        with open(meta_p, "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert "PythonAstToolExtractor" in meta["adapters_used"]


def test_v4_rejections_rationale_and_classification():
    """Verify all 6 rejections have rigorous, fail-closed rationale and correct codes."""
    with open(RESULTS_JSON, "r", encoding="utf-8") as f:
        res = json.load(f)

    rejections_by_slot = {r["slot_id"]: r for r in res["candidates_rejected"]}
    assert len(rejections_by_slot) == 6

    # 1. Stripe union slot
    assert "SLOT_STRIPE_03" in rejections_by_slot
    assert rejections_by_slot["SLOT_STRIPE_03"]["rejection_code"] == "FEAT_POLYMORPHIC_UNION"

    # 2. DigitalOcean readOnly properties
    assert "SLOT_DO_02" in rejections_by_slot
    assert rejections_by_slot["SLOT_DO_02"]["rejection_code"] == "ERR_READONLY_IN_REQUEST_SURFACE"

    assert "SLOT_DO_03" in rejections_by_slot
    assert rejections_by_slot["SLOT_DO_03"]["rejection_code"] == "ERR_READONLY_IN_REQUEST_SURFACE"

    # 3. TypeScript AST runtime schema builders
    for slot_id in ["SLOT_MCP_GITHUB_01", "SLOT_MCP_GITHUB_02", "SLOT_MCP_GITHUB_03"]:
        assert slot_id in rejections_by_slot
        assert rejections_by_slot[slot_id]["rejection_code"] == "ERR_RUNTIME_SCHEMA_BUILDER_REJECTED"


def test_v4_bundle_intermediate_representation_compliance():
    """Verify each candidate bundle contains a valid intermediate representation."""
    ir_validator = IntermediateRepresentationValidator()
    slot_dirs = sorted(os.listdir(V4_OUTPUT_BASE))
    assert len(slot_dirs) == 22

    for slot_id in slot_dirs:
        ir_file = os.path.join(V4_OUTPUT_BASE, slot_id, "intermediate_representation.json")
        assert os.path.exists(ir_file)
        with open(ir_file, "r", encoding="utf-8") as f:
            ir_data = json.load(f)
        valid, errors = ir_validator.validate(ir_data)
        assert valid, f"IR validation failed for {slot_id}: {errors}"


def test_v4_strict_anti_ai_and_lifecycle_invariants():
    """Verify strict invariants across all V4 candidate bundles."""
    slot_dirs = sorted(os.listdir(V4_OUTPUT_BASE))
    for slot_id in slot_dirs:
        slot_path = os.path.join(V4_OUTPUT_BASE, slot_id)
        for fname in os.listdir(slot_path):
            fpath = os.path.join(slot_path, fname)
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            assert "CANONICAL_FAITHFUL" not in content, f"Forbidden CANONICAL_FAITHFUL in {fpath}"
            if fname == "candidate_contract.json":
                assert '"nullable"' not in content, f"Raw nullable found in contract {fpath}"

        meta_p = os.path.join(slot_path, "extraction_metadata.json")
        with open(meta_p, "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert meta["lifecycle_status"] == "EXTRACTED_PENDING_HUMAN_VALIDATION"
        assert meta["declaration"] == "NOT_INDEPENDENTLY_VALIDATED"
        assert meta["extractor_version"] == "4.0.0"


def test_historical_lineage_immutability():
    """Verify prior extraction candidates V1, V2, and V3 remain intact."""
    v1_dir = os.path.join(ROOT_DIR, "data_stage_b", "extraction_candidates")
    v2_dir = os.path.join(ROOT_DIR, "data_stage_b", "extraction_candidates_v2")
    v3_dir = os.path.join(ROOT_DIR, "data_stage_b", "extraction_candidates_v3")

    assert os.path.exists(v1_dir)
    assert len(os.listdir(v1_dir)) == 13

    assert os.path.exists(v2_dir)
    assert len(os.listdir(v2_dir)) == 13

    assert os.path.exists(v3_dir)
    assert len(os.listdir(v3_dir)) == 18

#!/usr/bin/env python3
"""Tests for Stage B Candidate Extraction Pipeline V3."""

import glob
import json
import os
import pytest

from src.extract_stage_b_batch_candidates_v3 import (
    run_batch_v3_extraction,
    V3_OUTPUT_BASE,
    RESULTS_JSON,
    RESULTS_MD,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_batch_v3_execution_produces_exact_counts():
    """Verify Batch V3 produces exactly 18 candidates and 10 rejections."""
    assert os.path.exists(RESULTS_JSON)
    assert os.path.exists(RESULTS_MD)

    with open(RESULTS_JSON, "r", encoding="utf-8") as f:
        res = json.load(f)

    summary = res["summary"]
    assert summary["total_manifest"] == 30
    assert summary["extracted_pilots_skipped"] == 2
    assert summary["candidates_generated"] == 18
    assert summary["candidates_rejected"] == 10
    assert summary["candidates_generated"] + summary["candidates_rejected"] + summary["extracted_pilots_skipped"] == 30


def test_v3_candidates_adapter_attribution():
    """Verify that Chatwoot and Slack candidates correctly record adapter usage."""
    # Slack candidates must use OpenAPI2FormDataAdapter
    for slot_id in ["SLOT_SLACK_01", "SLOT_SLACK_02", "SLOT_SLACK_03"]:
        meta_p = os.path.join(V3_OUTPUT_BASE, slot_id, "extraction_metadata.json")
        with open(meta_p, "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert "OpenAPI2FormDataAdapter" in meta["adapters_used"]

        contract_p = os.path.join(V3_OUTPUT_BASE, slot_id, "candidate_contract.json")
        with open(contract_p, "r", encoding="utf-8") as f:
            contract = json.load(f)
        assert "form" in contract["properties"]
        assert "body" not in contract["properties"]

    # Chatwoot 02 and 03 must use ParameterInheritanceAdapter
    for slot_id in ["SLOT_CHATWOOT_02", "SLOT_CHATWOOT_03"]:
        meta_p = os.path.join(V3_OUTPUT_BASE, slot_id, "extraction_metadata.json")
        with open(meta_p, "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert "ParameterInheritanceAdapter" in meta["adapters_used"]

        contract_p = os.path.join(V3_OUTPUT_BASE, slot_id, "candidate_contract.json")
        with open(contract_p, "r", encoding="utf-8") as f:
            contract = json.load(f)
        assert "path" in contract["properties"]
        assert "body" in contract["properties"]


def test_v3_zero_canonical_faithful_and_all_pending_validation():
    """Verify that zero candidates in V3 have CANONICAL_FAITHFUL status."""
    for sdir in glob.glob(os.path.join(V3_OUTPUT_BASE, "*")):
        meta_p = os.path.join(sdir, "extraction_metadata.json")
        with open(meta_p, "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert meta["lifecycle_status"] == "EXTRACTED_PENDING_HUMAN_VALIDATION"
        assert meta["lifecycle_status"] != "CANONICAL_FAITHFUL"
        assert meta["declaration"] == "NOT_INDEPENDENTLY_VALIDATED"


def test_historical_v1_and_v2_artifacts_remain_immutable():
    """Verify that historical V1 and V2 candidate directories are preserved."""
    v1_dir = os.path.join(ROOT_DIR, "data_stage_b", "extraction_candidates")
    v2_dir = os.path.join(ROOT_DIR, "data_stage_b", "extraction_candidates_v2")

    assert os.path.exists(v1_dir), "Historical V1 directory must exist"
    assert os.path.exists(v2_dir), "Historical V2 directory must exist"

    v1_slots = [d for d in glob.glob(os.path.join(v1_dir, "*")) if os.path.isdir(d)]
    v2_slots = [d for d in glob.glob(os.path.join(v2_dir, "*")) if os.path.isdir(d)]

    assert len(v1_slots) == 13, f"Expected 13 V1 candidates, found {len(v1_slots)}"
    assert len(v2_slots) == 13, f"Expected 13 V2 candidates, found {len(v2_slots)}"

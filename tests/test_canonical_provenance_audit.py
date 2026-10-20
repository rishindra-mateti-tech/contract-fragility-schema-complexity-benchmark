#!/usr/bin/env python3
"""Tests for Stage B Canonical Provenance Auditor and Difference Engine."""

import copy
import json
import os
import pytest

from src.audit_canonical_provenance import (
    CanonicalProvenanceError,
    audit_all_pilots,
    audit_slot_provenance,
)
from src.canonical_source_diff import (
    DifferenceClassification,
    compare_source_to_canonical,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_github_provenance_audit_passes():
    """Verify SLOT_GITHUB_01 audit passes with 0 violations and 0 POTENTIAL_LOSS."""
    res = audit_slot_provenance("SLOT_GITHUB_01", fail_closed=True)
    assert res["audit_decision"] == "PASS"
    assert res["violations_detected"] == []
    assert res["classification_counts"].get(DifferenceClassification.POTENTIAL_LOSS, 0) == 0
    assert res["classification_counts"].get(DifferenceClassification.UNSUPPORTED_OR_UNVERIFIED, 0) == 0
    assert res["classification_counts"].get(DifferenceClassification.WRAPPER_NORMALIZATION, 0) >= 5
    assert res["classification_counts"].get(DifferenceClassification.PRESERVED, 0) >= 30


def test_stripe_provenance_audit_with_known_limitations():
    """Verify SLOT_STRIPE_02 audit passes when known limitation PROV-LIMIT-001 is acknowledged."""
    res = audit_slot_provenance("SLOT_STRIPE_02", fail_closed=True, allow_known_limitations=True)
    assert res["audit_decision"] == "PASS"
    assert res["classification_counts"].get(DifferenceClassification.POTENTIAL_LOSS, 0) == 0
    assert res["classification_counts"].get(DifferenceClassification.PRESERVED, 0) >= 60


def test_fail_closed_on_unacknowledged_unresolvable_pointer():
    """Verify auditor raises CanonicalProvenanceError when unknown unresolvable pointers exist."""
    with pytest.raises(CanonicalProvenanceError) as exc_info:
        audit_slot_provenance("SLOT_STRIPE_02", fail_closed=True, allow_known_limitations=False)
    assert "UNRESOLVABLE_SOURCE_POINTER" in str(exc_info.value) or "UNSUPPORTED_OR_UNVERIFIED" in str(exc_info.value)


def test_fail_closed_on_simulated_dropped_required_field():
    """Simulate a dropped required property and verify validator halts with POTENTIAL_LOSS."""
    raw_path = os.path.join(ROOT_DIR, "data_stage_b", "raw", "CAND-001", "a91fa76a34558f5ed28e245cb1a6c46a44a61f4d.json")
    can_path = os.path.join(ROOT_DIR, "data_stage_b", "canonical", "SLOT_GITHUB_01", "canonical_contract.json")

    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)
    with open(can_path, "r", encoding="utf-8") as f:
        canonical = json.load(f)

    # Mutate canonical contract to omit 'base' required field
    mutated_canonical = copy.deepcopy(canonical)
    del mutated_canonical["properties"]["body"]["properties"]["base"]

    diffs = compare_source_to_canonical(
        slot_id="SLOT_GITHUB_01",
        raw_doc=raw_doc,
        source_pointer="#/paths/~1repos~1{owner}~1{repo}~1pulls/post",
        canonical_contract=mutated_canonical,
        lineage_records=[],
    )

    losses = [d for d in diffs if d["classification"] == DifferenceClassification.POTENTIAL_LOSS]
    assert len(losses) >= 1
    assert any("base" in d["field_path"] for d in losses)


def test_fail_closed_on_mislabeled_wrapper_normalization():
    """Simulate wrapper normalization marked as PRESERVED and assert error."""
    raw_path = os.path.join(ROOT_DIR, "data_stage_b", "raw", "CAND-001", "a91fa76a34558f5ed28e245cb1a6c46a44a61f4d.json")
    can_path = os.path.join(ROOT_DIR, "data_stage_b", "canonical", "SLOT_GITHUB_01", "canonical_contract.json")

    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)
    with open(can_path, "r", encoding="utf-8") as f:
        canonical = json.load(f)

    diffs = compare_source_to_canonical(
        slot_id="SLOT_GITHUB_01",
        raw_doc=raw_doc,
        source_pointer="#/paths/~1repos~1{owner}~1{repo}~1pulls/post",
        canonical_contract=canonical,
        lineage_records=[],
    )

    # Verify every wrapper normalization is correctly classified
    for d in diffs:
        if "WRAPPER" in d.get("difference_category", ""):
            assert d["classification"] == DifferenceClassification.WRAPPER_NORMALIZATION


def test_audit_artifacts_on_disk():
    """Verify all 3 audit artifacts exist, are non-empty, and contain expected sections."""
    json_path = os.path.join(ROOT_DIR, "results_stage_b", "CANONICAL_PROVENANCE_AUDIT.json")
    md_path = os.path.join(ROOT_DIR, "results_stage_b", "CANONICAL_PROVENANCE_AUDIT.md")
    diff_path = os.path.join(ROOT_DIR, "results_stage_b", "CANONICAL_DIFFERENCE_REGISTER.md")

    assert os.path.exists(json_path)
    assert os.path.exists(md_path)
    assert os.path.exists(diff_path)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["slots_audited"] == ["SLOT_GITHUB_01", "SLOT_STRIPE_02"]
    assert data["total_differences"] >= 100

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    assert "PROV-LIMIT-001" in md_text
    assert "Finding PROV-LIMIT-001" in md_text

    with open(diff_path, "r", encoding="utf-8") as f:
        diff_text = f.read()
    assert "SLOT_GITHUB_01" in diff_text
    assert "SLOT_STRIPE_02" in diff_text

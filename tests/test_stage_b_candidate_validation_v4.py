#!/usr/bin/env python3
"""Tests for Stage B Candidate Bundle Validator V4."""

import json
import os
import shutil
import sys
import tempfile
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.stage_b_candidate_validation_v4 import (
    CandidateValidatorV4,
    REQUIRED_V4_ARTIFACTS,
)
V4_OUTPUT_BASE = os.path.join(ROOT_DIR, "data_stage_b", "extraction_candidates_v4")


def test_validator_validates_all_22_bundles_on_disk():
    """Verify that every generated candidate bundle in data_stage_b passes validation."""
    validator = CandidateValidatorV4()
    slot_dirs = sorted(os.listdir(V4_OUTPUT_BASE))
    assert len(slot_dirs) == 22

    for slot_id in slot_dirs:
        slot_dir = os.path.join(V4_OUTPUT_BASE, slot_id)
        valid, errors = validator.validate_candidate_bundle(slot_dir, slot_id)
        assert valid, f"Candidate validation failed for {slot_id}: {errors}"
        assert len(errors) == 0


def test_validator_rejects_missing_artifact():
    """Verify that validator fails closed when any of the 13 required artifacts is absent."""
    validator = CandidateValidatorV4()
    sample_slot = "SLOT_BOX_01"
    src_slot_dir = os.path.join(V4_OUTPUT_BASE, sample_slot)

    with tempfile.TemporaryDirectory() as tmp_dir:
        test_slot_dir = os.path.join(tmp_dir, sample_slot)
        shutil.copytree(src_slot_dir, test_slot_dir)

        # Remove one required artifact
        os.remove(os.path.join(test_slot_dir, "intermediate_representation.json"))

        valid, errors = validator.validate_candidate_bundle(test_slot_dir, sample_slot)
        assert not valid
        assert any("Missing required V4 artifact: intermediate_representation.json" in e for e in errors)


def test_validator_rejects_canonical_faithful():
    """Verify that validator strictly rejects bundles containing CANONICAL_FAITHFUL."""
    validator = CandidateValidatorV4()
    sample_slot = "SLOT_BOX_01"
    src_slot_dir = os.path.join(V4_OUTPUT_BASE, sample_slot)

    with tempfile.TemporaryDirectory() as tmp_dir:
        test_slot_dir = os.path.join(tmp_dir, sample_slot)
        shutil.copytree(src_slot_dir, test_slot_dir)

        # Inject forbidden token into review packet
        packet_path = os.path.join(test_slot_dir, "review_packet.md")
        with open(packet_path, "a", encoding="utf-8") as f:
            f.write("\nStatus: CANONICAL_FAITHFUL\n")

        valid, errors = validator.validate_candidate_bundle(test_slot_dir, sample_slot)
        assert not valid
        assert any("CANONICAL_FAITHFUL" in e for e in errors)


def test_validator_rejects_raw_nullable():
    """Verify that validator rejects candidate contracts containing raw OpenAPI nullable."""
    validator = CandidateValidatorV4()
    sample_slot = "SLOT_BOX_01"
    src_slot_dir = os.path.join(V4_OUTPUT_BASE, sample_slot)

    with tempfile.TemporaryDirectory() as tmp_dir:
        test_slot_dir = os.path.join(tmp_dir, sample_slot)
        shutil.copytree(src_slot_dir, test_slot_dir)

        contract_path = os.path.join(test_slot_dir, "candidate_contract.json")
        with open(contract_path, "r", encoding="utf-8") as f:
            contract = json.load(f)

        # Inject raw nullable keyword
        contract["properties"]["description"] = {"type": "string", "nullable": True}
        with open(contract_path, "w", encoding="utf-8") as f:
            json.dump(contract, f, indent=2)

        valid, errors = validator.validate_candidate_bundle(test_slot_dir, sample_slot)
        assert not valid
        assert any("Raw OpenAPI 'nullable' keyword detected" in e for e in errors)


def test_validator_rejects_mismatched_slot_id():
    """Verify that validator detects slot_id mismatch between folder and metadata."""
    validator = CandidateValidatorV4()
    src_slot_dir = os.path.join(V4_OUTPUT_BASE, "SLOT_BOX_01")

    valid, errors = validator.validate_candidate_bundle(src_slot_dir, "SLOT_MISMATCH_99")
    assert not valid
    assert any("Slot ID mismatch in metadata" in e for e in errors)

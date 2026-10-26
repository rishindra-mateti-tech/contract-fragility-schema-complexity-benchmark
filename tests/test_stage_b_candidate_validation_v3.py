#!/usr/bin/env python3
"""Tests for Stage B Candidate Validator V3."""

import glob
import json
import os
import pytest

from src.stage_b_candidate_validation_v3 import (
    CandidateValidatorV3,
    REQUIRED_V3_ARTIFACTS,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V3_DIR = os.path.join(ROOT_DIR, "data_stage_b", "extraction_candidates_v3")


@pytest.fixture
def validator():
    return CandidateValidatorV3()


def test_all_18_generated_v3_bundles_pass_validation(validator):
    """Assert every generated V3 candidate passes strict V3 validation."""
    slot_dirs = sorted([d for d in glob.glob(os.path.join(V3_DIR, "*")) if os.path.isdir(d)])
    assert len(slot_dirs) == 18, f"Expected 18 candidate directories, got {len(slot_dirs)}"

    for sdir in slot_dirs:
        slot_id = os.path.basename(sdir)
        is_valid, errors = validator.validate_candidate_bundle(sdir, expected_slot_id=slot_id)
        assert is_valid is True, f"Candidate {slot_id} failed validation with errors:\n" + "\n".join(errors)


def test_validator_rejects_canonical_placement(validator, tmp_path):
    """Test that placing a candidate bundle inside canonical directory is rejected."""
    canonical_dir = os.path.join(ROOT_DIR, "data_stage_b", "canonical", "SLOT_FAKE")
    is_valid, errors = validator.validate_candidate_bundle(canonical_dir)
    assert is_valid is False
    assert any("QUARANTINE_VIOLATION" in e for e in errors)


def test_validator_rejects_missing_required_file(validator):
    """Test that missing one of the 11 required files causes validation failure."""
    first_slot = sorted(glob.glob(os.path.join(V3_DIR, "*")))[0]
    slot_id = os.path.basename(first_slot)

    # Validate against empty temp directory
    import tempfile
    with tempfile.TemporaryDirectory() as empty_dir:
        is_valid, errors = validator.validate_candidate_bundle(empty_dir, expected_slot_id=slot_id)
        assert is_valid is False
        assert len(errors) >= 11
        assert any("MISSING_ARTIFACT" in e for e in errors)

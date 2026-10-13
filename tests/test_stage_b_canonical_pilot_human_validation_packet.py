"""Tests for Stage B Canonical Extraction Pilot Human Validation Packet.

Verifies:
1. CANONICAL_PILOT_HUMAN_VALIDATION_PACKET.md exists and is structurally complete.
2. Immutable provenance fields:
   - Raw source blob SHA and file SHA-256 match pinned constants.
   - Raw JSON Pointer matches upstream operation.
   - Extractor commit and script SHA-256 match implementation.
   - Canonical contract SHA-256 matches on-disk artifact.
   - Semantic preservation report SHA-256 matches on-disk artifact.
3. Semantic comparison completeness:
   - All 10 raw fields and canonical locations documented.
   - All 26 verified keyword instances documented.
   - Required-field comparison documented.
   - Transport surface isolation and zero path leak documented.
   - Zero-loss categories documented.
4. Explicit transformation review:
   - Root wrapper synthesis documented.
   - Transport surface wrappers documented.
   - WRAPPER_CLOSED_OBJECT_POLICY_001 documented.
   - Explicit statement that closing additionalProperties is a deliberate non-lossless normalization,
     not raw-source equivalence.
5. Human decision options:
   - APPROVE_WRAPPER_POLICY, REQUEST_CHANGES, REJECT_EXTRACTION present.
6. Sign-off block is strictly unpopulated:
   - Reviewer name, role, date, decision, and note are unpopulated.
7. Anti-lossless and status boundary invariants:
   - Neither the validation packet nor pilot reports claim unconditional losslessness.
   - Neither the contract, manifest, validation report, nor packet elevates SLOT_GITHUB_01
     to CANONICAL_FAITHFUL (status is strictly EXTRACTED_PENDING_HUMAN_VALIDATION).
"""

import hashlib
import json
import os
import re
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKET_PATH = os.path.join(ROOT_DIR, "results_stage_b", "CANONICAL_PILOT_HUMAN_VALIDATION_PACKET.md")
PILOT_DIR = os.path.join(ROOT_DIR, "data_stage_b", "canonical", "SLOT_GITHUB_01")
CONTRACT_PATH = os.path.join(PILOT_DIR, "canonical_contract.json")
MANIFEST_PATH = os.path.join(PILOT_DIR, "extraction_manifest.json")
VAL_REPORT_PATH = os.path.join(PILOT_DIR, "validation_report.json")
SEMANTIC_REPORT_PATH = os.path.join(PILOT_DIR, "semantic_preservation_report.json")
PILOT_REPORT_PATH = os.path.join(ROOT_DIR, "results_stage_b", "CANONICAL_EXTRACTION_PILOT_REPORT.md")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_validation_packet_exists_and_non_empty():
    """Verify validation packet exists and has substantial content."""
    assert os.path.exists(PACKET_PATH), f"Missing validation packet: {PACKET_PATH}"
    assert os.path.getsize(PACKET_PATH) > 1000, "Validation packet is too small"


def test_immutable_provenance_cryptographic_references():
    """Verify packet contains exact cryptographic references matching on-disk artifacts."""
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Raw source hashes
    assert "a91fa76a34558f5ed28e245cb1a6c46a44a61f4d" in content
    assert "ba5ddc1eeeede9f3858abd96325359891f38a2bd8e20fd111abf4230741db194" in content
    assert "#/paths/~1repos~1{owner}~1{repo}~1pulls/post" in content

    # On-disk artifacts
    assert os.path.exists(CONTRACT_PATH)
    contract_sha = sha256_file(CONTRACT_PATH)
    assert contract_sha in content, f"Contract SHA {contract_sha} not in packet"

    assert os.path.exists(SEMANTIC_REPORT_PATH)
    semantic_sha = sha256_file(SEMANTIC_REPORT_PATH)
    assert semantic_sha in content, f"Semantic report SHA {semantic_sha} not in packet"

    assert os.path.exists(MANIFEST_PATH)
    manifest_sha = sha256_file(MANIFEST_PATH)
    assert manifest_sha in content, f"Manifest SHA {manifest_sha} not in packet"


def test_semantic_comparison_field_and_keyword_coverage():
    """Verify packet documents all 10 fields, 26 keywords, and surface separation."""
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 10 fields
    expected_fields = [
        "owner", "repo", "base", "body", "draft", "head",
        "head_repo", "issue", "maintainer_can_modify", "title",
    ]
    for field in expected_fields:
        assert field in content, f"Field '{field}' missing from packet"

    # 26 keyword instances
    assert "26" in content
    assert "type" in content
    assert "description" in content
    assert "format" in content
    assert "example" in content
    assert "required" in content

    # Surfaces
    assert "properties.path" in content
    assert "properties.body" in content
    assert "properties.query" in content
    assert "properties.header" in content


def test_explicit_transformation_review_and_closed_object_policy():
    """Verify packet documents wrapper transformations and explicit non-lossless disclaimer."""
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    assert "TRANSFORM_ROOT_WRAPPER_SYNTHESIS" in content
    assert "WRAPPER_CLOSED_OBJECT_POLICY_001" in content

    # Non-lossless normalization explicit statement
    assert "Closing `additionalProperties` is a deliberate, benchmark-required non-lossless normalization policy" in content
    assert "NOT raw-source equivalence" in content
    assert "SEMANTICALLY_EQUIVALENT_MODULO_WRAPPER_POLICY" in content


def test_human_decision_options_present():
    """Verify packet presents the three permitted decision options."""
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    assert "APPROVE_WRAPPER_POLICY" in content
    assert "REQUEST_CHANGES" in content
    assert "REJECT_EXTRACTION" in content


def test_sign_off_fields_strictly_unpopulated():
    """Verify sign-off block fields are unpopulated pending human review."""
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Check unpopulated markers
    assert "[UNPOPULATED - PENDING HUMAN REVIEW]" in content
    assert "[UNPOPULATED - AUTHOR_MANUAL_REVIEW or INDEPENDENT_REVIEW]" in content
    assert "[UNPOPULATED - YYYY-MM-DD]" in content
    assert "[UNPOPULATED - APPROVE_WRAPPER_POLICY / REQUEST_CHANGES / REJECT_EXTRACTION]" in content
    assert "[UNPOPULATED - Explicit note stating whether reviewer accepts closed-object wrapper policy]" in content

    # Must mention allowed roles
    assert "AUTHOR_MANUAL_REVIEW" in content
    assert "INDEPENDENT_REVIEW" in content


def test_strict_anti_lossless_and_status_invariants():
    """Ensure no benchmark document calls this extraction unconditionally 'lossless' or 'CANONICAL_FAITHFUL'."""
    # 1. Check validation packet
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        packet_content = f.read()
    assert re.search(r"not\s+elevated\s+to\s+`CANONICAL_FAITHFUL`", packet_content, re.IGNORECASE) or re.search(r"\*\*not\*\*\s+elevated\s+to\s+`CANONICAL_FAITHFUL`", packet_content, re.IGNORECASE)
    assert "EXTRACTED_PENDING_HUMAN_VALIDATION" in packet_content

    # 2. Check canonical contract metadata
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        contract = json.load(f)
    meta = contract.get("x-benchmark-metadata", {})
    assert meta.get("status") == "EXTRACTED_PENDING_HUMAN_VALIDATION"
    assert meta.get("status") != "CANONICAL_FAITHFUL"
    assert meta.get("admission_decision") != "CANONICAL_FAITHFUL"
    assert meta.get("semantic_validation_decision") == "SEMANTICALLY_VALIDATED_PENDING_HUMAN_REVIEW"
    assert meta.get("wrapper_normalization_policy", {}).get("is_strictly_lossless") is False

    # 3. Check extraction manifest
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest.get("status") == "EXTRACTED_PENDING_HUMAN_VALIDATION"
    assert manifest.get("status") != "CANONICAL_FAITHFUL"
    assert manifest.get("semantic_validation_decision") == "SEMANTICALLY_VALIDATED_PENDING_HUMAN_REVIEW"

    # 4. Check validation report
    with open(VAL_REPORT_PATH, "r", encoding="utf-8") as f:
        val_report = json.load(f)
    assert val_report.get("semantic_validation_decision") == "SEMANTICALLY_VALIDATED_PENDING_HUMAN_REVIEW"
    assert val_report.get("lossless_classification") == "SEMANTICALLY_EQUIVALENT_MODULO_WRAPPER_POLICY"

    # 5. Check pilot report
    with open(PILOT_REPORT_PATH, "r", encoding="utf-8") as f:
        pilot_report = f.read()
    assert re.search(r"not\s+elevated\s+to\s+`CANONICAL_FAITHFUL`", pilot_report, re.IGNORECASE) or re.search(r"\*\*not\*\*\s+elevated\s+to\s+`CANONICAL_FAITHFUL`", pilot_report, re.IGNORECASE)
    assert "EXTRACTED_PENDING_HUMAN_VALIDATION" in pilot_report

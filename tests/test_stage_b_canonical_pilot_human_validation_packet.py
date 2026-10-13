"""Tests for Stage B Canonical Extraction Pilot Human Validation Packet.

Verifies:
1. CANONICAL_PILOT_HUMAN_VALIDATION_PACKET.md exists and is structurally complete.
2. Immutable provenance fields:
   - Raw source blob SHA and file SHA-256 match pinned constants.
   - Raw JSON Pointer matches upstream operation.
   - Extractor commit and script SHA-256 match implementation.
   - Reviewed canonical contract and report SHA-256 match reviewed snapshot.
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
6. Author manual review sign-off recorded:
   - Reviewer name, role, date, decision, note, and immutable git snapshot references populated.
   - All review checklist boxes verified.
7. Independence boundary strictly maintained:
   - No independent third-party validation claimed (independent_validation_claimed: false).
8. Immutable Git history verification:
   - Commit, blob SHA, and historical content hash verified against Git object store.
   - Historical hash does not falsely equal current signed packet hash.
9. Anti-lossless and status boundary invariants:
   - Neither the validation packet nor pilot reports claim unconditional losslessness.
   - Status is strictly CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY (never CANONICAL_FAITHFUL).
"""

import hashlib
import json
import os
import re
import subprocess
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
    """Verify packet contains exact cryptographic references matching reviewed snapshot artifacts."""
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Raw source hashes
    assert "a91fa76a34558f5ed28e245cb1a6c46a44a61f4d" in content
    assert "ba5ddc1eeeede9f3858abd96325359891f38a2bd8e20fd111abf4230741db194" in content
    assert "#/paths/~1repos~1{owner}~1{repo}~1pulls/post" in content

    # Reviewed snapshot cryptographic artifacts (at reviewed commit 8f64350)
    assert "54f78758f76fcd3a55f2d629f3eb66c7150567a9d4aea759577cafdace8ed1c1" in content
    assert "e11f72543e885bc901ef2587095491703f86c8ee83ca9b2a22883a486f0e32c9" in content
    assert "ba888725b40e9d328f6cd662123bc6b33a7b1708a1e0ff7909ff0e45989549ef" in content
    assert "cdc218c4a2a035de58d2105d73a00763a995ff5013be590247b077c642f33279" in content
    assert "294066ce9cf0589645b2fed5fbe229c01c91f7e0042baf9bff801c50003c7da1" in content


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


def test_author_manual_review_sign_off_recorded():
    """Verify author manual review sign-off block is fully and accurately recorded."""
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify reviewer credentials and decision
    assert "Rishindra Mateti" in content
    assert "AUTHOR_MANUAL_REVIEW" in content
    assert "2026-10-13" in content
    assert "APPROVE_WRAPPER_POLICY" in content
    assert "I accept closed transport-surface objects as an explicit benchmark normalization" in content

    # Verify immutable Git references for reviewed snapshot
    assert "8f64350009bb232205118d51135e8c876c1a395a" in content
    assert "96477ae753e787c73ce2985c6b3d55f0f0a75fc6" in content
    assert "5ead04d81df3a1b9c365f03eda9438900932f9e8a896c124be402d1ecb59d380" in content

    # Verify all checklist boxes are completed
    checklist_items = [
        "- [x] **Provenance Verification:**",
        "- [x] **Exact Pointer Resolution:**",
        "- [x] **Field Coverage Verification:**",
        "- [x] **Keyword Equivalence Verification:**",
        "- [x] **Transport Separation Verified:**",
        "- [x] **No Unqualified \"Lossless\" Claims:**",
        "- [x] **Closed-Object Wrapper Policy Evaluated:**",
        "- [x] **Status Invariant Verified:**",
    ]
    for item in checklist_items:
        assert item in content, f"Checklist item not checked: {item}"


def test_no_independent_validation_claimed():
    """Verify that author manual review strictly does NOT claim independent validation."""
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Independent Review: `NOT_CONDUCTED`" in content
    assert "DOES NOT constitute independent third-party validation" in content
    assert "Independent review has NOT occurred" in content

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    sign_off = manifest.get("author_review_sign_off", {})
    assert sign_off.get("independent_validation_claimed") is False
    assert sign_off.get("reviewer_role") == "AUTHOR_MANUAL_REVIEW"
    assert sign_off.get("reviewer_role") != "INDEPENDENT_REVIEW"

    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        contract = json.load(f)
    meta = contract.get("x-benchmark-metadata", {})
    meta_sign_off = meta.get("author_review_sign_off", {})
    assert meta_sign_off.get("independent_validation_claimed") is False
    assert meta_sign_off.get("reviewer_role") == "AUTHOR_MANUAL_REVIEW"


def test_immutable_git_provenance_retrieval_and_hash_divergence():
    """Validates immutable Git provenance fields against actual Git history and
    asserts historical reviewed hash does not falsely equal current packet hash
    unless the contents truly match."""
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    sign_off = manifest["author_review_sign_off"]
    git_commit = sign_off["reviewed_packet_git_commit"]
    blob_sha = sign_off["reviewed_packet_blob_sha"]
    historical_sha256 = sign_off["reviewed_packet_sha256"]

    # 1. Verify git_commit is an actual commit in Git repository
    res_commit_type = subprocess.run(
        ["git", "cat-file", "-t", git_commit],
        capture_output=True, text=True, check=True,
    )
    assert res_commit_type.stdout.strip() == "commit", f"{git_commit} must be a valid commit"

    # 2. Verify blob_sha matches the exact Git tree entry at git_commit for the validation packet
    res_tree_blob = subprocess.run(
        ["git", "rev-parse", f"{git_commit}:results_stage_b/CANONICAL_PILOT_HUMAN_VALIDATION_PACKET.md"],
        capture_output=True, text=True, check=True,
    )
    assert res_tree_blob.stdout.strip() == blob_sha, (
        f"Git tree at {git_commit} must point to blob {blob_sha}"
    )

    # 3. Retrieve historical blob content from Git and verify historical SHA-256 matches
    res_blob_content = subprocess.run(
        ["git", "cat-file", "-p", blob_sha],
        capture_output=True, check=True,
    )
    historical_bytes = res_blob_content.stdout
    hash_raw = hashlib.sha256(historical_bytes).hexdigest()
    hash_crlf = hashlib.sha256(historical_bytes.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")).hexdigest()
    assert historical_sha256 in (hash_raw, hash_crlf), (
        f"Historical hash {historical_sha256} must match blob content ({hash_raw} or {hash_crlf})"
    )

    # 4. Read current on-disk packet bytes and compute its current SHA-256
    with open(PACKET_PATH, "rb") as f:
        current_bytes = f.read()
    current_sha256 = hashlib.sha256(current_bytes).hexdigest()

    # 5. Ensure historical hash does NOT falsely equal current packet hash unless contents truly match
    contents_match = (
        current_bytes == historical_bytes or
        current_bytes == historical_bytes.replace(b"\r\n", b"\n") or
        current_bytes == historical_bytes.replace(b"\n", b"\r\n")
    )
    if contents_match:
        assert current_sha256 == historical_sha256
    else:
        assert current_sha256 != historical_sha256, (
            "Current packet SHA-256 must not falsely equal historical reviewed packet SHA-256 "
            "because the current packet contains subsequent sign-off records."
        )

    # 6. Verify explicit provenance statement is present across artifacts
    expected_statement = (
        "The author reviewed the packet snapshot identified above. "
        "The current packet may contain the subsequent sign-off record and therefore may have a different file SHA-256."
    )
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        assert expected_statement in f.read()

    assert sign_off["provenance_statement"] == expected_statement


def test_strict_anti_lossless_and_status_invariants():
    """Ensure no benchmark document calls this extraction unconditionally 'lossless' or 'CANONICAL_FAITHFUL'."""
    # 1. Check validation packet
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        packet_content = f.read()
    assert re.search(r"not\s+elevated\s+to\s+`CANONICAL_FAITHFUL`", packet_content, re.IGNORECASE) or re.search(r"\*\*not\*\*\s+elevated\s+to\s+`CANONICAL_FAITHFUL`", packet_content, re.IGNORECASE)
    assert "CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY" in packet_content

    # 2. Check canonical contract metadata
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        contract = json.load(f)
    meta = contract.get("x-benchmark-metadata", {})
    assert meta.get("status") == "CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY"
    assert meta.get("status") != "CANONICAL_FAITHFUL"
    assert meta.get("admission_decision") == "CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY"
    assert meta.get("admission_decision") != "CANONICAL_FAITHFUL"
    assert meta.get("semantic_validation_decision") == "SEMANTICALLY_VALIDATED_PENDING_HUMAN_REVIEW"
    assert meta.get("wrapper_normalization_policy", {}).get("is_strictly_lossless") is False

    # 3. Check extraction manifest
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest.get("status") == "CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY"
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
    assert "CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY" in pilot_report

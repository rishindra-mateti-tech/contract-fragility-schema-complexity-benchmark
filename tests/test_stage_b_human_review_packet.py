"""Tests for Stage B Human Admission Review Packet and Author Instructions.

Verifies:
1. HUMAN_ADMISSION_REVIEW_PACKET.md and AUTHOR_REVIEW_INSTRUCTIONS.md exist.
2. All five admitted operations have concise, complete review pages with required fields:
   - Operation and source link/pointer
   - Raw blob SHA, raw file SHA-256, and reviewed artifact SHAs
   - Selection rationale ("why selected")
   - Required future mock fixtures
   - Statefulness classification (schema_invocation_mode, external_prerequisite_state)
   - Competing candidates evaluated and rejected with explicit rationales
   - Checkbox list for human reviewer (checked by author reviewer)
   - Signature block with reviewer name, role, date, immutable Git provenance fields, and decision.
3. Cryptographic SHA references match actual on-disk files.
4. Permitted reviewer roles (AUTHOR_MANUAL_REVIEW, INDEPENDENT_REVIEW) are documented.
5. Author review instructions clearly state author review confirms provenance and design
   decisions but does not constitute independent validation.
6. Author manual review is completed and approved, but independent validation is NOT claimed.
7. Immutable Git provenance references (commit, blob SHA, historical SHA-256, recording commit)
   are validated against Git history and verified not to falsely equal current packet hash.
"""

import hashlib
import json
import os
import re
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKET_PATH = os.path.join(ROOT_DIR, "results_stage_b", "HUMAN_ADMISSION_REVIEW_PACKET.md")
INSTRUCTIONS_STAGE_B_PATH = os.path.join(ROOT_DIR, "results_stage_b", "AUTHOR_REVIEW_INSTRUCTIONS.md")
INSTRUCTIONS_ROOT_PATH = os.path.join(ROOT_DIR, "AUTHOR_REVIEW_INSTRUCTIONS.md")
MANIFEST_PATH = os.path.join(ROOT_DIR, "results_stage_b", "stage_b_operation_manifest.yaml")
DECISIONS_JSON_PATH = os.path.join(ROOT_DIR, "results_stage_b", "candidate_admission_decisions.json")
ADMISSION_REVIEW_MD_PATH = os.path.join(ROOT_DIR, "results_stage_b", "CANDIDATE_ADMISSION_REVIEW.md")
REGISTRY_PATH = os.path.join(ROOT_DIR, "results_stage_b", "raw_sources_provenance_registry.json")

EXPECTED_OPERATIONS = [
    ("SLOT_GITHUB_01", "pulls/create", "#/paths/~1repos~1{owner}~1{repo}~1pulls/post"),
    ("SLOT_STRIPE_01", "PostPayouts", "#/paths/~1v1~1payouts/post"),
    ("SLOT_STRIPE_02", "PostShippingRates", "#/paths/~1v1~1shipping_rates/post"),
    ("SLOT_CHATWOOT_01", "create-a-webhook", "#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks/post"),
    ("SLOT_LINE_01", "showLoadingAnimation", "#/paths/~1v2~1bot~1chat~1loading~1start/post"),
]


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_review_packet_and_instructions_exist():
    assert os.path.exists(PACKET_PATH), f"Missing review packet: {PACKET_PATH}"
    assert os.path.getsize(PACKET_PATH) > 1000, "Review packet is empty or suspiciously small"

    assert os.path.exists(INSTRUCTIONS_STAGE_B_PATH), f"Missing author review instructions: {INSTRUCTIONS_STAGE_B_PATH}"
    assert os.path.getsize(INSTRUCTIONS_STAGE_B_PATH) > 500, "Author review instructions file is too small"

    assert os.path.exists(INSTRUCTIONS_ROOT_PATH), f"Missing root author review instructions: {INSTRUCTIONS_ROOT_PATH}"


def test_packet_contains_all_admitted_operations_and_slots():
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    for slot_id, op_id, pointer in EXPECTED_OPERATIONS:
        assert slot_id in content, f"Missing slot ID {slot_id} in review packet"
        assert op_id in content, f"Missing operation ID {op_id} in review packet"
        assert pointer in content, f"Missing pointer {pointer} in review packet"


def test_packet_required_fields_and_sections_per_operation():
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into sections by operation review headers
    op_sections = re.split(r"### Operation Review \d+:", content)
    assert len(op_sections) == 6, f"Expected 5 operation review sections, found {len(op_sections) - 1}"

    for section in op_sections[1:]:
        # 1. Operation Identification & Source Link / Pointer
        assert "Operation Identification & Source Link / Pointer" in section
        assert "HTTP Method & Endpoint:" in section
        assert "Exact OpenAPI Pointer:" in section
        assert "Raw On-Disk Source Path:" in section

        # 2. Cryptographic Provenance & Artifact SHAs
        assert "Cryptographic Provenance & Artifact SHAs" in section
        assert "Raw Source Git Blob SHA:" in section
        assert "Raw Source File SHA-256:" in section
        assert "Reviewed Operation Manifest SHA-256:" in section
        assert "Reviewed Decisions Artifact SHA-256:" in section

        # 3. Selection Rationale
        assert "Selection Rationale (Why Selected)" in section
        assert "Rationale:" in section
        assert "Maximum Nesting Depth:" in section
        assert "Property Count:" in section

        # 4. Required Future Mock Fixtures
        assert "Required Future Mock Fixtures" in section
        assert "_fixture" in section
        assert "Mock Feasibility Status:" in section
        assert "PENDING" in section

        # 5. Operational Statefulness & Invocation Mode
        assert "Operational Statefulness & Invocation Mode Classification" in section
        assert "`schema_invocation_mode`:** `SINGLE_TURN_CONSTRUCTIBLE`" in section
        assert "`external_prerequisite_state`:** `FIXTURE_REQUIRED`" in section

        # 6. Competing Candidates Evaluated & Rejected
        assert "Competing Candidates Evaluated & Rejected" in section
        assert "Explicit Rejection Rationale" in section

        # 7. Checkbox List for Human Reviewer (checked by author reviewer)
        assert "Checkbox List for Human Reviewer" in section
        assert "- [x]" in section
        assert "Provenance Verification:" in section
        assert "JSON Pointer Resolution:" in section
        assert "Structural Rules Compliance:" in section
        assert "Invocation Mode Verified:" in section
        assert "Fixture Requirements Verified:" in section

        # 8. Human Review Sign-Off Block
        assert "Human Review Sign-Off Block" in section
        assert "Reviewer Name:** `Rishindra Mateti`" in section
        assert "Reviewer Role:** `AUTHOR_MANUAL_REVIEW`" in section
        assert "Review Date:** `2026-10-12`" in section
        assert "Reviewed Packet Git Commit:** `bafc6f554e24f8f50346b8fff2afbdfc7acfdb5e`" in section
        assert "Reviewed Packet Git Blob SHA:** `ac7a02cf8543e3ec310bcf3928a44b7c66b7031d`" in section
        assert "Reviewed Packet SHA-256:** `419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b`" in section
        assert "Sign-Off Recording Commit:** `5175e6f7f4049dbbbd3f94ed7e04c932b3d68066`" in section
        assert "Review Decision:** `APPROVE`" in section


def test_packet_sha_references_match_on_disk_artifacts():
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        packet_content = f.read()

    # Manifest SHA-256 match
    manifest_sha = sha256_file(MANIFEST_PATH)
    assert manifest_sha in packet_content, f"Manifest SHA {manifest_sha} not referenced in review packet"

    # Decisions JSON SHA-256 match
    decisions_sha = sha256_file(DECISIONS_JSON_PATH)
    assert decisions_sha in packet_content, f"Decisions JSON SHA {decisions_sha} not referenced in review packet"

    # Raw source hashes match registry
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)
    sources_by_id = {s["candidate_source_id"]: s for s in registry["sources"]}

    with open(DECISIONS_JSON_PATH, "r", encoding="utf-8") as f:
        decisions_data = json.load(f)

    for d in decisions_data["decisions"]:
        c = d["admitted_candidate"]
        cid = c["candidate_source_id"]
        reg_source = sources_by_id[cid]

        assert c["source_blob_sha"] == reg_source["source_file_blob_sha"]
        assert c["raw_file_sha256"] == reg_source["downloaded_file_sha256"]
        assert c["source_blob_sha"] in packet_content
        assert c["raw_file_sha256"] in packet_content


def test_author_review_instructions_integrity_and_boundaries():
    with open(INSTRUCTIONS_STAGE_B_PATH, "r", encoding="utf-8") as f:
        inst = f.read()

    # Must explain that author review confirms provenance and design decisions but is NOT independent validation
    assert "AUTHOR_MANUAL_REVIEW" in inst
    assert "INDEPENDENT_REVIEW" in inst
    assert "DOES NOT constitute independent" in inst or "does not constitute independent" in inst.lower()
    assert "authorial design decisions" in inst.lower() or "design decision" in inst.lower()
    assert "provenance" in inst.lower()
    assert "NOT CONDUCTED" in inst or "not conducted" in inst.lower()

    # Decision options
    assert "APPROVE" in inst
    assert "REQUEST_CHANGES" in inst
    assert "REJECT" in inst


def test_author_manual_review_completed_and_approved():
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        packet_content = f.read()

    assert "**Document Status:** `AUTHOR_MANUAL_REVIEW_COMPLETED` (Independent Review: `NOT_CONDUCTED`)" in packet_content
    assert "Rishindra Mateti" in packet_content
    assert "2026-10-12" in packet_content
    assert "bafc6f554e24f8f50346b8fff2afbdfc7acfdb5e" in packet_content
    assert "ac7a02cf8543e3ec310bcf3928a44b7c66b7031d" in packet_content
    assert "419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b" in packet_content
    assert "5175e6f7f4049dbbbd3f94ed7e04c932b3d68066" in packet_content

    with open(DECISIONS_JSON_PATH, "r", encoding="utf-8") as f:
        decisions = json.load(f)

    meta = decisions["metadata"]
    assert meta["human_review_status"] == "AUTHOR_MANUAL_REVIEW_COMPLETED"
    assert meta["author_review_sign_off"]["reviewer_name"] == "Rishindra Mateti"
    assert meta["author_review_sign_off"]["reviewer_role"] == "AUTHOR_MANUAL_REVIEW"
    assert meta["author_review_sign_off"]["review_date"] == "2026-10-12"
    assert meta["author_review_sign_off"]["reviewed_packet_git_commit"] == "bafc6f554e24f8f50346b8fff2afbdfc7acfdb5e"
    assert meta["author_review_sign_off"]["reviewed_packet_blob_sha"] == "ac7a02cf8543e3ec310bcf3928a44b7c66b7031d"
    assert meta["author_review_sign_off"]["reviewed_packet_sha256"] == "419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b"
    assert meta["author_review_sign_off"]["sign_off_recording_commit"] == "5175e6f7f4049dbbbd3f94ed7e04c932b3d68066"
    assert meta["author_review_sign_off"]["decision"] == "APPROVE"

    for d in decisions["decisions"]:
        admitted = d["admitted_candidate"]
        assert admitted["human_review_status"] == "AUTHOR_MANUAL_REVIEW_COMPLETED"
        sign_off = admitted["human_sign_off_record"]
        assert sign_off["reviewer_name"] == "Rishindra Mateti"
        assert sign_off["reviewer_role"] == "AUTHOR_MANUAL_REVIEW"
        assert sign_off["review_date"] == "2026-10-12"
        assert sign_off["reviewed_packet_git_commit"] == "bafc6f554e24f8f50346b8fff2afbdfc7acfdb5e"
        assert sign_off["reviewed_packet_blob_sha"] == "ac7a02cf8543e3ec310bcf3928a44b7c66b7031d"
        assert sign_off["reviewed_packet_sha256"] == "419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b"
        assert sign_off["sign_off_recording_commit"] == "5175e6f7f4049dbbbd3f94ed7e04c932b3d68066"
        assert sign_off["human_sign_off_decision"] == "APPROVE"
        assert "reviewed_artifact_sha256" not in sign_off


def test_no_independent_validation_claimed():
    with open(DECISIONS_JSON_PATH, "r", encoding="utf-8") as f:
        decisions = json.load(f)

    meta = decisions["metadata"]
    assert meta["independent_review_conducted"] is False
    assert meta["author_review_sign_off"]["independent_validation_claimed"] is False

    # No sign-off record has INDEPENDENT_REVIEW
    for d in decisions["decisions"]:
        admitted = d["admitted_candidate"]
        sign_off = admitted["human_sign_off_record"]
        assert sign_off["reviewer_role"] != "INDEPENDENT_REVIEW"
        assert sign_off["reviewer_role"] == "AUTHOR_MANUAL_REVIEW"

    # Both documents explicitly declare independent review was NOT conducted
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        packet_content = f.read()
    assert "Independent Review: `NOT_CONDUCTED`" in packet_content
    assert "DOES NOT constitute independent third-party validation" in packet_content
    assert "*Independent review has NOT occurred.*" in packet_content

    with open(ADMISSION_REVIEW_MD_PATH, "r", encoding="utf-8") as f:
        review_content = f.read()
    assert "Independent Review: `NOT_CONDUCTED`" in review_content
    assert "Independent third-party validation has not been conducted" in review_content


def test_conservative_pre_extraction_classification_wording():
    expected_phrase = "conservative, protocol-defined pre-extraction classifications subject to extraction validation and human review"

    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        assert expected_phrase in f.read()

    with open(ADMISSION_REVIEW_MD_PATH, "r", encoding="utf-8") as f:
        assert expected_phrase in f.read()

    with open(DECISIONS_JSON_PATH, "r", encoding="utf-8") as f:
        assert expected_phrase in f.read()


def test_immutable_git_provenance_retrieval_and_hash_divergence():
    """Validates immutable Git provenance fields against actual Git history and
    asserts historical reviewed hash does not falsely equal current packet hash
    unless the contents truly match."""
    import subprocess

    with open(DECISIONS_JSON_PATH, "r", encoding="utf-8") as f:
        decisions = json.load(f)

    meta = decisions["metadata"]
    sign_off = meta["author_review_sign_off"]
    git_commit = sign_off["reviewed_packet_git_commit"]
    blob_sha = sign_off["reviewed_packet_blob_sha"]
    historical_sha256 = sign_off["reviewed_packet_sha256"]
    recording_commit = sign_off["sign_off_recording_commit"]

    # 1. Verify git_commit is an actual commit in Git repository
    res_commit_type = subprocess.run(
        ["git", "cat-file", "-t", git_commit],
        capture_output=True, text=True, check=True
    )
    assert res_commit_type.stdout.strip() == "commit", f"{git_commit} must be a valid commit"

    # 2. Verify recording_commit is an actual commit in Git repository
    res_rec_type = subprocess.run(
        ["git", "cat-file", "-t", recording_commit],
        capture_output=True, text=True, check=True
    )
    assert res_rec_type.stdout.strip() == "commit", f"{recording_commit} must be a valid commit"

    # 3. Verify blob_sha matches the exact Git tree entry at git_commit for the review packet
    res_tree_blob = subprocess.run(
        ["git", "rev-parse", f"{git_commit}:results_stage_b/HUMAN_ADMISSION_REVIEW_PACKET.md"],
        capture_output=True, text=True, check=True
    )
    assert res_tree_blob.stdout.strip() == blob_sha, (
        f"Git tree at {git_commit} must point to blob {blob_sha}"
    )

    # 4. Retrieve historical blob content from Git and verify historical SHA-256 matches
    res_blob_content = subprocess.run(
        ["git", "cat-file", "-p", blob_sha],
        capture_output=True, check=True
    )
    historical_bytes = res_blob_content.stdout
    hash_raw = hashlib.sha256(historical_bytes).hexdigest()
    hash_crlf = hashlib.sha256(historical_bytes.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")).hexdigest()
    assert historical_sha256 in (hash_raw, hash_crlf), (
        f"Historical hash {historical_sha256} must match blob content ({hash_raw} or {hash_crlf})"
    )

    # 5. Read current on-disk packet bytes and compute its current SHA-256
    with open(PACKET_PATH, "rb") as f:
        current_bytes = f.read()
    current_sha256 = hashlib.sha256(current_bytes).hexdigest()

    # 6. Ensure historical hash does NOT falsely equal current packet hash unless contents truly match
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

    # 7. Verify explicit provenance statement is present across artifacts
    expected_statement = (
        "The author reviewed the packet snapshot identified above. "
        "The current packet may contain the subsequent sign-off record and therefore may have a different file SHA-256."
    )
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        assert expected_statement in f.read()

    with open(ADMISSION_REVIEW_MD_PATH, "r", encoding="utf-8") as f:
        assert expected_statement in f.read()

    assert sign_off["provenance_statement"] == expected_statement

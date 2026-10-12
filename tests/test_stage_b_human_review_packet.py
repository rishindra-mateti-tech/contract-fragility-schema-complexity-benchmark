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
   - Unchecked checkbox list for human reviewer
   - Signature block with reviewer name, role, date, artifact SHA, and decision options.
3. Cryptographic SHA references match actual on-disk files.
4. Permitted reviewer roles (AUTHOR_MANUAL_REVIEW, INDEPENDENT_REVIEW) are documented.
5. Author review instructions clearly state author review confirms provenance and design
   decisions but does not constitute independent validation.
6. Zero completed human sign-offs are claimed (status remains PENDING).
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

        # 7. Checkbox List for Human Reviewer (unchecked)
        assert "Checkbox List for Human Reviewer" in section
        assert "- [ ]" in section
        assert "Provenance Verification:" in section
        assert "JSON Pointer Resolution:" in section
        assert "Structural Rules Compliance:" in section
        assert "Invocation Mode Verified:" in section
        assert "Fixture Requirements Verified:" in section

        # 8. Human Review Sign-Off Block
        assert "Human Review Sign-Off Block" in section
        assert "Reviewer Name:** `[PENDING_HUMAN_REVIEWER]`" in section
        assert "Reviewer Role:** `[PENDING_ROLE: AUTHOR_MANUAL_REVIEW | INDEPENDENT_REVIEW]`" in section
        assert "Review Date:** `[PENDING_DATE]`" in section
        assert "Reviewed Artifact SHA-256:** `[PENDING_SHA256]`" in section
        assert "APPROVE | REJECT | REQUEST_CHANGES" in section


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


def test_no_completed_human_review_claimed():
    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        packet_content = f.read()

    assert "**Document Status:** `PENDING_HUMAN_REVIEW`" in packet_content
    assert "[PENDING_HUMAN_REVIEWER]" in packet_content
    assert "[PENDING_DATE]" in packet_content
    assert "[PENDING_SHA256]" in packet_content

    with open(DECISIONS_JSON_PATH, "r", encoding="utf-8") as f:
        decisions = json.load(f)

    meta = decisions["metadata"]
    assert meta["human_review_status"] == "PENDING"
    assert meta["independent_review_conducted"] is False
    assert set(meta["reviewer_roles_permitted"]) == {"AUTHOR_MANUAL_REVIEW", "INDEPENDENT_REVIEW"}

    for d in decisions["decisions"]:
        admitted = d["admitted_candidate"]
        assert admitted["human_review_status"] == "PENDING"
        sign_off = admitted["human_sign_off_record"]
        assert sign_off["reviewer_name"] == "[PENDING_HUMAN_REVIEWER]"
        assert sign_off["human_sign_off_decision"] == "PENDING_REVIEW"
        assert "AUTHOR_MANUAL_REVIEW" in sign_off["reviewer_role"]
        assert "INDEPENDENT_REVIEW" in sign_off["reviewer_role"]


def test_conservative_pre_extraction_classification_wording():
    expected_phrase = "conservative, protocol-defined pre-extraction classifications subject to extraction validation and human review"

    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        assert expected_phrase in f.read()

    with open(ADMISSION_REVIEW_MD_PATH, "r", encoding="utf-8") as f:
        assert expected_phrase in f.read()

    with open(DECISIONS_JSON_PATH, "r", encoding="utf-8") as f:
        assert expected_phrase in f.read()

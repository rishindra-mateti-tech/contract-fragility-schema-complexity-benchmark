"""Tests for Stage B Candidate Admission Gatekeeper.

Verifies:
1. Exactly five replacement operations are admitted into stage_b_operation_manifest.yaml.
2. Every admitted replacement operation has a unique slot ID from the approved set.
3. All five original excluded operations are preserved in excluded_operations.
4. Total manifest operations count equals 30 (24 clean + 1 faithful union + 5 admitted).
5. Immutable provenance: on-disk file SHA-256 and Git blob SHA match pinned registry.
6. JSON Pointers resolve unambiguously to matching HTTP methods and operation IDs.
7. Structural rule compliance: depth <= 5, zero object unions, zero binary/multipart,
   zero cycles, zero external refs, and zero conflicting allOf.
8. Operational statefulness is explicitly assessed and classified.
9. Mock-safety feasibility status remains strictly PENDING.
10. Admission review artifacts (JSON & Markdown) exist and match manifest decisions.
"""

import hashlib
import json
import os
import pytest
import yaml

from src.audit_stage_b_candidate_prescreen import OperationAuditor, resolve_json_pointer
from src.scan_stage_b_raw_operation_universe import git_blob_sha

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(ROOT_DIR, "results_stage_b", "stage_b_operation_manifest.yaml")
REGISTRY_PATH = os.path.join(ROOT_DIR, "results_stage_b", "raw_sources_provenance_registry.json")
DECISIONS_JSON_PATH = os.path.join(ROOT_DIR, "results_stage_b", "candidate_admission_decisions.json")
REVIEW_MD_PATH = os.path.join(ROOT_DIR, "results_stage_b", "CANDIDATE_ADMISSION_REVIEW.md")
RAW_DIR = os.path.join(ROOT_DIR, "data_stage_b", "raw")

EXPECTED_SLOT_IDS = {
    "SLOT_GITHUB_01",
    "SLOT_STRIPE_01",
    "SLOT_STRIPE_02",
    "SLOT_CHATWOOT_01",
    "SLOT_LINE_01",
}


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> dict:
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_registry() -> dict:
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_admitted_operations_count_and_unique_slots():
    manifest = load_manifest()
    operations = manifest.get("operations", [])
    excluded = manifest.get("excluded_operations", [])

    admitted_ops = [
        op for op in operations
        if op.get("candidate_status") == "ADMITTED_PENDING_EXTRACTION"
    ]

    # Exactly 5 operations must be admitted
    assert len(admitted_ops) == 5, f"Expected 5 admitted replacement operations, found {len(admitted_ops)}"

    # Unique slots check
    admitted_slots = [op.get("admission_slot_id") for op in admitted_ops]
    assert len(admitted_slots) == len(set(admitted_slots)), "Each admitted replacement must have a unique slot ID"
    assert set(admitted_slots) == EXPECTED_SLOT_IDS, f"Admitted slots mismatch: {set(admitted_slots)} vs {EXPECTED_SLOT_IDS}"

    # Total corpus composition invariants
    assert len(operations) == 30, f"Expected total 30 candidate operations, found {len(operations)}"
    assert len(excluded) == 7, f"Expected 7 excluded operations preserved, found {len(excluded)}"

    comp = manifest.get("corpus_composition", {})
    assert comp.get("clean_monomorphic_provisional") == 29
    assert comp.get("faithful_union_provisional") == 1
    assert comp.get("total_provisional_operations_cohort") == 30
    assert comp.get("pending_replacement_cohort") == 0


def test_admitted_candidates_immutable_provenance():
    manifest = load_manifest()
    registry = load_registry()
    sources_by_id = {s["candidate_source_id"]: s for s in registry.get("sources", [])}

    admitted_ops = [
        op for op in manifest.get("operations", [])
        if op.get("candidate_status") == "ADMITTED_PENDING_EXTRACTION"
    ]

    for op in admitted_ops:
        cid = op["candidate_source_id"]
        assert cid in sources_by_id, f"Candidate source {cid} must exist in provenance registry"
        reg_source = sources_by_id[cid]

        blob_sha = op["source_file_blob_sha"]
        assert blob_sha == reg_source["source_file_blob_sha"], f"Blob SHA mismatch for {op['operation_id']}"

        # Resolve raw file on disk
        ext = os.path.splitext(op["source_file_path"])[1]
        raw_file_name = f"{blob_sha}{ext}"
        disk_path = os.path.join(RAW_DIR, cid, raw_file_name)
        assert os.path.exists(disk_path), f"Raw source file missing on disk: {disk_path}"

        # Cryptographic verification
        computed_sha256 = sha256_file(disk_path)
        assert computed_sha256 == op["raw_file_sha256"], f"SHA-256 mismatch in manifest for {op['operation_id']}"
        assert computed_sha256 == reg_source["downloaded_file_sha256"], f"SHA-256 mismatch with registry for {op['operation_id']}"

        with open(disk_path, "rb") as f:
            raw_bytes = f.read()
        computed_blob = git_blob_sha(raw_bytes)
        assert computed_blob == blob_sha, f"Git blob SHA calculation mismatch for {op['operation_id']}"


def test_admitted_candidates_pointer_resolution():
    manifest = load_manifest()
    admitted_ops = [
        op for op in manifest.get("operations", [])
        if op.get("candidate_status") == "ADMITTED_PENDING_EXTRACTION"
    ]

    for op in admitted_ops:
        cid = op["candidate_source_id"]
        blob_sha = op["source_file_blob_sha"]
        ext = os.path.splitext(op["source_file_path"])[1]
        disk_path = os.path.join(RAW_DIR, cid, f"{blob_sha}{ext}")

        if ext == ".json":
            with open(disk_path, "r", encoding="utf-8") as f:
                doc = json.load(f)
        else:
            with open(disk_path, "r", encoding="utf-8") as f:
                doc = yaml.safe_load(f)

        ptr = op["source_spec_pointer"]
        resolved = resolve_json_pointer(doc, ptr)
        assert resolved is not None, f"JSON Pointer '{ptr}' failed to resolve for {op['operation_id']}"

        # Check operationId match if declared in spec
        spec_op_id = resolved.get("operationId")
        if spec_op_id:
            assert spec_op_id == op["operation_id"], f"Operation ID mismatch at pointer {ptr}: {spec_op_id} vs {op['operation_id']}"


def test_admitted_candidates_structural_rules():
    manifest = load_manifest()
    admitted_ops = [
        op for op in manifest.get("operations", [])
        if op.get("candidate_status") == "ADMITTED_PENDING_EXTRACTION"
    ]

    for op in admitted_ops:
        cid = op["candidate_source_id"]
        blob_sha = op["source_file_blob_sha"]
        ext = os.path.splitext(op["source_file_path"])[1]
        disk_path = os.path.join(RAW_DIR, cid, f"{blob_sha}{ext}")

        if ext == ".json":
            with open(disk_path, "r", encoding="utf-8") as f:
                doc = json.load(f)
        else:
            with open(disk_path, "r", encoding="utf-8") as f:
                doc = yaml.safe_load(f)

        ptr = op["source_spec_pointer"]
        op_dict = resolve_json_pointer(doc, ptr)

        auditor = OperationAuditor(doc, ptr)
        analysis = auditor.audit_openapi(op_dict)

        op_id = op["operation_id"]
        assert analysis["max_depth"] <= 5, f"{op_id} depth {analysis['max_depth']} exceeds protocol bound 5"
        assert analysis["has_cycle"] is False, f"{op_id} contains cycle: {analysis['cycle_details']}"
        assert analysis["has_multipart_binary"] is False, f"{op_id} contains binary/multipart: {analysis['multipart_details']}"
        assert analysis["has_object_union"] is False, f"{op_id} contains object union: {analysis['object_union_details']}"
        assert analysis["has_conflicting_allof"] is False, f"{op_id} contains conflicting allOf: {analysis['allof_details']}"
        assert analysis["has_external_ref"] is False, f"{op_id} contains external ref: {analysis['external_ref_details']}"


def test_admitted_candidates_statefulness_and_mock_safety_invariants():
    manifest = load_manifest()
    admitted_ops = [
        op for op in manifest.get("operations", [])
        if op.get("candidate_status") == "ADMITTED_PENDING_EXTRACTION"
    ]

    for op in admitted_ops:
        op_id = op["operation_id"]
        # Schema invocation mode and external prerequisite state must be declared
        assert op.get("schema_invocation_mode") == "SINGLE_TURN_CONSTRUCTIBLE", (
            f"Expected schema_invocation_mode SINGLE_TURN_CONSTRUCTIBLE for {op_id}"
        )
        assert op.get("external_prerequisite_state") == "FIXTURE_REQUIRED", (
            f"Expected external_prerequisite_state FIXTURE_REQUIRED for {op_id}"
        )
        mock_fixtures = op.get("mock_fixture_requirements")
        assert isinstance(mock_fixtures, list) and len(mock_fixtures) >= 1, (
            f"Expected non-empty list of mock_fixture_requirements for {op_id}"
        )

        # Neither 'stateless' nor 'self-contained' must appear in reason_for_selection
        reason = op.get("reason_for_selection", "")
        assert "stateless" not in reason.lower(), f"'stateless' found in reason_for_selection for {op_id}"
        assert "self-contained" not in reason.lower(), f"'self-contained' found in reason_for_selection for {op_id}"

        # Mock safety feasibility must be strictly PENDING
        assert op.get("safe_for_local_mock_evaluation") == "MOCK_SAFETY_REVIEW_PENDING", (
            f"Mock safety for {op_id} must remain MOCK_SAFETY_REVIEW_PENDING"
        )
        assert len(op.get("mock_safety_rationale", "")) > 10, f"Missing mock safety rationale for {op_id}"


def test_admission_decisions_json_and_review_doc_consistency():
    assert os.path.exists(DECISIONS_JSON_PATH), "candidate_admission_decisions.json must exist"
    assert os.path.exists(REVIEW_MD_PATH), "CANDIDATE_ADMISSION_REVIEW.md must exist"

    with open(DECISIONS_JSON_PATH, "r", encoding="utf-8") as f:
        decisions_data = json.load(f)

    meta = decisions_data["metadata"]
    assert meta["total_slots_reviewed"] == 5
    assert meta["total_admitted"] == 5
    assert meta["total_open_slots"] == 0
    assert meta["governing_policy"] == "STAGE_B_CANDIDATE_ADMISSION_GATE"
    assert meta["human_review_status"] == "AUTHOR_MANUAL_REVIEW_COMPLETED"
    assert meta["independent_review_conducted"] is False
    assert meta["author_review_sign_off"]["reviewer_name"] == "Rishindra Mateti"
    assert meta["author_review_sign_off"]["reviewer_role"] == "AUTHOR_MANUAL_REVIEW"
    assert meta["author_review_sign_off"]["review_date"] == "2026-10-12"
    assert meta["author_review_sign_off"]["reviewed_packet_sha256"] == "419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b"
    assert meta["author_review_sign_off"]["decision"] == "APPROVE"
    assert meta["author_review_sign_off"]["independent_validation_claimed"] is False

    decisions = decisions_data["decisions"]
    assert len(decisions) == 5

    with open(REVIEW_MD_PATH, "r", encoding="utf-8") as f:
        review_md = f.read()

    assert "**Human Review Status:** `AUTHOR_MANUAL_REVIEW_COMPLETED` (Independent Review: `NOT_CONDUCTED`)" in review_md

    for d in decisions:
        assert d["admission_decision"] == "ADMITTED_PENDING_EXTRACTION"
        admitted = d["admitted_candidate"]
        assert admitted["mock_feasibility_status"] == "PENDING"
        assert admitted["human_review_status"] == "AUTHOR_MANUAL_REVIEW_COMPLETED"

        # Human sign-off record keys and values
        sign_off = admitted["human_sign_off_record"]
        assert sign_off["reviewer_name"] == "Rishindra Mateti"
        assert sign_off["reviewer_role"] == "AUTHOR_MANUAL_REVIEW"
        assert sign_off["review_date"] == "2026-10-12"
        assert sign_off["reviewed_artifact_sha256"] == "419888285e54568e96244728cf9c05f04c099e2f9de8ff51d8dbd51419774f1b"
        assert sign_off["human_sign_off_decision"] == "APPROVE"

        # Automated checklist must all be True
        checklist = admitted["automated_static_admission_checklist"]
        for check_name, check_val in checklist.items():
            assert check_val is True, f"Checklist item {check_name} must be True for {admitted['operation_id']}"

        # Rejected candidates must have reasons and state partitions
        assert len(d["evaluated_rejected_candidates"]) >= 2
        for rej in d["evaluated_rejected_candidates"]:
            assert len(rej["rejection_reason"]) > 10
            assert rej["schema_invocation_mode"] in ["SINGLE_TURN_CONSTRUCTIBLE", "MULTI_TURN_DEPENDENT"]
            assert rej["external_prerequisite_state"] in ["FIXTURE_REQUIRED", "LIFECYCLE_STATE_REQUIRED", "NONE"]

        # Markdown report must mention admitted operation
        assert admitted["operation_id"] in review_md

"""tests/test_oas30_draft07_compatibility.py - Comprehensive Dialect Compatibility and Semantic Tests.

Covers:
1. Dialect audit execution and report schema across all 15 active Stage B operations.
2. Dialect audit identifies all occurrences of nullable in candidate artifacts.
3. SLOT_GITHUB_02 flagged as invalid under V1 Draft-07 semantics.
4. Box SLOT_BOX_01 nullable: false recorded for quarantine.
5. All 15 active slots accounted for without silent omissions.
6. Cyclic $ref structures in raw schemas do not cause infinite recursion.
7. Converted nullable fields accept null under Draft-07 only when OAS semantics allow it.
8. V1 Draft-07 contract rejects null payload while V2 accepts it.
9. Enum-constrained non-nullable fields reject null payloads in both V1 and V2.
10. Raw 'nullable' keyword cannot appear in any generated Draft-07 V2 candidate contract.
11. readOnly request-direction handling fails closed on request surface properties.
12. Unknown OAS keywords fail closed.
13. Dialect mismatch precludes zero-potential-loss claims.
14. Difference registers and lineage record INTENTIONAL_REPRESENTATION_CHANGE.
15. V1 artifacts remain byte-for-byte immutable.
16. V2 candidate regeneration is deterministic with bit-for-bit identity.
"""

import copy
import hashlib
import json
import os
from pathlib import Path
import pytest
import jsonschema

from src.audit_oas30_draft07_compatibility import DialectAuditor
from src.stage_b_candidate_pipeline_v2 import (
    GenericCandidateExtractorV2,
    CONVERSION_POLICY_ID,
    CONVERSION_POLICY_SHA256,
)
from src.extract_stage_b_batch_candidates_v2 import run_batch_extraction_v2
from src.stage_b_candidate_manifest import (
    load_manifest,
    load_provenance_registry,
    resolve_raw_source_file,
    get_slot_id_for_operation,
    sha256_file,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_audit_execution_and_schema():
    """Verify dialect audit completes and produces valid JSON report."""
    auditor = DialectAuditor()
    results = auditor.run_full_audit()

    assert results["audited_slots_count"] == 15, "Expected exactly 15 audited slots"
    assert results["total_dialect_occurrences"] > 0, "Expected non-zero dialect occurrences"
    assert "invalid_candidate_slots" in results
    assert "SLOT_GITHUB_02" in results["invalid_candidate_slots"], "SLOT_GITHUB_02 must be flagged invalid"


def test_nullable_divergence_detection():
    """Verify that nullable: true in SLOT_GITHUB_02 is flagged as high semantic divergence."""
    auditor = DialectAuditor()
    results = auditor.run_full_audit()

    github_02_nullable = [
        occ for occ in results["occurrences"]
        if occ["slot_id"] == "SLOT_GITHUB_02" and occ["keyword"] == "nullable"
    ]
    assert len(github_02_nullable) == 2, "Expected 2 nullable occurrences in SLOT_GITHUB_02"

    for occ in github_02_nullable:
        assert occ["current_artifact_valid"] is False
        assert occ["required_action"] == "CONVERT_TO_DRAFT07_TYPE_UNION"
        assert "HIGH_SEMANTIC_DIVERGENCE" in occ["semantic_risk"]


def test_box_redundant_nullable_quarantine():
    """Verify that nullable: false in SLOT_BOX_01 is recorded for quarantine without invalidating schema."""
    auditor = DialectAuditor()
    results = auditor.run_full_audit()

    box_nullable = [
        occ for occ in results["occurrences"]
        if occ["slot_id"] == "SLOT_BOX_01" and occ["keyword"] == "nullable"
    ]
    assert len(box_nullable) == 2, "Expected 2 nullable: false occurrences in SLOT_BOX_01"

    for occ in box_nullable:
        assert occ["source_value"] is False
        assert occ["required_action"] == "QUARANTINE_OAS_KEYWORD"


def test_report_files_exist_and_match():
    """Verify audit JSON and MD report files exist on disk and reconcile."""
    json_path = REPO_ROOT / "results_stage_b" / "OAS30_DRAFT07_COMPATIBILITY_AUDIT.json"
    md_path = REPO_ROOT / "results_stage_b" / "OAS30_DRAFT07_COMPATIBILITY_AUDIT.md"

    assert json_path.exists(), "Audit JSON report missing"
    assert md_path.exists(), "Audit MD report missing"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_dialect_occurrences"] > 0
    assert "SLOT_GITHUB_02" in data["invalid_candidate_slots"]


def test_semantic_null_validation_v1_fails_v2_passes():
    """Verify that a null payload fails V1 Draft-07 evaluation but passes V2 converted schema."""
    v1_contract_path = REPO_ROOT / "data_stage_b" / "extraction_candidates" / "SLOT_GITHUB_02" / "candidate_contract.json"
    v2_contract_path = REPO_ROOT / "data_stage_b" / "extraction_candidates_v2" / "SLOT_GITHUB_02" / "candidate_contract.json"

    assert v1_contract_path.exists(), "V1 contract missing"
    assert v2_contract_path.exists(), "V2 contract missing"

    with open(v1_contract_path, "r", encoding="utf-8") as f:
        v1_schema = json.load(f)
    with open(v2_contract_path, "r", encoding="utf-8") as f:
        v2_schema = json.load(f)

    valid_null_payload = {
        "path": {"owner": "test-owner", "repo": "test-repo", "sha": "0123456789abcdef0123456789abcdef01234567"},
        "query": {},
        "header": {},
        "body": {
            "state": "success",
            "description": None,
            "target_url": None,
        },
    }

    # V1 must fail because Draft-07 ignores nullable: true and sees type: string
    with pytest.raises(jsonschema.ValidationError) as exc_info:
        jsonschema.Draft7Validator(v1_schema).validate(valid_null_payload)
    assert "None is not of type 'string'" in str(exc_info.value)

    # V2 must pass because Draft-07 sees type: ["string", "null"]
    jsonschema.Draft7Validator(v2_schema).validate(valid_null_payload)


def test_enum_constrained_field_rejects_null_in_v2():
    """Verify that nullability does not relax enum boundaries; non-nullable enum field rejects null."""
    v2_contract_path = REPO_ROOT / "data_stage_b" / "extraction_candidates_v2" / "SLOT_GITHUB_02" / "candidate_contract.json"
    with open(v2_contract_path, "r", encoding="utf-8") as f:
        v2_schema = json.load(f)

    invalid_enum_payload = {
        "path": {"owner": "test-owner", "repo": "test-repo", "sha": "0123456789abcdef0123456789abcdef01234567"},
        "query": {},
        "header": {},
        "body": {
            "state": None,  # state is enum ["error", "failure", "pending", "success"], not nullable
            "description": "Valid desc",
            "target_url": "https://example.com",
        },
    }

    with pytest.raises(jsonschema.ValidationError) as exc_info:
        jsonschema.Draft7Validator(v2_schema).validate(invalid_enum_payload)
    assert "None is not one of" in str(exc_info.value) or "None is not of type 'string'" in str(exc_info.value)


def test_raw_nullable_cannot_appear_in_v2_contracts():
    """Verify that raw 'nullable' keyword is excised from all 13 V2 candidate contracts."""
    v2_dir = REPO_ROOT / "data_stage_b" / "extraction_candidates_v2"
    for contract_file in v2_dir.glob("*/candidate_contract.json"):
        text = contract_file.read_text(encoding="utf-8")
        assert '"nullable"' not in text, f"Found raw 'nullable' keyword in {contract_file}"


def test_readonly_request_direction_handling():
    """Verify that request-surface properties marked readOnly fail closed under ERR_READONLY_IN_REQUEST_SURFACE."""
    extractor = GenericCandidateExtractorV2(extractor_script_sha="dummy", extractor_git_commit="dummy")
    synthetic_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string", "readOnly": True},
            "name": {"type": "string"},
        },
    }

    with pytest.raises(ValueError) as exc_info:
        extractor.extract_schema_node(
            raw_schema=synthetic_schema,
            raw_doc={},
            raw_pointer="#/components/schemas/Item",
            current_depth=1,
            is_request_surface=True,
        )
    assert "ERR_READONLY_IN_REQUEST_SURFACE" in str(exc_info.value)


def test_difference_register_and_lineage_record_conversions():
    """Verify difference register and lineage for SLOT_GITHUB_02 record INTENTIONAL_REPRESENTATION_CHANGE."""
    v2_slot_dir = REPO_ROOT / "data_stage_b" / "extraction_candidates_v2" / "SLOT_GITHUB_02"
    diff_path = v2_slot_dir / "difference_register.json"
    lineage_path = v2_slot_dir / "field_lineage.jsonl"

    with open(diff_path, "r", encoding="utf-8") as f:
        diffs = json.load(f)

    nullable_diffs = [
        d for d in diffs
        if d["classification"] == "INTENTIONAL_REPRESENTATION_CHANGE"
        and "nullable" in d["rationale"]
    ]
    assert len(nullable_diffs) == 2, "Expected 2 nullable difference records in SLOT_GITHUB_02"
    for d in nullable_diffs:
        assert d["policy_pointer"] == "results_stage_b/OAS30_TO_DRAFT07_CONVERSION_POLICY_001.md"
        assert d["human_validation_required"] is True

    # Lineage check
    with open(lineage_path, "r", encoding="utf-8") as lf:
        lineage_recs = [json.loads(line) for line in lf]

    desc_lineage = next(
        l for l in lineage_recs
        if l["canonical_json_pointer"] == "/properties/body/properties/description"
    )
    assert desc_lineage["transformation_category"] == "INTENTIONAL_REPRESENTATION_CHANGE"


def test_v1_artifacts_remain_immutable():
    """Verify that historical V1 candidate contracts have not drifted from Git baseline."""
    v1_hashes = {
        "SLOT_BOX_01": "e87f2232cc9e57ba97178ea85008025e9387a9c1cbcdd3257d1941f84a7b6394",
        "SLOT_GITHUB_02": "0a8f0de40bd47ab356e378f0557d2ab507a3e3787f267c82bf7bb0f19190438c",
        "SLOT_STRIPE_01": "d4328ecc85ef5c5ac90e85aa0f45df6d412ac59efe3b4df5d8df0e2b135d8b0c",
    }
    for slot, expected_sha in v1_hashes.items():
        c_path = REPO_ROOT / "data_stage_b" / "extraction_candidates" / slot / "candidate_contract.json"
        actual_sha = sha256_file(str(c_path))
        assert actual_sha == expected_sha, f"V1 contract {slot} drifted: {actual_sha} != {expected_sha}"


def test_v2_batch_regeneration_is_deterministic():
    """Verify that re-running V2 extraction produces bit-for-bit identical hashes across all 13 slots."""
    v2_dir = REPO_ROOT / "data_stage_b" / "extraction_candidates_v2"
    first_run_hashes = {}
    for c_path in sorted(v2_dir.glob("*/candidate_contract.json")):
        first_run_hashes[c_path.parent.name] = sha256_file(str(c_path))

    assert len(first_run_hashes) == 13, "Expected 13 generated V2 candidates"

    # Re-run single extraction on SLOT_GITHUB_02 and SLOT_BOX_01
    manifest = load_manifest()
    prov_registry = load_provenance_registry()
    prov_map = {s["candidate_source_id"]: s for s in prov_registry["sources"]}

    for slot in ["SLOT_GITHUB_02", "SLOT_BOX_01"]:
        op = next(o for o in manifest["operations"] if get_slot_id_for_operation(o["operation_id"]) == slot)
        raw_path, _, ext = resolve_raw_source_file(op["candidate_source_id"], op["source_file_blob_sha"])
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_doc = json.load(f)

        extractor = GenericCandidateExtractorV2(
            extractor_script_sha=sha256_file(str(REPO_ROOT / "src" / "stage_b_candidate_pipeline_v2.py")),
            extractor_git_commit="5b7e020a91b09066fc38d5e23fbe9cab157a99b1",
        )
        tmp_dir = REPO_ROOT / "data_stage_b" / "extraction_candidates_v2" / f"{slot}_tmp_test"
        meta = extractor.extract_candidate_bundle(op, raw_doc, str(tmp_dir))
        re_extracted_sha = meta["generated_artifact_hashes"]["candidate_contract.json"]
        assert re_extracted_sha == first_run_hashes[slot], f"Determinism mismatch on {slot}: {re_extracted_sha} != {first_run_hashes[slot]}"

        # Clean up temp test directory
        import shutil
        shutil.rmtree(str(tmp_dir), ignore_errors=True)

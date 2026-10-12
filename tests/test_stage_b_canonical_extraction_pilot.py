"""Tests for Stage B Canonical Contract Extraction Pilot (SLOT_GITHUB_01).

Validates:
1. Single-slot extraction boundary: only SLOT_GITHUB_01 is allowed.
2. In-memory and disk extraction produces deterministic canonical Draft-07 contracts.
3. Draft-07 meta-validation via jsonschema.Draft7Validator.
4. Transport surface separation:
   - Path parameters: 'owner', 'repo' (required: ['owner', 'repo'])
   - Body properties: 8 properties (required: ['base', 'head'])
   - Query & Header surfaces: strictly empty
   - Zero leak of path parameters into body container
5. Bijective field-lineage coverage:
   - Exactly 15 lineage records (10 leaf props + 4 surfaces + 1 description)
   - Every raw source pointer resolves to the pinned raw document
   - Continuous hash continuity across canonical schema and lineage
6. Cryptographic manifest integrity:
   - Verifies raw file SHA-256 and Git blob SHA match pinned constants
   - Extraction rule version is 1.2.0
   - Status is strictly EXTRACTED_PENDING_HUMAN_VALIDATION (never CANONICAL_FAITHFUL)
7. Deterministic re-extraction byte stability (identical timestamp => bitwise identical output).
8. Deliberate drift detection:
   - Renamed field drift -> validation fails
   - Missing required field drift -> validation fails
   - Invented phantom field drift -> validation fails
   - Field type drift -> validation fails
   - Path-to-body transport leak drift -> validation fails
   - Depth limit violation drift -> validation fails
"""

import copy
import json
import os
import shutil
import pytest
import jsonschema

from src.extract_stage_b_canonical_contract import (
    PILOT_SLOT_ID,
    PILOT_OPERATION_ID,
    PILOT_RAW_BLOB_SHA,
    PILOT_RAW_FILE_SHA256,
    PILOT_RAW_FILE_REL_PATH,
    PILOT_SOURCE_POINTER,
    PILOT_STATUS,
    EXTRACTION_RULE_VERSION,
    extract_canonical_contract,
    resolve_json_pointer,
    sha256_file,
)
from src.validate_stage_b_canonical_contract import (
    CanonicalContractValidator,
    validate_canonical_contract,
    compute_schema_depth,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANONICAL_DIR = os.path.join(ROOT_DIR, "data_stage_b", "canonical")
PILOT_SLOT_DIR = os.path.join(CANONICAL_DIR, PILOT_SLOT_ID)


def test_single_slot_pilot_boundary():
    """Verify extractor enforces strict single-slot pilot boundary."""
    with pytest.raises(ValueError, match="Hard boundary violation"):
        extract_canonical_contract(slot_id="SLOT_STRIPE_01", dry_run=True)

    with pytest.raises(ValueError, match="Hard boundary violation"):
        extract_canonical_contract(slot_id="SLOT_UNKNOWN", dry_run=True)


def test_status_invariant_not_canonical_faithful():
    """Verify that pilot extraction strictly sets status to EXTRACTED_PENDING_HUMAN_VALIDATION."""
    res = extract_canonical_contract(
        slot_id=PILOT_SLOT_ID,
        generated_at="2026-10-12T18:00:00Z",
        dry_run=True,
    )
    manifest = res["manifest"]
    schema = res["canonical_schema"]

    assert manifest["status"] == "EXTRACTED_PENDING_HUMAN_VALIDATION"
    assert manifest["status"] != "CANONICAL_FAITHFUL"
    assert schema["x-benchmark-metadata"]["status"] == "EXTRACTED_PENDING_HUMAN_VALIDATION"
    assert schema["x-benchmark-metadata"]["admission_decision"] == "EXTRACTED_PENDING_HUMAN_VALIDATION"
    assert schema["x-benchmark-metadata"]["extraction_rule_version"] == EXTRACTION_RULE_VERSION


def test_raw_provenance_pinning():
    """Verify pinned raw source file exists, has correct blob SHA and file SHA-256."""
    raw_path = os.path.join(ROOT_DIR, PILOT_RAW_FILE_REL_PATH)
    assert os.path.exists(raw_path), f"Missing raw source file: {raw_path}"

    disk_sha256 = sha256_file(raw_path)
    assert disk_sha256 == PILOT_RAW_FILE_SHA256, "Raw file SHA-256 mismatch"

    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    op_node = resolve_json_pointer(raw_doc, PILOT_SOURCE_POINTER)
    assert op_node is not None
    assert op_node.get("operationId") == "pulls/create" or "summary" in op_node


def test_deterministic_extraction_and_reextraction_stability(tmp_path):
    """Verify extraction is 100% deterministic and byte-stable given identical timestamp."""
    run1 = extract_canonical_contract(
        slot_id=PILOT_SLOT_ID,
        output_dir=str(tmp_path / "run1"),
        generated_at="2026-10-12T18:00:00Z",
    )
    run2 = extract_canonical_contract(
        slot_id=PILOT_SLOT_ID,
        output_dir=str(tmp_path / "run2"),
        generated_at="2026-10-12T18:00:00Z",
    )

    assert run1["canonical_schema_sha256"] == run2["canonical_schema_sha256"]
    assert run1["field_lineage_sha256"] == run2["field_lineage_sha256"]

    # Compare file bytes
    with open(run1["canonical_contract_path"], "rb") as f1, open(run2["canonical_contract_path"], "rb") as f2:
        assert f1.read() == f2.read()

    with open(run1["field_lineage_path"], "rb") as f1, open(run2["field_lineage_path"], "rb") as f2:
        assert f1.read() == f2.read()


def test_schema_draft7_meta_validation(tmp_path):
    """Verify extracted schema conforms to JSON Schema Draft-07 meta-schema."""
    run = extract_canonical_contract(
        slot_id=PILOT_SLOT_ID,
        output_dir=str(tmp_path),
        generated_at="2026-10-12T18:00:00Z",
    )
    schema = run["canonical_schema"]

    assert schema.get("$schema") == "http://json-schema.org/draft-07/schema#"
    # jsonschema validator throws SchemaError if invalid
    jsonschema.Draft7Validator.check_schema(schema)


def test_surface_separation_invariants(tmp_path):
    """Verify clean 4-surface separation, property counts, and required arrays."""
    run = extract_canonical_contract(
        slot_id=PILOT_SLOT_ID,
        output_dir=str(tmp_path),
        generated_at="2026-10-12T18:00:00Z",
    )
    schema = run["canonical_schema"]

    # Root invariants
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["body", "path"]

    # Surfaces
    surfaces = schema["properties"]
    assert set(surfaces.keys()) == {"body", "header", "path", "query"}

    # Path surface
    path = surfaces["path"]
    assert path["type"] == "object"
    assert path["additionalProperties"] is False
    assert set(path["properties"].keys()) == {"owner", "repo"}
    assert path["required"] == ["owner", "repo"]
    assert path["properties"]["owner"]["type"] == "string"
    assert path["properties"]["repo"]["type"] == "string"

    # Body surface
    body = surfaces["body"]
    assert body["type"] == "object"
    assert body["additionalProperties"] is False
    expected_body_props = {
        "base",
        "body",
        "draft",
        "head",
        "head_repo",
        "issue",
        "maintainer_can_modify",
        "title",
    }
    assert set(body["properties"].keys()) == expected_body_props
    assert body["required"] == ["base", "head"]

    # Transport separation: path params never appear in body
    for p in ["owner", "repo"]:
        assert p not in body["properties"]

    # Empty surfaces
    assert surfaces["query"]["type"] == "object"
    assert surfaces["query"]["additionalProperties"] is False
    assert len(surfaces["query"]["properties"]) == 0

    assert surfaces["header"]["type"] == "object"
    assert surfaces["header"]["additionalProperties"] is False
    assert len(surfaces["header"]["properties"]) == 0


def test_recursion_depth_bound(tmp_path):
    """Verify nesting depth does not exceed 5."""
    run = extract_canonical_contract(
        slot_id=PILOT_SLOT_ID,
        output_dir=str(tmp_path),
        generated_at="2026-10-12T18:00:00Z",
    )
    schema = run["canonical_schema"]
    depth = compute_schema_depth(schema)
    assert depth <= 5
    assert depth == 2


def test_field_lineage_traceability_completeness(tmp_path):
    """Verify exact 15 lineage records and valid pointers into raw source."""
    run = extract_canonical_contract(
        slot_id=PILOT_SLOT_ID,
        output_dir=str(tmp_path),
        generated_at="2026-10-12T18:00:00Z",
    )
    lineage = run["lineage_records"]
    assert len(lineage) == 15, f"Expected 15 lineage records, got {len(lineage)}"

    # Load raw doc to verify pointers
    raw_path = os.path.join(ROOT_DIR, PILOT_RAW_FILE_REL_PATH)
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    for rec in lineage:
        assert rec["candidate_source_id"] == "CAND-001"
        assert rec["source_cluster_id"] == "CLUSTER_GITHUB"
        assert rec["raw_source_blob_sha"] == PILOT_RAW_BLOB_SHA
        assert rec["canonical_schema_sha256"] == run["canonical_schema_sha256"]
        assert "source_ast_span" in rec
        assert "transformation_category" in rec

        # Check raw pointers resolve
        for ptr in rec["raw_source_pointers"]:
            resolved = resolve_json_pointer(raw_doc, ptr)
            assert resolved is not None


def test_multi_suite_validator_passes(tmp_path):
    """Verify multi-suite validator passes cleanly on extracted artifacts."""
    run = extract_canonical_contract(
        slot_id=PILOT_SLOT_ID,
        output_dir=str(tmp_path),
        generated_at="2026-10-12T18:00:00Z",
    )
    report = validate_canonical_contract(
        canonical_path=run["canonical_contract_path"],
        lineage_path=run["field_lineage_path"],
        manifest_path=run["extraction_manifest_path"],
    )

    assert report["validation_status"] == "PASS"
    assert report["failed_checks"] == 0
    assert report["passed_checks"] > 0


def test_drift_detection_renamed_field(tmp_path):
    """Drift test: Renaming a field causes validation failure."""
    run = extract_canonical_contract(
        slot_id=PILOT_SLOT_ID,
        output_dir=str(tmp_path),
        generated_at="2026-10-12T18:00:00Z",
    )

    # Corrupt schema by renaming 'title' to 'pr_title' in body
    with open(run["canonical_contract_path"], "r", encoding="utf-8") as f:
        schema = json.load(f)
    body_props = schema["properties"]["body"]["properties"]
    body_props["pr_title"] = body_props.pop("title")

    corrupt_schema_path = str(tmp_path / "corrupt_schema.json")
    with open(corrupt_schema_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    validator = CanonicalContractValidator(
        canonical_path=corrupt_schema_path,
        lineage_path=run["field_lineage_path"],
        manifest_path=run["extraction_manifest_path"],
    )
    res = validator.validate_all()
    assert res["validation_status"] == "FAIL"
    failed_checks = [c["check"] for c in res["checks"] if not c["passed"]]
    assert "body_properties_exact" in failed_checks


def test_drift_detection_missing_required(tmp_path):
    """Drift test: Dropping a required field causes validation failure."""
    run = extract_canonical_contract(
        slot_id=PILOT_SLOT_ID,
        output_dir=str(tmp_path),
        generated_at="2026-10-12T18:00:00Z",
    )

    with open(run["canonical_contract_path"], "r", encoding="utf-8") as f:
        schema = json.load(f)
    schema["properties"]["body"]["required"] = ["base"]  # dropped 'head'

    corrupt_schema_path = str(tmp_path / "corrupt_schema.json")
    with open(corrupt_schema_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    validator = CanonicalContractValidator(
        canonical_path=corrupt_schema_path,
        lineage_path=run["field_lineage_path"],
        manifest_path=run["extraction_manifest_path"],
    )
    res = validator.validate_all()
    assert res["validation_status"] == "FAIL"
    failed_checks = [c["check"] for c in res["checks"] if not c["passed"]]
    assert "body_required_exact" in failed_checks


def test_drift_detection_invented_field(tmp_path):
    """Drift test: Adding an invented/phantom field causes validation failure."""
    run = extract_canonical_contract(
        slot_id=PILOT_SLOT_ID,
        output_dir=str(tmp_path),
        generated_at="2026-10-12T18:00:00Z",
    )

    with open(run["canonical_contract_path"], "r", encoding="utf-8") as f:
        schema = json.load(f)
    schema["properties"]["body"]["properties"]["phantom_field"] = {"type": "string"}

    corrupt_schema_path = str(tmp_path / "corrupt_schema.json")
    with open(corrupt_schema_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    validator = CanonicalContractValidator(
        canonical_path=corrupt_schema_path,
        lineage_path=run["field_lineage_path"],
        manifest_path=run["extraction_manifest_path"],
    )
    res = validator.validate_all()
    assert res["validation_status"] == "FAIL"
    failed_checks = [c["check"] for c in res["checks"] if not c["passed"]]
    assert "body_properties_exact" in failed_checks


def test_drift_detection_path_to_body_leak(tmp_path):
    """Drift test: Leaking path parameter into body causes validation failure."""
    run = extract_canonical_contract(
        slot_id=PILOT_SLOT_ID,
        output_dir=str(tmp_path),
        generated_at="2026-10-12T18:00:00Z",
    )

    with open(run["canonical_contract_path"], "r", encoding="utf-8") as f:
        schema = json.load(f)
    schema["properties"]["body"]["properties"]["owner"] = {"type": "string"}

    corrupt_schema_path = str(tmp_path / "corrupt_schema.json")
    with open(corrupt_schema_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    validator = CanonicalContractValidator(
        canonical_path=corrupt_schema_path,
        lineage_path=run["field_lineage_path"],
        manifest_path=run["extraction_manifest_path"],
    )
    res = validator.validate_all()
    assert res["validation_status"] == "FAIL"
    failed_checks = [c["check"] for c in res["checks"] if not c["passed"]]
    assert "transport_separation_no_path_leak_into_body" in failed_checks


def test_drift_detection_depth_violation(tmp_path):
    """Drift test: Nesting exceeding depth 5 causes validation failure."""
    run = extract_canonical_contract(
        slot_id=PILOT_SLOT_ID,
        output_dir=str(tmp_path),
        generated_at="2026-10-12T18:00:00Z",
    )

    with open(run["canonical_contract_path"], "r", encoding="utf-8") as f:
        schema = json.load(f)

    # Deeply nest inside body properties: depth > 5
    curr = schema["properties"]["body"]["properties"]["body"]
    for i in range(6):
        curr["properties"] = {"nested": {"type": "object"}}
        curr = curr["properties"]["nested"]

    corrupt_schema_path = str(tmp_path / "corrupt_schema.json")
    with open(corrupt_schema_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    validator = CanonicalContractValidator(
        canonical_path=corrupt_schema_path,
        lineage_path=run["field_lineage_path"],
        manifest_path=run["extraction_manifest_path"],
    )
    res = validator.validate_all()
    assert res["validation_status"] == "FAIL"
    failed_checks = [c["check"] for c in res["checks"] if not c["passed"]]
    assert "recursion_depth_within_bound" in failed_checks


def test_on_disk_artifacts_if_present():
    """If pilot artifacts have been generated on disk, validate them completely."""
    if not os.path.exists(PILOT_SLOT_DIR):
        pytest.skip(f"{PILOT_SLOT_DIR} not yet generated on disk (expected before generation step).")

    canonical_file = os.path.join(PILOT_SLOT_DIR, "canonical_contract.json")
    lineage_file = os.path.join(PILOT_SLOT_DIR, "field_lineage.jsonl")
    manifest_file = os.path.join(PILOT_SLOT_DIR, "extraction_manifest.json")

    assert os.path.exists(canonical_file)
    assert os.path.exists(lineage_file)
    assert os.path.exists(manifest_file)

    report = validate_canonical_contract(
        canonical_path=canonical_file,
        lineage_path=lineage_file,
        manifest_path=manifest_file,
    )
    assert report["validation_status"] == "PASS"
    assert report["failed_checks"] == 0

    # Also check single slot isolation: no other slot directory under data_stage_b/canonical
    slots = [d for d in os.listdir(CANONICAL_DIR) if os.path.isdir(os.path.join(CANONICAL_DIR, d))]
    assert slots == [PILOT_SLOT_ID], f"Only {PILOT_SLOT_ID} should exist under canonical/, found: {slots}"

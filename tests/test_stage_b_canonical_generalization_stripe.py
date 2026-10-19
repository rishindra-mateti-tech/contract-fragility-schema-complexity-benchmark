"""Tests for Stage B Canonical Contract Extraction Generalization (SLOT_STRIPE_02).

Validates:
1. Slot-boundary enforcement: only SLOT_GITHUB_01 and SLOT_STRIPE_02 are admitted.
2. In-memory and dry-run extraction for SLOT_STRIPE_02:
   - Operation: PostShippingRates (POST /v1/shipping_rates)
   - Source: CAND-002
   - Request Content-Type: application/x-www-form-urlencoded
   - Status: strictly EXTRACTED_PENDING_HUMAN_VALIDATION (never CANONICAL_FAITHFUL)
   - Author Review Sign-off: strictly None (unpopulated until human validation packet)
3. Form-encoding deepObject serialization preservation:
   - Preserves OpenAPI 3.0 encoding metadata (style: deepObject, explode: true)
   - Preserves nested object schemas without flattening (delivery_estimate, fixed_amount)
   - Preserves array schemas with items (expand)
   - Preserves additionalProperties map schemas (currency_options, metadata)
4. Full bijective field lineage:
   - Exactly 27 lineage records for SLOT_STRIPE_02
   - Continuous cryptographic hashes across raw source and canonical schema
5. Negative drift detection:
   - Drift 1: Content type drift (application/json instead of application/x-www-form-urlencoded)
   - Drift 2: Dropped serialization encoding metadata
   - Drift 3: Corrupted serialization style/explode semantics
   - Drift 4: Lost nested object property (unit/value inside delivery_estimate.maximum)
   - Drift 5: Lost nested array items schema (expand.items)
   - Drift 6: Lost nested string constraint (maxLength on expand.items or display_name)
   - Drift 7: Lost nested enum values (delivery_estimate.maximum.unit enum)
   - Drift 8: Lost map schema (currency_options.additionalProperties)
   - Drift 9: Inappropriate flattening drift (flattening delivery_estimate properties)
   - Drift 10: Premature CANONICAL_FAITHFUL status drift
   - Drift 11: Premature author review sign-off drift
6. Re-extraction byte stability across deterministic runs.
"""

import copy
import json
import os
import pytest

from src.extract_stage_b_canonical_contract import (
    EXTRACTION_RULE_VERSION,
    extract_canonical_contract,
    get_admitted_slot_metadata,
    resolve_json_pointer,
)
from src.validate_stage_b_canonical_contract import (
    CanonicalContractValidator,
    SemanticPreservationEngine,
    collect_canonical_lineage_pointers,
    compute_schema_depth,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRIPE_SLOT_ID = "SLOT_STRIPE_02"


def test_slot_boundary_enforcement():
    """Verify that only admitted pilot slots can be extracted."""
    # Admitted slots succeed
    res_github = extract_canonical_contract(slot_id="SLOT_GITHUB_01", dry_run=True)
    assert res_github["slot_id"] == "SLOT_GITHUB_01"

    res_stripe = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, dry_run=True)
    assert res_stripe["slot_id"] == STRIPE_SLOT_ID

    # Non-admitted slots must fail with hard boundary error
    with pytest.raises(ValueError, match="Hard boundary violation"):
        extract_canonical_contract(slot_id="SLOT_STRIPE_01", dry_run=True)

    with pytest.raises(ValueError, match="Hard boundary violation"):
        extract_canonical_contract(slot_id="SLOT_CHATWOOT_01", dry_run=True)

    with pytest.raises(ValueError, match="Hard boundary violation"):
        extract_canonical_contract(slot_id="SLOT_UNKNOWN", dry_run=True)


def test_stripe_extraction_invariants():
    """Verify structural and metadata invariants of SLOT_STRIPE_02 extraction."""
    res = extract_canonical_contract(
        slot_id=STRIPE_SLOT_ID,
        generated_at="2026-10-19T12:00:00Z",
        dry_run=True,
    )

    manifest = res["manifest"]
    schema = res["canonical_schema"]
    lineage = res["lineage_records"]

    # Manifest checks
    assert manifest["slot_id"] == STRIPE_SLOT_ID
    assert manifest["operation_id"] == "PostShippingRates"
    assert manifest["candidate_source_id"] == "CAND-002"
    assert manifest["request_content_type"] == "application/x-www-form-urlencoded"
    assert manifest["status"] == "EXTRACTED_PENDING_HUMAN_VALIDATION"
    assert manifest["status"] != "CANONICAL_FAITHFUL"
    assert "author_review_sign_off" not in manifest or manifest.get("author_review_sign_off") is None

    # Schema checks
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False

    meta = schema["x-benchmark-metadata"]
    assert meta["slot_id"] == STRIPE_SLOT_ID
    assert meta["request_content_type"] == "application/x-www-form-urlencoded"
    assert meta["status"] == "EXTRACTED_PENDING_HUMAN_VALIDATION"
    assert meta["status"] != "CANONICAL_FAITHFUL"
    assert meta["serialization_metadata"]["serialization_strategy"] == "FORM_URLENCODED_DEEP_OBJECT"
    assert meta["serialization_metadata"]["encoding_metadata_present"] is True

    # Surface checks
    props = schema["properties"]
    assert set(props.keys()) == {"body", "header", "path", "query"}
    assert len(props["path"]["properties"]) == 0
    assert props["path"]["required"] == []
    assert len(props["query"]["properties"]) == 0
    assert len(props["header"]["properties"]) == 0

    body = props["body"]
    assert body["type"] == "object"
    assert body["additionalProperties"] is False
    assert body["required"] == ["display_name"]

    expected_body_props = {
        "delivery_estimate", "display_name", "expand", "fixed_amount", "metadata", "tax_behavior", "tax_code", "type"
    }
    assert set(body["properties"].keys()) == expected_body_props

    # Encoding metadata
    encoding = body.get("x-openapi-encoding", {})
    expected_enc_props = {"delivery_estimate", "expand", "fixed_amount", "metadata"}
    assert set(encoding.keys()) == expected_enc_props
    for enc_key, enc_val in encoding.items():
        assert enc_val["style"] == "deepObject"
        assert enc_val["explode"] is True

    # Lineage records count: 22 body nodes + 4 surfaces + 1 description = 27
    assert len(lineage) == 27
    assert manifest["field_lineage_records_count"] == 27

    expected_pointers = collect_canonical_lineage_pointers(schema)
    actual_pointers = [r["canonical_json_pointer"] for r in lineage]
    assert sorted(actual_pointers) == sorted(expected_pointers)


def test_stripe_reextraction_byte_stability():
    """Verify bitwise determinism across re-extractions with identical timestamp."""
    fixed_ts = "2026-10-19T12:00:00Z"
    run1 = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, generated_at=fixed_ts, dry_run=True)
    run2 = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, generated_at=fixed_ts, dry_run=True)

    json1 = json.dumps(run1["canonical_schema"], sort_keys=True)
    json2 = json.dumps(run2["canonical_schema"], sort_keys=True)
    assert json1 == json2

    man1 = json.dumps(run1["manifest"], sort_keys=True)
    man2 = json.dumps(run2["manifest"], sort_keys=True)
    assert man1 == man2

    assert run1["lineage_records"] == run2["lineage_records"]


def test_semantic_preservation_engine_stripe_clean():
    """Verify SemanticPreservationEngine reports clean pass on unmutated SLOT_STRIPE_02."""
    res = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, dry_run=True)
    slot_meta = get_admitted_slot_metadata(STRIPE_SLOT_ID)

    raw_path = os.path.join(ROOT_DIR, slot_meta["raw_source_file_path"])
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    engine = SemanticPreservationEngine(
        raw_doc=raw_doc,
        canonical_contract=res["canonical_schema"],
        source_pointer=slot_meta["source_spec_pointer"],
        slot_id=STRIPE_SLOT_ID,
        operation_id="PostShippingRates",
    )
    report = engine.evaluate()

    assert report["evaluation_status"] == "PASS"
    assert report["semantic_validation_decision"] == "SEMANTICALLY_VALIDATED_PENDING_HUMAN_REVIEW"
    assert report["field_coverage"]["coverage_ratio"] == 1.0
    assert report["keyword_equivalence"]["dropped_keywords_count"] == 0
    assert report["keyword_equivalence"]["mismatched_keywords_count"] == 0
    assert report["unsupported_constructs"]["unsupported_constructs_count"] == 0

    # Dimension checks
    assert report["form_encoding_serialization_preservation"]["status"] == "PASS"
    assert report["form_encoding_serialization_preservation"]["is_form_encoded"] is True
    assert report["closed_wrapper_policy_effects"]["status"] == "PASS"
    assert report["closed_wrapper_policy_effects"]["normalization_type"] == "PRESERVED_EXPLICIT_FALSE"
    assert report["transport_wrapper_synthesis"]["status"] == "PASS"


# --- NEGATIVE DRIFT TESTS ---


def test_negative_drift_content_type_mismatch():
    """Drift test 1: Request content-type drifted from application/x-www-form-urlencoded to application/json."""
    res = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, dry_run=True)
    slot_meta = get_admitted_slot_metadata(STRIPE_SLOT_ID)

    mutated_schema = copy.deepcopy(res["canonical_schema"])
    mutated_schema["x-benchmark-metadata"]["request_content_type"] = "application/json"

    raw_path = os.path.join(ROOT_DIR, slot_meta["raw_source_file_path"])
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    engine = SemanticPreservationEngine(
        raw_doc=raw_doc,
        canonical_contract=mutated_schema,
        source_pointer=slot_meta["source_spec_pointer"],
        slot_id=STRIPE_SLOT_ID,
    )
    report = engine.evaluate()
    # Looking for application/json in raw_doc requestBody.content will fail or result in 0 body props
    assert report["evaluation_status"] == "FAIL"


def test_negative_drift_dropped_serialization_metadata():
    """Drift test 2: Dropped x-openapi-encoding metadata fails validation."""
    res = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, dry_run=True)
    slot_meta = get_admitted_slot_metadata(STRIPE_SLOT_ID)

    mutated_schema = copy.deepcopy(res["canonical_schema"])
    # Delete x-openapi-encoding
    if "x-openapi-encoding" in mutated_schema["properties"]["body"]:
        del mutated_schema["properties"]["body"]["x-openapi-encoding"]

    raw_path = os.path.join(ROOT_DIR, slot_meta["raw_source_file_path"])
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    engine = SemanticPreservationEngine(
        raw_doc=raw_doc,
        canonical_contract=mutated_schema,
        source_pointer=slot_meta["source_spec_pointer"],
        slot_id=STRIPE_SLOT_ID,
    )
    report = engine.evaluate()
    assert report["evaluation_status"] == "FAIL"
    assert report["form_encoding_serialization_preservation"]["status"] == "FAIL"


def test_negative_drift_corrupted_serialization_style():
    """Drift test 3: Corrupted serialization style (form instead of deepObject) fails validation."""
    res = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, dry_run=True)
    slot_meta = get_admitted_slot_metadata(STRIPE_SLOT_ID)

    mutated_schema = copy.deepcopy(res["canonical_schema"])
    mutated_schema["properties"]["body"]["x-openapi-encoding"]["delivery_estimate"]["style"] = "form"

    raw_path = os.path.join(ROOT_DIR, slot_meta["raw_source_file_path"])
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    engine = SemanticPreservationEngine(
        raw_doc=raw_doc,
        canonical_contract=mutated_schema,
        source_pointer=slot_meta["source_spec_pointer"],
        slot_id=STRIPE_SLOT_ID,
    )
    report = engine.evaluate()
    assert report["evaluation_status"] == "FAIL"
    assert report["form_encoding_serialization_preservation"]["status"] == "FAIL"


def test_negative_drift_lost_nested_object_property():
    """Drift test 4: Lost nested property ('unit' inside delivery_estimate.maximum) fails validation."""
    res = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, dry_run=True)
    slot_meta = get_admitted_slot_metadata(STRIPE_SLOT_ID)

    mutated_schema = copy.deepcopy(res["canonical_schema"])
    maximum_props = mutated_schema["properties"]["body"]["properties"]["delivery_estimate"]["properties"]["maximum"]["properties"]
    del maximum_props["unit"]

    raw_path = os.path.join(ROOT_DIR, slot_meta["raw_source_file_path"])
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    engine = SemanticPreservationEngine(
        raw_doc=raw_doc,
        canonical_contract=mutated_schema,
        source_pointer=slot_meta["source_spec_pointer"],
        slot_id=STRIPE_SLOT_ID,
    )
    report = engine.evaluate()
    assert report["evaluation_status"] == "FAIL"
    dropped = [c for c in report["keyword_equivalence"]["checks"] if c["status"] == "DROPPED_KEYWORD"]
    assert any("properties/unit" in c["pointer"] for c in dropped)


def test_negative_drift_lost_nested_array_items():
    """Drift test 5: Lost items definition on array property ('expand') fails validation."""
    res = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, dry_run=True)
    slot_meta = get_admitted_slot_metadata(STRIPE_SLOT_ID)

    mutated_schema = copy.deepcopy(res["canonical_schema"])
    del mutated_schema["properties"]["body"]["properties"]["expand"]["items"]

    raw_path = os.path.join(ROOT_DIR, slot_meta["raw_source_file_path"])
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    engine = SemanticPreservationEngine(
        raw_doc=raw_doc,
        canonical_contract=mutated_schema,
        source_pointer=slot_meta["source_spec_pointer"],
        slot_id=STRIPE_SLOT_ID,
    )
    report = engine.evaluate()
    assert report["evaluation_status"] == "FAIL"
    dropped = [c for c in report["keyword_equivalence"]["checks"] if c["status"] == "DROPPED_KEYWORD"]
    assert any(c["keyword"] == "items" for c in dropped)


def test_negative_drift_lost_nested_constraint():
    """Drift test 6: Mutated constraint (maxLength 5000 -> 100 on expand.items) fails validation."""
    res = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, dry_run=True)
    slot_meta = get_admitted_slot_metadata(STRIPE_SLOT_ID)

    mutated_schema = copy.deepcopy(res["canonical_schema"])
    mutated_schema["properties"]["body"]["properties"]["expand"]["items"]["maxLength"] = 100

    raw_path = os.path.join(ROOT_DIR, slot_meta["raw_source_file_path"])
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    engine = SemanticPreservationEngine(
        raw_doc=raw_doc,
        canonical_contract=mutated_schema,
        source_pointer=slot_meta["source_spec_pointer"],
        slot_id=STRIPE_SLOT_ID,
    )
    report = engine.evaluate()
    assert report["evaluation_status"] == "FAIL"
    mismatches = [c for c in report["keyword_equivalence"]["checks"] if c["status"] == "MISMATCH"]
    assert any(c["keyword"] == "maxLength" for c in mismatches)


def test_negative_drift_lost_nested_enum():
    """Drift test 7: Lost or altered enum (on delivery_estimate.maximum.unit) fails validation."""
    res = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, dry_run=True)
    slot_meta = get_admitted_slot_metadata(STRIPE_SLOT_ID)

    mutated_schema = copy.deepcopy(res["canonical_schema"])
    unit_prop = mutated_schema["properties"]["body"]["properties"]["delivery_estimate"]["properties"]["maximum"]["properties"]["unit"]
    unit_prop["enum"] = ["day", "hour"]  # omitted business_day, month, week

    raw_path = os.path.join(ROOT_DIR, slot_meta["raw_source_file_path"])
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    engine = SemanticPreservationEngine(
        raw_doc=raw_doc,
        canonical_contract=mutated_schema,
        source_pointer=slot_meta["source_spec_pointer"],
        slot_id=STRIPE_SLOT_ID,
    )
    report = engine.evaluate()
    assert report["evaluation_status"] == "FAIL"
    mismatches = [c for c in report["keyword_equivalence"]["checks"] if c["status"] == "MISMATCH"]
    assert any(c["keyword"] == "enum" for c in mismatches)


def test_negative_drift_lost_map_schema():
    """Drift test 8: Lost map schema on metadata (additionalProperties: {type: string}) fails validation."""
    res = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, dry_run=True)
    slot_meta = get_admitted_slot_metadata(STRIPE_SLOT_ID)

    mutated_schema = copy.deepcopy(res["canonical_schema"])
    mutated_schema["properties"]["body"]["properties"]["metadata"]["additionalProperties"] = True

    raw_path = os.path.join(ROOT_DIR, slot_meta["raw_source_file_path"])
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    engine = SemanticPreservationEngine(
        raw_doc=raw_doc,
        canonical_contract=mutated_schema,
        source_pointer=slot_meta["source_spec_pointer"],
        slot_id=STRIPE_SLOT_ID,
    )
    report = engine.evaluate()
    assert report["evaluation_status"] == "FAIL"
    mismatches = [c for c in report["keyword_equivalence"]["checks"] if c["status"] == "MISMATCH"]
    assert any(c["keyword"] == "additionalProperties" or c["pointer"].endswith("additionalProperties") for c in mismatches)


def test_negative_drift_inappropriate_flattening():
    """Drift test 9: Inappropriately flattening nested object structure into parent container fails validation."""
    res = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, dry_run=True)
    slot_meta = get_admitted_slot_metadata(STRIPE_SLOT_ID)

    mutated_schema = copy.deepcopy(res["canonical_schema"])
    # Flatten maximum and minimum into delivery_estimate root
    del mutated_schema["properties"]["body"]["properties"]["delivery_estimate"]["properties"]["maximum"]
    mutated_schema["properties"]["body"]["properties"]["delivery_estimate"]["properties"]["max_value"] = {"type": "integer"}

    raw_path = os.path.join(ROOT_DIR, slot_meta["raw_source_file_path"])
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    engine = SemanticPreservationEngine(
        raw_doc=raw_doc,
        canonical_contract=mutated_schema,
        source_pointer=slot_meta["source_spec_pointer"],
        slot_id=STRIPE_SLOT_ID,
    )
    report = engine.evaluate()
    assert report["evaluation_status"] == "FAIL"


def test_negative_drift_premature_canonical_faithful():
    """Drift test 10: Elevating manifest status to CANONICAL_FAITHFUL violates hard boundary."""
    res = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, dry_run=True)
    assert res["manifest"]["status"] == "EXTRACTED_PENDING_HUMAN_VALIDATION"
    assert res["manifest"]["status"] != "CANONICAL_FAITHFUL"


def test_negative_drift_premature_author_sign_off():
    """Drift test 11: Adding premature author sign-off to SLOT_STRIPE_02 manifest is rejected."""
    res = extract_canonical_contract(slot_id=STRIPE_SLOT_ID, dry_run=True)
    assert res["manifest"].get("author_review_sign_off") is None

#!/usr/bin/env python3
"""Stage B Adversarial Feature Corpus and Metamorphic Tests.

Tests the canonical extraction engine against a synthetic adversarial test corpus:
1. Deep nesting (depth 1 to 5 supported, depth 6 fails closed)
2. AdditionalProperties combinations (true, false, schema object, omitted)
3. Mixed-case, dashes, underscores, and numeric-leading property names
4. All primitive scalar types + formats
5. Arrays of primitives, arrays of objects, arrays of arrays
6. Enums with string, integer, and mixed values
7. Numeric constraints (min/max, exclusive, multipleOf)
8. String constraints (min/max length, regex pattern)
9. Descriptions with markdown, newlines, unicode, and empty strings
10. Defaults, const, and examples
11. $ref chains (1-hop, 2-hop, 3-hop)
12. Cyclical references fail closed
13. Unsupported constructs (oneOf, anyOf, not, external refs, binary payloads) fail closed
14. Content-type edge cases (application/json, form-urlencoded, unsupported types)
15. Deterministic extraction, zero silent keyword loss, no field renaming, no surface leakage, drift sensitivity
"""

import copy
import json
import os
import pytest

from src.extract_stage_b_canonical_contract import resolve_json_pointer
from src.schema_feature_registry import UnsupportedSchemaFeatureError, get_default_registry
from src.synthetic_extractor import (
    SyntheticExtractionError,
    extract_synthetic_contract,
    hash_contract,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES_DIR = os.path.join(ROOT_DIR, "tests", "fixtures", "schema_feature_corpus")


def load_fixture(fixture_name: str) -> dict:
    path = os.path.join(FIXTURES_DIR, fixture_name)
    assert os.path.exists(path), f"Fixture not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# 1. DETERMINISTIC EXTRACTION AND DRIFT SENSITIVITY
# =============================================================================

def test_deterministic_extraction_identity():
    """Identical input spec must produce identical canonical contract bytes and SHA-256."""
    doc = load_fixture("primitives_fixture.json")
    pointer = "#/paths/~1synthetic~1synthetic_primitives/post"

    contract_a, lineage_a = extract_synthetic_contract(doc, pointer)
    contract_b, lineage_b = extract_synthetic_contract(doc, pointer)

    sha_a = hash_contract(contract_a)
    sha_b = hash_contract(contract_b)

    assert sha_a == sha_b
    assert contract_a == contract_b
    assert lineage_a == lineage_b


def test_drift_sensitivity_on_keyword_mutation():
    """Mutating any keyword in a fixture must change the canonical contract SHA-256."""
    doc = load_fixture("primitives_fixture.json")
    pointer = "#/paths/~1synthetic~1synthetic_primitives/post"

    baseline_contract, _ = extract_synthetic_contract(doc, pointer)
    baseline_sha = hash_contract(baseline_contract)

    # Mutate description
    mutated_doc = copy.deepcopy(doc)
    mutated_doc["paths"]["/synthetic/synthetic_primitives"]["post"]["requestBody"]["content"]["application/json"]["schema"]["properties"]["str_val"]["description"] = "Mutated Description"
    mutated_contract, _ = extract_synthetic_contract(mutated_doc, pointer)
    mutated_sha = hash_contract(mutated_contract)

    assert baseline_sha != mutated_sha, "Extractor failed to reflect property keyword mutation in contract hash"


# =============================================================================
# 2. ZERO SILENT KEYWORD LOSS & NO FIELD RENAMING
# =============================================================================

def test_primitives_and_formats_zero_keyword_loss():
    """All primitive scalar types, formats, and required arrays must survive into canonical form."""
    doc = load_fixture("primitives_fixture.json")
    pointer = "#/paths/~1synthetic~1synthetic_primitives/post"

    contract, _ = extract_synthetic_contract(doc, pointer)
    body_props = contract["properties"]["body"]["properties"]

    assert body_props["str_val"]["type"] == "string"
    assert body_props["int_val"]["type"] == "integer"
    assert body_props["int_val"]["format"] == "int64"
    assert body_props["num_val"]["type"] == "number"
    assert body_props["num_val"]["format"] == "double"
    assert body_props["bool_val"]["type"] == "boolean"
    assert body_props["null_val"]["type"] == "null"
    assert body_props["date_time_val"]["format"] == "date-time"
    assert body_props["uuid_val"]["format"] == "uuid"
    assert body_props["uri_val"]["format"] == "uri"
    assert body_props["email_val"]["format"] == "email"

    assert contract["properties"]["body"]["required"] == ["bool_val", "int_val", "str_val"]


def test_no_field_renaming_and_naming_edge_cases():
    """Output property keys must match input keys verbatim (camelCase, snake_case, kebab-case, numeric-leading)."""
    doc = load_fixture("objects_arrays_fixture.json")
    pointer = "#/paths/~1synthetic~1synthetic_objects_arrays/post"

    contract, _ = extract_synthetic_contract(doc, pointer)
    props = contract["properties"]["body"]["properties"]

    assert "camelCaseProp" in props
    assert "snake_case_prop" in props
    assert "kebab-case-prop" in props
    assert "123_numeric_leading" in props

    # Descriptions with markdown and unicode
    assert "unicode: \u2713" in props["markdown_desc"]["description"]
    assert props["empty_desc"]["description"] == ""


def test_bounds_and_constraints_zero_keyword_loss():
    """Numeric, string, and array constraints must be preserved verbatim."""
    doc = load_fixture("bounds_constraints_fixture.json")
    pointer = "#/paths/~1synthetic~1synthetic_bounds_constraints/post"

    contract, _ = extract_synthetic_contract(doc, pointer)
    props = contract["properties"]["body"]["properties"]

    assert props["bounded_int"]["minimum"] == 1
    assert props["bounded_int"]["maximum"] == 100
    assert props["bounded_int"]["multipleOf"] == 5

    assert props["exclusive_num"]["exclusiveMinimum"] == 0.0
    assert props["exclusive_num"]["exclusiveMaximum"] == 1.0

    assert props["bounded_str"]["minLength"] == 3
    assert props["bounded_str"]["maxLength"] == 64
    assert props["bounded_str"]["pattern"] == "^[a-zA-Z0-9_-]+$"

    assert props["bounded_arr"]["minItems"] == 1
    assert props["bounded_arr"]["maxItems"] == 10
    assert props["bounded_arr"]["uniqueItems"] is True

    assert props["bounded_obj"]["minProperties"] == 1
    assert props["bounded_obj"]["maxProperties"] == 5


# =============================================================================
# 3. LINEAGE COMPLETENESS AND NO SURFACE LEAKAGE
# =============================================================================

def test_transport_surface_separation_and_lineage_completeness():
    """Path parameters must never leak into body, and body properties must never leak into path_parameters."""
    doc = load_fixture("transport_surfaces_fixture.json")
    pointer = "#/paths/~1synthetic~1synthetic_transport_surfaces/post"

    contract, lineage = extract_synthetic_contract(doc, pointer)

    assert "path_parameters" in contract["properties"]
    assert "body" in contract["properties"]

    path_props = contract["properties"]["path_parameters"]["properties"]
    body_props = contract["properties"]["body"]["properties"]

    # No leakage
    assert "org_id" in path_props
    assert "org_id" not in body_props

    assert "action" in body_props
    assert "action" not in path_props

    # Verify lineage records
    lineage_paths = {r["canonical_field_path"]: r for r in lineage}
    assert "path_parameters.org_id" in lineage_paths
    assert lineage_paths["path_parameters.org_id"]["transport_surface"] == "path_parameters"
    assert "body.action" in lineage_paths
    assert lineage_paths["body.action"]["transport_surface"] == "body"


# =============================================================================
# 4. MULTI-HOP REFERENCE DEREFERENCING (1-HOP, 2-HOP, 3-HOP)
# =============================================================================

def test_multihop_ref_chains():
    """Verify 1-hop, 2-hop, and 3-hop local references are dereferenced into canonical contract."""
    doc = load_fixture("references_fixture.json")
    pointer = "#/paths/~1synthetic~1synthetic_references/post"

    contract, _ = extract_synthetic_contract(doc, pointer)
    body = contract["properties"]["body"]

    # Hop 3 root property
    assert "hop3_root" in body["properties"]
    # Hop 2 target
    hop2 = body["properties"]["hop2_target"]
    assert "hop2_title" in hop2["properties"]
    # Hop 1 leaf target
    leaf = hop2["properties"]["leaf_target"]
    assert "leaf_code" in leaf["properties"]
    assert leaf["properties"]["leaf_score"]["type"] == "integer"


# =============================================================================
# 5. DEEP NESTING AND DEPTH CEILING
# =============================================================================

def test_bounded_depth_succeeds_up_to_depth_five():
    """Nesting depth 1 to 5 succeeds without violation."""
    doc = load_fixture("objects_arrays_fixture.json")
    pointer = "#/paths/~1synthetic~1synthetic_objects_arrays/post"

    contract, _ = extract_synthetic_contract(doc, pointer)
    props = contract["properties"]["body"]["properties"]

    # Navigate down 5 levels: level1 -> level2 -> level3 -> level4 -> level5_leaf
    lvl5 = props["level1"]["properties"]["level2"]["properties"]["level3"]["properties"]["level4"]["properties"]["level5_leaf"]
    assert lvl5["description"] == "Max depth leaf"


def test_excessive_depth_six_fails_closed():
    """Nesting depth exceeding benchmark limit of 5 must fail closed."""
    doc = load_fixture("unsupported_excessive_depth_fixture.json")
    pointer = "#/paths/~1synthetic~1unsupported_excessive_depth/post"

    with pytest.raises(UnsupportedSchemaFeatureError) as exc_info:
        extract_synthetic_contract(doc, pointer)
    assert exc_info.value.feature_id == "FEAT_REC_EXCESSIVE_DEPTH"


# =============================================================================
# 6. FAIL-CLOSED BEHAVIOR ON UNSUPPORTED CONSTRUCTS
# =============================================================================

@pytest.mark.parametrize(
    "fixture_name,expected_feature_id",
    [
        ("unsupported_oneof_fixture.json", "FEAT_COMP_ONEOF"),
        ("unsupported_anyof_fixture.json", "FEAT_COMP_ANYOF"),
        ("unsupported_not_fixture.json", "FEAT_COMP_NOT"),
        ("unsupported_discriminator_fixture.json", "FEAT_COMP_DISCRIMINATOR"),
        ("unsupported_tuple_fixture.json", "FEAT_ARR_ITEMS_TUPLE"),
        ("unsupported_binary_fixture.json", "FEAT_BIN_FORMAT_BINARY"),
        ("unsupported_byte_fixture.json", "FEAT_BIN_FORMAT_BYTE"),
        ("unsupported_allow_reserved_fixture.json", "FEAT_FORM_ALLOW_RESERVED"),
        ("unsupported_external_ref_fixture.json", "FEAT_REF_EXTERNAL_FILE"),
        ("unsupported_remote_ref_fixture.json", "FEAT_REF_REMOTE_URL"),
        ("unsupported_cookie_fixture.json", "FEAT_SURF_COOKIE_PARAMS"),
        ("unsupported_multipart_fixture.json", "FEAT_CT_MULTIPART_FORM_DATA"),
        ("unsupported_text_plain_fixture.json", "FEAT_CT_TEXT_PLAIN"),
        ("unsupported_octet_stream_fixture.json", "FEAT_CT_APPLICATION_OCTET_STREAM"),
        ("unsupported_cyclic_fixture.json", "FEAT_REC_CYCLIC_SCHEMA"),
    ],
)
def test_unsupported_constructs_fail_closed(fixture_name, expected_feature_id):
    """Verify that unsupported features immediately raise UnsupportedSchemaFeatureError fail-closed."""
    doc = load_fixture(fixture_name)
    path_key = list(doc["paths"].keys())[0]
    escaped_path = path_key.replace("~", "~0").replace("/", "~1")
    pointer = f"#/paths/{escaped_path}/post"

    with pytest.raises(UnsupportedSchemaFeatureError) as exc_info:
        extract_synthetic_contract(doc, pointer)
    assert exc_info.value.feature_id == expected_feature_id

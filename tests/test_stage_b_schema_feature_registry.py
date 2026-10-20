#!/usr/bin/env python3
"""Tests for Stage B Schema Feature Support Registry and Fail-Closed Validation."""

import json
import os
import pytest
import yaml

from src.schema_feature_registry import (
    SchemaFeatureRegistry,
    UnsupportedSchemaFeatureError,
    get_default_registry,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(ROOT_DIR, "results_stage_b", "SCHEMA_FEATURE_SUPPORT_REGISTRY.yaml")

EXPECTED_CATEGORIES = {
    "PRIMITIVE_TYPES",
    "ENUMS_CONST_DEFAULTS",
    "BOUNDS_CONSTRAINTS",
    "OBJECTS_ARRAYS_MAPS",
    "SCHEMA_REFERENCES",
    "COMPOSITION_POLYMORPHISM",
    "MODIFIERS_METADATA",
    "TRANSPORT_SURFACES",
    "CONTENT_TYPES",
    "FORM_ENCODING_MODIFIERS",
    "BINARY_MULTIPART",
    "RECURSION_CYCLES",
}

VALID_EXTRACTION_BEHAVIORS = {
    "PRESERVE_VERBATIM",
    "EXPLICIT_NORMALIZATION",
    "REJECT_AND_REPORT",
}

VALID_BENCHMARK_STATUSES = {
    "SUPPORTED",
    "EXPERIMENTAL",
    "UNSUPPORTED_FAIL_CLOSED",
}

REQUIRED_FEATURE_FIELDS = {
    "feature_id",
    "name",
    "category",
    "extraction_behavior",
    "validator_behavior",
    "lineage_behavior",
    "current_benchmark_status",
    "rationale",
    "canonical_test_fixture",
}


def test_registry_file_exists_and_parses():
    """Verify registry YAML exists, is readable, and contains basic structure."""
    assert os.path.exists(REGISTRY_PATH), f"Registry file missing: {REGISTRY_PATH}"
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert isinstance(data, dict)
    assert data.get("registry_version") == "1.0.0"
    assert "taxonomies" in data
    assert "categories" in data
    assert "features" in data
    assert len(data["features"]) >= 35


def test_registry_covers_all_twelve_categories():
    """Verify all 12 required categories are present in the registry."""
    registry = get_default_registry()
    observed_categories = {feat["category"] for feat in registry.features}
    assert observed_categories == EXPECTED_CATEGORIES, (
        f"Mismatch in feature categories: diff={observed_categories ^ EXPECTED_CATEGORIES}"
    )


def test_registry_feature_field_schema_integrity():
    """Verify every feature has valid fields and taxonomy values."""
    registry = get_default_registry()
    for feat in registry.features:
        missing = REQUIRED_FEATURE_FIELDS - set(feat.keys())
        assert not missing, f"Feature {feat.get('feature_id')} missing required fields: {missing}"

        assert feat["extraction_behavior"] in VALID_EXTRACTION_BEHAVIORS, (
            f"Feature {feat['feature_id']} has invalid extraction_behavior: {feat['extraction_behavior']}"
        )
        assert feat["current_benchmark_status"] in VALID_BENCHMARK_STATUSES, (
            f"Feature {feat['feature_id']} has invalid status: {feat['current_benchmark_status']}"
        )


def test_registry_lookup_helpers():
    """Verify programmatic query helpers on SchemaFeatureRegistry."""
    registry = get_default_registry()
    prim = registry.get_feature("FEAT_PRIM_STRING")
    assert prim["name"] == "Primitive String Type"
    assert prim["extraction_behavior"] == "PRESERVE_VERBATIM"
    assert prim["current_benchmark_status"] == "SUPPORTED"

    rejects = registry.get_features_by_behavior("REJECT_AND_REPORT")
    assert len(rejects) >= 15
    for r in rejects:
        assert r["extraction_behavior"] == "REJECT_AND_REPORT"

    unsupported = registry.get_features_by_status("UNSUPPORTED_FAIL_CLOSED")
    assert len(unsupported) >= 15


@pytest.mark.parametrize(
    "schema_fragment,expected_feature_id",
    [
        ({"oneOf": [{"type": "string"}, {"type": "integer"}]}, "FEAT_COMP_ONEOF"),
        ({"anyOf": [{"type": "string"}, {"type": "number"}]}, "FEAT_COMP_ANYOF"),
        ({"not": {"type": "string"}}, "FEAT_COMP_NOT"),
        ({"discriminator": {"propertyName": "petType"}}, "FEAT_COMP_DISCRIMINATOR"),
        ({"items": [{"type": "string"}, {"type": "integer"}]}, "FEAT_ARR_ITEMS_TUPLE"),
        ({"type": "string", "format": "binary"}, "FEAT_BIN_FORMAT_BINARY"),
        ({"type": "string", "format": "byte"}, "FEAT_BIN_FORMAT_BYTE"),
        ({"type": "string", "allowReserved": True}, "FEAT_FORM_ALLOW_RESERVED"),
        ({"$ref": "./external_schema.json#/definitions/User"}, "FEAT_REF_EXTERNAL_FILE"),
        ({"$ref": "https://example.com/schemas/address.json"}, "FEAT_REF_REMOTE_URL"),
    ],
)
def test_fail_closed_on_unsupported_features(schema_fragment, expected_feature_id):
    """Verify that unsupported features raise UnsupportedSchemaFeatureError fail-closed."""
    registry = get_default_registry()
    with pytest.raises(UnsupportedSchemaFeatureError) as exc_info:
        registry.validate_schema_compliance(schema_fragment, fail_closed=True)
    assert exc_info.value.feature_id == expected_feature_id


def test_fail_closed_on_excessive_depth():
    """Verify that schemas deeper than 5 levels fail closed with FEAT_REC_EXCESSIVE_DEPTH."""
    registry = get_default_registry()
    # Build a schema with depth 6
    deep_schema = {"type": "object", "properties": {}}
    cur = deep_schema
    for i in range(6):
        cur["properties"] = {"nested": {"type": "object", "properties": {}}}
        cur = cur["properties"]["nested"]

    with pytest.raises(UnsupportedSchemaFeatureError) as exc_info:
        registry.validate_schema_compliance(deep_schema, fail_closed=True)
    assert exc_info.value.feature_id == "FEAT_REC_EXCESSIVE_DEPTH"


def test_canonical_contracts_pass_feature_validation():
    """Verify that existing pilot contracts (GitHub and Stripe) pass registry validation."""
    registry = get_default_registry()
    pilot_paths = [
        os.path.join(ROOT_DIR, "data_stage_b", "canonical", "SLOT_GITHUB_01", "canonical_contract.json"),
        os.path.join(ROOT_DIR, "data_stage_b", "canonical", "SLOT_STRIPE_02", "canonical_contract.json"),
    ]
    for path in pilot_paths:
        assert os.path.exists(path), f"Canonical contract missing: {path}"
        with open(path, "r", encoding="utf-8") as f:
            contract = json.load(f)

        # The canonical contract itself is the root JSON Schema tool contract
        violations = registry.validate_schema_compliance(contract, fail_closed=False)
        assert violations == [], f"Unexpected violations in validated contract {path}: {violations}"

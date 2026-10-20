"""
test_schema_feature_property_based.py - Property-Based & Adversarial Red-Team Schema Feature Tests.

Verifies:
1. Recursion depth boundary progression (depths 1-5 pass, 6-10 fail closed with FEAT_REC_EXCESSIVE_DEPTH).
2. Fail-closed rejection of polymorphic constructs (oneOf, anyOf, not, discriminator, tuple items).
3. Fail-closed cycle detection for direct and indirect reference loops.
4. Fail-closed rejection of external files and remote HTTP URLs.
5. Fail-closed rejection of binary, byte, and allowReserved modifiers.
6. Proper handling of additionalProperties policies.
7. Verification of 60/60 registered features in coverage matrix.
"""

import json
import pytest
from pathlib import Path
from jsonschema import Draft7Validator
from src.schema_feature_registry import (
    get_default_registry,
    UnsupportedSchemaFeatureError,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = REPO_ROOT / "tests" / "fixtures" / "schema_feature_corpus" / "generated"


def test_depth_progression_fuzzed_boundary():
    """Verifies that depths 1-5 pass compliance, while depths 6-10 fail closed."""
    fixture_path = GENERATED_DIR / "fuzzed_depth_progression.json"
    assert fixture_path.exists(), "Missing fuzzed depth progression fixture"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    registry = get_default_registry()

    for depth_key, item in data["schemas"].items():
        schema = item["schema"]
        expected_valid = item["expected_valid"]

        if expected_valid:
            violations = registry.validate_schema_compliance(schema, fail_closed=True)
            assert len(violations) == 0, f"Unexpected violation for {depth_key}: {violations}"
        else:
            with pytest.raises(UnsupportedSchemaFeatureError) as exc_info:
                registry.validate_schema_compliance(schema, fail_closed=True)
            assert exc_info.value.feature_id == item["expected_violation_code"]


def test_polymorphism_fail_closed_fuzzed():
    """Verifies that all polymorphic constructs fail closed with explicit feature codes."""
    fixture_path = GENERATED_DIR / "fuzzed_polymorphism.json"
    assert fixture_path.exists(), "Missing fuzzed polymorphism fixture"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    registry = get_default_registry()

    for case_name, item in data["schemas"].items():
        schema = item["schema"]
        expected_code = item["expected_violation_code"]

        with pytest.raises(UnsupportedSchemaFeatureError) as exc_info:
            registry.validate_schema_compliance(schema, fail_closed=True)
        assert (
            exc_info.value.feature_id == expected_code
        ), f"Expected {expected_code} for {case_name}, got {exc_info.value.feature_id}"


def test_cyclic_refs_detection_fuzzed():
    """Verifies that direct and indirect reference loops fail closed with FEAT_REC_CYCLIC_SCHEMA."""
    fixture_path = GENERATED_DIR / "fuzzed_cyclic_refs.json"
    assert fixture_path.exists(), "Missing fuzzed cyclic refs fixture"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    registry = get_default_registry()

    for case_name, item in data["schemas"].items():
        raw_doc = item["raw_doc"]
        entry_ptr = item["entry_pointer"]
        expected_code = item["expected_violation_code"]

        # Dereference entry point
        from src.extract_stage_b_canonical_contract import resolve_json_pointer
        entry_schema = resolve_json_pointer(raw_doc, entry_ptr)

        with pytest.raises(UnsupportedSchemaFeatureError) as exc_info:
            registry.validate_schema_compliance(
                entry_schema,
                pointer=entry_ptr,
                visited_ptrs={entry_ptr},
                fail_closed=True,
                raw_doc=raw_doc,
            )
        assert exc_info.value.feature_id == expected_code


def test_external_refs_fail_closed_fuzzed():
    """Verifies that external files and remote URLs fail closed."""
    fixture_path = GENERATED_DIR / "fuzzed_external_refs.json"
    assert fixture_path.exists(), "Missing fuzzed external refs fixture"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    registry = get_default_registry()

    for case_name, item in data["schemas"].items():
        schema = item["schema"]
        expected_code = item["expected_violation_code"]

        with pytest.raises(UnsupportedSchemaFeatureError) as exc_info:
            registry.validate_schema_compliance(schema, fail_closed=True)
        assert exc_info.value.feature_id == expected_code


def test_binary_multipart_fail_closed_fuzzed():
    """Verifies that format binary, format byte, and allowReserved fail closed."""
    fixture_path = GENERATED_DIR / "fuzzed_binary_multipart.json"
    assert fixture_path.exists(), "Missing fuzzed binary multipart fixture"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    registry = get_default_registry()

    for case_name, item in data["schemas"].items():
        schema = item["schema"]
        expected_code = item["expected_violation_code"]

        with pytest.raises(UnsupportedSchemaFeatureError) as exc_info:
            registry.validate_schema_compliance(schema, fail_closed=True)
        assert exc_info.value.feature_id == expected_code


def test_additional_properties_fuzzed():
    """Verifies that closed wrapper objects and dynamic maps comply with policy."""
    fixture_path = GENERATED_DIR / "fuzzed_additional_properties.json"
    assert fixture_path.exists(), "Missing fuzzed additional properties fixture"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    registry = get_default_registry()

    for case_name, item in data["schemas"].items():
        schema = item["schema"]
        violations = registry.validate_schema_compliance(schema, fail_closed=True)
        assert len(violations) == 0, f"Expected clean pass for {case_name}, got: {violations}"
        # Assert Draft-07 syntax validity
        Draft7Validator.check_schema(schema)


def test_composite_constraints_validity():
    """Verifies that composite bounds constraints pass Draft-07 validation."""
    fixture_path = GENERATED_DIR / "fuzzed_composite_constraints.json"
    assert fixture_path.exists(), "Missing fuzzed composite constraints fixture"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    registry = get_default_registry()

    for case_name, schema in data["schemas"].items():
        violations = registry.validate_schema_compliance(schema, fail_closed=True)
        assert len(violations) == 0, f"Expected clean compliance for {case_name}: {violations}"
        Draft7Validator.check_schema(schema)


def test_feature_coverage_matrix_integrity():
    """Verifies that 60/60 features are accounted for in the coverage matrix."""
    matrix_path = REPO_ROOT / "results_stage_b" / "FEATURE_REGISTRY_COVERAGE_MATRIX.json"
    audit_path = REPO_ROOT / "results_stage_b" / "FEATURE_REGISTRY_RED_TEAM_AUDIT.md"

    assert matrix_path.exists(), "Missing coverage matrix JSON"
    assert audit_path.exists(), "Missing red-team audit Markdown"

    with open(matrix_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_registered_features"] == 60
    assert data["total_covered_features"] == 60
    assert len(data["coverage_matrix"]) == 60

    bdist = data["behavior_distribution"]
    assert bdist["PRESERVE_VERBATIM"] == 34
    assert bdist["REJECT_AND_REPORT"] == 19
    assert bdist["EXPLICIT_NORMALIZATION"] == 7

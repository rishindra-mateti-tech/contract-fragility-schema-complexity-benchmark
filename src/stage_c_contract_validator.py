#!/usr/bin/env python3
"""Stage C Synthetic Contract Validator.

Validates that synthetic base contracts adhere to Draft-07 syntax,
declared complexity strata, gold examples, invalid counterexamples,
and strict synthetic provenance rules.
"""

import json
import os
import sys
from typing import Any, Dict, List, Tuple
import jsonschema

REQUIRED_BASE_CONTRACT_FIELDS = [
    "contract_id",
    "tool_name",
    "title",
    "description",
    "stratum",
    "domain",
    "schema",
    "latent_intent_schema",
    "gold_examples",
    "counterexamples",
    "provenance_statement",
    "complexity_metrics",
    "seed",
    "generator_version",
]

ALLOWED_STRATA = ["SIMPLE_FLAT", "MEDIUM_ARRAYS_ENUMS", "NESTED_OBJECTS_SURFACES"]
EXPECTED_PROVENANCE_STATEMENT = (
    "Explicitly synthetic contract generated deterministically from seed without production API or real endpoint derivation."
)


def compute_schema_depth(schema: Any, current_depth: int = 1) -> int:
    """Compute maximum nesting depth of object/array containers in a schema."""
    if not isinstance(schema, dict):
        return current_depth

    max_d = current_depth
    s_type = schema.get("type")

    if s_type == "object" or "properties" in schema:
        props = schema.get("properties", {})
        for _, prop_schema in props.items():
            if isinstance(prop_schema, dict):
                p_type = prop_schema.get("type")
                if p_type in ["object", "array"] or "properties" in prop_schema or "items" in prop_schema:
                    max_d = max(max_d, compute_schema_depth(prop_schema, current_depth + 1))

    elif s_type == "array" or "items" in schema:
        items = schema.get("items", {})
        if isinstance(items, dict):
            max_d = max(max_d, compute_schema_depth(items, current_depth + 1))

    return max_d


def compute_contract_complexity_metrics(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate complexity metrics for a Draft-07 schema."""
    props = schema.get("properties", {})
    required = schema.get("required", [])

    has_nested = False
    has_arrays = False
    has_enums = False
    has_numeric = False
    has_temporal = False

    enum_count = 0
    numeric_constraints = 0

    def inspect_node(node: Any):
        nonlocal has_nested, has_arrays, has_enums, has_numeric, has_temporal, enum_count, numeric_constraints
        if not isinstance(node, dict):
            return

        ntype = node.get("type")
        if ntype == "object" or "properties" in node:
            # Check if this is a nested object
            for _, child in node.get("properties", {}).items():
                if isinstance(child, dict):
                    if child.get("type") == "object" or "properties" in child:
                        has_nested = True
                    inspect_node(child)

        if ntype == "array" or "items" in node:
            has_arrays = True
            if isinstance(node.get("items"), dict):
                inspect_node(node["items"])

        if "enum" in node:
            has_enums = True
            enum_count += len(node["enum"])

        for num_key in ["minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf"]:
            if num_key in node:
                has_numeric = True
                numeric_constraints += 1

        for str_key in ["minLength", "maxLength", "pattern"]:
            if str_key in node:
                numeric_constraints += 1

        if node.get("format") in ["date-time", "date", "time"]:
            has_temporal = True

    inspect_node(schema)

    return {
        "property_count": len(props),
        "required_count": len(required),
        "max_nesting_depth": compute_schema_depth(schema),
        "has_nested_objects": has_nested,
        "has_arrays": has_arrays,
        "has_enums": has_enums,
        "enum_count": enum_count,
        "has_numeric_constraints": has_numeric,
        "has_temporal_fields": has_temporal,
    }


class StageCContractValidator:
    """Validator for synthetic base contracts under Stage C Protocol."""

    def __init__(self):
        pass

    def validate_contract(self, contract: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a synthetic base contract object in memory."""
        errors: List[str] = []

        # 1. Required top-level keys
        for key in REQUIRED_BASE_CONTRACT_FIELDS:
            if key not in contract:
                errors.append(f"Missing required contract field: '{key}'")

        if errors:
            return False, errors

        # 2. Stratum and Provenance checks
        stratum = contract.get("stratum")
        if stratum not in ALLOWED_STRATA:
            errors.append(f"Invalid stratum '{stratum}'. Must be one of {ALLOWED_STRATA}")

        prov = contract.get("provenance_statement")
        if prov != EXPECTED_PROVENANCE_STATEMENT:
            errors.append(f"Provenance statement mismatch. Expected exact declaration, got '{prov}'")

        # Anti-production claim invariant
        c_str = json.dumps(contract)
        if "production-derived" in c_str.lower():
            errors.append("Contract contains forbidden claim 'production-derived'")
        if "canonical_faithful" in c_str.lower():
            errors.append("Contract contains forbidden claim 'canonical_faithful'")

        # 3. Draft-07 Schema Validation
        schema = contract.get("schema", {})
        if schema.get("$schema") != "http://json-schema.org/draft-07/schema#":
            errors.append("Schema $schema must be 'http://json-schema.org/draft-07/schema#'")

        if schema.get("type") != "object":
            errors.append("Schema root type must be 'object'")

        if schema.get("additionalProperties") is not False:
            errors.append("Schema root must declare 'additionalProperties: false'")

        try:
            jsonschema.Draft7Validator.check_schema(schema)
        except jsonschema.SchemaError as e:
            errors.append(f"Schema Draft-07 validation error: {e.message}")

        validator = jsonschema.Draft7Validator(schema)

        # 4. Gold Examples Validation (must all be valid)
        gold_examples = contract.get("gold_examples", [])
        if len(gold_examples) < 2:
            errors.append(f"Contract must provide at least 2 gold examples, got {len(gold_examples)}")

        for i, ex in enumerate(gold_examples):
            if not isinstance(ex, dict):
                errors.append(f"Gold example {i} must be a dictionary object")
            elif not validator.is_valid(ex):
                v_errs = [err.message for err in validator.iter_errors(ex)]
                errors.append(f"Gold example {i} fails schema validation: {v_errs}")

        # 5. Counterexamples Validation (must all be invalid)
        counterexamples = contract.get("counterexamples", [])
        if len(counterexamples) < 2:
            errors.append(f"Contract must provide at least 2 counterexamples, got {len(counterexamples)}")

        for i, cex in enumerate(counterexamples):
            if not isinstance(cex, dict):
                errors.append(f"Counterexample {i} must be a dictionary object")
            elif validator.is_valid(cex):
                errors.append(f"Counterexample {i} unexpectedly passed schema validation; must be invalid")

        # 6. Latent Intent Schema
        latent = contract.get("latent_intent_schema", {})
        if not isinstance(latent, dict) or not latent:
            errors.append("latent_intent_schema must be a non-empty dictionary defining latent fields")

        # 7. Complexity Metrics Consistency
        declared_metrics = contract.get("complexity_metrics", {})
        recomputed = compute_contract_complexity_metrics(schema)
        for metric_k, expected_v in recomputed.items():
            declared_v = declared_metrics.get(metric_k)
            if declared_v != expected_v:
                errors.append(
                    f"Complexity metric mismatch for '{metric_k}': declared {declared_v}, computed {expected_v}"
                )

        return len(errors) == 0, errors

    def validate_contract_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validate a synthetic base contract JSON file on disk."""
        if not os.path.exists(file_path):
            return False, [f"Contract file not found: {file_path}"]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
        except Exception as e:
            return False, [f"Failed to parse JSON in {file_path}: {e}"]

        return self.validate_contract(contract)

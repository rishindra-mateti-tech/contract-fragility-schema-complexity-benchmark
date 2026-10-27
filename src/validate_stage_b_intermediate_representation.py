#!/usr/bin/env python3
"""Validator for Stage B Intermediate Representations.

Enforces structural integrity, JSON Schema Draft-07 compliance, and
epistemic lifecycle boundaries under STATIC_SOURCE_INTERMEDIATE_REPRESENTATION_SPEC_001.
"""

from typing import Any, Dict, List, Tuple
import jsonschema

REQUIRED_IR_KEYS = [
    "spec_id",
    "ir_version",
    "operation_identity",
    "source_file_closure",
    "input_surface",
    "schema_complexity_metrics",
    "source_lineage_and_evidence",
    "transformation_and_adapter_decisions",
    "unsupported_feature_flags",
    "status_and_confidence",
]


class IntermediateRepresentationValidator:
    """Validates intermediate representation artifacts against specification requirements."""

    def validate(self, ir_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate an intermediate representation record.
        
        Returns:
            Tuple of (is_valid, list_of_error_strings)
        """
        errors: List[str] = []

        if not isinstance(ir_data, dict):
            return False, ["IR record must be a dictionary"]

        # 1. Top-level keys
        for k in REQUIRED_IR_KEYS:
            if k not in ir_data:
                errors.append(f"Missing required top-level key: {k}")

        if errors:
            return False, errors

        # 2. Operation identity
        op_id = ir_data["operation_identity"]
        for field in ["operation_id", "slot_id", "candidate_source_id", "source_dialect", "target_dialect"]:
            if not op_id.get(field):
                errors.append(f"Missing or empty operation_identity.{field}")

        # 3. Input surface checks
        surface = ir_data.get("input_surface", {})
        if surface.get("type") != "object":
            errors.append(f"input_surface.type must be 'object', got {surface.get('type')}")
        if surface.get("additionalProperties") is not False:
            errors.append("input_surface.additionalProperties must be explicitly False")
        if not isinstance(surface.get("properties"), dict):
            errors.append("input_surface.properties must be a dictionary")
        if not isinstance(surface.get("required"), list):
            errors.append("input_surface.required must be a list")

        # 4. JSON Schema Draft-07 syntax validity
        try:
            jsonschema.Draft7Validator.check_schema(surface)
        except jsonschema.SchemaError as e:
            errors.append(f"input_surface violates Draft-07 syntax: {e.message}")

        # 5. Check raw nullable keyword absence
        def check_no_nullable(node: Any, path: str = "#"):
            if isinstance(node, dict):
                if "nullable" in node:
                    errors.append(f"Raw OpenAPI 'nullable' keyword detected at {path}")
                for k, v in node.items():
                    check_no_nullable(v, f"{path}/{k}")
            elif isinstance(node, list):
                for i, elt in enumerate(node):
                    check_no_nullable(elt, f"{path}/{i}")

        check_no_nullable(surface)

        # 6. Status and lifecycle invariants
        status = ir_data.get("status_and_confidence", {})
        if status.get("lifecycle_status") != "EXTRACTED_PENDING_HUMAN_VALIDATION":
            errors.append(
                f"Unauthorized lifecycle status '{status.get('lifecycle_status')}'; must be EXTRACTED_PENDING_HUMAN_VALIDATION"
            )
        if status.get("independent_validation_status") != "NOT_INDEPENDENTLY_VALIDATED":
            errors.append("independent_validation_status must be NOT_INDEPENDENTLY_VALIDATED")

        # Global CANONICAL_FAITHFUL prohibition
        raw_repr = str(ir_data)
        if "CANONICAL_FAITHFUL" in raw_repr:
            errors.append("Strict prohibition violation: CANONICAL_FAITHFUL found in IR record")

        return len(errors) == 0, errors

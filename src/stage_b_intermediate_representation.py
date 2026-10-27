#!/usr/bin/env python3
"""Stage B Common Source-Neutral Intermediate Representation.

Constructs and models the standardized Intermediate Representation (IR)
under STATIC_SOURCE_INTERMEDIATE_REPRESENTATION_SPEC_001.

Unifies tool operations extracted across:
- OpenAPI 3.0 / 3.0.3 (single-file and multi-file local refs)
- OpenAPI 2.0 (formData surfaces)
- Python 3 AST tool declarations
- TypeScript AST tool declarations
"""

import copy
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

SPEC_ID = "STATIC_SOURCE_INTERMEDIATE_REPRESENTATION_SPEC_001"
IR_VERSION = "1.0.0"


def compute_schema_depth(schema: Any, current_depth: int = 1) -> int:
    """Calculate maximum nesting depth in a JSON Schema."""
    if not isinstance(schema, dict):
        return current_depth

    max_d = current_depth

    # Check object properties
    props = schema.get("properties", {})
    if isinstance(props, dict):
        for _, p_val in props.items():
            if isinstance(p_val, dict):
                max_d = max(max_d, compute_schema_depth(p_val, current_depth + 1))

    # Check array items
    items = schema.get("items")
    if isinstance(items, dict):
        max_d = max(max_d, compute_schema_depth(items, current_depth + 1))
    elif isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                max_d = max(max_d, compute_schema_depth(item, current_depth + 1))

    # Check combinators
    for comb in ["allOf", "anyOf", "oneOf"]:
        for child in schema.get(comb, []):
            if isinstance(child, dict):
                max_d = max(max_d, compute_schema_depth(child, current_depth + 1))

    return max_d


def compute_complexity_metrics(input_surface: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate complexity metrics for an input surface schema."""
    props = input_surface.get("properties", {})
    req = input_surface.get("required", [])

    has_nested = False
    has_arrays = False
    has_enums = False

    def scan_schema(node: Any):
        nonlocal has_nested, has_arrays, has_enums
        if isinstance(node, dict):
            if node.get("type") == "object" and node != input_surface:
                has_nested = True
            if node.get("type") == "array":
                has_arrays = True
            if "enum" in node:
                has_enums = True
            for v in node.values():
                scan_schema(v)
        elif isinstance(node, list):
            for item in node:
                scan_schema(item)

    scan_schema(input_surface)

    return {
        "property_count": len(props) if isinstance(props, dict) else 0,
        "required_count": len(req) if isinstance(req, list) else 0,
        "max_nesting_depth": compute_schema_depth(input_surface),
        "has_nested_objects": has_nested,
        "has_arrays": has_arrays,
        "has_enums": has_enums,
    }


def build_intermediate_representation(
    operation_id: str,
    slot_id: str,
    candidate_source_id: str,
    source_dialect: str,
    primary_source_file: str,
    primary_source_file_blob_sha: str,
    primary_source_file_sha256: str,
    input_surface: Dict[str, Any],
    source_pointer: Optional[str] = None,
    ast_span: Optional[Dict[str, int]] = None,
    ast_path: Optional[str] = None,
    source_snippet: Optional[str] = None,
    source_snippet_sha256: Optional[str] = None,
    parser_name: str = "native_json_yaml",
    parser_version: str = "1.0.0",
    closure_files_accessed: Optional[List[str]] = None,
    closure_manifest_sha256: Optional[str] = None,
    adapter_decisions: Optional[List[Dict[str, Any]]] = None,
    unsupported_feature_flags: Optional[List[str]] = None,
    sub_surfaces: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    """Construct a compliant Intermediate Representation dictionary."""
    clean_surface = copy.deepcopy(input_surface)
    if clean_surface.get("type") != "object":
        clean_surface["type"] = "object"
    clean_surface["additionalProperties"] = False

    metrics = compute_complexity_metrics(clean_surface)

    span_data = ast_span or {"lineno": 0, "col_offset": 0, "end_lineno": 0, "end_col_offset": 0}

    sub_surfs = sub_surfaces or {
        "path": [],
        "query": [],
        "header": [],
        "form": [],
        "body": [],
        "rpc_arguments": list(clean_surface.get("properties", {}).keys()),
    }

    return {
        "spec_id": SPEC_ID,
        "ir_version": IR_VERSION,
        "operation_identity": {
            "operation_id": operation_id,
            "slot_id": slot_id,
            "candidate_source_id": candidate_source_id,
            "source_dialect": source_dialect,
            "target_dialect": "JSON Schema Draft-07",
        },
        "source_file_closure": {
            "primary_source_file": primary_source_file.replace("\\", "/"),
            "primary_source_file_blob_sha": primary_source_file_blob_sha,
            "primary_source_file_sha256": primary_source_file_sha256,
            "closure_files_accessed": closure_files_accessed or [primary_source_file.replace("\\", "/")],
            "closure_manifest_sha256": closure_manifest_sha256,
        },
        "input_surface": {
            "type": clean_surface["type"],
            "properties": clean_surface.get("properties", {}),
            "required": clean_surface.get("required", []),
            "additionalProperties": False,
            "sub_surfaces": sub_surfs,
        },
        "schema_complexity_metrics": metrics,
        "source_lineage_and_evidence": {
            "source_pointer": source_pointer,
            "ast_span": span_data,
            "ast_path": ast_path,
            "source_snippet": source_snippet,
            "source_snippet_sha256": source_snippet_sha256,
            "parser_name": parser_name,
            "parser_version": parser_version,
        },
        "transformation_and_adapter_decisions": adapter_decisions or [],
        "unsupported_feature_flags": unsupported_feature_flags or [],
        "status_and_confidence": {
            "lifecycle_status": "EXTRACTED_PENDING_HUMAN_VALIDATION",
            "confidence_assessment": "STATICALLY_VERIFIED_LITERAL",
            "independent_validation_status": "NOT_INDEPENDENTLY_VALIDATED",
        },
    }

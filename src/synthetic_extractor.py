#!/usr/bin/env python3
"""Synthetic Extraction Pipeline for Stage B Adversarial Test Corpus.

Enables unit and metamorphic testing of canonical contract extraction rules
on synthetic OpenAPI fixtures without touching real benchmark operations or slots.
"""

import copy
import hashlib
import json
from typing import Any, Dict, List, Optional, Set, Tuple

from src.extract_stage_b_canonical_contract import (
    compute_schema_depth,
    extract_schema_node,
    resolve_json_pointer,
)
from src.schema_feature_registry import (
    SchemaFeatureRegistry,
    UnsupportedSchemaFeatureError,
    get_default_registry,
)


class SyntheticExtractionError(ValueError):
    """Raised when synthetic extraction fails closed on invalid or unsupported constructs."""
    pass


def extract_synthetic_contract(
    raw_doc: Dict[str, Any],
    operation_pointer: str,
    registry: Optional[SchemaFeatureRegistry] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Extract canonical Draft-07 tool contract and field lineage from a synthetic OpenAPI document.

    Fails closed if the specification contains unsupported features, recursion cycles,
    unsupported transport surfaces (cookie), unsupported content-types, or excessive depth.
    """
    if registry is None:
        registry = get_default_registry()

    op_node = resolve_json_pointer(raw_doc, operation_pointer)
    if not isinstance(op_node, dict):
        raise SyntheticExtractionError(f"Operation node at {operation_pointer} is not an object")

    parameters = op_node.get("parameters", [])
    request_body = op_node.get("requestBody")

    # 1. Transport Surface Checks
    path_props: Dict[str, Any] = {}
    path_req: List[str] = []
    lineage_records: List[Dict[str, Any]] = []

    for idx, param in enumerate(parameters):
        if "$ref" in param:
            param = resolve_json_pointer(raw_doc, param["$ref"])

        p_in = param.get("in")
        p_name = param.get("name")
        param_ptr = f"{operation_pointer}/parameters/{idx}"

        if p_in == "cookie":
            raise UnsupportedSchemaFeatureError(
                "FEAT_SURF_COOKIE_PARAMS",
                "Cookie transport surface is unsupported fail-closed",
                param_ptr,
            )

        if p_in == "path":
            schema = param.get("schema", {"type": "string"})
            registry.validate_schema_compliance(schema, pointer=f"{param_ptr}/schema", fail_closed=True, raw_doc=raw_doc)
            extracted = extract_schema_node(schema, raw_doc, f"{param_ptr}/schema")
            path_props[p_name] = extracted
            if param.get("required", False):
                path_req.append(p_name)

            lineage_records.append({
                "canonical_field_path": f"path_parameters.{p_name}",
                "raw_source_pointer": f"{param_ptr}/schema",
                "transport_surface": "path_parameters",
                "field_name": p_name,
            })

    # 2. Body Schema Extraction
    body_schema_node: Optional[Dict[str, Any]] = None
    content_type_used = "none"

    if request_body:
        rb_ptr = f"{operation_pointer}/requestBody"
        if "$ref" in request_body:
            request_body = resolve_json_pointer(raw_doc, request_body["$ref"])

        content_map = request_body.get("content", {})
        for ct in content_map.keys():
            if ct in ("multipart/form-data", "text/plain", "application/octet-stream"):
                feat_map = {
                    "multipart/form-data": "FEAT_CT_MULTIPART_FORM_DATA",
                    "text/plain": "FEAT_CT_TEXT_PLAIN",
                    "application/octet-stream": "FEAT_CT_APPLICATION_OCTET_STREAM",
                }
                raise UnsupportedSchemaFeatureError(
                    feat_map[ct],
                    f"Content-type '{ct}' is unsupported fail-closed",
                    f"{rb_ptr}/content/{ct}",
                )

        if "application/json" in content_map:
            content_type_used = "application/json"
            raw_b_schema = content_map["application/json"].get("schema", {})
            schema_ptr = f"{rb_ptr}/content/application~1json/schema"
        elif "application/x-www-form-urlencoded" in content_map:
            content_type_used = "application/x-www-form-urlencoded"
            raw_b_schema = content_map["application/x-www-form-urlencoded"].get("schema", {})
            schema_ptr = f"{rb_ptr}/content/application~1x-www-form-urlencoded/schema"
        else:
            raw_b_schema = {}
            schema_ptr = f"{rb_ptr}/content"

        if raw_b_schema:
            registry.validate_schema_compliance(raw_b_schema, pointer=schema_ptr, fail_closed=True, raw_doc=raw_doc)
            body_schema_node = extract_schema_node(raw_b_schema, raw_doc, schema_ptr)

            # Record body lineage
            def record_body_lineage(node: Any, curr_path: str, curr_ptr: str):
                if not isinstance(node, dict):
                    return
                props = node.get("properties", {})
                for k, v in props.items():
                    sub_path = f"{curr_path}.{k}" if curr_path else k
                    sub_ptr = f"{curr_ptr}/properties/{k}"
                    lineage_records.append({
                        "canonical_field_path": f"body.{sub_path}",
                        "raw_source_pointer": sub_ptr,
                        "transport_surface": "body",
                        "field_name": k,
                    })
                    record_body_lineage(v, sub_path, sub_ptr)

            record_body_lineage(body_schema_node, "", schema_ptr)

    # 3. Assemble Canonical Contract
    root_properties: Dict[str, Any] = {}
    root_required: List[str] = []

    if path_props:
        root_properties["path_parameters"] = {
            "type": "object",
            "additionalProperties": False,
            "properties": {k: path_props[k] for k in sorted(path_props.keys())},
        }
        if path_req:
            root_properties["path_parameters"]["required"] = sorted(path_req)
        root_required.append("path_parameters")

    if body_schema_node:
        root_properties["body"] = body_schema_node
        root_required.append("body")

    canonical_contract = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": op_node.get("operationId", "SyntheticContract"),
        "description": op_node.get("description", "Synthetic contract"),
        "type": "object",
        "additionalProperties": False,
        "properties": root_properties,
    }
    if root_required:
        canonical_contract["required"] = sorted(root_required)

    return canonical_contract, lineage_records


def hash_contract(contract: Dict[str, Any]) -> str:
    """Return deterministic SHA-256 of canonical contract."""
    serialized = json.dumps(contract, indent=2, sort_keys=True).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()

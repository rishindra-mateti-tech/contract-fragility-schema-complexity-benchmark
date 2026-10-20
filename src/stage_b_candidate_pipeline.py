#!/usr/bin/env python3
"""Stage B Generic Batch Candidate Extraction Pipeline.

Implements the generic, fail-closed batch extraction pipeline for Stage B candidates:
- Deterministic preflight verification of raw sources, hashes, pointers, and features.
- Fail-closed stops on unratified unions, external references, recursion cycles, depth > 5, or binary formats.
- Verbatim keyword preservation without hand-maintained property whitelists.
- Explicit classification of WRAPPER_CLOSED_OBJECT_POLICY_001 (additionalProperties: false).
- Production of 8 quarantined candidate artifacts per eligible operation:
  1. candidate_contract.json
  2. field_lineage.jsonl
  3. difference_register.json
  4. extraction_metadata.json
  5. feature_inventory.json
  6. serialization_characterization.json
  7. candidate_validation_report.md
  8. review_packet.md
- Strict lifecycle status invariant: EXTRACTED_PENDING_HUMAN_VALIDATION (never CANONICAL_FAITHFUL).
- Creation mode: BATCH_GENERATED_CANDIDATE with NOT_INDEPENDENTLY_VALIDATED declaration.
"""

import copy
import datetime
import glob
import hashlib
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.stage_b_candidate_manifest import (
    RAW_DIR,
    FEATURE_REGISTRY_PATH,
    sha256_file,
    git_blob_sha,
    load_feature_registry,
    load_provenance_registry,
    resolve_raw_source_file,
)

EXTRACTOR_VERSION = "2.0.0"
EXTRACTION_RULE_VERSION = "2.0.0"
GOVERNING_SPECIFICATION = "STAGE_B_EXTRACTION_SPEC.md"
WRAPPER_POLICY_ID = "WRAPPER_CLOSED_OBJECT_POLICY_001"
AST_SPAN_OMISSION_REASON = (
    "Line numbers not deterministically preserved across JSON/YAML parsers; "
    "RFC 6901 JSON pointers provide exact cryptographic and structural AST provenance."
)
DEFAULT_GENERATION_TIMESTAMP = "2026-10-20T08:00:00Z"


def resolve_json_pointer(doc: Any, pointer: str) -> Any:
    """Resolve an RFC 6901 JSON Pointer against a Python dict/list structure."""
    if not pointer or pointer == "#":
        return doc
    clean = pointer.lstrip("#")
    if clean.startswith("/"):
        clean = clean[1:]
    tokens = clean.split("/")
    curr = doc
    for t in tokens:
        decoded = t.replace("~1", "/").replace("~0", "~")
        if isinstance(curr, dict):
            if decoded in curr:
                curr = curr[decoded]
            else:
                raise KeyError(f"Pointer token '{decoded}' not found in dict")
        elif isinstance(curr, list):
            try:
                idx = int(decoded)
                curr = curr[idx]
            except (ValueError, IndexError) as exc:
                raise KeyError(f"Pointer token '{decoded}' invalid index for list: {exc}")
        else:
            raise KeyError(f"Cannot traverse scalar value at token '{decoded}'")
    return curr


def compute_schema_depth(schema: Any, current_depth: int = 0, visited: Optional[Set[int]] = None) -> int:
    """Recursively compute maximum nesting depth of a schema."""
    if visited is None:
        visited = set()
    if not isinstance(schema, dict):
        return current_depth

    schema_id = id(schema)
    if schema_id in visited:
        return current_depth
    visited.add(schema_id)

    max_d = current_depth
    if "properties" in schema and isinstance(schema["properties"], dict):
        for prop in schema["properties"].values():
            d = compute_schema_depth(prop, current_depth + 1, visited.copy())
            if d > max_d:
                max_d = d
    if "items" in schema:
        if isinstance(schema["items"], dict):
            d = compute_schema_depth(schema["items"], current_depth + 1, visited.copy())
            if d > max_d:
                max_d = d
        elif isinstance(schema["items"], list):
            for item in schema["items"]:
                d = compute_schema_depth(item, current_depth + 1, visited.copy())
                if d > max_d:
                    max_d = d
    if "additionalProperties" in schema and isinstance(schema["additionalProperties"], dict):
        d = compute_schema_depth(schema["additionalProperties"], current_depth + 1, visited.copy())
        if d > max_d:
            max_d = d
    return max_d


class PreflightChecker:
    """Validates an operation before extraction and rejects unverified or prohibited constructs."""

    def __init__(self, feature_registry: Optional[Dict[str, Any]] = None):
        self.feature_registry = feature_registry or load_feature_registry()
        self.registry_features = {
            f["feature_id"]: f for f in self.feature_registry.get("features", [])
        }

    def run_preflight(
        self,
        op_entry: Dict[str, Any],
        raw_doc: Any,
        raw_file_path: str,
        ext: str,
    ) -> Dict[str, Any]:
        """Execute all deterministic preflight gates for an operation entry.

        Returns a dictionary:
        {
            "passed": bool,
            "rejection_code": Optional[str],
            "rejection_category": Optional[str],
            "rejection_reason": Optional[str],
            "evidence": Dict[str, Any],
            "detected_features": List[Dict[str, Any]],
        }
        """
        slot_id = op_entry.get("slot_id", "UNKNOWN_SLOT")
        op_id = op_entry.get("operation_id", "UNKNOWN_OP")
        pointer = op_entry.get("source_spec_pointer", "")
        cid = op_entry.get("candidate_source_id", "")
        bsha = op_entry.get("source_file_blob_sha", "")

        detected_features: List[Dict[str, Any]] = []

        # Gate 1: Source format check (must be OpenAPI JSON or YAML)
        if ext not in [".json", ".yaml", ".yml"]:
            return {
                "passed": False,
                "rejection_code": "NON_OPENAPI_SPEC_SOURCE_CODE",
                "rejection_category": "UNSUPPORTED_SPEC_FORMAT",
                "rejection_reason": f"Source file format '{ext}' is source code AST, not an OpenAPI specification.",
                "evidence": {"ext": ext, "path": raw_file_path},
                "detected_features": [],
            }

        # Gate 2: Pointer resolution check
        try:
            op_node = resolve_json_pointer(raw_doc, pointer)
        except Exception as e:
            return {
                "passed": False,
                "rejection_code": "POINTER_RESOLUTION_FAILED",
                "rejection_category": "SPEC_INTEGRITY_FAILURE",
                "rejection_reason": f"JSON pointer '{pointer}' failed to resolve in source: {e}",
                "evidence": {"pointer": pointer, "error": str(e)},
                "detected_features": [],
            }

        if not isinstance(op_node, dict):
            return {
                "passed": False,
                "rejection_code": "OPERATION_NODE_NOT_DICT",
                "rejection_category": "SPEC_INTEGRITY_FAILURE",
                "rejection_reason": f"Resolved operation at '{pointer}' is not an object node.",
                "evidence": {"type": str(type(op_node))},
                "detected_features": [],
            }

        # Gate 3: Check $ref at operation node level
        if "$ref" in op_node:
            ref_val = op_node["$ref"]
            if not ref_val.startswith("#/"):
                return {
                    "passed": False,
                    "rejection_code": "FEAT_REF_EXTERNAL_FILE",
                    "rejection_category": "PROHIBITED_FEATURE",
                    "rejection_reason": f"Operation defines external file reference: {ref_val}",
                    "evidence": {"ref": ref_val, "pointer": pointer},
                    "detected_features": [],
                }

        # Gate 4: Swagger 2.0 in:formData check
        params = op_node.get("parameters", [])
        if params is None:
            params = []
        for idx, p in enumerate(params):
            resolved_p = p
            if isinstance(p, dict) and "$ref" in p and p["$ref"].startswith("#/"):
                try:
                    resolved_p = resolve_json_pointer(raw_doc, p["$ref"])
                except Exception:
                    pass
            if isinstance(resolved_p, dict) and resolved_p.get("in") == "formData":
                return {
                    "passed": False,
                    "rejection_code": "FEAT_SWAGGER_FORM_DATA_UNSUPPORTED",
                    "rejection_category": "UNSUPPORTED_SURFACE",
                    "rejection_reason": (
                        "Operation declares Swagger 2.0 in:formData parameters. "
                        "Current benchmark extraction requires OpenAPI 3.0 requestBody."
                    ),
                    "evidence": {"param": resolved_p.get("name"), "pointer": f"{pointer}/parameters/{idx}"},
                    "detected_features": [],
                }

        # Gate 5: Uninherited path-level parameters check
        if pointer.startswith("#/paths/"):
            ptr_tokens = pointer.lstrip("#/").split("/")
            if len(ptr_tokens) >= 2:
                path_item_ptr = "#/" + "/".join(ptr_tokens[:-1])
                try:
                    path_item_node = resolve_json_pointer(raw_doc, path_item_ptr)
                    if isinstance(path_item_node, dict):
                        raw_plp = path_item_node.get("parameters", [])
                        if isinstance(raw_plp, list) and raw_plp and not params:
                            return {
                                "passed": False,
                                "rejection_code": "UNINHERITED_PATH_PARAMETERS",
                                "rejection_category": "SPEC_STRUCTURE_AMBIGUITY",
                                "rejection_reason": (
                                    f"Operation defines {len(raw_plp)} path-level parameter(s) on parent "
                                    f"path item not inherited in operation parameters."
                                ),
                                "evidence": {"path_level_params_count": len(raw_plp), "path_item": path_item_ptr},
                                "detected_features": [],
                            }
                except Exception:
                    pass

        # Gate 6: Deep schema feature inspection (unions, format binary, cycles, depth)
        traversal_errors: List[Dict[str, str]] = []
        visited_refs: Set[str] = set()

        def inspect_schema(schema_node: Any, curr_ptr: str, depth: int):
            if depth > 5:
                traversal_errors.append({
                    "code": "FEAT_REC_EXCESSIVE_DEPTH",
                    "reason": f"Schema nesting depth {depth} exceeds limit of 5 at {curr_ptr}",
                    "pointer": curr_ptr,
                })
                return
            if not isinstance(schema_node, dict):
                return

            if "$ref" in schema_node:
                ref_ptr = schema_node["$ref"]
                if not ref_ptr.startswith("#/"):
                    traversal_errors.append({
                        "code": "FEAT_REF_EXTERNAL_FILE",
                        "reason": f"External schema reference '{ref_ptr}' at {curr_ptr}",
                        "pointer": curr_ptr,
                    })
                    return
                if ref_ptr in visited_refs:
                    traversal_errors.append({
                        "code": "FEAT_REC_CYCLIC_SCHEMA",
                        "reason": f"Cyclic reference to '{ref_ptr}' detected at {curr_ptr}",
                        "pointer": curr_ptr,
                    })
                    return
                visited_refs.add(ref_ptr)
                try:
                    deref = resolve_json_pointer(raw_doc, ref_ptr)
                    inspect_schema(deref, ref_ptr, depth)
                except Exception as ex:
                    traversal_errors.append({
                        "code": "POINTER_RESOLUTION_FAILED",
                        "reason": f"Failed to resolve ref '{ref_ptr}' from {curr_ptr}: {ex}",
                        "pointer": curr_ptr,
                    })
                return

            # Check for polymorphic unions
            if "oneOf" in schema_node:
                traversal_errors.append({
                    "code": "FEAT_COMP_ONEOF",
                    "reason": f"Polymorphic oneOf union detected at {curr_ptr}",
                    "pointer": curr_ptr,
                })
                return
            if "anyOf" in schema_node:
                traversal_errors.append({
                    "code": "FEAT_COMP_ANYOF",
                    "reason": f"Polymorphic anyOf union detected at {curr_ptr}",
                    "pointer": curr_ptr,
                })
                return
            if "discriminator" in schema_node:
                traversal_errors.append({
                    "code": "FEAT_COMP_DISCRIMINATOR",
                    "reason": f"OpenAPI discriminator object detected at {curr_ptr}",
                    "pointer": curr_ptr,
                })
                return

            # Check for binary payload
            if schema_node.get("format") in ["binary", "byte"]:
                traversal_errors.append({
                    "code": "FEAT_BIN_FORMAT_BINARY",
                    "reason": f"Binary payload format '{schema_node.get('format')}' at {curr_ptr}",
                    "pointer": curr_ptr,
                })
                return

            # Traverse properties
            if "properties" in schema_node and isinstance(schema_node["properties"], dict):
                for p_name, p_schema in schema_node["properties"].items():
                    inspect_schema(p_schema, f"{curr_ptr}/properties/{p_name}", depth + 1)

            # Traverse items
            if "items" in schema_node:
                if isinstance(schema_node["items"], dict):
                    inspect_schema(schema_node["items"], f"{curr_ptr}/items", depth + 1)
                elif isinstance(schema_node["items"], list):
                    for idx_item, it in enumerate(schema_node["items"]):
                        inspect_schema(it, f"{curr_ptr}/items/{idx_item}", depth + 1)

            # Traverse additionalProperties
            if "additionalProperties" in schema_node and isinstance(schema_node["additionalProperties"], dict):
                inspect_schema(schema_node["additionalProperties"], f"{curr_ptr}/additionalProperties", depth + 1)

        # Inspect parameters schemas
        for idx, p in enumerate(params):
            resolved_p = p
            if isinstance(p, dict) and "$ref" in p and p["$ref"].startswith("#/"):
                try:
                    resolved_p = resolve_json_pointer(raw_doc, p["$ref"])
                except Exception:
                    pass
            if isinstance(resolved_p, dict) and "schema" in resolved_p:
                inspect_schema(resolved_p["schema"], f"{pointer}/parameters/{idx}/schema", 1)

        # Inspect requestBody schemas
        rb = op_node.get("requestBody", {})
        if isinstance(rb, dict):
            if "$ref" in rb and rb["$ref"].startswith("#/"):
                try:
                    rb = resolve_json_pointer(raw_doc, rb["$ref"])
                except Exception:
                    pass
            content = rb.get("content", {})
            if isinstance(content, dict):
                if "multipart/form-data" in content:
                    return {
                        "passed": False,
                        "rejection_code": "FEAT_CT_MULTIPART_FORM_DATA",
                        "rejection_category": "PROHIBITED_FEATURE",
                        "rejection_reason": "Content-Type multipart/form-data is prohibited in canonical benchmark.",
                        "evidence": {"pointer": f"{pointer}/requestBody/content/multipart~1form-data"},
                        "detected_features": [],
                    }
                for ct, citem in content.items():
                    if isinstance(citem, dict) and "schema" in citem:
                        encoded_ct = ct.replace("~", "~0").replace("/", "~1")
                        inspect_schema(citem["schema"], f"{pointer}/requestBody/content/{encoded_ct}/schema", 1)

        if traversal_errors:
            first_err = traversal_errors[0]
            return {
                "passed": False,
                "rejection_code": first_err["code"],
                "rejection_category": "SCHEMA_SEMANTIC_PROHIBITION",
                "rejection_reason": first_err["reason"],
                "evidence": {"pointer": first_err["pointer"], "all_errors": traversal_errors},
                "detected_features": [],
            }

        # Collect detected features
        detected_features.append(self.registry_features.get("FEAT_WRAPPER_CLOSED_OBJECT", {
            "feature_id": "FEAT_WRAPPER_CLOSED_OBJECT",
            "name": "Root and Transport Wrapper Object Closure",
            "category": "OBJECT_CONTAINERS",
            "extraction_behavior": "EXPLICIT_NORMALIZATION",
            "current_benchmark_status": "SUPPORTED",
        }))

        return {
            "passed": True,
            "rejection_code": None,
            "rejection_category": None,
            "rejection_reason": None,
            "evidence": {
                "parameters_count": len(params),
                "request_body_present": bool(rb),
            },
            "detected_features": detected_features,
        }


class GenericCandidateExtractor:
    """Generic extraction engine producing quarantined candidate bundles."""

    def __init__(self, extractor_script_sha: str, extractor_git_commit: str):
        self.extractor_script_sha = extractor_script_sha
        self.extractor_git_commit = extractor_git_commit
        self.feature_registry = load_feature_registry()

    def extract_schema_node(
        self,
        raw_schema: Any,
        raw_doc: Any,
        raw_pointer: str,
        current_depth: int = 0,
    ) -> Any:
        """Recursively extract a schema node preserving all supported keywords."""
        if not isinstance(raw_schema, dict):
            return copy.deepcopy(raw_schema)

        if current_depth > 5:
            raise ValueError(f"Recursion depth exceeded limit of 5 at {raw_pointer}")

        if "$ref" in raw_schema:
            ref_ptr = raw_schema["$ref"]
            dereferenced = resolve_json_pointer(raw_doc, ref_ptr)
            return self.extract_schema_node(dereferenced, raw_doc, ref_ptr, current_depth)

        node: Dict[str, Any] = {}
        for key, val in sorted(raw_schema.items()):
            if key == "properties" and isinstance(val, dict):
                node["properties"] = {
                    prop_name: self.extract_schema_node(
                        prop_def,
                        raw_doc,
                        f"{raw_pointer}/properties/{prop_name}",
                        current_depth + 1,
                    )
                    for prop_name, prop_def in sorted(val.items())
                }
            elif key == "items":
                if isinstance(val, dict):
                    node["items"] = self.extract_schema_node(
                        val,
                        raw_doc,
                        f"{raw_pointer}/items",
                        current_depth + 1,
                    )
                elif isinstance(val, list):
                    node["items"] = [
                        self.extract_schema_node(
                            it,
                            raw_doc,
                            f"{raw_pointer}/items/{idx}",
                            current_depth + 1,
                        )
                        for idx, it in enumerate(val)
                    ]
                else:
                    node["items"] = copy.deepcopy(val)
            elif key == "required" and isinstance(val, list):
                node["required"] = sorted(copy.deepcopy(val))
            elif key == "additionalProperties":
                if isinstance(val, dict):
                    node["additionalProperties"] = self.extract_schema_node(
                        val,
                        raw_doc,
                        f"{raw_pointer}/additionalProperties",
                        current_depth + 1,
                    )
                else:
                    node["additionalProperties"] = val
            elif key == "allOf" and isinstance(val, list):
                node["allOf"] = [
                    self.extract_schema_node(
                        sub,
                        raw_doc,
                        f"{raw_pointer}/allOf/{idx}",
                        current_depth + 1,
                    )
                    for idx, sub in enumerate(val)
                ]
            else:
                node[key] = copy.deepcopy(val)
        return node

    def extract_candidate_bundle(
        self,
        op_entry: Dict[str, Any],
        raw_doc: Any,
        raw_file_sha: str,
        raw_blob_sha: str,
        generated_at_utc: str = DEFAULT_GENERATION_TIMESTAMP,
    ) -> Dict[str, Any]:
        """Extract a complete 8-artifact candidate package for an eligible slot."""
        slot_id = op_entry["slot_id"]
        op_id = op_entry["operation_id"]
        cid = op_entry["candidate_source_id"]
        cluster_id = op_entry.get("source_cluster_id", "UNKNOWN_CLUSTER")
        target_domain = op_entry.get("intended_benchmark_domain", "UNKNOWN_DOMAIN")
        method = op_entry.get("http_method", "POST")
        endpoint = op_entry.get("endpoint_path", op_entry.get("endpoint", "UNKNOWN_ENDPOINT"))
        source_pointer = op_entry["source_spec_pointer"]

        op_node = resolve_json_pointer(raw_doc, source_pointer)

        summary = op_node.get("summary", "")
        op_description = summary if summary else op_node.get(
            "description", f"{method} {endpoint} ({op_id})"
        )
        desc_transformation = (
            "RAW_SUMMARY" if summary else ("RAW_DESCRIPTION" if op_node.get("description") else "DETERMINISTIC_TEMPLATE_FALLBACK")
        )
        desc_raw_pointer = f"{source_pointer}/summary" if summary else f"{source_pointer}/description"

        lineage_records: List[Dict[str, Any]] = []
        difference_records: List[Dict[str, Any]] = []

        # 1. Transport Surfaces extraction
        path_parameters: Dict[str, Any] = {}
        path_required: List[str] = []
        query_parameters: Dict[str, Any] = {}
        query_required: List[str] = []
        header_parameters: Dict[str, Any] = {}
        header_required: List[str] = []

        raw_params = op_node.get("parameters", [])
        if raw_params is None:
            raw_params = []

        for idx, p in enumerate(raw_params):
            param_pointer = f"{source_pointer}/parameters/{idx}"
            resolved_param = p
            ref_pointer = None
            if isinstance(p, dict) and "$ref" in p:
                ref_pointer = p["$ref"]
                resolved_param = resolve_json_pointer(raw_doc, ref_pointer)

            param_name = resolved_param["name"]
            param_in = resolved_param.get("in", "path")
            param_required = resolved_param.get("required", False)

            param_schema = copy.deepcopy(resolved_param.get("schema", {}))
            if "description" in resolved_param and "description" not in param_schema:
                param_schema["description"] = resolved_param["description"]

            prop_node = self.extract_schema_node(
                raw_schema=param_schema,
                raw_doc=raw_doc,
                raw_pointer=ref_pointer or param_pointer,
                current_depth=1,
            )

            raw_pointers = [param_pointer]
            if ref_pointer:
                raw_pointers.append(ref_pointer)

            if param_in == "path":
                path_parameters[param_name] = prop_node
                if param_required:
                    path_required.append(param_name)
                canonical_ptr = f"/properties/path/properties/{param_name}"
            elif param_in == "query":
                query_parameters[param_name] = prop_node
                if param_required:
                    query_required.append(param_name)
                canonical_ptr = f"/properties/query/properties/{param_name}"
            elif param_in == "header":
                header_parameters[param_name] = prop_node
                if param_required:
                    header_required.append(param_name)
                canonical_ptr = f"/properties/header/properties/{param_name}"
            else:
                continue

            lineage_records.append({
                "canonical_json_pointer": canonical_ptr,
                "candidate_source_id": cid,
                "source_cluster_id": cluster_id,
                "raw_source_blob_sha": raw_blob_sha,
                "raw_source_pointers": raw_pointers,
                "source_ast_span": None,
                "source_ast_span_reason": AST_SPAN_OMISSION_REASON,
                "transformation_category": "SURFACE_WRAPPING",
                "is_reversible": True,
                "extractor_version": EXTRACTOR_VERSION,
                "extraction_timestamp": generated_at_utc,
                "reviewer_decision": "PENDING_REVIEW",
            })

            difference_records.append({
                "source_json_pointer": raw_pointers[0],
                "candidate_json_pointer": canonical_ptr,
                "field_path": f"{param_in}.{param_name}",
                "source_value_or_type": param_schema.get("type", "object"),
                "candidate_value_or_type": prop_node.get("type", "object"),
                "difference_category": "TRANSPORT_SURFACE_PARAMETER",
                "classification": "PRESERVED",
                "policy_pointer": "STAGE_B_EXTRACTION_SPEC.md",
                "human_validation_required": False,
                "rationale": f"Preserved {param_in} parameter '{param_name}' verbatim into canonical surface container.",
            })

        # 2. Body surface extraction
        body_parameters: Dict[str, Any] = {}
        body_required: List[str] = []

        body_node = op_node.get("requestBody", {})
        body_content = body_node.get("content", {}) if isinstance(body_node, dict) else {}

        target_ct = op_entry.get("request_content_type")
        if not target_ct or target_ct not in body_content:
            if "application/json" in body_content:
                target_ct = "application/json"
            elif "application/x-www-form-urlencoded" in body_content:
                target_ct = "application/x-www-form-urlencoded"
            elif body_content:
                target_ct = list(body_content.keys())[0]
            else:
                target_ct = "application/json"

        content_item = body_content.get(target_ct, {}) if isinstance(body_content, dict) else {}
        raw_body_schema = content_item.get("schema", {})
        encoding_obj = content_item.get("encoding", {})

        if isinstance(raw_body_schema, dict) and "$ref" in raw_body_schema:
            ref_ptr = raw_body_schema["$ref"]
            raw_body_schema = resolve_json_pointer(raw_doc, ref_ptr)

        encoded_ct = target_ct.replace("~", "~0").replace("/", "~1")
        raw_body_schema_pointer = f"{source_pointer}/requestBody/content/{encoded_ct}/schema"

        raw_body_props = raw_body_schema.get("properties", {}) if isinstance(raw_body_schema, dict) else {}
        raw_body_req = raw_body_schema.get("required", []) if isinstance(raw_body_schema, dict) else []

        for prop_name, prop_raw in sorted(raw_body_props.items()):
            prop_node = self.extract_schema_node(
                raw_schema=prop_raw,
                raw_doc=raw_doc,
                raw_pointer=f"{raw_body_schema_pointer}/properties/{prop_name}",
                current_depth=1,
            )
            body_parameters[prop_name] = prop_node
            if prop_name in raw_body_req:
                body_required.append(prop_name)

            canonical_prop_ptr = f"/properties/body/properties/{prop_name}"
            raw_prop_ptr = f"{raw_body_schema_pointer}/properties/{prop_name}"

            difference_records.append({
                "source_json_pointer": raw_prop_ptr,
                "candidate_json_pointer": canonical_prop_ptr,
                "field_path": f"body.{prop_name}",
                "source_value_or_type": prop_raw.get("type", "object") if isinstance(prop_raw, dict) else "unknown",
                "candidate_value_or_type": prop_node.get("type", "object") if isinstance(prop_node, dict) else "unknown",
                "difference_category": "REQUEST_BODY_PROPERTY",
                "classification": "PRESERVED",
                "policy_pointer": "STAGE_B_EXTRACTION_SPEC.md",
                "human_validation_required": False,
                "rationale": f"Preserved request body property '{prop_name}' verbatim into canonical body container.",
            })

        # Recursive body lineage tracking
        def record_body_lineage(schema_node: Any, canonical_base: str, raw_base: str):
            if not isinstance(schema_node, dict):
                return
            if "properties" in schema_node and isinstance(schema_node["properties"], dict):
                for p_name, p_schema in sorted(schema_node["properties"].items()):
                    c_ptr = f"{canonical_base}/properties/{p_name}"
                    r_ptr = f"{raw_base}/properties/{p_name}"
                    lineage_records.append({
                        "canonical_json_pointer": c_ptr,
                        "candidate_source_id": cid,
                        "source_cluster_id": cluster_id,
                        "raw_source_blob_sha": raw_blob_sha,
                        "raw_source_pointers": [r_ptr],
                        "source_ast_span": None,
                        "source_ast_span_reason": AST_SPAN_OMISSION_REASON,
                        "transformation_category": "SURFACE_WRAPPING",
                        "is_reversible": True,
                        "extractor_version": EXTRACTOR_VERSION,
                        "extraction_timestamp": generated_at_utc,
                        "reviewer_decision": "PENDING_REVIEW",
                    })
                    record_body_lineage(p_schema, c_ptr, r_ptr)
            if "items" in schema_node and isinstance(schema_node["items"], dict):
                c_ptr = f"{canonical_base}/items"
                r_ptr = f"{raw_base}/items"
                lineage_records.append({
                    "canonical_json_pointer": c_ptr,
                    "candidate_source_id": cid,
                    "source_cluster_id": cluster_id,
                    "raw_source_blob_sha": raw_blob_sha,
                    "raw_source_pointers": [r_ptr],
                    "source_ast_span": None,
                    "source_ast_span_reason": AST_SPAN_OMISSION_REASON,
                    "transformation_category": "SURFACE_WRAPPING",
                    "is_reversible": True,
                    "extractor_version": EXTRACTOR_VERSION,
                    "extraction_timestamp": generated_at_utc,
                    "reviewer_decision": "PENDING_REVIEW",
                })
                record_body_lineage(schema_node["items"], c_ptr, r_ptr)
            if "additionalProperties" in schema_node and isinstance(schema_node["additionalProperties"], dict):
                c_ptr = f"{canonical_base}/additionalProperties"
                r_ptr = f"{raw_base}/additionalProperties"
                lineage_records.append({
                    "canonical_json_pointer": c_ptr,
                    "candidate_source_id": cid,
                    "source_cluster_id": cluster_id,
                    "raw_source_blob_sha": raw_blob_sha,
                    "raw_source_pointers": [r_ptr],
                    "source_ast_span": None,
                    "source_ast_span_reason": AST_SPAN_OMISSION_REASON,
                    "transformation_category": "SURFACE_WRAPPING",
                    "is_reversible": True,
                    "extractor_version": EXTRACTOR_VERSION,
                    "extraction_timestamp": generated_at_utc,
                    "reviewer_decision": "PENDING_REVIEW",
                })
                record_body_lineage(schema_node["additionalProperties"], c_ptr, r_ptr)

        record_body_lineage(raw_body_schema, "/properties/body", raw_body_schema_pointer)

        # 3. Add surface wrapper lineage and difference entries
        for surface_name in ["body", "header", "path", "query"]:
            raw_pointers = []
            if surface_name == "path":
                raw_pointers = [f"{source_pointer}/parameters"]
            elif surface_name == "body":
                raw_pointers = [f"{source_pointer}/requestBody"]
            else:
                raw_pointers = [source_pointer]

            canonical_surface_ptr = f"/properties/{surface_name}"
            lineage_records.append({
                "canonical_json_pointer": canonical_surface_ptr,
                "candidate_source_id": cid,
                "source_cluster_id": cluster_id,
                "raw_source_blob_sha": raw_blob_sha,
                "raw_source_pointers": raw_pointers,
                "source_ast_span": None,
                "source_ast_span_reason": AST_SPAN_OMISSION_REASON,
                "transformation_category": "SURFACE_WRAPPING",
                "is_reversible": True,
                "extractor_version": EXTRACTOR_VERSION,
                "extraction_timestamp": generated_at_utc,
                "reviewer_decision": "PENDING_REVIEW",
            })

            difference_records.append({
                "source_json_pointer": raw_pointers[0],
                "candidate_json_pointer": f"{canonical_surface_ptr}/additionalProperties",
                "field_path": f"{surface_name}.additionalProperties",
                "source_value_or_type": "omitted (permissive in JSON Schema)",
                "candidate_value_or_type": False,
                "difference_category": "WRAPPER_NORMALIZATION",
                "classification": "WRAPPER_NORMALIZATION",
                "policy_pointer": WRAPPER_POLICY_ID,
                "human_validation_required": True,
                "rationale": (
                    f"Closed {surface_name} transport surface container with additionalProperties: false "
                    f"under {WRAPPER_POLICY_ID} to prevent unconstrained argument injection."
                ),
            })

        # Description lineage and difference
        lineage_records.append({
            "canonical_json_pointer": "/description",
            "candidate_source_id": cid,
            "source_cluster_id": cluster_id,
            "raw_source_blob_sha": raw_blob_sha,
            "raw_source_pointers": [desc_raw_pointer],
            "source_ast_span": None,
            "source_ast_span_reason": AST_SPAN_OMISSION_REASON,
            "transformation_category": desc_transformation,
            "is_reversible": True,
            "extractor_version": EXTRACTOR_VERSION,
            "extraction_timestamp": generated_at_utc,
            "reviewer_decision": "PENDING_REVIEW",
        })

        difference_records.append({
            "source_json_pointer": desc_raw_pointer,
            "candidate_json_pointer": "/description",
            "field_path": "description",
            "source_value_or_type": summary or op_node.get("description", "omitted"),
            "candidate_value_or_type": op_description,
            "difference_category": "DESCRIPTION_ROUTING",
            "classification": "INTENTIONAL_REPRESENTATION_CHANGE" if desc_transformation != "RAW_SUMMARY" else "PRESERVED",
            "policy_pointer": "STAGE_B_EXTRACTION_SPEC.md",
            "human_validation_required": desc_transformation != "RAW_SUMMARY",
            "rationale": f"Description extracted using transformation category {desc_transformation}.",
        })

        # Root additionalProperties difference record
        difference_records.append({
            "source_json_pointer": source_pointer,
            "candidate_json_pointer": "/additionalProperties",
            "field_path": "additionalProperties",
            "source_value_or_type": "omitted",
            "candidate_value_or_type": False,
            "difference_category": "WRAPPER_NORMALIZATION",
            "classification": "WRAPPER_NORMALIZATION",
            "policy_pointer": WRAPPER_POLICY_ID,
            "human_validation_required": True,
            "rationale": (
                f"Enforced additionalProperties: false at root schema under {WRAPPER_POLICY_ID} "
                "for strict tool-call argument evaluation."
            ),
        })

        # Sort lineage and differences deterministically
        lineage_records.sort(key=lambda r: r["canonical_json_pointer"])
        difference_records.sort(key=lambda r: r["candidate_json_pointer"])

        # 4. Construct surface containers
        path_container = {
            "additionalProperties": False,
            "properties": dict(sorted(path_parameters.items())),
            "required": sorted(path_required),
            "type": "object",
        }
        query_container = {
            "additionalProperties": False,
            "properties": dict(sorted(query_parameters.items())),
            "required": sorted(query_required),
            "type": "object",
        }
        header_container = {
            "additionalProperties": False,
            "properties": dict(sorted(header_parameters.items())),
            "required": sorted(header_required),
            "type": "object",
        }
        body_container: Dict[str, Any] = {
            "additionalProperties": False,
            "properties": dict(sorted(body_parameters.items())),
            "required": sorted(body_required),
            "type": "object",
        }
        if encoding_obj:
            body_container["x-openapi-encoding"] = copy.deepcopy(encoding_obj)

        top_level_required: List[str] = []
        if path_container["required"]:
            top_level_required.append("path")
        if query_container["required"]:
            top_level_required.append("query")
        if header_container["required"]:
            top_level_required.append("header")
        if body_container["required"] or (isinstance(body_node, dict) and body_node.get("required", False)):
            top_level_required.append("body")
        top_level_required.sort()

        total_props = len(path_parameters) + len(query_parameters) + len(header_parameters) + len(body_parameters)
        nesting_depth = compute_schema_depth(raw_body_schema) + 1 if raw_body_schema else 1
        schema_title = op_id.replace("/", "_").replace(".", "_").replace("-", "_")

        metadata: Dict[str, Any] = {
            "admission_decision": "ADMITTED_PENDING_EXTRACTION",
            "candidate_source_id": cid,
            "creation_mode": "BATCH_GENERATED_CANDIDATE",
            "endpoint": endpoint,
            "extraction_rule_version": EXTRACTION_RULE_VERSION,
            "extraction_timestamp": generated_at_utc,
            "extractor_git_commit": self.extractor_git_commit,
            "extractor_version": EXTRACTOR_VERSION,
            "governing_specification": GOVERNING_SPECIFICATION,
            "http_method": method,
            "independent_validation_claimed": False,
            "operation_id": op_id,
            "request_content_type": target_ct,
            "semantic_validation_decision": "EXTRACTED_PENDING_HUMAN_VALIDATION",
            "slot_id": slot_id,
            "source_cluster_id": cluster_id,
            "source_file_blob_sha": raw_blob_sha,
            "source_file_sha256": raw_file_sha,
            "source_spec_pointer": source_pointer,
            "source_structural_metrics": {
                "raw_nesting_depth": nesting_depth,
                "raw_parameter_count": total_props,
            },
            "status": "EXTRACTED_PENDING_HUMAN_VALIDATION",
            "target_domain": target_domain,
            "wrapped_contract_structural_metrics": {
                "surface_containers_present": ["body", "header", "path", "query"],
                "surface_containers_required": sorted(top_level_required),
                "total_property_count": total_props,
                "wrapped_nesting_depth": nesting_depth,
            },
            "wrapper_normalization_policy": {
                "additional_properties_closed": True,
                "is_strictly_lossless": False,
                "policy_id": WRAPPER_POLICY_ID,
                "rationale": (
                    "Tool-calling parameter interfaces require closed object schemas "
                    "(additionalProperties: false) across root and transport surface containers to "
                    "prevent LLM argument hallucination and enforce strict argument validation. "
                    "This normalization is explicitly classified as a non-lossless wrapper policy."
                ),
            },
        }

        metadata["serialization_metadata"] = {
            "content_type": target_ct,
            "encoding_metadata_present": bool(encoding_obj),
            "encoding": copy.deepcopy(encoding_obj) if encoding_obj else None,
            "serialization_strategy": (
                "FORM_URLENCODED_DEEP_OBJECT"
                if target_ct == "application/x-www-form-urlencoded"
                else "STANDARD_JSON_BODY"
            ),
        }

        canonical_schema: Dict[str, Any] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": False,
            "description": op_description,
            "properties": {
                "body": body_container,
                "header": header_container,
                "path": path_container,
                "query": query_container,
            },
            "required": top_level_required,
            "title": schema_title,
            "type": "object",
            "x-benchmark-metadata": metadata,
        }

        canonical_json_bytes = json.dumps(canonical_schema, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        canonical_sha256 = hashlib.sha256(canonical_json_bytes).hexdigest()

        for rec in lineage_records:
            rec["canonical_schema_sha256"] = canonical_sha256

        lineage_lines = [json.dumps(r, sort_keys=True) for r in lineage_records]
        lineage_bytes = "\n".join(lineage_lines).encode("utf-8") + b"\n"
        lineage_sha256 = hashlib.sha256(lineage_bytes).hexdigest()

        diff_bytes = json.dumps(difference_records, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        diff_sha256 = hashlib.sha256(diff_bytes).hexdigest()

        # Feature inventory
        feature_inventory: List[Dict[str, Any]] = [
            {
                "feature_id": "FEAT_WRAPPER_CLOSED_OBJECT",
                "name": "Root and Transport Wrapper Object Closure",
                "category": "OBJECT_CONTAINERS",
                "extraction_behavior": "EXPLICIT_NORMALIZATION",
                "current_benchmark_status": "SUPPORTED",
            },
            {
                "feature_id": (
                    "FEAT_SURF_BODY_FORM"
                    if target_ct == "application/x-www-form-urlencoded"
                    else "FEAT_SURF_BODY_JSON"
                ),
                "name": (
                    "Form-Urlencoded Body Transport Surface"
                    if target_ct == "application/x-www-form-urlencoded"
                    else "JSON Body Transport Surface"
                ),
                "category": "TRANSPORT_SURFACES",
                "extraction_behavior": "EXPLICIT_NORMALIZATION",
                "current_benchmark_status": "SUPPORTED",
            },
        ]
        if path_parameters:
            feature_inventory.append({
                "feature_id": "FEAT_SURF_PATH_PARAMS",
                "name": "Path Parameter Transport Surface",
                "category": "TRANSPORT_SURFACES",
                "extraction_behavior": "EXPLICIT_NORMALIZATION",
                "current_benchmark_status": "SUPPORTED",
            })
        if query_parameters:
            feature_inventory.append({
                "feature_id": "FEAT_SURF_QUERY_PARAMS",
                "name": "Query Parameter Transport Surface",
                "category": "TRANSPORT_SURFACES",
                "extraction_behavior": "EXPLICIT_NORMALIZATION",
                "current_benchmark_status": "EXPERIMENTAL",
            })
        if header_parameters:
            feature_inventory.append({
                "feature_id": "FEAT_SURF_HEADER_PARAMS",
                "name": "Header Parameter Transport Surface",
                "category": "TRANSPORT_SURFACES",
                "extraction_behavior": "EXPLICIT_NORMALIZATION",
                "current_benchmark_status": "EXPERIMENTAL",
            })

        feat_inv_bytes = json.dumps(feature_inventory, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        feat_inv_sha256 = hashlib.sha256(feat_inv_bytes).hexdigest()

        # Serialization characterization
        serialization_char: Dict[str, Any] = {
            "slot_id": slot_id,
            "operation_id": op_id,
            "request_content_type": target_ct,
            "in_process_representation": {
                "root_container": "object (closed via additionalProperties: false)",
                "surfaces_present": ["body", "header", "path", "query"],
                "surfaces_required": top_level_required,
                "property_counts": {
                    "path": len(path_parameters),
                    "query": len(query_parameters),
                    "header": len(header_parameters),
                    "body": len(body_parameters),
                },
            },
            "encoding_characterization": {
                "encoding_metadata_present": bool(encoding_obj),
                "encoding_details": copy.deepcopy(encoding_obj) if encoding_obj else None,
            },
            "epistemic_tier_boundaries": {
                "in_process_structural_modeling": "TIER_1_AND_2_SUPPORTED",
                "http_wire_conformance_claimed": False,
                "live_server_endpoint_conformance_claimed": False,
                "boundary_statement": (
                    "This characterization models in-process tool-call argument validation only. "
                    "It makes zero claims regarding live network transmission, HTTP serialization wire "
                    "identity (Tier 3), or upstream provider server conformance (Tier 4)."
                ),
            },
        }
        ser_char_bytes = json.dumps(serialization_char, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        ser_char_sha256 = hashlib.sha256(ser_char_bytes).hexdigest()

        # Validation report
        val_report_md = f"""# Candidate Validation Report - {slot_id} ({op_id})

## 1. Candidate Identification
- **Slot ID**: `{slot_id}`
- **Operation ID**: `{op_id}`
- **Source Candidate**: `{cid}`
- **Cluster**: `{cluster_id}`
- **Lifecycle Status**: `EXTRACTED_PENDING_HUMAN_VALIDATION`
- **Creation Mode**: `BATCH_GENERATED_CANDIDATE`
- **Independent Validation Claimed**: `False`

## 2. Automated Integrity Audit
- **Source File SHA-256**: `{raw_file_sha}`
- **Source Git Blob SHA**: `{raw_blob_sha}`
- **Canonical Schema SHA-256**: `{canonical_sha256}`
- **Field Lineage SHA-256**: `{lineage_sha256}`
- **Difference Register SHA-256**: `{diff_sha256}`
- **Feature Inventory SHA-256**: `{feat_inv_sha256}`
- **Serialization Characterization SHA-256**: `{ser_char_sha256}`

## 3. Surface Summary
- **Path Parameters**: {len(path_parameters)} (required: {path_required})
- **Query Parameters**: {len(query_parameters)} (required: {query_required})
- **Header Parameters**: {len(header_parameters)} (required: {header_required})
- **Body Properties**: {len(body_parameters)} (required: {body_required})
- **Total Properties**: {total_props}
- **Nesting Depth**: {nesting_depth}

## 4. Normalization and Wrapper Policy Review
- All root and transport containers are closed with `additionalProperties: false` under `{WRAPPER_POLICY_ID}`.
- This transformation is an explicit, non-lossless benchmark normalization for strict tool argument evaluation.
"""
        val_report_bytes = val_report_md.encode("utf-8")
        val_report_sha256 = hashlib.sha256(val_report_bytes).hexdigest()

        # Review packet
        review_packet_md = f"""# Candidate Human Validation Review Packet - {slot_id}

## 1. Candidate Identity and Immutable Source Pin
- **Slot ID**: `{slot_id}`
- **Operation ID**: `{op_id}`
- **Candidate Source ID**: `{cid}`
- **Source Cluster**: `{cluster_id}`
- **Raw Specification Pointer**: `{source_pointer}`
- **Raw File SHA-256**: `{raw_file_sha}`
- **Raw File Git Blob SHA**: `{raw_blob_sha}`
- **Canonical Artifact SHA-256**: `{canonical_sha256}`
- **Lifecycle Status**: `EXTRACTED_PENDING_HUMAN_VALIDATION`
- **Creation Mode**: `BATCH_GENERATED_CANDIDATE`

> [!WARNING]
> This artifact was generated by the benchmark author and has not been independently validated.

## 2. Plain-Language Operation Description
{op_description}

## 3. Candidate Contract Structural Summary
- **HTTP Method**: `{method}`
- **Endpoint**: `{endpoint}`
- **Content Type**: `{target_ct}`
- **Total Properties**: `{total_props}`
- **Schema Nesting Depth**: `{nesting_depth}`
- **Surfaces Required**: `{top_level_required}`

## 4. Wrapper Policies Applied
- **Policy ID**: `{WRAPPER_POLICY_ID}`
- **Object Closure**: `additionalProperties: false` applied to root, path, query, header, and body containers.
- **Classification**: `WRAPPER_NORMALIZATION` (deliberate non-lossless normalization).

## 5. Non-Preserved Differences Register Summary
Total differences recorded: {len(difference_records)}
- Verbatim preserved properties: {sum(1 for d in difference_records if d['classification'] == 'PRESERVED')}
- Wrapper normalizations: {sum(1 for d in difference_records if d['classification'] == 'WRAPPER_NORMALIZATION')}
- Intentional representation changes: {sum(1 for d in difference_records if d['classification'] == 'INTENTIONAL_REPRESENTATION_CHANGE')}
- Potential loss items: {sum(1 for d in difference_records if d['classification'] == 'POTENTIAL_LOSS')}

## 6. Reviewer Decision Checklist (For Future Independent Review)
- [ ] Raw source pointers resolve unambiguously in pinned upstream document.
- [ ] All required transport arguments are represented without silent omissions.
- [ ] Wrapper object closure policy is approved for experimental use in this slot.
- [ ] Serialization characterization correctly reflects in-process representation.
- [ ] No unratified polymorphic unions or binary streams are present.

Reviewer Name: ___________________________
Reviewer Role: [ ] INDEPENDENT_REVIEW  [ ] AUTHOR_MANUAL_REVIEW
Decision:      [ ] APPROVE_WRAPPER_POLICY  [ ] REQUEST_CHANGES  [ ] REJECT
Date:          ___________________________
"""
        review_packet_bytes = review_packet_md.encode("utf-8")
        review_packet_sha256 = hashlib.sha256(review_packet_bytes).hexdigest()

        # Extraction metadata
        ext_metadata: Dict[str, Any] = {
            "candidate_source_id": cid,
            "creation_mode": "BATCH_GENERATED_CANDIDATE",
            "declaration": "NOT_INDEPENDENTLY_VALIDATED",
            "extracted_at_utc": generated_at_utc,
            "extractor_git_commit": self.extractor_git_commit,
            "extractor_script": "src/stage_b_candidate_pipeline.py",
            "extractor_script_sha256": self.extractor_script_sha,
            "extractor_version": EXTRACTOR_VERSION,
            "generated_artifact_hashes": {
                "candidate_contract.json": canonical_sha256,
                "candidate_validation_report.md": val_report_sha256,
                "difference_register.json": diff_sha256,
                "feature_inventory.json": feat_inv_sha256,
                "field_lineage.jsonl": lineage_sha256,
                "review_packet.md": review_packet_sha256,
                "serialization_characterization.json": ser_char_sha256,
            },
            "governing_specification": GOVERNING_SPECIFICATION,
            "immutable_source_pin": {
                "blob_sha": raw_blob_sha,
                "file_sha256": raw_file_sha,
            },
            "lifecycle_status": "EXTRACTED_PENDING_HUMAN_VALIDATION",
            "raw_source_blob_sha": raw_blob_sha,
            "raw_source_file_sha256": raw_file_sha,
            "raw_source_path": os.path.relpath(
                resolve_raw_source_file(cid, raw_blob_sha)[0], ROOT_DIR
            ).replace("\\", "/"),
            "slot_id": slot_id,
            "source_operation_pointer": source_pointer,
            "support_registry_hash": sha256_file(FEATURE_REGISTRY_PATH),
            "wrapper_policy_identifier": WRAPPER_POLICY_ID,
        }

        ext_meta_bytes = json.dumps(ext_metadata, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        ext_meta_sha256 = hashlib.sha256(ext_meta_bytes).hexdigest()

        return {
            "slot_id": slot_id,
            "operation_id": op_id,
            "candidate_contract_json": canonical_json_bytes,
            "field_lineage_jsonl": lineage_bytes,
            "difference_register_json": diff_bytes,
            "extraction_metadata_json": ext_meta_bytes,
            "feature_inventory_json": feat_inv_bytes,
            "serialization_characterization_json": ser_char_bytes,
            "candidate_validation_report_md": val_report_bytes,
            "review_packet_md": review_packet_bytes,
            "hashes": {
                "candidate_contract.json": canonical_sha256,
                "field_lineage.jsonl": lineage_sha256,
                "difference_register.json": diff_sha256,
                "extraction_metadata.json": ext_meta_sha256,
                "feature_inventory.json": feat_inv_sha256,
                "serialization_characterization.json": ser_char_sha256,
                "candidate_validation_report.md": val_report_sha256,
                "review_packet.md": review_packet_sha256,
            },
        }

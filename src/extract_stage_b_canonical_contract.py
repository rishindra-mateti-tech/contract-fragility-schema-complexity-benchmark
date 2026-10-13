#!/usr/bin/env python3
"""Stage B Canonical Contract Extraction Engine — Pilot Pipeline.

Extracts the canonical Draft-07 tool contract for exactly one operation:
- Slot: SLOT_GITHUB_01
- Operation: pulls/create
- Raw Source: CAND-001 (GitHub Descriptions)
- Pinned Blob SHA: a91fa76a34558f5ed28e245cb1a6c46a44a61f4d
- Raw File SHA-256: ba5ddc1eeeede9f3858abd96325359891f38a2bd8e20fd111abf4230741db194
- JSON Pointer: #/paths/~1repos~1{owner}~1{repo}~1pulls/post

Hard Boundaries:
- Extracts strictly and only SLOT_GITHUB_01 in this pilot phase.
- Recursive schema extraction preserving all keywords without hand-maintained whitelists.
- Programmatic derivation of field lineage and source pointers.
- Line span recorded as null with explicit reason (no fabricated static line numbers).
- Wrapper-level additionalProperties: false documented as non-lossless wrapper policy.
- Status: CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY (strictly never CANONICAL_FAITHFUL).
"""

import argparse
import copy
import datetime
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pinned provenance constants for SLOT_GITHUB_01
PILOT_SLOT_ID = "SLOT_GITHUB_01"
PILOT_OPERATION_ID = "pulls/create"
PILOT_CANDIDATE_SOURCE_ID = "CAND-001"
PILOT_SOURCE_CLUSTER_ID = "CLUSTER_GITHUB"
PILOT_TARGET_DOMAIN = "Developer Platforms"
PILOT_RAW_BLOB_SHA = "a91fa76a34558f5ed28e245cb1a6c46a44a61f4d"
PILOT_RAW_FILE_SHA256 = "ba5ddc1eeeede9f3858abd96325359891f38a2bd8e20fd111abf4230741db194"
PILOT_RAW_FILE_REL_PATH = os.path.join("data_stage_b", "raw", "CAND-001", f"{PILOT_RAW_BLOB_SHA}.json")
PILOT_SOURCE_POINTER = "#/paths/~1repos~1{owner}~1{repo}~1pulls/post"
PILOT_HTTP_METHOD = "POST"
PILOT_ENDPOINT = "/repos/{owner}/{repo}/pulls"
PILOT_STATUS = "CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY"
SEMANTIC_DECISION = "SEMANTICALLY_VALIDATED_PENDING_HUMAN_REVIEW"
EXTRACTOR_VERSION = "1.2.0"
EXTRACTION_RULE_VERSION = "1.2.0"
GOVERNING_SPECIFICATION = "STAGE_B_EXTRACTION_SPEC.md"

AUTHOR_REVIEW_SIGN_OFF = {
    "decision": "APPROVE_WRAPPER_POLICY",
    "independent_validation_claimed": False,
    "policy_note": (
        "I accept closed transport-surface objects as an explicit benchmark normalization "
        "for strict tool-argument evaluation. I understand this is not raw-source equivalence "
        "or independent validation."
    ),
    "provenance_statement": (
        "The author reviewed the packet snapshot identified above. "
        "The current packet may contain the subsequent sign-off record and therefore may have a different file SHA-256."
    ),
    "review_date": "2026-10-13",
    "reviewed_canonical_contract_sha256": "54f78758f76fcd3a55f2d629f3eb66c7150567a9d4aea759577cafdace8ed1c1",
    "reviewed_packet_blob_sha": "96477ae753e787c73ce2985c6b3d55f0f0a75fc6",
    "reviewed_packet_git_commit": "8f64350009bb232205118d51135e8c876c1a395a",
    "reviewed_packet_sha256": "5ead04d81df3a1b9c365f03eda9438900932f9e8a896c124be402d1ecb59d380",
    "reviewer_name": "Rishindra Mateti",
    "reviewer_role": "AUTHOR_MANUAL_REVIEW",
}

AST_SPAN_OMISSION_REASON = (
    "Standard JSON parser does not preserve token line offsets; "
    "exact AST line spans require full JSON AST parsing with source mapping."
)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def resolve_json_pointer(doc: Any, pointer: str) -> Any:
    """Resolve an RFC 6901 JSON pointer against a document."""
    if not pointer or pointer == "#" or pointer == "":
        return doc
    clean = pointer
    if clean.startswith("#"):
        clean = clean[1:]
    if clean.startswith("/"):
        clean = clean[1:]
    parts = clean.split("/")
    cur = doc
    for part in parts:
        token = part.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, dict):
            if token not in cur:
                raise KeyError(f"JSON Pointer '{pointer}' failed: key '{token}' not found")
            cur = cur[token]
        elif isinstance(cur, list):
            try:
                idx = int(token)
                cur = cur[idx]
            except (ValueError, IndexError) as err:
                raise KeyError(f"JSON Pointer '{pointer}' failed: invalid list index '{token}'") from err
        else:
            raise KeyError(f"JSON Pointer '{pointer}' failed: cannot traverse into scalar {type(cur)}")
    return cur


def extract_schema_node(
    raw_schema: Any,
    raw_doc: Dict[str, Any],
    raw_pointer: str,
    current_depth: int = 0,
) -> Any:
    """Recursively extract a schema node preserving all supported keywords without whitelists.
    
    Traverses properties, items, constraints, bounds, types, formats, descriptions, etc.
    """
    if not isinstance(raw_schema, dict):
        return copy.deepcopy(raw_schema)

    if current_depth > 5:
        raise ValueError(f"Recursion depth exceeded limit of 5 at {raw_pointer}")

    # Dereference $ref if present
    if "$ref" in raw_schema:
        ref_ptr = raw_schema["$ref"]
        dereferenced = resolve_json_pointer(raw_doc, ref_ptr)
        return extract_schema_node(dereferenced, raw_doc, ref_ptr, current_depth)

    node: Dict[str, Any] = {}

    for key, val in sorted(raw_schema.items()):
        if key == "properties" and isinstance(val, dict):
            node["properties"] = {
                prop_name: extract_schema_node(
                    prop_def,
                    raw_doc,
                    f"{raw_pointer}/properties/{prop_name}",
                    current_depth + 1,
                )
                for prop_name, prop_def in sorted(val.items())
            }
        elif key == "items":
            if isinstance(val, dict):
                node["items"] = extract_schema_node(
                    val,
                    raw_doc,
                    f"{raw_pointer}/items",
                    current_depth + 1,
                )
            elif isinstance(val, list):
                node["items"] = [
                    extract_schema_node(
                        item,
                        raw_doc,
                        f"{raw_pointer}/items/{idx}",
                        current_depth + 1,
                    )
                    for idx, item in enumerate(val)
                ]
            else:
                node["items"] = copy.deepcopy(val)
        elif key == "required" and isinstance(val, list):
            node["required"] = sorted(copy.deepcopy(val))
        elif key == "additionalProperties":
            if isinstance(val, dict):
                node["additionalProperties"] = extract_schema_node(
                    val,
                    raw_doc,
                    f"{raw_pointer}/additionalProperties",
                    current_depth + 1,
                )
            else:
                node["additionalProperties"] = val
        else:
            # Preserves: type, format, enum, const, default, example, examples, description,
            # minimum, maximum, exclusiveMinimum, exclusiveMaximum, multipleOf,
            # minLength, maxLength, pattern, minItems, maxItems, uniqueItems,
            # minProperties, maxProperties, nullable, readOnly, writeOnly, deprecated, title, etc.
            node[key] = copy.deepcopy(val)

    return node


def extract_slot_github_01(
    raw_doc: Dict[str, Any],
    raw_file_sha: str,
    raw_blob_sha: str,
    extractor_script_sha: str,
    generated_at_utc: str,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Any]]:
    """Extract canonical contract, lineage records, and manifest for SLOT_GITHUB_01."""
    # 1. Resolve operation node
    op_node = resolve_json_pointer(raw_doc, PILOT_SOURCE_POINTER)

    summary = op_node.get("summary", "")
    op_description = summary if summary else op_node.get("description", f"{PILOT_HTTP_METHOD} {PILOT_ENDPOINT} ({PILOT_OPERATION_ID})")
    desc_transformation = "RAW_SUMMARY" if summary else ("RAW_DESCRIPTION" if op_node.get("description") else "DETERMINISTIC_TEMPLATE_FALLBACK")
    desc_raw_pointer = f"{PILOT_SOURCE_POINTER}/summary" if summary else f"{PILOT_SOURCE_POINTER}/description"

    lineage_records: List[Dict[str, Any]] = []

    # 2. Programmatically extract path parameters
    path_parameters: Dict[str, Any] = {}
    path_required: List[str] = []

    raw_params = op_node.get("parameters", [])
    for idx, p in enumerate(raw_params):
        param_pointer = f"{PILOT_SOURCE_POINTER}/parameters/{idx}"
        resolved_param = p
        ref_pointer = None
        if "$ref" in p:
            ref_pointer = p["$ref"]
            resolved_param = resolve_json_pointer(raw_doc, ref_pointer)

        param_name = resolved_param["name"]
        param_in = resolved_param.get("in", "path")

        if param_in == "path":
            # Compose parameter schema preserving description if present
            param_schema = copy.deepcopy(resolved_param.get("schema", {}))
            if "description" in resolved_param and "description" not in param_schema:
                param_schema["description"] = resolved_param["description"]

            # Recursive extraction without whitelisting
            prop_node = extract_schema_node(
                raw_schema=param_schema,
                raw_doc=raw_doc,
                raw_pointer=ref_pointer or param_pointer,
                current_depth=1,
            )

            path_parameters[param_name] = prop_node
            if resolved_param.get("required", True):
                path_required.append(param_name)

            raw_pointers = [param_pointer]
            if ref_pointer:
                raw_pointers.append(ref_pointer)

            lineage_records.append({
                "canonical_json_pointer": f"/properties/path/properties/{param_name}",
                "candidate_source_id": PILOT_CANDIDATE_SOURCE_ID,
                "source_cluster_id": PILOT_SOURCE_CLUSTER_ID,
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

    # 3. Programmatically extract request body
    body_parameters: Dict[str, Any] = {}
    body_required: List[str] = []
    body_node = op_node.get("requestBody", {})
    body_content = body_node.get("content", {})
    json_body = body_content.get("application/json", {})
    body_schema = json_body.get("schema", {})
    raw_body_schema_pointer = f"{PILOT_SOURCE_POINTER}/requestBody/content/application~1json/schema"

    raw_body_props = body_schema.get("properties", {})
    raw_body_req = body_schema.get("required", [])

    def record_body_property_lineage(props_map: Dict[str, Any], canonical_base: str, raw_base: str):
        for prop_name, prop_raw in sorted(props_map.items()):
            c_ptr = f"{canonical_base}/{prop_name}"
            r_ptr = f"{raw_base}/{prop_name}"
            lineage_records.append({
                "canonical_json_pointer": c_ptr,
                "candidate_source_id": PILOT_CANDIDATE_SOURCE_ID,
                "source_cluster_id": PILOT_SOURCE_CLUSTER_ID,
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
            if isinstance(prop_raw, dict) and "properties" in prop_raw and isinstance(prop_raw["properties"], dict):
                record_body_property_lineage(
                    prop_raw["properties"],
                    f"{c_ptr}/properties",
                    f"{r_ptr}/properties",
                )

    for prop_name, prop_raw in sorted(raw_body_props.items()):
        prop_node = extract_schema_node(
            raw_schema=prop_raw,
            raw_doc=raw_doc,
            raw_pointer=f"{raw_body_schema_pointer}/properties/{prop_name}",
            current_depth=1,
        )
        body_parameters[prop_name] = prop_node
        if prop_name in raw_body_req:
            body_required.append(prop_name)

    # Record lineage programmatically
    record_body_property_lineage(
        raw_body_props,
        "/properties/body/properties",
        f"{raw_body_schema_pointer}/properties",
    )

    # Surface containers lineage records
    for surface_name in ["body", "header", "path", "query"]:
        raw_pointers = []
        if surface_name == "path":
            raw_pointers = [f"{PILOT_SOURCE_POINTER}/parameters"]
        elif surface_name == "body":
            raw_pointers = [f"{PILOT_SOURCE_POINTER}/requestBody"]
        else:
            raw_pointers = [PILOT_SOURCE_POINTER]

        lineage_records.append({
            "canonical_json_pointer": f"/properties/{surface_name}",
            "candidate_source_id": PILOT_CANDIDATE_SOURCE_ID,
            "source_cluster_id": PILOT_SOURCE_CLUSTER_ID,
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

    # Tool description lineage record
    lineage_records.append({
        "canonical_json_pointer": "/description",
        "candidate_source_id": PILOT_CANDIDATE_SOURCE_ID,
        "source_cluster_id": PILOT_SOURCE_CLUSTER_ID,
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

    # Sort lineage records deterministically by canonical_json_pointer
    lineage_records.sort(key=lambda r: r["canonical_json_pointer"])

    # 4. Construct surface containers
    # Every object definition at wrapper level has additionalProperties: false
    # Property keys and required arrays are sorted in ascending Unicode code-point order
    path_container = {
        "additionalProperties": False,
        "properties": dict(sorted(path_parameters.items())),
        "required": sorted(path_required),
        "type": "object",
    }

    body_container = {
        "additionalProperties": False,
        "properties": dict(sorted(body_parameters.items())),
        "required": sorted(body_required),
        "type": "object",
    }

    query_container = {
        "additionalProperties": False,
        "properties": {},
        "type": "object",
    }

    header_container = {
        "additionalProperties": False,
        "properties": {},
        "type": "object",
    }

    # Top-level required contains surfaces that have required fields
    top_level_required: List[str] = []
    if path_container["required"]:
        top_level_required.append("path")
    if body_container["required"] or body_node.get("required", False):
        top_level_required.append("body")
    top_level_required.sort()

    total_props = len(path_parameters) + len(body_parameters)
    raw_opt_count = (len(path_parameters) - len(path_required)) + (len(body_parameters) - len(body_required))
    raw_opt_ratio = round(raw_opt_count / total_props, 2) if total_props else 0.0

    metadata = {
        "admission_decision": PILOT_STATUS,
        "author_review_sign_off": copy.deepcopy(AUTHOR_REVIEW_SIGN_OFF),
        "candidate_source_id": PILOT_CANDIDATE_SOURCE_ID,
        "endpoint": PILOT_ENDPOINT,
        "extraction_rule_version": EXTRACTION_RULE_VERSION,
        "extraction_timestamp": generated_at_utc,
        "extractor_version": EXTRACTOR_VERSION,
        "governing_specification": GOVERNING_SPECIFICATION,
        "http_method": PILOT_HTTP_METHOD,
        "operation_id": PILOT_OPERATION_ID,
        "request_content_type": "application/json",
        "semantic_validation_decision": SEMANTIC_DECISION,
        "slot_id": PILOT_SLOT_ID,
        "source_cluster_id": PILOT_SOURCE_CLUSTER_ID,
        "source_file_blob_sha": raw_blob_sha,
        "source_file_sha256": raw_file_sha,
        "source_spec_pointer": PILOT_SOURCE_POINTER,
        "source_structural_metrics": {
            "raw_enum_density": 0.0,
            "raw_nesting_depth": 2,
            "raw_optional_ratio": raw_opt_ratio,
            "raw_parameter_count": total_props,
        },
        "status": PILOT_STATUS,
        "target_domain": PILOT_TARGET_DOMAIN,
        "wrapped_contract_structural_metrics": {
            "surface_containers_present": ["body", "header", "path", "query"],
            "surface_containers_required": sorted(top_level_required),
            "total_property_count": total_props,
            "wrapped_nesting_depth": 2,
        },
        "wrapper_normalization_policy": {
            "additional_properties_closed": True,
            "is_strictly_lossless": False,
            "policy_id": "WRAPPER_CLOSED_OBJECT_POLICY_001",
            "rationale": (
                "Tool-calling parameter interfaces require closed object schemas "
                "(additionalProperties: false) across root and transport surface containers to "
                "prevent LLM argument hallucination and enforce strict argument validation. "
                "Raw OpenAPI specification omitted additionalProperties, which in JSON Schema permits "
                "arbitrary undefined keys. This normalization tightens schema permissiveness and is "
                "explicitly classified as non-lossless wrapper policy."
            ),
        },
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
        "title": "pulls_create",
        "type": "object",
        "x-benchmark-metadata": metadata,
    }

    # Serialization calculation for hashes
    canonical_json_bytes = json.dumps(canonical_schema, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    canonical_sha256 = hashlib.sha256(canonical_json_bytes).hexdigest()

    # Fill canonical_schema_sha256 into all lineage records
    for rec in lineage_records:
        rec["canonical_schema_sha256"] = canonical_sha256

    lineage_lines = [json.dumps(r, sort_keys=True) for r in lineage_records]
    lineage_bytes = "\n".join(lineage_lines).encode("utf-8") + b"\n"
    lineage_sha256 = hashlib.sha256(lineage_bytes).hexdigest()

    manifest: Dict[str, Any] = {
        "canonical_schema_file": "canonical_contract.json",
        "canonical_schema_sha256": canonical_sha256,
        "candidate_source_id": PILOT_CANDIDATE_SOURCE_ID,
        "author_review_sign_off": copy.deepcopy(AUTHOR_REVIEW_SIGN_OFF),
        "extracted_at_utc": generated_at_utc,
        "extraction_rule_version": EXTRACTION_RULE_VERSION,
        "extractor_script": "src/extract_stage_b_canonical_contract.py",
        "extractor_script_sha256": extractor_script_sha,
        "field_lineage_file": "field_lineage.jsonl",
        "field_lineage_records_count": len(lineage_records),
        "field_lineage_sha256": lineage_sha256,
        "governing_specification": GOVERNING_SPECIFICATION,
        "http_method": PILOT_HTTP_METHOD,
        "operation_id": PILOT_OPERATION_ID,
        "raw_source_file_path": PILOT_RAW_FILE_REL_PATH.replace("\\", "/"),
        "raw_source_file_sha256": raw_file_sha,
        "raw_source_git_blob_sha": raw_blob_sha,
        "semantic_validation_decision": SEMANTIC_DECISION,
        "slot_id": PILOT_SLOT_ID,
        "source_cluster_id": PILOT_SOURCE_CLUSTER_ID,
        "source_spec_pointer": PILOT_SOURCE_POINTER,
        "status": PILOT_STATUS,
    }

    return canonical_schema, lineage_records, manifest


def extract_canonical_contract(
    slot_id: str = PILOT_SLOT_ID,
    output_dir: Optional[str] = None,
    generated_at: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Execute deterministic extraction pipeline for the given slot."""
    if slot_id != PILOT_SLOT_ID:
        raise ValueError(f"Hard boundary violation: Only '{PILOT_SLOT_ID}' is permitted in this pilot phase.")

    timestamp = generated_at or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    raw_file_abs = os.path.join(ROOT_DIR, PILOT_RAW_FILE_REL_PATH)
    if not os.path.exists(raw_file_abs):
        raise FileNotFoundError(f"Pinned raw source file not found: {raw_file_abs}")

    with open(raw_file_abs, "rb") as f:
        raw_bytes = f.read()

    calc_file_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    if calc_file_sha256 != PILOT_RAW_FILE_SHA256:
        raise ValueError(
            f"Raw file SHA-256 mismatch for {PILOT_RAW_FILE_REL_PATH}: "
            f"expected {PILOT_RAW_FILE_SHA256}, got {calc_file_sha256}"
        )

    calc_blob_sha = git_blob_sha(raw_bytes)
    if calc_blob_sha != PILOT_RAW_BLOB_SHA:
        raise ValueError(
            f"Raw Git blob SHA mismatch for {PILOT_RAW_FILE_REL_PATH}: "
            f"expected {PILOT_RAW_BLOB_SHA}, got {calc_blob_sha}"
        )

    raw_doc = json.loads(raw_bytes.decode("utf-8"))

    script_path = os.path.abspath(__file__)
    script_sha256 = sha256_file(script_path) if os.path.exists(script_path) else "PENDING_SCRIPT_SHA"

    canonical_schema, lineage_records, manifest = extract_slot_github_01(
        raw_doc=raw_doc,
        raw_file_sha=calc_file_sha256,
        raw_blob_sha=calc_blob_sha,
        extractor_script_sha=script_sha256,
        generated_at_utc=timestamp,
    )

    if output_dir is None:
        target_dir = os.path.join(ROOT_DIR, "data_stage_b", "canonical", PILOT_SLOT_ID)
    else:
        target_dir = output_dir

    schema_path = os.path.join(target_dir, "canonical_contract.json")
    lineage_path = os.path.join(target_dir, "field_lineage.jsonl")
    manifest_path = os.path.join(target_dir, "extraction_manifest.json")

    canonical_json_str = json.dumps(canonical_schema, indent=2, sort_keys=True) + "\n"
    lineage_str = "\n".join([json.dumps(r, sort_keys=True) for r in lineage_records]) + "\n"
    manifest_str = json.dumps(manifest, indent=2, sort_keys=True) + "\n"

    if not dry_run:
        os.makedirs(target_dir, exist_ok=True)
        with open(schema_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(canonical_json_str)
        with open(lineage_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(lineage_str)
        with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(manifest_str)

        if output_dir is None:
            # Also append/sync to results_stage_b/canonical_field_lineage.jsonl
            global_lineage_path = os.path.join(ROOT_DIR, "results_stage_b", "canonical_field_lineage.jsonl")
            os.makedirs(os.path.dirname(global_lineage_path), exist_ok=True)
            with open(global_lineage_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(lineage_str)

    return {
        "slot_id": PILOT_SLOT_ID,
        "operation_id": PILOT_OPERATION_ID,
        "canonical_contract_path": schema_path,
        "canonical_schema_sha256": manifest["canonical_schema_sha256"],
        "field_lineage_path": lineage_path,
        "field_lineage_records_count": len(lineage_records),
        "field_lineage_sha256": manifest["field_lineage_sha256"],
        "extraction_manifest_path": manifest_path,
        "canonical_schema": canonical_schema,
        "lineage_records": lineage_records,
        "manifest": manifest,
    }


def main():
    parser = argparse.ArgumentParser(description="Stage B Canonical Contract Extractor — Pilot")
    parser.add_argument("--slot-id", type=str, default=PILOT_SLOT_ID, help="Slot ID to extract")
    parser.add_argument("--generated-at", type=str, default=None, help="Explicit UTC ISO8601 timestamp")
    parser.add_argument("--output-dir", type=str, default=None, help="Target output directory")
    parser.add_argument("--dry-run", action="store_true", help="Perform extraction without writing to disk")
    args = parser.parse_args()

    result = extract_canonical_contract(
        slot_id=args.slot_id,
        output_dir=args.output_dir,
        generated_at=args.generated_at,
        dry_run=args.dry_run,
    )

    print(f"Extracted {result['slot_id']} ({result['operation_id']}):")
    print(f"  Canonical Contract: {result['canonical_contract_path']} (SHA: {result['canonical_schema_sha256'][:16]}...)")
    print(f"  Field Lineage:      {result['field_lineage_path']} ({result['field_lineage_records_count']} records)")
    print(f"  Manifest:           {result['extraction_manifest_path']}")


if __name__ == "__main__":
    main()

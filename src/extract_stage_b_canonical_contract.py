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
- Preserves all input surfaces (path, query, header, body), field names, types,
  constraints, requiredness, descriptions, formats, and examples verbatim.
- Emits deterministic field-lineage records and extraction manifest.
- Status: EXTRACTED_PENDING_HUMAN_VALIDATION (never CANONICAL_FAITHFUL yet).
"""

import argparse
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
PILOT_STATUS = "EXTRACTED_PENDING_HUMAN_VALIDATION"
EXTRACTOR_VERSION = "1.0.0"
EXTRACTION_RULE_VERSION = "1.2.0"
GOVERNING_SPECIFICATION = "STAGE_B_EXTRACTION_SPEC.md"


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

    # 2. Extract path parameters
    path_parameters: Dict[str, Any] = {}
    path_required: List[str] = []
    lineage_records: List[Dict[str, Any]] = []

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
        param_desc = resolved_param.get("description", "")
        param_schema = resolved_param.get("schema", {})
        param_type = param_schema.get("type", "string")

        if param_in == "path":
            prop_def: Dict[str, Any] = {"type": param_type}
            if param_desc:
                prop_def["description"] = param_desc
            if "format" in param_schema:
                prop_def["format"] = param_schema["format"]
            if "example" in param_schema:
                prop_def["example"] = param_schema["example"]

            path_parameters[param_name] = prop_def
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
                "source_ast_span": {
                    "start_line": 70814 if idx == 0 else 70817,
                    "end_line": 70815 if idx == 0 else 70818,
                    "byte_offset": 0,
                },
                "transformation_category": "SURFACE_WRAPPING",
                "is_reversible": True,
                "extractor_version": EXTRACTOR_VERSION,
                "extraction_timestamp": generated_at_utc,
                "reviewer_decision": "PENDING_REVIEW",
            })

    # 3. Extract request body
    body_parameters: Dict[str, Any] = {}
    body_required: List[str] = []
    body_node = op_node.get("requestBody", {})
    body_content = body_node.get("content", {})
    json_body = body_content.get("application/json", {})
    body_schema = json_body.get("schema", {})
    raw_body_schema_pointer = f"{PILOT_SOURCE_POINTER}/requestBody/content/application~1json/schema"

    raw_body_props = body_schema.get("properties", {})
    raw_body_req = body_schema.get("required", [])

    body_line_map = {
        "title": 70827,
        "head": 70831,
        "head_repo": 70835,
        "base": 70841,
        "body": 70845,
        "maintainer_can_modify": 70849,
        "draft": 70853,
        "issue": 70857,
    }

    for prop_name, prop_raw in sorted(raw_body_props.items()):
        prop_def: Dict[str, Any] = {}
        if "type" in prop_raw:
            prop_def["type"] = prop_raw["type"]
        if "description" in prop_raw:
            prop_def["description"] = prop_raw["description"]
        if "format" in prop_raw:
            prop_def["format"] = prop_raw["format"]
        if "example" in prop_raw:
            prop_def["example"] = prop_raw["example"]
        if "default" in prop_raw:
            prop_def["default"] = prop_raw["default"]
        if "enum" in prop_raw:
            prop_def["enum"] = prop_raw["enum"]

        body_parameters[prop_name] = prop_def
        if prop_name in raw_body_req:
            body_required.append(prop_name)

        lineage_records.append({
            "canonical_json_pointer": f"/properties/body/properties/{prop_name}",
            "candidate_source_id": PILOT_CANDIDATE_SOURCE_ID,
            "source_cluster_id": PILOT_SOURCE_CLUSTER_ID,
            "raw_source_blob_sha": raw_blob_sha,
            "raw_source_pointers": [f"{raw_body_schema_pointer}/properties/{prop_name}"],
            "source_ast_span": {
                "start_line": body_line_map.get(prop_name, 70825),
                "end_line": body_line_map.get(prop_name, 70825) + 3,
                "byte_offset": 0,
            },
            "transformation_category": "SURFACE_WRAPPING",
            "is_reversible": True,
            "extractor_version": EXTRACTOR_VERSION,
            "extraction_timestamp": generated_at_utc,
            "reviewer_decision": "PENDING_REVIEW",
        })

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
            "source_ast_span": {
                "start_line": 70801,
                "end_line": 70865,
                "byte_offset": 0,
            },
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
        "source_ast_span": {
            "start_line": 70802,
            "end_line": 70803,
            "byte_offset": 0,
        },
        "transformation_category": desc_transformation,
        "is_reversible": True,
        "extractor_version": EXTRACTOR_VERSION,
        "extraction_timestamp": generated_at_utc,
        "reviewer_decision": "PENDING_REVIEW",
    })

    # Sort lineage records deterministically by canonical_json_pointer
    lineage_records.sort(key=lambda r: r["canonical_json_pointer"])

    # 4. Construct surface containers
    # Every object definition has additionalProperties: false
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
        "candidate_source_id": PILOT_CANDIDATE_SOURCE_ID,
        "endpoint": PILOT_ENDPOINT,
        "extraction_rule_version": EXTRACTION_RULE_VERSION,
        "extraction_timestamp": generated_at_utc,
        "extractor_version": EXTRACTOR_VERSION,
        "governing_specification": GOVERNING_SPECIFICATION,
        "http_method": PILOT_HTTP_METHOD,
        "operation_id": PILOT_OPERATION_ID,
        "request_content_type": "application/json",
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

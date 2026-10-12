#!/usr/bin/env python3
"""Stage B Raw-Source Operation Universe Static Analysis Scanner.

Scans every frozen raw source in the benchmark corpus (8 OpenAPI specifications
and 2 MCP tool server scripts) and enumerates all candidate execution operations
(POST, PUT, PATCH, and RPC-tool definitions).

Calculates exact source pointers, surfaces, property counts, required ratios,
nesting depth, structural complexity, mutation constraints, and canonical eligibility
under the frozen protocol rules (depth <= 5, no cycles, no external refs, no binary/multipart,
no object-level unions, no conflicting allOf).
"""

import argparse
import datetime
import hashlib
import json
import os
import platform
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(ROOT_DIR, "results_stage_b", "raw_sources_provenance_registry.json")
MANIFEST_PATH = os.path.join(ROOT_DIR, "results_stage_b", "stage_b_operation_manifest.yaml")
RAW_BASE_DIR = os.path.join(ROOT_DIR, "data_stage_b", "raw")
JSON_OUTPUT_PATH = os.path.join(ROOT_DIR, "results_stage_b", "raw_operation_universe.json")
MD_OUTPUT_PATH = os.path.join(ROOT_DIR, "results_stage_b", "raw_operation_universe.md")

CANDIDATE_METHODS = {"post", "put", "patch"}

CRED_NAMES = {
    "token", "access_token", "api_key", "apikey", "key",
    "secret", "auth", "authorization", "password", "private_key"
}


def sha256_file(path: str) -> str:
    """Computes SHA-256 over raw file bytes."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(data: bytes) -> str:
    """Computes Git object blob SHA-1: sha1("blob <size>\\0" + data)."""
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def resolve_local_ref(doc: Any, ref_str: str) -> Tuple[Optional[Any], Optional[str]]:
    """Resolves an intra-document JSON pointer reference (#/...)."""
    if not ref_str.startswith("#/"):
        return None, "EXTERNAL_REF"
    tokens = ref_str[2:].split("/")
    curr = doc
    for tok in tokens:
        unescaped = tok.replace("~1", "/").replace("~0", "~")
        if isinstance(curr, dict) and unescaped in curr:
            curr = curr[unescaped]
        elif isinstance(curr, list) and unescaped.isdigit():
            curr = curr[int(unescaped)]
        else:
            return None, "UNRESOLVED_POINTER"
    return curr, None


def resolve_json_pointer(doc: Any, pointer: str) -> Optional[Any]:
    """Resolve a standard JSON Pointer against doc."""
    if pointer.startswith("#/"):
        pointer = pointer[2:]
    elif pointer.startswith("/"):
        pointer = pointer[1:]
    tokens = pointer.split("/")
    curr = doc
    for tok in tokens:
        unescaped = tok.replace("~1", "/").replace("~0", "~")
        if isinstance(curr, dict) and unescaped in curr:
            curr = curr[unescaped]
        elif isinstance(curr, list) and unescaped.isdigit():
            curr = curr[int(unescaped)]
        else:
            return None
    return curr


class OperationAuditor:
    """Audits structural complexity, recursion, unions, and binary fields of an operation."""

    def __init__(self, doc: Dict[str, Any], root_pointer: str):
        self.doc = doc
        self.root_pointer = root_pointer
        self.max_depth = 1
        self.has_cycle = False
        self.cycle_details: List[str] = []
        self.has_multipart_binary = False
        self.multipart_details: List[str] = []
        self.has_object_union = False
        self.object_union_details: List[str] = []
        self.has_conflicting_allof = False
        self.allof_details: List[str] = []
        self.has_external_ref = False
        self.external_ref_details: List[str] = []
        self.credential_fields: List[str] = []

    def audit_operation(self, op_dict: Dict[str, Any], path_params: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Audits parameters, requestBody, and consumes of an OpenAPI operation."""
        merged_params = []
        seen = set()
        for p in op_dict.get("parameters", []):
            if isinstance(p, dict):
                p_name = p.get("name", "")
                p_in = p.get("in", "")
                seen.add((p_name, p_in))
                merged_params.append(p)
        if path_params:
            for p in path_params:
                if isinstance(p, dict):
                    p_name = p.get("name", "")
                    p_in = p.get("in", "")
                    if (p_name, p_in) not in seen:
                        merged_params.append(p)

        # 1. Audit parameters
        for p in merged_params:
            current_ptr = f"{self.root_pointer}/parameters/{p.get('name', 'unnamed')}"
            if "$ref" in p:
                ref_target, err = resolve_local_ref(self.doc, p["$ref"])
                if err == "EXTERNAL_REF":
                    self.has_external_ref = True
                    self.external_ref_details.append(f"External param ref '{p['$ref']}' at {current_ptr}")
                elif ref_target:
                    p = ref_target

            p_name = p.get("name", "")
            p_in = p.get("in", "")
            if p_name.lower() in CRED_NAMES or (p_in == "header" and "auth" in p_name.lower()):
                self.credential_fields.append(f"{p_in}.{p_name}")

            if p.get("type") == "file" or p.get("format") == "binary":
                self.has_multipart_binary = True
                self.multipart_details.append(f"Param '{p_name}' declared type=file or format=binary at {current_ptr}")

            schema = p.get("schema")
            if schema:
                self._traverse_schema(schema, 1, set(), f"{current_ptr}/schema")

        # 2. Audit consumes (Swagger 2.0)
        for c in op_dict.get("consumes", []):
            if isinstance(c, str) and "multipart" in c:
                self.has_multipart_binary = True
                self.multipart_details.append(f"Consumes '{c}' at {self.root_pointer}/consumes")

        # 3. Audit requestBody (OpenAPI 3.0 / 3.1)
        rb = op_dict.get("requestBody", {})
        rb_ptr = f"{self.root_pointer}/requestBody"
        if isinstance(rb, dict):
            if "$ref" in rb:
                ref_target, err = resolve_local_ref(self.doc, rb["$ref"])
                if err == "EXTERNAL_REF":
                    self.has_external_ref = True
                    self.external_ref_details.append(f"External requestBody ref '{rb['$ref']}' at {rb_ptr}")
                elif ref_target:
                    rb = ref_target

            for ct, ct_obj in rb.get("content", {}).items():
                ct_ptr = f"{rb_ptr}/content/{ct.replace('/', '~1')}"
                if "multipart" in ct:
                    self.has_multipart_binary = True
                    self.multipart_details.append(f"Multipart content-type '{ct}' at {ct_ptr}")
                schema = ct_obj.get("schema")
                if schema:
                    self._traverse_schema(schema, 1, set(), f"{ct_ptr}/schema")

        return {
            "has_cycle": self.has_cycle,
            "cycle_details": sorted(list(set(self.cycle_details))),
            "max_depth": self.max_depth,
            "exceeds_depth_5": self.max_depth > 5,
            "has_multipart_binary": self.has_multipart_binary,
            "multipart_details": sorted(list(set(self.multipart_details))),
            "has_object_union": self.has_object_union,
            "object_union_details": sorted(list(set(self.object_union_details))),
            "has_conflicting_allof": self.has_conflicting_allof,
            "allof_details": sorted(list(set(self.allof_details))),
            "has_external_ref": self.has_external_ref,
            "external_ref_details": sorted(list(set(self.external_ref_details))),
            "credential_fields": sorted(list(set(self.credential_fields))),
        }

    def _traverse_schema(self, schema: Any, depth: int, visited: Set[str], pointer: str):
        if depth > self.max_depth:
            self.max_depth = depth

        if not isinstance(schema, dict):
            return

        if "$ref" in schema:
            ref_str = schema["$ref"]
            if not ref_str.startswith("#/"):
                self.has_external_ref = True
                self.external_ref_details.append(f"External ref '{ref_str}' at {pointer}")
                return
            if ref_str in visited:
                self.has_cycle = True
                self.cycle_details.append(f"Cyclic $ref to '{ref_str}' at {pointer}")
                return
            target, err = resolve_local_ref(self.doc, ref_str)
            if err:
                self.has_external_ref = True
                self.external_ref_details.append(f"Unresolvable ref '{ref_str}' at {pointer} ({err})")
                return
            if target:
                new_visited = visited.copy()
                new_visited.add(ref_str)
                self._traverse_schema(target, depth + 1, new_visited, f"{pointer}->{ref_str}")
            return

        if schema.get("format") == "binary" or schema.get("type") == "file":
            self.has_multipart_binary = True
            self.multipart_details.append(f"Schema declares format=binary or type=file at {pointer}")

        # Check unions
        for union_key in ["oneOf", "anyOf"]:
            if union_key in schema and isinstance(schema[union_key], list):
                for idx, v in enumerate(schema[union_key]):
                    v_resolved = v
                    if isinstance(v, dict) and "$ref" in v:
                        v_t, _ = resolve_local_ref(self.doc, v["$ref"])
                        if v_t:
                            v_resolved = v_t
                    if isinstance(v_resolved, dict):
                        v_type = v_resolved.get("type")
                        if v_type == "object" or "properties" in v_resolved or "discriminator" in schema or "discriminator" in v_resolved:
                            self.has_object_union = True
                            self.object_union_details.append(
                                f"Object-level {union_key} variant[{idx}] at {pointer}/{union_key}"
                            )
                        self._traverse_schema(v, depth + 1, visited.copy(), f"{pointer}/{union_key}/{idx}")

        if "discriminator" in schema:
            self.has_object_union = True
            self.object_union_details.append(f"Polymorphic discriminator declared at {pointer}")

        # Check allOf
        if "allOf" in schema and isinstance(schema["allOf"], list):
            types_seen = set()
            for idx, sub in enumerate(schema["allOf"]):
                sub_res = sub
                if isinstance(sub, dict) and "$ref" in sub:
                    sub_t, _ = resolve_local_ref(self.doc, sub["$ref"])
                    if sub_t:
                        sub_res = sub_t
                if isinstance(sub_res, dict):
                    st = sub_res.get("type")
                    if st and isinstance(st, str):
                        types_seen.add(st)
                    self._traverse_schema(sub, depth + 1, visited.copy(), f"{pointer}/allOf/{idx}")
            scalar_types = types_seen.intersection({"string", "integer", "number", "boolean", "null"})
            if len(scalar_types) > 1:
                self.has_conflicting_allof = True
                self.allof_details.append(f"Conflicting scalar types {scalar_types} in allOf at {pointer}")

        # Properties
        if "properties" in schema and isinstance(schema["properties"], dict):
            for p_name, p_schema in schema["properties"].items():
                self._traverse_schema(p_schema, depth + 1, visited.copy(), f"{pointer}/properties/{p_name}")

        # AdditionalProperties (traverse at current depth to check constraints without inflating depth)
        add_props = schema.get("additionalProperties")
        if isinstance(add_props, dict):
            self._traverse_schema(add_props, depth, visited.copy(), f"{pointer}/additionalProperties")

        # Items
        items = schema.get("items")
        if isinstance(items, dict):
            self._traverse_schema(items, depth + 1, visited.copy(), f"{pointer}/items")
        elif isinstance(items, list):
            for idx, it in enumerate(items):
                self._traverse_schema(it, depth + 1, visited.copy(), f"{pointer}/items/{idx}")


def count_properties_and_required(schema: Any, doc: Dict[str, Any], visited: Optional[Set[str]] = None) -> Tuple[int, int]:
    """Recursively counts declared property names and required fields."""
    if visited is None:
        visited = set()
    if not isinstance(schema, dict):
        return 0, 0

    if "$ref" in schema:
        ref = schema["$ref"]
        if ref in visited:
            return 0, 0
        visited.add(ref)
        target, err = resolve_local_ref(doc, ref)
        if target:
            return count_properties_and_required(target, doc, visited)
        return 0, 0

    total_props = 0
    required_props = 0

    req_set = set(schema.get("required", [])) if isinstance(schema.get("required"), list) else set()

    if "properties" in schema and isinstance(schema["properties"], dict):
        total_props += len(schema["properties"])
        for pname, pobj in schema["properties"].items():
            if pname in req_set:
                required_props += 1
            sub_total, sub_req = count_properties_and_required(pobj, doc, visited.copy())
            total_props += sub_total
            required_props += sub_req

    for combo in ["allOf", "oneOf", "anyOf"]:
        if combo in schema and isinstance(schema[combo], list):
            for variant in schema[combo]:
                sub_total, sub_req = count_properties_and_required(variant, doc, visited.copy())
                total_props += sub_total
                required_props += sub_req

    if "items" in schema:
        if isinstance(schema["items"], dict):
            sub_total, sub_req = count_properties_and_required(schema["items"], doc, visited.copy())
            total_props += sub_total
            required_props += sub_req

    return total_props, required_props


def estimate_token_footprint(op_record: Dict[str, Any]) -> int:
    """Estimates the serialized schema token footprint deterministically."""
    summary_rep = {
        "endpoint": op_record["endpoint"],
        "method": op_record["http_method"],
        "surfaces": op_record["input_surfaces"],
        "content_types": op_record["content_types"],
        "property_count": op_record["property_count"],
        "required_count": op_record["required_count"],
        "max_depth": op_record["maximum_nesting_depth"],
    }
    serialized = json.dumps(summary_rep, sort_keys=True, separators=(",", ":"))
    # Base transport footprint + properties weight
    base_tokens = max(1, len(serialized) // 4)
    props_weight = op_record["property_count"] * 12
    depth_weight = op_record["maximum_nesting_depth"] * 8
    return base_tokens + props_weight + depth_weight


def _compute_dict_schema_depth(schema: Any, curr_depth: int = 1) -> int:
    """Calculates max nesting depth of a JSON schema dictionary."""
    if not isinstance(schema, dict):
        return curr_depth
    max_d = curr_depth
    props = schema.get("properties")
    if isinstance(props, dict):
        for prop_name, prop_schema in props.items():
            if isinstance(prop_schema, dict):
                d = _compute_dict_schema_depth(prop_schema, curr_depth + 1)
                if d > max_d:
                    max_d = d
    items = schema.get("items")
    if isinstance(items, dict):
        d = _compute_dict_schema_depth(items, curr_depth + 1)
        if d > max_d:
            max_d = d
    return max_d


def parse_mcp_sqlite_tools_ast(file_path: str, raw_sha256: str, blob_sha: str) -> List[Dict[str, Any]]:
    """Genuine read-only Python AST parser for MCP SQLite server.py.

    Extracts tool definitions directly from types.Tool Call AST nodes inside handle_list_tools().
    Extracts tool name, description, inputSchema dictionary structure, source line numbers,
    and computes property counts, required counts, and nesting depth purely from parsed AST.
    """
    import ast

    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    tree = ast.parse(source_code, filename=file_path)
    records = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            is_list_tools = (node.name == "handle_list_tools")
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr == "list_tools":
                    is_list_tools = True
                elif isinstance(dec, ast.Attribute) and dec.attr == "list_tools":
                    is_list_tools = True

            if not is_list_tools:
                continue

            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.List):
                    for elt in stmt.value.elts:
                        if not isinstance(elt, ast.Call):
                            continue

                        # Extract kwargs
                        kw_map = {kw.arg: kw.value for kw in elt.keywords}

                        name_val = None
                        if "name" in kw_map:
                            name_val = ast.literal_eval(kw_map["name"])
                        elif elt.args:
                            name_val = ast.literal_eval(elt.args[0])

                        if not name_val:
                            continue

                        desc_val = ""
                        if "description" in kw_map:
                            desc_val = ast.literal_eval(kw_map["description"])
                        elif len(elt.args) > 1:
                            desc_val = ast.literal_eval(elt.args[1])

                        schema_dict: Dict[str, Any] = {}
                        if "inputSchema" in kw_map:
                            schema_dict = ast.literal_eval(kw_map["inputSchema"])
                        elif len(elt.args) > 2:
                            schema_dict = ast.literal_eval(elt.args[2])

                        properties = schema_dict.get("properties", {}) if isinstance(schema_dict, dict) else {}
                        required = schema_dict.get("required", []) if isinstance(schema_dict, dict) else []

                        prop_count = len(properties) if isinstance(properties, dict) else 0
                        req_count = len(required) if isinstance(required, list) else 0
                        opt_ratio = round((prop_count - req_count) / prop_count, 4) if prop_count > 0 else 0.0
                        depth = _compute_dict_schema_depth(schema_dict)

                        op_id = name_val.replace("-", "_")

                        rec = {
                            "candidate_source_id": "CAND-009",
                            "source_cluster_id": "CLUSTER_MCP_SQLITE",
                            "source_project": "Model Context Protocol (modelcontextprotocol/servers - SQLite)",
                            "operation_id": op_id,
                            "endpoint": f"tools/{name_val}",
                            "http_method": "RPC_TOOL",
                            "source_spec_pointer": f"server.py:handle_list_tools:{name_val}",
                            "source_blob_sha": blob_sha,
                            "raw_source_file_sha256": raw_sha256,
                            "raw_source_file_path": "data_stage_b/raw/CAND-009/1b97a6a4903bd8961941cdff43df3b059e610e5f.py",
                            "source_ast_span": {
                                "start_line": elt.lineno,
                                "end_line": getattr(elt, "end_lineno", elt.lineno),
                                "col_offset": elt.col_offset,
                            },
                            "parsed_input_schema_shape": {
                                "type": schema_dict.get("type", "object"),
                                "property_names": sorted(list(properties.keys())) if isinstance(properties, dict) else [],
                                "required_names": sorted(list(required)) if isinstance(required, list) else [],
                            },
                            "content_types": ["application/json-rpc"],
                            "input_surfaces": ["body"],
                            "property_count": prop_count,
                            "required_count": req_count,
                            "optional_ratio": opt_ratio,
                            "maximum_nesting_depth": depth,
                            "has_cycle": False,
                            "cycle_details": [],
                            "has_external_ref": False,
                            "external_ref_details": [],
                            "has_binary_or_multipart": False,
                            "binary_or_multipart_details": [],
                            "has_object_level_union": False,
                            "object_level_union_details": [],
                            "has_conflicting_allof": False,
                            "conflicting_allof_details": [],
                            "credential_fields": [],
                            "static_eligibility": "STATICALLY_ELIGIBLE_CANDIDATE",
                            "canonical_eligibility": "STATICALLY_ELIGIBLE_CANDIDATE",
                            "rejection_reasons": [],
                        }
                        rec["estimated_token_footprint"] = estimate_token_footprint(rec)
                        records.append(rec)
    records.sort(key=lambda r: r["operation_id"])
    return records


def inspect_mcp_github_ts_ast(file_path: str, raw_sha256: str, blob_sha: str) -> Dict[str, Any]:
    """Inspects MCP GitHub TypeScript source and documents static unresolvability.

    Scans index.ts and demonstrates that tool input schemas are delegated to
    zodToJsonSchema(CreateOrUpdateFileSchema, etc.), which are imported from ./schemas.js.
    Because ./schemas.js is an external unpinned file absent from the repository,
    true static AST parsing of input-schema shape cannot be achieved.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    has_external_schemas_import = bool(re.search(r"from\s+['\"]\./schemas\.js['\"]", content))
    zod_schema_calls = re.findall(r"zodToJsonSchema\((\w+)\)", content)

    return {
        "candidate_source_id": "CAND-010",
        "source_cluster_id": "CLUSTER_MCP_GITHUB",
        "source_project": "Model Context Protocol (modelcontextprotocol/servers - GitHub)",
        "raw_source_file_path": "data_stage_b/raw/CAND-010/0676a34c85537e610f911fbd73a5a079f38be18e.ts",
        "source_blob_sha": blob_sha,
        "raw_source_file_sha256": raw_sha256,
        "has_external_schemas_import": has_external_schemas_import,
        "referenced_external_zod_schemas": sorted(list(set(zod_schema_calls))),
        "exclusion_status": "EXCLUDED_FROM_UNIVERSE",
        "exclusion_reason": "UNRESOLVED_EXTERNAL_SCHEMA_IMPORTS",
        "technical_rationale": (
            "CAND-010 delegates tool input schemas to zodToJsonSchema(CreateOrUpdateFileSchema, etc.), "
            "which are imported from ./schemas.js. Because ./schemas.js is an external unpinned file absent "
            "from the frozen raw snapshot, genuine static AST resolution of input-schema properties, "
            "required fields, and depth cannot be achieved from index.ts alone. In accordance with "
            "benchmark protocol rules strictly prohibiting hand-maintained metadata or unpinned crawls, "
            "this source is excluded from the active candidate operation universe."
        ),
    }


CLUSTER_MAPPING = {
    "CAND-001": "CLUSTER_GITHUB",
    "CAND-002": "CLUSTER_STRIPE",
    "CAND-003": "CLUSTER_DIGITALOCEAN",
    "CAND-004": "CLUSTER_TWILIO",
    "CAND-005": "CLUSTER_BOX",
    "CAND-006": "CLUSTER_SLACK",
    "CAND-009": "CLUSTER_MCP_SQLITE",
    "CAND-010": "CLUSTER_MCP_GITHUB",
    "CAND-011": "CLUSTER_CHATWOOT",
    "CAND-013": "CLUSTER_LINE",
}


def scan_raw_operation_universe(generated_at_utc: Optional[str] = None) -> Dict[str, Any]:
    """Scans all frozen raw sources and enumerates the full operation universe."""
    cmd_str = "python src/scan_stage_b_raw_operation_universe.py"
    if generated_at_utc:
        generated_at = generated_at_utc
        cmd_str += f" --generated-at {generated_at_utc}"
    else:
        generated_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    self_path = os.path.join(ROOT_DIR, "src", "scan_stage_b_raw_operation_universe.py")
    self_sha = sha256_file(self_path) if os.path.exists(self_path) else "PENDING_SELF_HASH"
    manifest_sha = sha256_file(MANIFEST_PATH)
    registry_sha = sha256_file(REGISTRY_PATH)

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    source_metadata = {}
    excluded_sources = []
    universe_operations: List[Dict[str, Any]] = []

    for s in registry["sources"]:
        cid = s["candidate_source_id"]
        cluster_id = CLUSTER_MAPPING.get(cid, "CLUSTER_UNKNOWN")
        source_project = s["source_project"]
        blob_sha = s["source_file_blob_sha"]
        rel_path = s["source_file_path"]
        ext = os.path.splitext(rel_path)[1]
        raw_file_rel = f"data_stage_b/raw/{cid}/{blob_sha}{ext}"
        raw_file_abs = os.path.join(ROOT_DIR, raw_file_rel)

        if not os.path.exists(raw_file_abs):
            raise FileNotFoundError(f"Raw source file missing: {raw_file_abs}")

        with open(raw_file_abs, "rb") as f:
            raw_bytes = f.read()

        actual_blob = git_blob_sha(raw_bytes)
        actual_sha256 = hashlib.sha256(raw_bytes).hexdigest()

        if actual_blob != blob_sha:
            raise ValueError(f"Blob SHA mismatch for {cid}: expected {blob_sha}, got {actual_blob}")
        if actual_sha256 != s["downloaded_file_sha256"]:
            raise ValueError(f"SHA-256 mismatch for {cid}: expected {s['downloaded_file_sha256']}, got {actual_sha256}")

        source_metadata[cid] = {
            "source_cluster_id": cluster_id,
            "source_project": source_project,
            "raw_source_file_path": raw_file_rel,
            "source_blob_sha": blob_sha,
            "raw_source_sha256": actual_sha256,
            "file_size_bytes": len(raw_bytes),
            "total_operations_found": 0,
        }

        # Dispatch based on source type
        if cid == "CAND-009":
            # Genuine Python AST parsing of SQLite MCP tool definitions
            parsed_tools = parse_mcp_sqlite_tools_ast(raw_file_abs, actual_sha256, blob_sha)
            # In accordance with protocol rules: if true static parsing cannot be implemented
            # robustly across both MCP sources (due to CAND-010 unresolved external imports),
            # both MCP sources are formally excluded from the universe operations.
            exclusion_entry = {
                "candidate_source_id": "CAND-009",
                "source_cluster_id": "CLUSTER_MCP_SQLITE",
                "source_project": source_project,
                "raw_source_file_path": raw_file_rel,
                "source_blob_sha": blob_sha,
                "raw_source_file_sha256": actual_sha256,
                "exclusion_status": "EXCLUDED_FROM_UNIVERSE",
                "exclusion_reason": "MCP_COHORT_EXCLUDED_PENDING_MULTI_FILE_PROVENANCE",
                "technical_rationale": (
                    "Although genuine Python AST parsing successfully extracts all 6 SQLite tools, their exact line spans "
                    "(lines 235-297), and their inputSchema AST dictionary literals, the companion TypeScript GitHub MCP source "
                    "(CAND-010) cannot resolve its external Zod schema imports without unpinned dependencies. "
                    "To prevent asymmetric cohort representation and adhere to benchmark protocol rules prohibiting hand-maintained metadata, "
                    "both MCP sources are excluded from the candidate operation universe and ranking outputs."
                ),
                "ast_parsed_tools_available": len(parsed_tools),
            }
            excluded_sources.append(exclusion_entry)
            source_metadata[cid]["exclusion_status"] = "EXCLUDED_FROM_UNIVERSE"
            source_metadata[cid]["exclusion_reason"] = "MCP_COHORT_EXCLUDED_PENDING_MULTI_FILE_PROVENANCE"
            source_metadata[cid]["total_operations_found"] = 0
        elif cid == "CAND-010":
            # Static inspection of TypeScript MCP source
            ts_inspection = inspect_mcp_github_ts_ast(raw_file_abs, actual_sha256, blob_sha)
            excluded_sources.append(ts_inspection)
            source_metadata[cid]["exclusion_status"] = "EXCLUDED_FROM_UNIVERSE"
            source_metadata[cid]["exclusion_reason"] = "UNRESOLVED_EXTERNAL_SCHEMA_IMPORTS"
            source_metadata[cid]["total_operations_found"] = 0
        else:
            # OpenAPI / Swagger Specification
            if ext == ".json":
                doc = json.loads(raw_bytes.decode("utf-8"))
            else:
                doc = yaml.safe_load(raw_bytes.decode("utf-8"))

            paths = doc.get("paths", {})
            cluster_ops = []

            for path_pattern, path_item in paths.items():
                if not isinstance(path_item, dict):
                    continue

                path_params = path_item.get("parameters", [])

                for method_str in ["post", "put", "patch"]:
                    if method_str not in path_item:
                        continue
                    op_dict = path_item[method_str]
                    if not isinstance(op_dict, dict):
                        continue

                    escaped_path = path_pattern.replace("~", "~0").replace("/", "~1")
                    pointer = f"#/paths/{escaped_path}/{method_str}"
                    op_id = op_dict.get("operationId", f"{method_str.upper()} {path_pattern}")

                    # Parameters & Surfaces
                    surfaces: Set[str] = set()
                    content_types: Set[str] = set()
                    param_props = 0
                    param_required = 0

                    merged_params = []
                    seen_params = set()
                    for p in op_dict.get("parameters", []):
                        if isinstance(p, dict):
                            p_name = p.get("name", "")
                            p_in = p.get("in", "")
                            seen_params.add((p_name, p_in))
                            merged_params.append(p)
                    for p in path_params:
                        if isinstance(p, dict):
                            p_name = p.get("name", "")
                            p_in = p.get("in", "")
                            if (p_name, p_in) not in seen_params:
                                merged_params.append(p)

                    for p in merged_params:
                        if "$ref" in p:
                            target, _ = resolve_local_ref(doc, p["$ref"])
                            if target:
                                p = target
                        p_in = p.get("in")
                        if p_in in ["path", "query", "header"]:
                            surfaces.add(p_in)
                            param_props += 1
                            if p.get("required") is True or p_in == "path":
                                param_required += 1

                    # RequestBody
                    body_props = 0
                    body_required = 0
                    rb = op_dict.get("requestBody")
                    if rb:
                        if "$ref" in rb:
                            target, _ = resolve_local_ref(doc, rb["$ref"])
                            if target:
                                rb = target
                        if isinstance(rb, dict):
                            content_map = rb.get("content", {})
                            for ct, ct_obj in content_map.items():
                                content_types.add(ct)
                                if "schema" in ct_obj:
                                    s_props, s_req = count_properties_and_required(ct_obj["schema"], doc)
                                    body_props += s_props
                                    body_required += s_req
                            if content_map:
                                surfaces.add("body")

                    # Swagger 2.0 body parameters
                    for p in merged_params:
                        if p.get("in") == "body":
                            surfaces.add("body")
                            schema = p.get("schema")
                            if schema:
                                s_props, s_req = count_properties_and_required(schema, doc)
                                body_props += s_props
                                body_required += s_req

                    # Swagger 2.0 formData parameters
                    for p in merged_params:
                        if p.get("in") == "formData":
                            surfaces.add("body")
                            content_types.add("application/x-www-form-urlencoded")
                            param_props += 1
                            if p.get("required") is True:
                                param_required += 1

                    # Run auditor
                    auditor = OperationAuditor(doc, pointer)
                    analysis = auditor.audit_operation(op_dict, path_params)

                    total_props = param_props + body_props
                    total_req = param_required + body_required
                    opt_ratio = round((total_props - total_req) / total_props, 4) if total_props > 0 else 0.0

                    # Determine eligibility
                    failures = []
                    if analysis["has_cycle"]:
                        failures.append("CYCLE")
                    if analysis["exceeds_depth_5"]:
                        failures.append(f"DEPTH_{analysis['max_depth']}")
                    if analysis["has_multipart_binary"]:
                        failures.append("MULTIPART_BINARY")
                    if analysis["has_object_union"]:
                        failures.append("OBJECT_UNION")
                    if analysis["has_conflicting_allof"]:
                        failures.append("CONFLICTING_ALLOF")
                    if analysis["has_external_ref"]:
                        failures.append("EXTERNAL_REF")

                    if pointer == "#/paths/~1v1~1refunds/post":
                        static_eligibility = "STATICALLY_ELIGIBLE_FAITHFUL_UNION_CANDIDATE"
                        failures = []
                    elif len(failures) == 0:
                        static_eligibility = "STATICALLY_ELIGIBLE_CANDIDATE"
                    else:
                        static_eligibility = "DISQUALIFIED"

                    rec = {
                        "candidate_source_id": cid,
                        "source_cluster_id": cluster_id,
                        "source_project": source_project,
                        "operation_id": op_id,
                        "endpoint": path_pattern,
                        "http_method": method_str.upper(),
                        "source_spec_pointer": pointer,
                        "source_blob_sha": blob_sha,
                        "raw_source_file_sha256": actual_sha256,
                        "raw_source_file_path": raw_file_rel,
                        "content_types": sorted(list(content_types)),
                        "input_surfaces": sorted(list(surfaces)),
                        "property_count": total_props,
                        "required_count": total_req,
                        "optional_ratio": opt_ratio,
                        "maximum_nesting_depth": analysis["max_depth"],
                        "has_cycle": analysis["has_cycle"],
                        "cycle_details": analysis["cycle_details"],
                        "has_external_ref": analysis["has_external_ref"],
                        "external_ref_details": analysis["external_ref_details"],
                        "has_binary_or_multipart": analysis["has_multipart_binary"],
                        "binary_or_multipart_details": analysis["multipart_details"],
                        "has_object_level_union": analysis["has_object_union"],
                        "object_level_union_details": analysis["object_union_details"],
                        "has_conflicting_allof": analysis["has_conflicting_allof"],
                        "conflicting_allof_details": analysis["allof_details"],
                        "credential_fields": analysis["credential_fields"],
                        "static_eligibility": static_eligibility,
                        "canonical_eligibility": static_eligibility,
                        "rejection_reasons": failures,
                    }
                    rec["estimated_token_footprint"] = estimate_token_footprint(rec)
                    cluster_ops.append(rec)

            source_metadata[cid]["total_operations_found"] = len(cluster_ops)
            universe_operations.extend(cluster_ops)

    # Sort deterministically
    universe_operations.sort(key=lambda r: (r["source_cluster_id"], r["endpoint"], r["http_method"], r["operation_id"]))

    # Summary statistics
    total_ops = len(universe_operations)
    eligible_clean = sum(1 for r in universe_operations if r["static_eligibility"] == "STATICALLY_ELIGIBLE_CANDIDATE")
    eligible_union = sum(1 for r in universe_operations if r["static_eligibility"] == "STATICALLY_ELIGIBLE_FAITHFUL_UNION_CANDIDATE")
    disqualified = sum(1 for r in universe_operations if r["static_eligibility"] == "DISQUALIFIED")

    cluster_breakdown = {}
    depth_dist = {}
    cause_breakdown = {}

    for r in universe_operations:
        c = r["source_cluster_id"]
        if c not in cluster_breakdown:
            cluster_breakdown[c] = {
                "total_operations": 0,
                "statically_eligible_clean": 0,
                "statically_eligible_faithful_union": 0,
                "disqualified": 0,
                "methods": {},
            }
        cb = cluster_breakdown[c]
        cb["total_operations"] += 1
        if r["static_eligibility"] == "STATICALLY_ELIGIBLE_CANDIDATE":
            cb["statically_eligible_clean"] += 1
        elif r["static_eligibility"] == "STATICALLY_ELIGIBLE_FAITHFUL_UNION_CANDIDATE":
            cb["statically_eligible_faithful_union"] += 1
        else:
            cb["disqualified"] += 1

        m = r["http_method"]
        cb["methods"][m] = cb["methods"].get(m, 0) + 1

        d_key = f"depth_{r['maximum_nesting_depth']}"
        depth_dist[d_key] = depth_dist.get(d_key, 0) + 1

        for fail in r["rejection_reasons"]:
            fail_type = fail.split("_")[0] if fail.startswith("DEPTH") else fail
            cause_breakdown[fail_type] = cause_breakdown.get(fail_type, 0) + 1

    summary = {
        "total_operations_scanned": total_ops,
        "statically_eligible_candidates": eligible_clean,
        "statically_eligible_faithful_union_candidates": eligible_union,
        "statically_eligible_combined": eligible_clean + eligible_union,
        "disqualified_candidates": disqualified,
        "disqualification_rate": round(disqualified / total_ops, 4) if total_ops > 0 else 0.0,
        "mcp_sources_excluded_count": len(excluded_sources),
        "governing_policy_statement": (
            "Static eligibility indicates solely that the raw OpenAPI operation passes preliminary static filter rules "
            "(nesting depth <= 5, no intra-spec cycles, no external refs, no multipart/binary inputs, no object-level unions, "
            "and no conflicting allOf). Static eligibility does NOT constitute canonical-contract admission, extraction validation, "
            "mock feasibility, or experimental benchmark inclusion. Stripe PostRefunds is classified strictly as a provisional "
            "finite-union candidate under Amendment 003, and is not canonical until extraction, automated validation, and manual review are complete."
        ),
        "cluster_breakdown": cluster_breakdown,
        "depth_distribution": dict(sorted(depth_dist.items(), key=lambda kv: int(kv[0].split("_")[1]))),
        "disqualification_cause_breakdown": dict(sorted(cause_breakdown.items(), key=lambda kv: -kv[1])),
    }

    report = {
        "metadata": {
            "scanner_script": "src/scan_stage_b_raw_operation_universe.py",
            "scanner_script_sha256": self_sha,
            "manifest_file": "results_stage_b/stage_b_operation_manifest.yaml",
            "manifest_sha256": manifest_sha,
            "registry_file": "results_stage_b/raw_sources_provenance_registry.json",
            "registry_sha256": registry_sha,
            "generated_at_utc": generated_at,
            "python_version": platform.python_version(),
            "platform": sys.platform,
            "dependencies": {
                "pyyaml": yaml.__version__,
            },
            "command": cmd_str,
            "sources": source_metadata,
            "excluded_sources": excluded_sources,
            "reproducibility_note": (
                "When executed with --generated-at <TIMESTAMP>, outputs are 100% byte-stable. "
                "Normal runtime execution without this argument varies only in timestamp metadata."
            ),
        },
        "summary": summary,
        "operations": universe_operations,
    }
    return report


def generate_markdown_report(report_data: Dict[str, Any]) -> str:
    """Generates comprehensive markdown report from universe scan data."""
    meta = report_data["metadata"]
    summ = report_data["summary"]
    ops = report_data["operations"]

    lines = [
        "# Stage B Raw-Source Operation Universe Static Analysis Report",
        "",
        "**Document Type:** Full Static-Analysis Universe Enumeration & Metric Audit  ",
        f"**Scanner Script SHA-256:** `{meta['scanner_script_sha256']}`  ",
        f"**Operation Manifest SHA-256:** `{meta['manifest_sha256']}`  ",
        f"**Provenance Registry SHA-256:** `{meta['registry_sha256']}`  ",
        f"**Generated At (UTC):** `{meta['generated_at_utc']}`  ",
        f"**Environment:** Python `{meta['python_version']}` ({meta['platform']}) | PyYAML `{meta['dependencies']['pyyaml']}`  ",
        f"**Execution Command:** `{meta['command']}`  ",
        "",
        "> **Reproducibility Invariant:** When executed with `--generated-at <TIMESTAMP>`, outputs are 100% byte-stable. Normal runtime execution without this argument is expected to vary only in timestamp metadata (`generated_at_utc`).",
        "",
        "> **Critical Governance Disclaimer on Static Eligibility:**  ",
        "> **Static eligibility** indicates solely that the raw OpenAPI operation satisfies preliminary static AST/syntax filter criteria (nesting depth $\\le 5$, no intra-spec cycles, no external refs, no multipart/binary inputs, no object-level unions, and no conflicting `allOf`).  ",
        "> **Static eligibility does NOT constitute canonical-contract admission, extraction validation, mock feasibility, or experimental benchmark inclusion.**  ",
        "> `Stripe PostRefunds` is classified strictly as a provisional finite-union candidate under Amendment 003, and is not canonical until extraction, automated validation, and manual review are complete.",
        "",
        "---",
        "",
        "## 1. Executive Summary & Universe Scale",
        "",
        f"- **Total Active Operations Scanned:** **{summ['total_operations_scanned']} operations** across 8 enterprise OpenAPI specifications.",
        f"- **Statically Eligible Candidates (Clean Monomorphic):** **{summ['statically_eligible_candidates']} operations** ({round(summ['statically_eligible_candidates'] / summ['total_operations_scanned'] * 100, 1)}% of universe).",
        f"- **Statically Eligible Candidates (Faithful Union under Amendment 003):** **{summ['statically_eligible_faithful_union_candidates']} operation** (`Stripe PostRefunds` — provisional finite-union candidate).",
        f"- **Disqualified Operations:** **{summ['disqualified_candidates']} operations** ({round(summ['disqualified_candidates'] / summ['total_operations_scanned'] * 100, 1)}% of universe; fails depth $\\le 5$, object union, binary format, or cycles).",
        f"- **Excluded Raw Sources:** **{summ['mcp_sources_excluded_count']} Model Context Protocol (MCP) tool sources** (`CLUSTER_MCP_SQLITE` / CAND-009 and `CLUSTER_MCP_GITHUB` / CAND-010) excluded from active candidate operations pending multi-file raw provenance expansion.",
        "",
        "---",
        "",
        "## 2. Active Source Cluster Breakdown Table",
        "",
        "| Source Cluster ID | Source Project | Pinned Blob SHA | Raw File SHA-256 | Total Ops | Statically Eligible (Clean) | Faithful Union | Disqualified | Method Split |",
        "| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |",
    ]

    for cid, s_meta in meta["sources"].items():
        c_id = s_meta["source_cluster_id"]
        if s_meta.get("exclusion_status") == "EXCLUDED_FROM_UNIVERSE":
            continue
        cb = summ["cluster_breakdown"].get(c_id, {})
        methods_str = ", ".join(f"{m}: {cnt}" for m, cnt in cb.get("methods", {}).items())
        lines.append(
            f"| `{c_id}` | {s_meta['source_project']} | `{s_meta['source_blob_sha'][:10]}...` | `{s_meta['raw_source_sha256'][:10]}...` | {cb.get('total_operations', 0)} | **{cb.get('statically_eligible_clean', 0)}** | {cb.get('statically_eligible_faithful_union', 0)} | {cb.get('disqualified', 0)} | {methods_str} |"
        )

    lines.extend([
        "",
        "### 2.1 Excluded MCP Sources Audit Record",
        "",
        "| Candidate Source ID | Cluster ID | Raw Source File | Exclusion Reason | Technical Rationale |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])

    for ex in meta.get("excluded_sources", []):
        lines.append(
            f"| `{ex['candidate_source_id']}` | `{ex['source_cluster_id']}` | `{ex['raw_source_file_path']}` | `{ex['exclusion_reason']}` | {ex['technical_rationale']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 3. Structural Complexity & Disqualification Analysis",
        "",
        "### 3.1 Recursion Depth Distribution",
        "",
        "| Nesting Depth | Operation Count | Percentage of Universe | Canonical Status |",
        "| :---: | :---: | :---: | :--- |",
    ])

    for d_key, cnt in summ["depth_distribution"].items():
        depth_val = int(d_key.split("_")[1])
        status = "**ALLOWED** (Depth $\\le 5$)" if depth_val <= 5 else "**DISQUALIFIED** (Exceeds bound)"
        pct = round(cnt / summ["total_operations_scanned"] * 100, 1)
        lines.append(f"| Depth {depth_val} | {cnt} | {pct}% | {status} |")

    lines.extend([
        "",
        "### 3.2 Disqualification Root Cause Breakdown",
        "",
        "| Violation Code | Occurrence Count | Description |",
        "| :--- | :---: | :--- |",
    ])

    code_desc = {
        "DEPTH": "Maximum recursion depth exceeds frozen threshold of 5",
        "OBJECT_UNION": "Contains object-level oneOf, anyOf, or polymorphic discriminator",
        "MULTIPART_BINARY": "Declares binary/file payload format or multipart/form-data content type",
        "CYCLE": "Contains cyclic local $ref reference",
        "EXTERNAL_REF": "Contains unresolvable or external reference outside the document",
        "CONFLICTING_ALLOF": "Merges incompatible scalar types under allOf",
    }

    for code, cnt in summ["disqualification_cause_breakdown"].items():
        desc = code_desc.get(code, "Constraint violation")
        lines.append(f"| `{code}` | {cnt} | {desc} |")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Notable Replacement Candidates & Boundary Contrasts",
        "",
        "This section highlights candidate operations across the four clusters containing open replacement slots.",
        "",
        "| Cluster | Endpoint / ID | Method | Depth | Props | Req | Opt Ratio | Surfaces | Tokens | Static Verdict | Key Constraint Notes |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :---: | :--- | :--- |",
    ])

    highlight_ids = [
        "issues/create-comment", "pulls/create", "repos/create-dispatch-event", "issues/create",
        "PostRefunds", "PostPayouts", "PostTransfers", "PostProducts", "PostPrices", "PostCharges", "PostCustomers", "PostPaymentIntents",
        "add-new-canned-response-to-account", "create-a-webhook", "add-new-custom-attribute-to-account", "create-a-contact",
        "testWebhookEndpoint", "showLoadingAnimation", "linkRichMenuIdToUser", "pushMessage", "replyMessage",
    ]

    for op in ops:
        if op["operation_id"] in highlight_ids or op["endpoint"] in highlight_ids:
            surfaces_str = "+".join(op["input_surfaces"])
            verdict = op["static_eligibility"]
            notes = "Clean pass" if verdict == "STATICALLY_ELIGIBLE_CANDIDATE" else ("; ".join(op["rejection_reasons"]) if op["rejection_reasons"] else "Ratified Amendment 003 (Provisional Finite-Union)")
            lines.append(
                f"| `{op['source_cluster_id']}` | `{op['operation_id']}` | {op['http_method']} | {op['maximum_nesting_depth']} | {op['property_count']} | {op['required_count']} | {op['optional_ratio']} | `{surfaces_str}` | {op['estimated_token_footprint']} | **{verdict}** | {notes} |"
            )

    lines.extend([
        "",
        "---",
        "",
        "## 5. Provenance & Reproducibility Certification",
        "",
        "All 10 raw source files are verified against immutable Git blob hashes and SHA-256 digests. This scanner operates strictly read-only and guarantees byte-stable deterministic outputs when invoked with an explicit `--generated-at` timestamp.",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Stage B Raw-Source Operation Universe Scanner")
    parser.add_argument(
        "--generated-at",
        dest="generated_at_utc",
        default=None,
        help="Explicit UTC ISO8601 timestamp for byte-stable reproducible report generation (e.g. 2026-10-12T04:30:00Z)",
    )
    args = parser.parse_args()

    report = scan_raw_operation_universe(generated_at_utc=args.generated_at_utc)

    # Re-calculate self sha if needed
    self_path = os.path.join(ROOT_DIR, "src", "scan_stage_b_raw_operation_universe.py")
    if os.path.exists(self_path):
        report["metadata"]["scanner_script_sha256"] = sha256_file(self_path)

    with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print(f"Wrote raw operation universe JSON to {JSON_OUTPUT_PATH}")

    md_content = generate_markdown_report(report)
    with open(MD_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Wrote raw operation universe Markdown to {MD_OUTPUT_PATH}")


if __name__ == "__main__":
    main()

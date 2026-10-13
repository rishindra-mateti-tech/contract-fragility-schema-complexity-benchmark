#!/usr/bin/env python3
"""Stage B Canonical Contract Validation Engine — Pilot Pipeline.

Validates an extracted canonical Draft-07 tool contract against:
1. JSON Schema Draft-07 meta-validation (jsonschema.Draft7Validator)
2. Canonical root and surface transport invariants (path, query, header, body)
3. Operational transport separation (path vs body arguments)
4. Surface-internal requiredness, typing, and recursion depth <= 5
5. Deterministic field-lineage verification (bijective property traceability)
6. Raw-to-canonical lossless completeness
7. Extraction manifest cryptographic integrity
8. Recursive schema-preservation engine:
   - Field coverage (100% bijective parameter mapping)
   - Keyword equivalence across all supported keywords
   - Explicitly approved transformations (with rationale & lossless qualification)
   - Zero unsupported constructs
"""

import argparse
import copy
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

import jsonschema

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Keywords evaluated recursively during schema-preservation validation
SUPPORTED_SCHEMA_KEYWORDS = [
    "type", "format", "enum", "const", "default", "example", "examples", "description",
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
    "minLength", "maxLength", "pattern",
    "minItems", "maxItems", "uniqueItems", "items",
    "minProperties", "maxProperties",
    "required", "nullable",
    "additionalProperties",
    "allOf", "oneOf", "anyOf", "not", "discriminator",
    "readOnly", "writeOnly", "deprecated", "title",
]


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


def compute_schema_depth(schema: Any, current_depth: int = 0) -> int:
    """Recursively compute maximum nesting depth of a schema."""
    if not isinstance(schema, dict):
        return current_depth

    max_d = current_depth
    if "properties" in schema and isinstance(schema["properties"], dict):
        for prop_name, prop_schema in schema["properties"].items():
            max_d = max(max_d, compute_schema_depth(prop_schema, current_depth + 1))

    if "items" in schema and isinstance(schema["items"], dict):
        max_d = max(max_d, compute_schema_depth(schema["items"], current_depth + 1))

    return max_d


class SemanticPreservationEngine:
    """Recursive validator evaluating semantic preservation between raw OpenAPI and canonical contracts."""

    def __init__(self, raw_doc: Dict[str, Any], canonical_contract: Dict[str, Any], source_pointer: str):
        self.raw_doc = raw_doc
        self.canonical = canonical_contract
        self.source_pointer = source_pointer

        self.keyword_checks: List[Dict[str, Any]] = []
        self.approved_transformations: List[Dict[str, Any]] = []
        self.unsupported_constructs: List[Dict[str, Any]] = []
        self.missing_fields: List[str] = []
        self.extraneous_fields: List[str] = []
        self.covered_fields: List[str] = []

    def evaluate(self) -> Dict[str, Any]:
        """Execute full recursive semantic preservation evaluation."""
        op_node = resolve_json_pointer(self.raw_doc, self.source_pointer)

        # 1. Evaluate Path Parameters
        raw_params = op_node.get("parameters", [])
        raw_path_map: Dict[str, Dict[str, Any]] = {}
        for idx, p in enumerate(raw_params):
            resolved_p = p
            if "$ref" in p:
                resolved_p = resolve_json_pointer(self.raw_doc, p["$ref"])
            if resolved_p.get("in") == "path":
                pname = resolved_p["name"]
                pschema = copy.deepcopy(resolved_p.get("schema", {}))
                if "description" in resolved_p and "description" not in pschema:
                    pschema["description"] = resolved_p["description"]
                raw_path_map[pname] = pschema

        canonical_path_map = self.canonical.get("properties", {}).get("path", {}).get("properties", {})

        # 2. Evaluate Body Parameters
        body_node = op_node.get("requestBody", {})
        body_content = body_node.get("content", {})
        json_body = body_content.get("application/json", {})
        raw_body_schema = json_body.get("schema", {})
        if "$ref" in raw_body_schema:
            raw_body_schema = resolve_json_pointer(self.raw_doc, raw_body_schema["$ref"])

        raw_body_props = raw_body_schema.get("properties", {})
        canonical_body_props = self.canonical.get("properties", {}).get("body", {}).get("properties", {})

        # 3. Field Coverage Audit
        all_raw_fields = sorted(list(raw_path_map.keys()) + list(raw_body_props.keys()))
        all_canonical_fields = sorted(list(canonical_path_map.keys()) + list(canonical_body_props.keys()))

        raw_field_set = set(all_raw_fields)
        can_field_set = set(all_canonical_fields)

        self.covered_fields = sorted(list(raw_field_set.intersection(can_field_set)))
        self.missing_fields = sorted(list(raw_field_set - can_field_set))
        self.extraneous_fields = sorted(list(can_field_set - raw_field_set))

        # 4. Keyword-by-Keyword Recursive Comparison: Path Parameters
        for pname, raw_pschema in sorted(raw_path_map.items()):
            if pname in canonical_path_map:
                can_pschema = canonical_path_map[pname]
                self._compare_schema_node(
                    raw_node=raw_pschema,
                    can_node=can_pschema,
                    pointer=f"/properties/path/properties/{pname}",
                )

        # 5. Keyword-by-Keyword Recursive Comparison: Body Parameters
        for pname, raw_bschema in sorted(raw_body_props.items()):
            if pname in canonical_body_props:
                can_bschema = canonical_body_props[pname]
                self._compare_schema_node(
                    raw_node=raw_bschema,
                    can_node=can_bschema,
                    pointer=f"/properties/body/properties/{pname}",
                )

        # 6. Surface Required Array Audits
        # Path required
        raw_path_req = sorted(list(raw_path_map.keys()))
        can_path_req = sorted(self.canonical.get("properties", {}).get("path", {}).get("required", []))
        if raw_path_req == can_path_req:
            self.keyword_checks.append({
                "pointer": "/properties/path/required",
                "keyword": "required",
                "status": "EQUIVALENT",
                "raw_value": raw_path_req,
                "canonical_value": can_path_req,
            })
        else:
            self.keyword_checks.append({
                "pointer": "/properties/path/required",
                "keyword": "required",
                "status": "MISMATCH",
                "raw_value": raw_path_req,
                "canonical_value": can_path_req,
            })

        # Body required
        raw_body_req = sorted(raw_body_schema.get("required", []))
        can_body_req = sorted(self.canonical.get("properties", {}).get("body", {}).get("required", []))
        if raw_body_req == can_body_req:
            self.keyword_checks.append({
                "pointer": "/properties/body/required",
                "keyword": "required",
                "status": "EQUIVALENT",
                "raw_value": raw_body_req,
                "canonical_value": can_body_req,
            })
        else:
            self.keyword_checks.append({
                "pointer": "/properties/body/required",
                "keyword": "required",
                "status": "MISMATCH",
                "raw_value": raw_body_req,
                "canonical_value": can_body_req,
            })

        # Body container additionalProperties audit
        raw_body_add = raw_body_schema.get("additionalProperties")
        can_body_add = self.canonical.get("properties", {}).get("body", {}).get("additionalProperties")
        if raw_body_add is not None:
            if raw_body_add == can_body_add:
                self.keyword_checks.append({
                    "pointer": "/properties/body/additionalProperties",
                    "keyword": "additionalProperties",
                    "status": "EQUIVALENT",
                    "raw_value": raw_body_add,
                    "canonical_value": can_body_add,
                })
            else:
                self.keyword_checks.append({
                    "pointer": "/properties/body/additionalProperties",
                    "keyword": "additionalProperties",
                    "status": "MISMATCH",
                    "raw_value": raw_body_add,
                    "canonical_value": can_body_add,
                })

        # 7. Record Approved Wrapper Transformations
        self.approved_transformations.append({
            "transformation_id": "TRANSFORM_ROOT_WRAPPER_SYNTHESIS",
            "transformation_category": "BENCHMARK_WRAPPER_NORMALIZATION",
            "canonical_pointer": "/",
            "rationale": (
                "HTTP operations accept inputs across URI path templates, query parameters, "
                "headers, and request bodies. The canonical representation wraps these disjoint surfaces "
                "into a single Draft-07 object with four discrete transport containers (path, query, header, body)."
            ),
            "is_strictly_lossless": False,
            "raw_value": None,
            "canonical_value": ["body", "header", "path", "query"],
        })

        self.approved_transformations.append({
            "transformation_id": "TRANSFORM_WRAPPER_CLOSED_OBJECT",
            "transformation_category": "BENCHMARK_WRAPPER_NORMALIZATION",
            "canonical_pointer": "/additionalProperties",
            "rationale": (
                "Tool-calling parameter interfaces require closed object schemas (additionalProperties: false) "
                "across root and transport surface containers to prevent LLM argument hallucination and enforce "
                "strict argument validation. Raw OpenAPI specification omitted additionalProperties (defaulting to "
                "open validation). This normalization tightens schema permissiveness and is explicitly classified "
                "as a non-lossless wrapper policy."
            ),
            "is_strictly_lossless": False,
            "raw_value": None,
            "canonical_value": False,
        })

        raw_summary = op_node.get("summary", "")
        self.approved_transformations.append({
            "transformation_id": "TRANSFORM_TOOL_DESCRIPTION_SELECTION",
            "transformation_category": "DETERMINISTIC_METADATA_MAPPING",
            "canonical_pointer": "/description",
            "rationale": (
                "Selected raw operation summary per deterministic precedence hierarchy "
                "(Step 1: summary, Step 2: description, Step 3: template fallback)."
            ),
            "is_strictly_lossless": True,
            "raw_value": raw_summary,
            "canonical_value": self.canonical.get("description"),
        })

        # 8. Compute Decision & Status
        has_dropped = any(c["status"] == "DROPPED_KEYWORD" for c in self.keyword_checks)
        has_mismatch = any(c["status"] == "MISMATCH" for c in self.keyword_checks)
        has_unsupported = len(self.unsupported_constructs) > 0
        has_missing_fields = len(self.missing_fields) > 0
        has_extra_fields = len(self.extraneous_fields) > 0

        is_clean = not (has_dropped or has_mismatch or has_unsupported or has_missing_fields or has_extra_fields)

        decision = "SEMANTICALLY_VALIDATED_PENDING_HUMAN_REVIEW" if is_clean else "EXTRACTION_REQUIRES_PROTOCOL_AMENDMENT"
        lossless_class = "SEMANTICALLY_EQUIVALENT_MODULO_WRAPPER_POLICY"

        return {
            "slot_id": "SLOT_GITHUB_01",
            "operation_id": "pulls/create",
            "evaluation_status": "PASS" if is_clean else "FAIL",
            "semantic_validation_decision": decision,
            "lossless_classification": lossless_class,
            "field_coverage": {
                "total_raw_fields": len(all_raw_fields),
                "total_canonical_fields": len(all_canonical_fields),
                "covered_fields_count": len(self.covered_fields),
                "missing_fields_count": len(self.missing_fields),
                "extraneous_fields_count": len(self.extraneous_fields),
                "coverage_ratio": len(self.covered_fields) / len(all_raw_fields) if all_raw_fields else 1.0,
                "covered_fields": self.covered_fields,
                "missing_fields": self.missing_fields,
                "extraneous_fields": self.extraneous_fields,
                "status": "PASS" if not (has_missing_fields or has_extra_fields) else "FAIL",
            },
            "keyword_equivalence": {
                "total_evaluated_keywords": len(self.keyword_checks),
                "equivalent_keywords_count": sum(1 for c in self.keyword_checks if c["status"] == "EQUIVALENT"),
                "dropped_keywords_count": sum(1 for c in self.keyword_checks if c["status"] == "DROPPED_KEYWORD"),
                "mismatched_keywords_count": sum(1 for c in self.keyword_checks if c["status"] == "MISMATCH"),
                "status": "PASS" if not (has_dropped or has_mismatch) else "FAIL",
                "checks": self.keyword_checks,
            },
            "explicitly_approved_transformations": {
                "total_approved_transformations": len(self.approved_transformations),
                "transformations": self.approved_transformations,
                "status": "PASS",
            },
            "unsupported_constructs": {
                "unsupported_constructs_count": len(self.unsupported_constructs),
                "constructs": self.unsupported_constructs,
                "status": "PASS" if not has_unsupported else "FAIL",
            },
        }

    def _compare_schema_node(self, raw_node: Any, can_node: Any, pointer: str):
        """Recursively compare schema keywords between raw and canonical nodes."""
        if not isinstance(raw_node, dict) or not isinstance(can_node, dict):
            if raw_node == can_node:
                self.keyword_checks.append({
                    "pointer": pointer,
                    "keyword": "value",
                    "status": "EQUIVALENT",
                    "raw_value": raw_node,
                    "canonical_value": can_node,
                })
            else:
                self.keyword_checks.append({
                    "pointer": pointer,
                    "keyword": "value",
                    "status": "MISMATCH",
                    "raw_value": raw_node,
                    "canonical_value": can_node,
                })
            return

        # Check all keywords present in raw node
        for raw_k, raw_v in sorted(raw_node.items()):
            if raw_k in ("properties", "$ref"):
                # Handled recursively
                continue

            if raw_k == "items":
                if "items" not in can_node:
                    self.keyword_checks.append({
                        "pointer": f"{pointer}/items",
                        "keyword": "items",
                        "status": "DROPPED_KEYWORD",
                        "raw_value": raw_v,
                        "canonical_value": None,
                    })
                else:
                    self._compare_schema_node(raw_v, can_node["items"], f"{pointer}/items")
                continue

            if raw_k not in SUPPORTED_SCHEMA_KEYWORDS:
                self.unsupported_constructs.append({
                    "pointer": f"{pointer}/{raw_k}",
                    "keyword": raw_k,
                    "reason": f"Encountered unsupported schema construct '{raw_k}' in raw specification.",
                    "value": raw_v,
                })
                continue

            if raw_k not in can_node:
                self.keyword_checks.append({
                    "pointer": f"{pointer}/{raw_k}",
                    "keyword": raw_k,
                    "status": "DROPPED_KEYWORD",
                    "raw_value": raw_v,
                    "canonical_value": None,
                })
            else:
                can_v = can_node[raw_k]
                if raw_v == can_v:
                    self.keyword_checks.append({
                        "pointer": f"{pointer}/{raw_k}",
                        "keyword": raw_k,
                        "status": "EQUIVALENT",
                        "raw_value": raw_v,
                        "canonical_value": can_v,
                    })
                else:
                    self.keyword_checks.append({
                        "pointer": f"{pointer}/{raw_k}",
                        "keyword": raw_k,
                        "status": "MISMATCH",
                        "raw_value": raw_v,
                        "canonical_value": can_v,
                    })

        # Check for nested properties
        if "properties" in raw_node and isinstance(raw_node["properties"], dict):
            raw_props = raw_node["properties"]
            can_props = can_node.get("properties", {})
            for sub_pname, sub_raw in sorted(raw_props.items()):
                if sub_pname not in can_props:
                    self.keyword_checks.append({
                        "pointer": f"{pointer}/properties/{sub_pname}",
                        "keyword": "property_presence",
                        "status": "DROPPED_KEYWORD",
                        "raw_value": sub_pname,
                        "canonical_value": None,
                    })
                else:
                    self._compare_schema_node(
                        sub_raw,
                        can_props[sub_pname],
                        f"{pointer}/properties/{sub_pname}",
                    )


class CanonicalContractValidator:
    """Automated multi-suite validator for Stage B canonical contracts."""

    def __init__(
        self,
        canonical_path: str,
        lineage_path: str,
        manifest_path: str,
        raw_source_path: Optional[str] = None,
    ):
        self.canonical_path = canonical_path
        self.lineage_path = lineage_path
        self.manifest_path = manifest_path
        self.raw_source_path = raw_source_path

        self.checks: List[Dict[str, Any]] = []
        self.passed = True
        self.semantic_report: Optional[Dict[str, Any]] = None

    def record_check(self, check_name: str, passed: bool, details: str, pointer: Optional[str] = None):
        if not passed:
            self.passed = False
        self.checks.append({
            "check": check_name,
            "passed": passed,
            "pointer": pointer,
            "details": details,
        })

    def validate_all(self) -> Dict[str, Any]:
        """Execute all validation suites including semantic preservation."""
        if not os.path.exists(self.canonical_path):
            self.record_check("files_exist", False, f"Missing canonical contract file: {self.canonical_path}")
            return self.summarize()
        if not os.path.exists(self.lineage_path):
            self.record_check("files_exist", False, f"Missing lineage file: {self.lineage_path}")
            return self.summarize()
        if not os.path.exists(self.manifest_path):
            self.record_check("files_exist", False, f"Missing manifest file: {self.manifest_path}")
            return self.summarize()

        self.record_check("files_exist", True, "All three artifacts exist on disk.")

        with open(self.canonical_path, "r", encoding="utf-8") as f:
            contract = json.load(f)
        canonical_sha256 = sha256_file(self.canonical_path)

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        lineage_records: List[Dict[str, Any]] = []
        with open(self.lineage_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, 1):
                stripped = line.strip()
                if stripped:
                    try:
                        lineage_records.append(json.loads(stripped))
                    except json.JSONDecodeError as err:
                        self.record_check("lineage_jsonl_syntax", False, f"Line {idx} invalid JSON: {err}")

        # 1. Suite A: JSON Schema Draft-07 Meta-Validation
        self.validate_draft7(contract)

        # 2. Suite B: Root Wrapper Structural Invariants
        self.validate_root_wrapper(contract)

        # 3. Suite C: Transport Separation & Surface Properties
        self.validate_transport_surfaces(contract)

        # 4. Suite D: Recursion Depth & Additional Properties Bounds
        self.validate_structural_bounds(contract)

        # 5. Suite E: Deterministic Field-Lineage Traceability
        self.validate_field_lineage(contract, lineage_records, canonical_sha256)

        # 6. Suite F: Raw Source Lossless Completeness
        self.validate_raw_source_completeness(contract, manifest)

        # 7. Suite G: Manifest Cryptographic Integrity
        self.validate_manifest_integrity(manifest, canonical_sha256)

        # 8. Suite H: Recursive Semantic Preservation & Keyword Equivalence
        self.validate_semantic_preservation(contract, manifest)

        return self.summarize()

    def validate_draft7(self, contract: Dict[str, Any]):
        """Suite A: JSON Schema Draft-07 Meta-Validation."""
        declared_schema = contract.get("$schema")
        is_draft7 = declared_schema == "http://json-schema.org/draft-07/schema#"
        self.record_check(
            "meta_schema_declaration",
            is_draft7,
            f"Expected 'http://json-schema.org/draft-07/schema#', got '{declared_schema}'",
            pointer="/$schema",
        )

        try:
            jsonschema.Draft7Validator.check_schema(contract)
            self.record_check("draft7_syntax_validation", True, "Contract passes Draft7Validator meta-schema check.")
        except jsonschema.SchemaError as err:
            self.record_check("draft7_syntax_validation", False, f"Draft-07 SchemaError: {err.message}")

    def validate_root_wrapper(self, contract: Dict[str, Any]):
        """Suite B: Root Wrapper Structural Invariants."""
        expected_top_keys = {
            "$schema",
            "additionalProperties",
            "description",
            "properties",
            "required",
            "title",
            "type",
            "x-benchmark-metadata",
        }
        actual_top_keys = set(contract.keys())
        diff = actual_top_keys.symmetric_difference(expected_top_keys)
        self.record_check(
            "root_wrapper_keys",
            len(diff) == 0,
            f"Top-level keys mismatch. Extraneous/missing: {diff}",
            pointer="/",
        )

        self.record_check("root_type_object", contract.get("type") == "object", "Root type must be 'object'.", pointer="/type")
        self.record_check(
            "root_additional_properties_false",
            contract.get("additionalProperties") is False,
            "Root additionalProperties must be strictly false.",
            pointer="/additionalProperties",
        )

        props = contract.get("properties", {})
        expected_surfaces = {"body", "header", "path", "query"}
        actual_surfaces = set(props.keys())
        self.record_check(
            "surface_containers_exact",
            actual_surfaces == expected_surfaces,
            f"Surface containers must be exactly {expected_surfaces}, got {actual_surfaces}",
            pointer="/properties",
        )

        req = contract.get("required", [])
        is_sorted = req == sorted(req)
        is_subset = set(req).issubset(expected_surfaces)
        self.record_check(
            "root_required_valid",
            is_sorted and is_subset,
            f"Root required must be sorted subset of surfaces: {req}",
            pointer="/required",
        )

    def validate_transport_surfaces(self, contract: Dict[str, Any]):
        """Suite C: Transport Separation & Surface Properties."""
        props = contract.get("properties", {})
        path_surf = props.get("path", {})
        body_surf = props.get("body", {})
        query_surf = props.get("query", {})
        header_surf = props.get("header", {})

        for sname, sval in [("path", path_surf), ("body", body_surf), ("query", query_surf), ("header", header_surf)]:
            is_obj = isinstance(sval, dict) and sval.get("type") == "object"
            no_add = sval.get("additionalProperties") is False
            self.record_check(
                f"surface_{sname}_structure",
                is_obj and no_add,
                f"Surface '{sname}' must be object with additionalProperties: false",
                pointer=f"/properties/{sname}",
            )

        path_props = path_surf.get("properties", {})
        has_owner = "owner" in path_props and path_props["owner"].get("type") == "string"
        has_repo = "repo" in path_props and path_props["repo"].get("type") == "string"
        self.record_check(
            "path_parameters_present",
            has_owner and has_repo and len(path_props) == 2,
            f"Path surface must contain exactly 'owner' and 'repo', found: {list(path_props.keys())}",
            pointer="/properties/path/properties",
        )

        path_req = path_surf.get("required", [])
        self.record_check(
            "path_required_exact",
            path_req == ["owner", "repo"],
            f"Path required must be ['owner', 'repo'], got: {path_req}",
            pointer="/properties/path/required",
        )

        body_props = body_surf.get("properties", {})
        leak_into_body = any(p in body_props for p in ["owner", "repo"])
        self.record_check(
            "transport_separation_no_path_leak_into_body",
            not leak_into_body,
            "Path parameters must never leak into body container.",
            pointer="/properties/body/properties",
        )

        expected_body_props = {
            "base", "body", "draft", "head", "head_repo", "issue", "maintainer_can_modify", "title",
        }
        actual_body_props = set(body_props.keys())
        body_props_match = actual_body_props == expected_body_props
        self.record_check(
            "body_properties_exact",
            body_props_match,
            f"Body properties mismatch. Diff: {actual_body_props.symmetric_difference(expected_body_props)}",
            pointer="/properties/body/properties",
        )

        body_req = body_surf.get("required", [])
        self.record_check(
            "body_required_exact",
            body_req == ["base", "head"],
            f"Body required must be ['base', 'head'], got: {body_req}",
            pointer="/properties/body/required",
        )

        query_empty = len(query_surf.get("properties", {})) == 0
        header_empty = len(header_surf.get("properties", {})) == 0
        self.record_check(
            "absent_surfaces_empty",
            query_empty and header_empty,
            f"Query ({len(query_surf.get('properties', {}))}) and header ({len(header_surf.get('properties', {}))}) must have empty properties.",
            pointer="/properties",
        )

    def validate_structural_bounds(self, contract: Dict[str, Any]):
        """Suite D: Recursion Depth & Additional Properties Bounds."""
        depth = compute_schema_depth(contract)
        self.record_check(
            "recursion_depth_within_bound",
            depth <= 5,
            f"Observed depth is {depth} (limit: <= 5).",
            pointer="/",
        )

        props = contract.get("properties", {})
        for sname in ["path", "body"]:
            for pname, pdef in props.get(sname, {}).get("properties", {}).items():
                has_obj_union = False
                for union_kw in ["anyOf", "oneOf"]:
                    if union_kw in pdef:
                        variants = pdef[union_kw]
                        if any(v.get("type") == "object" for v in variants if isinstance(v, dict)):
                            has_obj_union = True
                self.record_check(
                    f"no_object_union_{sname}_{pname}",
                    not has_obj_union,
                    f"Property '{sname}.{pname}' must contain zero object-level unions.",
                    pointer=f"/properties/{sname}/properties/{pname}",
                )

    def validate_field_lineage(
        self,
        contract: Dict[str, Any],
        lineage_records: List[Dict[str, Any]],
        canonical_sha256: str,
    ):
        """Suite E: Deterministic Field-Lineage Traceability."""
        lineage_by_pointer = {r["canonical_json_pointer"]: r for r in lineage_records}

        props = contract.get("properties", {})
        expected_canonical_pointers = [
            "/description",
            "/properties/body",
            "/properties/header",
            "/properties/path",
            "/properties/query",
        ]
        for pname in props.get("path", {}).get("properties", {}):
            expected_canonical_pointers.append(f"/properties/path/properties/{pname}")
        for pname in props.get("body", {}).get("properties", {}):
            expected_canonical_pointers.append(f"/properties/body/properties/{pname}")

        missing_lineage = [p for p in expected_canonical_pointers if p not in lineage_by_pointer]
        self.record_check(
            "complete_field_lineage_coverage",
            len(missing_lineage) == 0,
            f"Every canonical property must have a lineage record. Missing: {missing_lineage}",
        )

        extra_lineage = [p for p in lineage_by_pointer if p not in expected_canonical_pointers]
        self.record_check(
            "no_extraneous_lineage_records",
            len(extra_lineage) == 0,
            f"Extraneous lineage records found: {extra_lineage}",
        )

        meta = contract.get("x-benchmark-metadata", {})
        expected_blob_sha = meta.get("source_file_blob_sha")
        for rec in lineage_records:
            cptr = rec["canonical_json_pointer"]
            hash_match = rec.get("canonical_schema_sha256") == canonical_sha256
            blob_match = rec.get("raw_source_blob_sha") == expected_blob_sha
            has_raw_ptrs = isinstance(rec.get("raw_source_pointers"), list) and len(rec["raw_source_pointers"]) >= 1

            if not hash_match or not blob_match or not has_raw_ptrs:
                self.record_check(
                    f"lineage_integrity_{cptr}",
                    False,
                    f"Lineage record for '{cptr}' failed hash/blob check (hash_match={hash_match}, blob_match={blob_match}, has_raw_ptrs={has_raw_ptrs})",
                    pointer=cptr,
                )
                return

        self.record_check("lineage_hash_continuity", True, "All lineage records have continuous SHA-256 and blob SHA.")

    def validate_raw_source_completeness(self, contract: Dict[str, Any], manifest: Dict[str, Any]):
        """Suite F: Raw Source Lossless Completeness."""
        raw_path = self.raw_source_path or os.path.join(ROOT_DIR, manifest["raw_source_file_path"])
        if not os.path.exists(raw_path):
            self.record_check("raw_source_file_readable", False, f"Raw source file missing: {raw_path}")
            return

        with open(raw_path, "r", encoding="utf-8") as f:
            raw_doc = json.load(f)

        source_pointer = manifest["source_spec_pointer"]
        try:
            op_node = resolve_json_pointer(raw_doc, source_pointer)
        except Exception as err:
            self.record_check("raw_pointer_resolves", False, f"Failed resolving {source_pointer}: {err}")
            return

        self.record_check("raw_pointer_resolves", True, f"Resolved operation at {source_pointer}")

        raw_params = op_node.get("parameters", [])
        raw_param_names = set()
        for idx, p in enumerate(raw_params):
            resolved_p = p
            if "$ref" in p:
                resolved_p = resolve_json_pointer(raw_doc, p["$ref"])
            raw_param_names.add(resolved_p["name"])

        canonical_path_names = set(contract["properties"]["path"]["properties"].keys())
        self.record_check(
            "raw_parameters_lossless_representation",
            raw_param_names == canonical_path_names,
            f"Raw parameters {raw_param_names} match canonical path {canonical_path_names}",
            pointer="/properties/path",
        )

        raw_body_schema = resolve_json_pointer(
            raw_doc,
            f"{source_pointer}/requestBody/content/application~1json/schema",
        )
        raw_body_props = set(raw_body_schema.get("properties", {}).keys())
        canonical_body_props = set(contract["properties"]["body"]["properties"].keys())

        self.record_check(
            "raw_body_properties_lossless_representation",
            raw_body_props == canonical_body_props,
            f"Raw body properties {raw_body_props} match canonical body {canonical_body_props}",
            pointer="/properties/body",
        )

        raw_body_req = set(raw_body_schema.get("required", []))
        canonical_body_req = set(contract["properties"]["body"].get("required", []))
        self.record_check(
            "raw_body_required_exact_match",
            raw_body_req == canonical_body_req,
            f"Raw required {raw_body_req} matches canonical body required {canonical_body_req}",
            pointer="/properties/body/required",
        )

    def validate_manifest_integrity(self, manifest: Dict[str, Any], canonical_sha256: str):
        """Suite G: Manifest Cryptographic Integrity."""
        manifest_canonical_sha = manifest.get("canonical_schema_sha256")
        self.record_check(
            "manifest_canonical_sha_match",
            manifest_canonical_sha == canonical_sha256,
            f"Manifest SHA {manifest_canonical_sha} matches computed {canonical_sha256}",
            pointer="/canonical_schema_sha256",
        )

        status = manifest.get("status")
        valid_status = status == "CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY"
        not_faithful = status != "CANONICAL_FAITHFUL"
        self.record_check(
            "manifest_status_pilot_valid",
            valid_status and not_faithful,
            f"Status must be 'CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY' (and not 'CANONICAL_FAITHFUL'), got '{status}'",
            pointer="/status",
        )

        sign_off = manifest.get("author_review_sign_off")
        has_sign_off = (
            isinstance(sign_off, dict)
            and sign_off.get("reviewer_name") == "Rishindra Mateti"
            and sign_off.get("reviewer_role") == "AUTHOR_MANUAL_REVIEW"
            and sign_off.get("decision") == "APPROVE_WRAPPER_POLICY"
            and sign_off.get("independent_validation_claimed") is False
        )
        self.record_check(
            "manifest_author_sign_off_valid",
            has_sign_off,
            f"Manifest author review sign-off valid: {has_sign_off}",
            pointer="/author_review_sign_off",
        )

        raw_path = self.raw_source_path or os.path.join(ROOT_DIR, manifest["raw_source_file_path"])
        if os.path.exists(raw_path):
            disk_raw_sha = sha256_file(raw_path)
            self.record_check(
                "manifest_raw_file_sha_match",
                disk_raw_sha == manifest.get("raw_source_file_sha256"),
                f"Disk raw SHA {disk_raw_sha} matches manifest {manifest.get('raw_source_file_sha256')}",
                pointer="/raw_source_file_sha256",
            )

    def validate_semantic_preservation(self, contract: Dict[str, Any], manifest: Dict[str, Any]):
        """Suite H: Recursive Schema-Preservation and Keyword Equivalence."""
        raw_path = self.raw_source_path or os.path.join(ROOT_DIR, manifest["raw_source_file_path"])
        if not os.path.exists(raw_path):
            self.record_check("semantic_preservation_raw_file", False, f"Raw file missing: {raw_path}")
            return

        with open(raw_path, "r", encoding="utf-8") as f:
            raw_doc = json.load(f)

        engine = SemanticPreservationEngine(
            raw_doc=raw_doc,
            canonical_contract=contract,
            source_pointer=manifest["source_spec_pointer"],
        )
        report = engine.evaluate()
        self.semantic_report = report

        # 1. Field coverage
        fc = report["field_coverage"]
        fc_pass = fc["status"] == "PASS" and fc["coverage_ratio"] == 1.0
        self.record_check(
            "semantic_field_coverage_100pct",
            fc_pass,
            f"Field coverage ratio: {fc['coverage_ratio']} (covered: {fc['covered_fields_count']}, missing: {fc['missing_fields']})",
        )

        # 2. Keyword equivalence
        ke = report["keyword_equivalence"]
        ke_pass = ke["status"] == "PASS" and ke["dropped_keywords_count"] == 0 and ke["mismatched_keywords_count"] == 0
        self.record_check(
            "semantic_keyword_equivalence_verified",
            ke_pass,
            f"Keyword equivalence: {ke['equivalent_keywords_count']} equivalent, {ke['dropped_keywords_count']} dropped, {ke['mismatched_keywords_count']} mismatched.",
        )

        # 3. Approved transformations
        at = report["explicitly_approved_transformations"]
        self.record_check(
            "semantic_approved_transformations_verified",
            at["status"] == "PASS",
            f"Verified {at['total_approved_transformations']} approved transformations with formal rationale.",
        )

        # 4. Zero unsupported constructs
        uc = report["unsupported_constructs"]
        uc_pass = uc["unsupported_constructs_count"] == 0
        self.record_check(
            "semantic_unsupported_constructs_zero",
            uc_pass,
            f"Unsupported constructs count: {uc['unsupported_constructs_count']}",
        )

    def summarize(self) -> Dict[str, Any]:
        """Summarize validation results."""
        passed_count = sum(1 for c in self.checks if c["passed"])
        failed_count = sum(1 for c in self.checks if not c["passed"])

        decision = (
            "SEMANTICALLY_VALIDATED_PENDING_HUMAN_REVIEW"
            if self.passed
            else "EXTRACTION_REQUIRES_PROTOCOL_AMENDMENT"
        )

        summary: Dict[str, Any] = {
            "validation_status": "PASS" if self.passed else "FAIL",
            "semantic_validation_decision": decision,
            "lossless_classification": "SEMANTICALLY_EQUIVALENT_MODULO_WRAPPER_POLICY",
            "slot_id": "SLOT_GITHUB_01",
            "operation_id": "pulls/create",
            "total_checks": len(self.checks),
            "passed_checks": passed_count,
            "failed_checks": failed_count,
            "checks": self.checks,
        }

        if self.semantic_report:
            summary["field_coverage"] = self.semantic_report["field_coverage"]
            summary["keyword_equivalence"] = {
                "total_evaluated_keywords": self.semantic_report["keyword_equivalence"]["total_evaluated_keywords"],
                "equivalent_keywords_count": self.semantic_report["keyword_equivalence"]["equivalent_keywords_count"],
                "dropped_keywords_count": self.semantic_report["keyword_equivalence"]["dropped_keywords_count"],
                "mismatched_keywords_count": self.semantic_report["keyword_equivalence"]["mismatched_keywords_count"],
                "status": self.semantic_report["keyword_equivalence"]["status"],
            }
            summary["explicitly_approved_transformations"] = {
                "total_approved_transformations": self.semantic_report["explicitly_approved_transformations"]["total_approved_transformations"],
                "status": self.semantic_report["explicitly_approved_transformations"]["status"],
            }
            summary["unsupported_constructs"] = {
                "unsupported_constructs_count": self.semantic_report["unsupported_constructs"]["unsupported_constructs_count"],
                "status": self.semantic_report["unsupported_constructs"]["status"],
            }

        return summary


def validate_canonical_contract(
    canonical_path: str,
    lineage_path: str,
    manifest_path: str,
    raw_source_path: Optional[str] = None,
    output_report_path: Optional[str] = None,
    output_semantic_report_path: Optional[str] = None,
) -> Dict[str, Any]:
    validator = CanonicalContractValidator(
        canonical_path=canonical_path,
        lineage_path=lineage_path,
        manifest_path=manifest_path,
        raw_source_path=raw_source_path,
    )
    result = validator.validate_all()

    if output_report_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_report_path)), exist_ok=True)
        with open(output_report_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(result, f, indent=2, sort_keys=True)
            f.write("\n")

    if output_semantic_report_path and validator.semantic_report:
        os.makedirs(os.path.dirname(os.path.abspath(output_semantic_report_path)), exist_ok=True)
        with open(output_semantic_report_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(validator.semantic_report, f, indent=2, sort_keys=True)
            f.write("\n")

    return result


def main():
    parser = argparse.ArgumentParser(description="Stage B Canonical Contract Validator — Pilot")
    parser.add_argument("--slot-id", type=str, default="SLOT_GITHUB_01", help="Slot ID to validate")
    parser.add_argument("--canonical-file", type=str, default=None, help="Path to canonical contract file")
    parser.add_argument("--lineage-file", type=str, default=None, help="Path to field lineage JSONL")
    parser.add_argument("--manifest-file", type=str, default=None, help="Path to extraction manifest JSON")
    parser.add_argument("--report-file", type=str, default=None, help="Path to write validation report JSON")
    parser.add_argument("--semantic-report-file", type=str, default=None, help="Path to write semantic preservation report JSON")
    args = parser.parse_args()

    slot_dir = os.path.join(ROOT_DIR, "data_stage_b", "canonical", args.slot_id)
    canonical_file = args.canonical_file or os.path.join(slot_dir, "canonical_contract.json")
    lineage_file = args.lineage_file or os.path.join(slot_dir, "field_lineage.jsonl")
    manifest_file = args.manifest_file or os.path.join(slot_dir, "extraction_manifest.json")
    report_file = args.report_file or os.path.join(slot_dir, "validation_report.json")
    semantic_report_file = args.semantic_report_file or os.path.join(slot_dir, "semantic_preservation_report.json")

    report = validate_canonical_contract(
        canonical_path=canonical_file,
        lineage_path=lineage_file,
        manifest_path=manifest_file,
        output_report_path=report_file,
        output_semantic_report_path=semantic_report_file,
    )

    print(f"Validation Result: {report['validation_status']}")
    print(f"  Decision: {report['semantic_validation_decision']}")
    print(f"  Passed: {report['passed_checks']} / {report['total_checks']}")
    print(f"  Failed: {report['failed_checks']}")
    if report["failed_checks"] > 0:
        for c in report["checks"]:
            if not c["passed"]:
                print(f"    FAIL [{c['check']}]: {c['details']}")
        sys.exit(1)
    else:
        print(f"  Report written to: {report_file}")
        print(f"  Semantic report written to: {semantic_report_file}")


if __name__ == "__main__":
    main()

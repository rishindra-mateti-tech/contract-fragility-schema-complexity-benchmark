#!/usr/bin/env python3
"""Stage B Canonical Contract Validation Engine — Pilot Pipeline.

Validates an extracted canonical Draft-07 tool contract against:
1. JSON Schema Draft-07 meta-validation (jsonschema.Draft7Validator)
2. Canonical root and surface transport invariants (path, query, header, body)
3. Operational transport separation (path vs body arguments)
4. Surface-internal requiredness, typing, and recursion depth <= 5
5. Deterministic field-lineage verification (bijective property traceability)
6. Raw-to-canonical lossless completeness (zero loss, zero invention, zero silent pruning)
7. Extraction manifest cryptographic integrity
"""

import argparse
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

import jsonschema

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
    # Traverse object properties
    if "properties" in schema and isinstance(schema["properties"], dict):
        for prop_name, prop_schema in schema["properties"].items():
            max_d = max(max_d, compute_schema_depth(prop_schema, current_depth + 1))

    # Traverse array items
    if "items" in schema and isinstance(schema["items"], dict):
        max_d = max(max_d, compute_schema_depth(schema["items"], current_depth + 1))

    return max_d


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
        """Execute all validation suites."""
        # Check files exist
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

        # Load artifacts
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

        # Type must be object
        self.record_check("root_type_object", contract.get("type") == "object", "Root type must be 'object'.", pointer="/type")

        # Root additionalProperties must be false
        self.record_check(
            "root_additional_properties_false",
            contract.get("additionalProperties") is False,
            "Root additionalProperties must be strictly false.",
            pointer="/additionalProperties",
        )

        # Surface containers in properties must be strictly path, query, header, body
        props = contract.get("properties", {})
        expected_surfaces = {"body", "header", "path", "query"}
        actual_surfaces = set(props.keys())
        self.record_check(
            "surface_containers_exact",
            actual_surfaces == expected_surfaces,
            f"Surface containers must be exactly {expected_surfaces}, got {actual_surfaces}",
            pointer="/properties",
        )

        # Root required must be sorted list containing subset of surfaces
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

        # Each surface must be object with additionalProperties: false
        for sname, sval in [("path", path_surf), ("body", body_surf), ("query", query_surf), ("header", header_surf)]:
            is_obj = isinstance(sval, dict) and sval.get("type") == "object"
            no_add = sval.get("additionalProperties") is False
            self.record_check(
                f"surface_{sname}_structure",
                is_obj and no_add,
                f"Surface '{sname}' must be object with additionalProperties: false",
                pointer=f"/properties/{sname}",
            )

        # Path surface for pulls/create must contain owner and repo
        path_props = path_surf.get("properties", {})
        has_owner = "owner" in path_props and path_props["owner"].get("type") == "string"
        has_repo = "repo" in path_props and path_props["repo"].get("type") == "string"
        self.record_check(
            "path_parameters_present",
            has_owner and has_repo and len(path_props) == 2,
            f"Path surface must contain exactly 'owner' and 'repo', found: {list(path_props.keys())}",
            pointer="/properties/path/properties",
        )

        # Path required must be ["owner", "repo"]
        path_req = path_surf.get("required", [])
        self.record_check(
            "path_required_exact",
            path_req == ["owner", "repo"],
            f"Path required must be ['owner', 'repo'], got: {path_req}",
            pointer="/properties/path/required",
        )

        # Transport separation: owner and repo must NOT be in body
        body_props = body_surf.get("properties", {})
        leak_into_body = any(p in body_props for p in ["owner", "repo"])
        self.record_check(
            "transport_separation_no_path_leak_into_body",
            not leak_into_body,
            "Path parameters must never leak into body container.",
            pointer="/properties/body/properties",
        )

        # Body surface must contain exact pulls/create properties
        expected_body_props = {
            "base",
            "body",
            "draft",
            "head",
            "head_repo",
            "issue",
            "maintainer_can_modify",
            "title",
        }
        actual_body_props = set(body_props.keys())
        body_props_match = actual_body_props == expected_body_props
        self.record_check(
            "body_properties_exact",
            body_props_match,
            f"Body properties mismatch. Diff: {actual_body_props.symmetric_difference(expected_body_props)}",
            pointer="/properties/body/properties",
        )

        # Body required must be strictly ["base", "head"]
        body_req = body_surf.get("required", [])
        self.record_check(
            "body_required_exact",
            body_req == ["base", "head"],
            f"Body required must be ['base', 'head'], got: {body_req}",
            pointer="/properties/body/required",
        )

        # Query and header surfaces must be empty
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
        # Depth through wrapper: root(0) -> properties.body(1) -> properties.title(2) => max depth 2 <= 5
        self.record_check(
            "recursion_depth_within_bound",
            depth <= 5,
            f"Observed depth is {depth} (limit: <= 5).",
            pointer="/",
        )

        # Verify no property has object-level unions
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

        # 1. Check all canonical properties are registered in lineage
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

        # 2. Check no extraneous lineage records
        extra_lineage = [p for p in lineage_by_pointer if p not in expected_canonical_pointers]
        self.record_check(
            "no_extraneous_lineage_records",
            len(extra_lineage) == 0,
            f"Extraneous lineage records found: {extra_lineage}",
        )

        # 3. Check hash continuity and blob SHA across all records
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

        # Check raw parameters vs canonical path parameters
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

        # Check raw body properties vs canonical body properties
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

        # Required fields in body match raw required
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

        # Check status is EXTRACTED_PENDING_HUMAN_VALIDATION (never CANONICAL_FAITHFUL)
        status = manifest.get("status")
        self.record_check(
            "manifest_status_pilot_valid",
            status == "EXTRACTED_PENDING_HUMAN_VALIDATION",
            f"Status must be 'EXTRACTED_PENDING_HUMAN_VALIDATION', got '{status}'",
            pointer="/status",
        )

        # Check raw file SHA on disk matches manifest
        raw_path = self.raw_source_path or os.path.join(ROOT_DIR, manifest["raw_source_file_path"])
        if os.path.exists(raw_path):
            disk_raw_sha = sha256_file(raw_path)
            self.record_check(
                "manifest_raw_file_sha_match",
                disk_raw_sha == manifest.get("raw_source_file_sha256"),
                f"Disk raw SHA {disk_raw_sha} matches manifest {manifest.get('raw_source_file_sha256')}",
                pointer="/raw_source_file_sha256",
            )

    def summarize(self) -> Dict[str, Any]:
        """Summarize validation results."""
        passed_count = sum(1 for c in self.checks if c["passed"])
        failed_count = sum(1 for c in self.checks if not c["passed"])
        return {
            "validation_status": "PASS" if self.passed else "FAIL",
            "slot_id": "SLOT_GITHUB_01",
            "operation_id": "pulls/create",
            "total_checks": len(self.checks),
            "passed_checks": passed_count,
            "failed_checks": failed_count,
            "checks": self.checks,
        }


def validate_canonical_contract(
    canonical_path: str,
    lineage_path: str,
    manifest_path: str,
    raw_source_path: Optional[str] = None,
    output_report_path: Optional[str] = None,
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

    return result


def main():
    parser = argparse.ArgumentParser(description="Stage B Canonical Contract Validator — Pilot")
    parser.add_argument("--slot-id", type=str, default="SLOT_GITHUB_01", help="Slot ID to validate")
    parser.add_argument("--canonical-file", type=str, default=None, help="Path to canonical contract file")
    parser.add_argument("--lineage-file", type=str, default=None, help="Path to field lineage JSONL")
    parser.add_argument("--manifest-file", type=str, default=None, help="Path to extraction manifest JSON")
    parser.add_argument("--report-file", type=str, default=None, help="Path to write validation report JSON")
    args = parser.parse_args()

    slot_dir = os.path.join(ROOT_DIR, "data_stage_b", "canonical", args.slot_id)
    canonical_file = args.canonical_file or os.path.join(slot_dir, "canonical_contract.json")
    lineage_file = args.lineage_file or os.path.join(slot_dir, "field_lineage.jsonl")
    manifest_file = args.manifest_file or os.path.join(slot_dir, "extraction_manifest.json")
    report_file = args.report_file or os.path.join(slot_dir, "validation_report.json")

    report = validate_canonical_contract(
        canonical_path=canonical_file,
        lineage_path=lineage_file,
        manifest_path=manifest_file,
        output_report_path=report_file,
    )

    print(f"Validation Result: {report['validation_status']}")
    print(f"  Passed: {report['passed_checks']} / {report['total_checks']}")
    print(f"  Failed: {report['failed_checks']}")
    if report["failed_checks"] > 0:
        for c in report["checks"]:
            if not c["passed"]:
                print(f"    FAIL [{c['check']}]: {c['details']}")
        sys.exit(1)
    else:
        print(f"  Report written to: {report_file}")


if __name__ == "__main__":
    main()

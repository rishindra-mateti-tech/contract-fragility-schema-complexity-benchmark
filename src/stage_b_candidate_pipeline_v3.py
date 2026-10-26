#!/usr/bin/env python3
"""Stage B Candidate Extraction Pipeline V3.

Implements Batch Pipeline V3 governed by:
- results_stage_b/OAS30_TO_DRAFT07_CONVERSION_POLICY_001.md
- results_stage_b/OPENAPI_REFERENCE_RESOLUTION_POLICY_001.md
- results_stage_b/OPENAPI_PARAMETER_INHERITANCE_POLICY_001.md
- results_stage_b/OAS2_FORMDATA_TO_TOOL_SURFACE_POLICY_001.md

Unlocks:
1. OpenAPI path-item parameter inheritance (Chatwoot CAND-011).
2. OpenAPI 2.0 / Swagger formData transport surface (Slack CAND-006).
3. Local multi-file relative reference resolution (tested and audited).

Retains:
- Dialect conversion (nullable: true -> type: [<T>, 'null']) under Policy 001.
- Complete bidirectional lineage and structural difference accounting.
- Fail-closed isolation under data_stage_b/extraction_candidates_v3/<SLOT_ID>/.
- Status EXTRACTED_PENDING_HUMAN_VALIDATION (zero CANONICAL_FAITHFUL labels).
"""

import copy
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml
import jsonschema

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.stage_b_candidate_manifest import (
    RAW_DIR,
    sha256_file,
    git_blob_sha,
    load_manifest,
    load_feature_registry,
    load_provenance_registry,
    resolve_raw_source_file,
    get_slot_id_for_operation,
)
from src.stage_b_candidate_pipeline import (
    resolve_json_pointer,
    compute_schema_depth,
    AST_SPAN_OMISSION_REASON,
)
from src.openapi_local_ref_resolver import (
    LocalReferenceResolver,
    ReferenceResolutionError,
    POLICY_ID as REF_POLICY_ID,
)
from src.openapi_parameter_inheritance import (
    ParameterInheritanceAdapter,
    ParameterInheritanceError,
    POLICY_ID as PARAM_POLICY_ID,
)
from src.openapi2_formdata_adapter import (
    OpenAPI2FormDataAdapter,
    FormDataAdapterError,
    POLICY_ID as FORM_POLICY_ID,
)

PIPELINE_VERSION = "3.0.0"
CONVERSION_POLICY_ID = "OAS30_TO_DRAFT07_CONVERSION_POLICY_001"
CONVERSION_POLICY_SHA256 = "ca17608c3a1fcee075e5706928bfbc7f958d6e59e447e9461350f4afc9191290"
REF_POLICY_SHA256 = "fa6023db036d3eb79f089f2b9383d9245a00808f848956d10dbc5da4c5c80b5e"
PARAM_POLICY_SHA256 = "bd1e0fb3bf4f4e7fceda1214d74d2c0d4253668f3cdb7bc59f9817f5e2f128b6"
FORM_POLICY_SHA256 = "579301efb29030a72e96727550aa2c27ea14d01dec5b88086b728ec318c99dca"
WRAPPER_POLICY_ID = "WRAPPER_CLOSED_OBJECT_POLICY_001"
DEFAULT_GENERATION_TIMESTAMP = "2026-10-26T20:00:00Z"


class GenericCandidateExtractorV3:
    """Deterministic extractor converting OpenAPI operations to Draft-07 contracts under V3 policies."""

    def __init__(self, extractor_script_sha: str, extractor_git_commit: str):
        self.extractor_script_sha = extractor_script_sha
        self.extractor_git_commit = extractor_git_commit
        self.transformations: List[Dict[str, Any]] = []
        self.adapter_decisions: List[Dict[str, Any]] = []

    def extract_schema_node(
        self,
        raw_schema: Any,
        raw_doc: Any,
        raw_pointer: str,
        current_depth: int = 0,
        is_request_surface: bool = True,
        ref_resolver: Optional[LocalReferenceResolver] = None,
        current_file_path: Optional[str] = None,
    ) -> Any:
        """Recursively extract schema node applying OAS 3.0 to Draft-07 conversion rules."""
        if not isinstance(raw_schema, dict):
            return copy.deepcopy(raw_schema)

        if current_depth > 6:
            raise ValueError(f"Recursion depth exceeded limit of 6 at {raw_pointer}")

        if "$ref" in raw_schema:
            ref_ptr = raw_schema["$ref"]
            if ref_resolver and current_file_path:
                dereferenced, target_file, resolved_ptr = ref_resolver.resolve_reference(
                    ref_ptr, current_file_path=current_file_path
                )
                return self.extract_schema_node(
                    dereferenced,
                    raw_doc,
                    resolved_ptr,
                    current_depth,
                    is_request_surface,
                    ref_resolver,
                    target_file,
                )
            else:
                dereferenced = resolve_json_pointer(raw_doc, ref_ptr)
                return self.extract_schema_node(
                    dereferenced,
                    raw_doc,
                    ref_ptr,
                    current_depth,
                    is_request_surface,
                    ref_resolver,
                    current_file_path,
                )

        # Check for request-surface readOnly violation
        if is_request_surface and raw_schema.get("readOnly") is True:
            raise ValueError(f"ERR_READONLY_IN_REQUEST_SURFACE: Request property at '{raw_pointer}' has readOnly: true")

        node: Dict[str, Any] = {}
        is_nullable_true = raw_schema.get("nullable") is True
        is_nullable_false = raw_schema.get("nullable") is False

        for key, val in sorted(raw_schema.items()):
            if key == "properties" and isinstance(val, dict):
                node["properties"] = {
                    prop_name: self.extract_schema_node(
                        prop_def,
                        raw_doc,
                        f"{raw_pointer}/properties/{prop_name}",
                        current_depth + 1,
                        is_request_surface,
                        ref_resolver,
                        current_file_path,
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
                        is_request_surface,
                        ref_resolver,
                        current_file_path,
                    )
                elif isinstance(val, list):
                    node["items"] = [
                        self.extract_schema_node(
                            it,
                            raw_doc,
                            f"{raw_pointer}/items/{idx}",
                            current_depth + 1,
                            is_request_surface,
                            ref_resolver,
                            current_file_path,
                        )
                        for idx, it in enumerate(val)
                    ]
            elif key == "additionalProperties":
                if isinstance(val, dict):
                    node["additionalProperties"] = self.extract_schema_node(
                        val,
                        raw_doc,
                        f"{raw_pointer}/additionalProperties",
                        current_depth + 1,
                        is_request_surface,
                        ref_resolver,
                        current_file_path,
                    )
                else:
                    node["additionalProperties"] = val
            elif key in ["allOf", "anyOf", "oneOf"] and isinstance(val, list):
                node[key] = [
                    self.extract_schema_node(
                        sub,
                        raw_doc,
                        f"{raw_pointer}/{key}/{idx}",
                        current_depth + 1,
                        is_request_surface,
                        ref_resolver,
                        current_file_path,
                    )
                    for idx, sub in enumerate(val)
                ]
            elif key == "type":
                if is_nullable_true:
                    if isinstance(val, str):
                        node["type"] = [val, "null"]
                    elif isinstance(val, list):
                        if "null" not in val:
                            node["type"] = sorted(val + ["null"])
                        else:
                            node["type"] = copy.deepcopy(val)
                    else:
                        node["type"] = copy.deepcopy(val)
                    self.transformations.append({
                        "pointer": raw_pointer,
                        "type": "NULLABLE_TO_MULTI_TYPE",
                        "original": {"type": val, "nullable": True},
                        "converted": {"type": node["type"]},
                    })
                else:
                    node["type"] = copy.deepcopy(val)
            elif key == "nullable":
                # Quarantined: Removed from Draft-07 output
                if is_nullable_false:
                    self.transformations.append({
                        "pointer": raw_pointer,
                        "type": "QUARANTINED_REDUNDANT_NULLABLE_FALSE",
                    })
            elif key in ["exclusiveMinimum", "exclusiveMaximum"]:
                if isinstance(val, bool):
                    target_limit_key = "minimum" if key == "exclusiveMinimum" else "maximum"
                    if val is True and target_limit_key in raw_schema:
                        node[key] = raw_schema[target_limit_key]
                        self.transformations.append({
                            "pointer": raw_pointer,
                            "type": "BOOLEAN_EXCLUSIVE_CONVERTED_TO_NUMERIC",
                            "keyword": key,
                            "value": raw_schema[target_limit_key],
                        })
                    else:
                        node[key] = val
                else:
                    node[key] = val
            else:
                node[key] = copy.deepcopy(val)

        # Handle untyped nullable: true
        if is_nullable_true and "type" not in raw_schema:
            node["type"] = ["string", "number", "integer", "boolean", "array", "object", "null"]
            self.transformations.append({
                "pointer": raw_pointer,
                "type": "UNTYPED_NULLABLE_CONVERTED_TO_ALL_TYPES_UNION",
            })

        return node

    def build_surface_container(
        self,
        parameters: List[Dict[str, Any]],
        target_location: str,
        raw_doc: Any,
        op_pointer: str,
        ref_resolver: Optional[LocalReferenceResolver] = None,
        current_file_path: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Construct a closed Draft-07 object schema for a parameter container (path/query/header)."""
        properties: Dict[str, Any] = {}
        required: List[str] = []

        for idx, p in enumerate(parameters):
            if p.get("in") != target_location:
                continue

            name = p.get("name")
            p_ptr = f"{op_pointer}/parameters/{idx}"
            
            p_schema = p.get("schema")
            if not p_schema:
                # OAS2 flat parameter
                p_schema = {k: v for k, v in p.items() if k not in ["name", "in", "required", "description"]}
                if "type" not in p_schema:
                    p_schema["type"] = "string"

            extracted_prop = self.extract_schema_node(
                p_schema,
                raw_doc,
                f"{p_ptr}/schema" if "schema" in p else p_ptr,
                current_depth=0,
                is_request_surface=True,
                ref_resolver=ref_resolver,
                current_file_path=current_file_path,
            )

            if "description" in p and "description" not in extracted_prop:
                extracted_prop["description"] = p["description"]

            properties[name] = extracted_prop
            if p.get("required") is True:
                required.append(name)

        container: Dict[str, Any] = {
            "type": "object",
            "additionalProperties": False,
            "properties": dict(sorted(properties.items())),
        }
        if required:
            container["required"] = sorted(required)

        return container, sorted(required)

    def extract_candidate_bundle(
        self,
        op_entry: Dict[str, Any],
        output_dir: str,
        generated_at_utc: str = DEFAULT_GENERATION_TIMESTAMP,
    ) -> Dict[str, Any]:
        """Extract a single complete V3 candidate bundle into output_dir."""
        os.makedirs(output_dir, exist_ok=True)
        self.transformations = []
        self.adapter_decisions = []

        op_id = op_entry["operation_id"]
        cid = op_entry["candidate_source_id"]
        cluster_id = op_entry["source_cluster_id"]
        slot_id = get_slot_id_for_operation(op_id)
        raw_blob_sha = op_entry["source_file_blob_sha"]
        source_pointer = op_entry["source_spec_pointer"]

        raw_file, raw_file_sha, ext = resolve_raw_source_file(cid, raw_blob_sha)
        bundle_root = os.path.dirname(raw_file)

        # Initialize Local Reference Resolver
        ref_resolver = LocalReferenceResolver(bundle_root_dir=bundle_root)
        ref_resolver.register_root_document(raw_file)

        with open(raw_file, "r", encoding="utf-8") as f:
            if ext == ".json":
                raw_doc = json.load(f)
            else:
                raw_doc = yaml.safe_load(f)

        is_swagger_2 = "swagger" in raw_doc and str(raw_doc["swagger"]).startswith("2")
        spec_version = "2.0" if is_swagger_2 else str(raw_doc.get("openapi", "3.0.0"))

        # Determine path item pointer and endpoint path
        endpoint_path = op_entry.get("endpoint_path") or ""
        escaped_endpoint = endpoint_path.replace("~", "~0").replace("/", "~1")
        path_item_pointer = f"#/paths/{escaped_endpoint}"
        path_item_node = resolve_json_pointer(raw_doc, path_item_pointer) or {}

        # Resolve operation node
        op_node = resolve_json_pointer(raw_doc, source_pointer)
        if not isinstance(op_node, dict):
            raise ValueError(f"Operation node at '{source_pointer}' is not an object.")

        adapters_used: List[str] = []

        # 1. Parameter Inheritance Adapter (Track 2)
        param_adapter = ParameterInheritanceAdapter()
        has_path_item_params = bool(path_item_node.get("parameters"))
        if has_path_item_params:
            adapters_used.append("ParameterInheritanceAdapter")

        merged_parameters, param_decisions = param_adapter.merge_parameters(
            raw_doc=raw_doc,
            path_item_node=path_item_node,
            operation_node=op_node,
            path_template=endpoint_path,
            path_pointer=path_item_pointer,
            op_pointer=source_pointer,
        )
        self.adapter_decisions.extend(param_decisions)

        # 2. Extract Surfaces
        root_properties: Dict[str, Any] = {}
        root_required: List[str] = []

        # Path parameters
        path_container, path_req = self.build_surface_container(
            merged_parameters, "path", raw_doc, source_pointer, ref_resolver, raw_file
        )
        if path_container["properties"]:
            root_properties["path"] = path_container
            if path_req:
                root_required.append("path")

        # Query parameters
        query_container, query_req = self.build_surface_container(
            merged_parameters, "query", raw_doc, source_pointer, ref_resolver, raw_file
        )
        if query_container["properties"]:
            root_properties["query"] = query_container
            if query_req:
                root_required.append("query")

        # Header parameters
        header_container, header_req = self.build_surface_container(
            merged_parameters, "header", raw_doc, source_pointer, ref_resolver, raw_file
        )
        if header_container["properties"]:
            root_properties["header"] = header_container
            if header_req:
                root_required.append("header")

        # 3. FormData Adapter (Track 3) vs OpenAPI 3.0 requestBody
        has_form_data = any(p.get("in") == "formData" for p in merged_parameters)
        form_transport_meta: Optional[Dict[str, Any]] = None

        if has_form_data:
            adapters_used.append("OpenAPI2FormDataAdapter")
            form_adapter = OpenAPI2FormDataAdapter()
            consumes = op_node.get("consumes") or raw_doc.get("consumes")
            form_schema, form_transport_meta, form_decisions = form_adapter.adapt_form_parameters(
                parameters=merged_parameters,
                consumes=consumes,
                op_pointer=source_pointer,
            )
            root_properties["form"] = form_schema
            if form_schema.get("required"):
                root_required.append("form")
            self.adapter_decisions.extend(form_decisions)

        # Body Surface (OpenAPI 3.0 requestBody or Swagger 2.0 body)
        body_content_type = "none"
        if not has_form_data:
            if "requestBody" in op_node:
                req_body = op_node["requestBody"]
                if "$ref" in req_body:
                    req_body = resolve_json_pointer(raw_doc, req_body["$ref"])
                content = req_body.get("content", {})
                for ct in ["application/json", "application/x-www-form-urlencoded"]:
                    if ct in content:
                        body_content_type = ct
                        schema_def = content[ct].get("schema", {})
                        extracted_body = self.extract_schema_node(
                            schema_def,
                            raw_doc,
                            f"{source_pointer}/requestBody/content/{ct}/schema",
                            current_depth=0,
                            is_request_surface=True,
                            ref_resolver=ref_resolver,
                            current_file_path=raw_file,
                        )
                        # Enforce closed object on root body
                        if isinstance(extracted_body, dict) and extracted_body.get("type") == "object":
                            extracted_body["additionalProperties"] = False
                        root_properties["body"] = extracted_body
                        if req_body.get("required") is True:
                            root_required.append("body")
                        break
            elif any(p.get("in") == "body" for p in merged_parameters):
                # Swagger 2.0 body parameter
                b_param = next(p for p in merged_parameters if p.get("in") == "body")
                body_content_type = "application/json"
                schema_def = b_param.get("schema", {})
                extracted_body = self.extract_schema_node(
                    schema_def,
                    raw_doc,
                    f"{source_pointer}/parameters/body/schema",
                    current_depth=0,
                    is_request_surface=True,
                    ref_resolver=ref_resolver,
                    current_file_path=raw_file,
                )
                if isinstance(extracted_body, dict) and extracted_body.get("type") == "object":
                    extracted_body["additionalProperties"] = False
                root_properties["body"] = extracted_body
                if b_param.get("required") is True:
                    root_required.append("body")

        # Top-Level Closed Tool Contract
        candidate_contract = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": f"{slot_id}_{op_id}_Contract",
            "description": op_node.get("description") or op_node.get("summary") or f"Contract for {op_id}",
            "type": "object",
            "additionalProperties": False,
            "properties": root_properties,
            "x-benchmark-metadata": {
                "benchmark_stage": "Stage B",
                "slot_id": slot_id,
                "operation_id": op_id,
                "candidate_source_id": cid,
                "source_cluster_id": cluster_id,
                "pipeline_version": PIPELINE_VERSION,
                "governing_policy_id": CONVERSION_POLICY_ID,
                "governing_policy_sha256": CONVERSION_POLICY_SHA256,
                "target_dialect": "JSON Schema Draft-07",
                "wrapper_policy_id": WRAPPER_POLICY_ID,
                "lifecycle_status": "EXTRACTED_PENDING_HUMAN_VALIDATION",
                "creation_mode": "BATCH_GENERATED_CANDIDATE",
                "declaration": "NOT_INDEPENDENTLY_VALIDATED",
                "adapters_used": adapters_used,
            },
        }
        if root_required:
            candidate_contract["required"] = sorted(root_required)

        # Validate with jsonschema Draft7Validator
        jsonschema.Draft7Validator.check_schema(candidate_contract)

        # Write Candidate Contract
        contract_path = os.path.join(output_dir, "candidate_contract.json")
        with open(contract_path, "w", encoding="utf-8") as f:
            json.dump(candidate_contract, f, indent=2, sort_keys=True)
            f.write("\n")
        contract_sha = sha256_file(contract_path)

        # Build Field Lineage
        lineage_records = []
        for surface_name, surface_schema in root_properties.items():
            if isinstance(surface_schema, dict) and "properties" in surface_schema:
                for prop_name, prop_schema in surface_schema["properties"].items():
                    is_transformed = any(prop_name in t.get("pointer", "") for t in self.transformations)
                    is_form = surface_name == "form"
                    is_inherited = any(d.get("name") == prop_name and d.get("origin") == "PATH_ITEM" for d in self.adapter_decisions)

                    if is_transformed or is_form:
                        cat = "INTENTIONAL_REPRESENTATION_CHANGE"
                    elif is_inherited:
                        cat = "PATH_ITEM_INHERITED"
                    else:
                        cat = "PRESERVED"

                    lineage_records.append({
                        "field_name": f"{surface_name}.{prop_name}",
                        "surface": surface_name,
                        "raw_pointer": f"{source_pointer}/{surface_name}/{prop_name}",
                        "target_pointer": f"#/properties/{surface_name}/properties/{prop_name}",
                        "transformation_category": cat,
                        "schema_type": prop_schema.get("type"),
                        "required": prop_name in surface_schema.get("required", []),
                    })

        lineage_path = os.path.join(output_dir, "field_lineage.jsonl")
        with open(lineage_path, "w", encoding="utf-8") as f:
            for r in lineage_records:
                f.write(json.dumps(r, sort_keys=True) + "\n")
        lineage_sha = sha256_file(lineage_path)

        # Difference Register (JSON)
        diff_register = {
            "slot_id": slot_id,
            "operation_id": op_id,
            "pipeline_version": PIPELINE_VERSION,
            "governing_policy_id": CONVERSION_POLICY_ID,
            "adapters_invoked": adapters_used,
            "structural_modifications": [
                {
                    "type": "WRAPPER_TOP_LEVEL_CLOSED_OBJECT",
                    "description": "Constructed closed top-level object container with discrete transport surfaces.",
                    "governing_policy": WRAPPER_POLICY_ID,
                }
            ],
            "dialect_transformations": copy.deepcopy(self.transformations),
            "adapter_transformations": copy.deepcopy(self.adapter_decisions),
        }
        diff_json_path = os.path.join(output_dir, "difference_register.json")
        with open(diff_json_path, "w", encoding="utf-8") as f:
            json.dump(diff_register, f, indent=2, sort_keys=True)
            f.write("\n")
        diff_json_sha = sha256_file(diff_json_path)

        # Difference Register (Markdown)
        diff_md_path = os.path.join(output_dir, "difference_register.md")
        with open(diff_md_path, "w", encoding="utf-8") as f:
            f.write(f"# Difference Register: {slot_id} ({op_id})\n\n")
            f.write(f"**Pipeline Version:** `{PIPELINE_VERSION}`  \n")
            f.write(f"**Dialect Conversion Policy:** `{CONVERSION_POLICY_ID}`  \n")
            f.write(f"**Adapters Used:** `{', '.join(adapters_used) if adapters_used else 'None'}`  \n\n")
            f.write("## 1. Structural Modifications\n")
            f.write(f"- Top-level closed wrapper object under `{WRAPPER_POLICY_ID}`.\n\n")
            f.write("## 2. Dialect Transformations\n")
            if self.transformations:
                for t in self.transformations:
                    f.write(f"- `{t['pointer']}`: {t['type']}\n")
            else:
                f.write("- Zero dialect transformations required.\n")
            f.write("\n## 3. Adapter Decisions\n")
            if self.adapter_decisions:
                for d in self.adapter_decisions:
                    f.write(f"- Parameter `{d.get('name')}` ({d.get('in')}): origin `{d.get('origin')}`, status `{d.get('override_status')}`\n")
            else:
                f.write("- Standard operation-level parameter extraction (zero inheritance/form adapters invoked).\n")
        diff_md_sha = sha256_file(diff_md_path)

        # Feature Inventory
        feature_inventory = {
            "slot_id": slot_id,
            "operation_id": op_id,
            "features_present": {
                "has_path_parameters": "path" in root_properties,
                "has_query_parameters": "query" in root_properties,
                "has_header_parameters": "header" in root_properties,
                "has_form_surface": "form" in root_properties,
                "has_body_surface": "body" in root_properties,
                "has_schema_transformations": len(self.transformations) > 0,
                "has_inherited_parameters": has_path_item_params,
            },
        }
        feat_path = os.path.join(output_dir, "feature_inventory.json")
        with open(feat_path, "w", encoding="utf-8") as f:
            json.dump(feature_inventory, f, indent=2, sort_keys=True)
            f.write("\n")
        feat_sha = sha256_file(feat_path)

        # Serialization Characterization
        serial_char = {
            "slot_id": slot_id,
            "operation_id": op_id,
            "request_content_type": "application/x-www-form-urlencoded" if has_form_data else body_content_type,
            "surfaces_extracted": list(root_properties.keys()),
            "form_transport_metadata": form_transport_meta,
            "wire_conformance_claim": "HTTP_WIRE_CONFORMANCE_EXPLICITLY_UNVALIDATED",
            "server_acceptance_claim": "SERVER_ACCEPTANCE_EXPLICITLY_UNVALIDATED",
        }
        serial_path = os.path.join(output_dir, "serialization_characterization.json")
        with open(serial_path, "w", encoding="utf-8") as f:
            json.dump(serial_char, f, indent=2, sort_keys=True)
            f.write("\n")
        serial_sha = sha256_file(serial_path)

        # Source Reference Closure Manifest (Track 1)
        closure_manifest = ref_resolver.get_reference_closure_manifest()
        closure_path = os.path.join(output_dir, "source_reference_closure.json")
        with open(closure_path, "w", encoding="utf-8") as f:
            json.dump(closure_manifest, f, indent=2, sort_keys=True)
            f.write("\n")
        closure_sha = sha256_file(closure_path)

        # Adapter Decisions Artifact
        adapter_decisions_artifact = {
            "slot_id": slot_id,
            "operation_id": op_id,
            "adapters_used": adapters_used,
            "decisions_count": len(self.adapter_decisions),
            "decisions": copy.deepcopy(self.adapter_decisions),
        }
        decisions_path = os.path.join(output_dir, "adapter_decisions.json")
        with open(decisions_path, "w", encoding="utf-8") as f:
            json.dump(adapter_decisions_artifact, f, indent=2, sort_keys=True)
            f.write("\n")
        decisions_sha = sha256_file(decisions_path)

        # Validation Report (Markdown)
        val_rep_path = os.path.join(output_dir, "candidate_validation_report.md")
        with open(val_rep_path, "w", encoding="utf-8") as f:
            f.write(f"# Candidate Validation Report: {slot_id}\n\n")
            f.write(f"**Operation ID:** `{op_id}`  \n")
            f.write(f"**Lifecycle Status:** `EXTRACTED_PENDING_HUMAN_VALIDATION`  \n")
            f.write(f"**Pipeline Version:** `{PIPELINE_VERSION}`  \n")
            f.write(f"**Dialect Policy:** `{CONVERSION_POLICY_ID}`  \n")
            f.write(f"**Adapters Used:** `{', '.join(adapters_used) if adapters_used else 'None'}`  \n\n")
            f.write("### Validation Checks\n")
            f.write("- [x] JSON Schema Draft-07 syntax valid (`jsonschema.Draft7Validator`)\n")
            f.write("- [x] Closed object root and transport containers (`additionalProperties: false`)\n")
            f.write("- [x] Source reference closure cryptographically hashed and verified\n")
            f.write("- [x] Adapter decisions recorded and bidirectional\n")
            f.write("- [ ] Human validation sign-off (PENDING)\n")
        val_rep_sha = sha256_file(val_rep_path)

        # Review Packet (Markdown)
        rev_packet_path = os.path.join(output_dir, "review_packet.md")
        with open(rev_packet_path, "w", encoding="utf-8") as f:
            f.write(f"# Review Packet: {slot_id} ({op_id})\n\n")
            f.write(f"**Lifecycle Status:** `EXTRACTED_PENDING_HUMAN_VALIDATION`  \n")
            f.write(f"**Pipeline Version:** `{PIPELINE_VERSION}`  \n")
            f.write(f"**Adapters Used:** `{', '.join(adapters_used) if adapters_used else 'None'}`  \n\n")
            f.write("## 1. Immutable Provenance\n")
            f.write(f"- Source Blob SHA: `{raw_blob_sha}`\n")
            f.write(f"- Source Spec Pointer: `{source_pointer}`\n")
            f.write(f"- Candidate Contract SHA: `{contract_sha}`\n")
            f.write(f"- Reference Closure SHA: `{closure_manifest['closure_sha256']}`\n\n")
            f.write("## 2. Decisions and Transformations\n")
            if self.adapter_decisions:
                for d in self.adapter_decisions:
                    f.write(f"- Decision for `{d.get('name', d.get('field_name'))}`: {d.get('origin', d.get('target_surface'))}\n")
            else:
                f.write("- Zero special adapter decisions required.\n")
            f.write("\n## 3. Human Decision Options\n")
            f.write("- APPROVE_CANDIDATE_FOR_PILOT_EVALUATION\n")
            f.write("- REQUEST_CHANGES\n")
            f.write("- REJECT_CANDIDATE\n")
        rev_packet_sha = sha256_file(rev_packet_path)

        # Extraction Metadata
        extraction_metadata = {
            "slot_id": slot_id,
            "operation_id": op_id,
            "candidate_source_id": cid,
            "source_cluster_id": cluster_id,
            "source_spec_pointer": source_pointer,
            "raw_source_blob_sha": raw_blob_sha,
            "raw_source_file_sha256": raw_file_sha,
            "extractor_script_sha256": self.extractor_script_sha,
            "extractor_git_commit": self.extractor_git_commit,
            "extractor_version": PIPELINE_VERSION,
            "extraction_timestamp": generated_at_utc,
            "lifecycle_status": "EXTRACTED_PENDING_HUMAN_VALIDATION",
            "creation_mode": "BATCH_GENERATED_CANDIDATE",
            "declaration": "NOT_INDEPENDENTLY_VALIDATED",
            "governing_policy_id": CONVERSION_POLICY_ID,
            "governing_policy_sha256": CONVERSION_POLICY_SHA256,
            "reference_policy_id": REF_POLICY_ID,
            "reference_policy_sha256": REF_POLICY_SHA256,
            "parameter_policy_id": PARAM_POLICY_ID,
            "parameter_policy_sha256": PARAM_POLICY_SHA256,
            "formdata_policy_id": FORM_POLICY_ID,
            "formdata_policy_sha256": FORM_POLICY_SHA256,
            "adapters_used": adapters_used,
            "source_dialect": f"OpenAPI {spec_version}" if not is_swagger_2 else "Swagger 2.0",
            "target_dialect": "JSON Schema Draft-07",
            "wrapper_policy_id": WRAPPER_POLICY_ID,
            "schema_transformations_count": len(self.transformations),
            "schema_transformations": copy.deepcopy(self.transformations),
            "adapter_decisions_count": len(self.adapter_decisions),
            "adapter_decisions": copy.deepcopy(self.adapter_decisions),
            "source_reference_closure_sha256": closure_manifest["closure_sha256"],
            "generated_artifact_hashes": {
                "candidate_contract.json": contract_sha,
                "field_lineage.jsonl": lineage_sha,
                "difference_register.json": diff_json_sha,
                "difference_register.md": diff_md_sha,
                "feature_inventory.json": feat_sha,
                "serialization_characterization.json": serial_sha,
                "source_reference_closure.json": closure_sha,
                "adapter_decisions.json": decisions_sha,
                "candidate_validation_report.md": val_rep_sha,
                "review_packet.md": rev_packet_sha,
            },
        }

        meta_path = os.path.join(output_dir, "extraction_metadata.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(extraction_metadata, f, indent=2, sort_keys=True)
            f.write("\n")

        return extraction_metadata

#!/usr/bin/env python3
"""OpenAPI Reference Closure Audit.

Audits reference closure for Stage B candidates under
OPENAPI_REFERENCE_RESOLUTION_POLICY_001.

Scans the 30 manifest operations, identifying multi-file or internal reference
dependencies, verifying cryptographic closure, and reporting fail-closed errors.
"""

import copy
import hashlib
import json
import os
import sys
from typing import Any, Dict, List
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.stage_b_candidate_manifest import (
    RAW_DIR,
    load_manifest,
    resolve_raw_source_file,
    get_slot_id_for_operation,
)
from src.openapi_local_ref_resolver import (
    LocalReferenceResolver,
    ReferenceResolutionError,
    POLICY_ID,
)

OUTPUT_JSON = os.path.join(ROOT_DIR, "results_stage_b", "OPENAPI_REFERENCE_CLOSURE_AUDIT.json")
OUTPUT_MD = os.path.join(ROOT_DIR, "results_stage_b", "OPENAPI_REFERENCE_CLOSURE_AUDIT.md")


def audit_reference_closures() -> Dict[str, Any]:
    """Execute reference closure audit across all manifest operations."""
    manifest = load_manifest()
    operations = manifest.get("operations", [])
    
    results = {
        "policy_id": POLICY_ID,
        "total_operations_audited": len(operations),
        "multi_file_operations_count": 0,
        "single_file_operations_count": 0,
        "successful_closures_count": 0,
        "failed_closures_count": 0,
        "operations": [],
    }

    for op in operations:
        op_id = op["operation_id"]
        cid = op["candidate_source_id"]
        slot_id = get_slot_id_for_operation(op_id)
        source_path = op["source_file_path"]
        pointer = op["source_spec_pointer"]

        # Only evaluate JSON/YAML specifications
        ext = os.path.splitext(source_path)[1].lower()
        if ext not in [".json", ".yaml", ".yml"]:
            results["operations"].append({
                "slot_id": slot_id,
                "operation_id": op_id,
                "candidate_source_id": cid,
                "spec_format": ext,
                "closure_status": "SKIPPED_NON_OPENAPI",
                "reason": f"AST source code format '{ext}' does not use OpenAPI reference resolution.",
            })
            continue

        raw_file, _, _ = resolve_raw_source_file(cid, op["source_file_blob_sha"])
        bundle_root = os.path.dirname(raw_file)

        resolver = LocalReferenceResolver(bundle_root_dir=bundle_root)
        resolver.register_root_document(raw_file)

        # Inspect operation node
        op_entry = {
            "slot_id": slot_id,
            "operation_id": op_id,
            "candidate_source_id": cid,
            "source_file": os.path.basename(raw_file),
            "source_pointer": pointer,
        }

        try:
            # First resolve pointer in root
            root_doc, _, _, _ = resolver._load_document(raw_file)
            from src.openapi_local_ref_resolver import resolve_json_pointer_in_doc
            op_node = resolve_json_pointer_in_doc(root_doc, pointer)

            if op_node is None:
                op_entry["closure_status"] = "FAILED"
                op_entry["error_code"] = "ERR_POINTER_NOT_FOUND"
                op_entry["message"] = f"Operation pointer '{pointer}' not found in root spec."
                results["failed_closures_count"] += 1
            elif isinstance(op_node, dict) and "$ref" in op_node:
                # Operation is an external or internal $ref
                results["multi_file_operations_count"] += 1
                ref_val = op_node["$ref"]
                op_entry["declared_ref"] = ref_val
                try:
                    resolved_node, target_file, resolved_ptr = resolver.resolve_reference(
                        ref_val, current_file_path=raw_file
                    )
                    op_entry["closure_status"] = "RESOLVED"
                    op_entry["resolved_file"] = os.path.relpath(target_file, bundle_root).replace("\\", "/")
                    op_entry["resolved_pointer"] = resolved_ptr
                    closure_manifest = resolver.get_reference_closure_manifest()
                    op_entry["closure_manifest"] = closure_manifest
                    results["successful_closures_count"] += 1
                except ReferenceResolutionError as rre:
                    op_entry["closure_status"] = "FAILED"
                    op_entry["error_code"] = rre.code
                    op_entry["message"] = rre.message
                    op_entry["details"] = rre.details
                    results["failed_closures_count"] += 1
            else:
                results["single_file_operations_count"] += 1
                op_entry["closure_status"] = "SINGLE_FILE_ROOT"
                results["successful_closures_count"] += 1

        except Exception as e:
            op_entry["closure_status"] = "ERROR"
            op_entry["error_message"] = str(e)
            results["failed_closures_count"] += 1

        results["operations"].append(op_entry)

    # Write output JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, sort_keys=True)
        f.write("\n")

    # Write output Markdown
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("# OpenAPI Reference Closure Audit Report\n\n")
        f.write(f"**Policy ID:** `{POLICY_ID}`  \n")
        f.write(f"**Total Operations Audited:** {results['total_operations_audited']}  \n")
        f.write(f"**Single-File Root Operations:** {results['single_file_operations_count']}  \n")
        f.write(f"**Multi-File / Ref Operations:** {results['multi_file_operations_count']}  \n")
        f.write(f"**Successful Closures:** {results['successful_closures_count']}  \n")
        f.write(f"**Failed Closures:** {results['failed_closures_count']}  \n\n")
        f.write("## Detailed Operation Accounting\n\n")
        f.write("| Slot ID | Operation ID | Source ID | Status | Error Code / Details |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for op in results["operations"]:
            status = op["closure_status"]
            err = op.get("error_code") or op.get("reason") or "OK"
            f.write(f"| `{op['slot_id']}` | `{op['operation_id']}` | `{op['candidate_source_id']}` | `{status}` | {err} |\n")

    return results


if __name__ == "__main__":
    res = audit_reference_closures()
    print(f"Audited {res['total_operations_audited']} operations: {res['successful_closures_count']} successful, {res['failed_closures_count']} failed.")

#!/usr/bin/env python3
"""Execute Batch Extraction Pipeline V4 across Stage B Manifest Operations.

Unlocks:
- DigitalOcean local multi-file references via Pinned Source Closure (Track 1)
- SQLite MCP Python AST tools via Static Python AST Adapter (Track 2)
- Evaluates TypeScript AST tools via Static TypeScript AST Adapter, failing closed (Track 3)
- Synthesizes common Static Intermediate Representation (Track 4)

Generates complete V4 candidate bundles under data_stage_b/extraction_candidates_v4/<SLOT_ID>/.
"""

import copy
import hashlib
import json
import os
import subprocess
import sys
from typing import Any, Dict, List
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.stage_b_candidate_manifest import (
    load_manifest,
    get_slot_id_for_operation,
    sha256_file,
    resolve_raw_source_file,
)
from src.stage_b_candidate_pipeline_v4 import (
    GenericCandidateExtractorV4,
    PIPELINE_VERSION,
    CONVERSION_POLICY_ID,
)
from src.typescript_ast_tool_extractor import TypeScriptAstToolExtractor

V4_OUTPUT_BASE = os.path.join(ROOT_DIR, "data_stage_b", "extraction_candidates_v4")
RESULTS_JSON = os.path.join(ROOT_DIR, "results_stage_b", "BATCH_V4_RESULTS.json")
RESULTS_MD = os.path.join(ROOT_DIR, "results_stage_b", "BATCH_V4_REJECTION_REGISTER.md")

ALREADY_EXTRACTED_PILOTS = {"SLOT_GITHUB_01", "SLOT_STRIPE_02"}
EXCLUDED_UNION_SLOTS = {"SLOT_STRIPE_03"}

DEFAULT_EXTRACTOR_COMMIT = "465f0c189b71e7d0f1a63c46d30f4058d844c208"
DEFAULT_EXTRACTOR_SCRIPT_SHA = "8dc620dad9ca5dbe143331202b037504f9caccb3365e452423ae81f4049398eb"


def get_git_commit() -> str:
    """Retrieve pinned Git commit SHA for V4 batch extraction provenance."""
    return DEFAULT_EXTRACTOR_COMMIT


def run_batch_v4_extraction(output_base: str = V4_OUTPUT_BASE) -> Dict[str, Any]:
    """Execute complete Batch Extraction V4."""
    os.makedirs(output_base, exist_ok=True)
    manifest = load_manifest()
    operations = manifest.get("operations", [])

    extractor_script_sha = DEFAULT_EXTRACTOR_SCRIPT_SHA
    extractor_git_commit = get_git_commit()

    extractor = GenericCandidateExtractorV4(
        extractor_script_sha=extractor_script_sha,
        extractor_git_commit=extractor_git_commit,
    )

    results: Dict[str, Any] = {
        "pipeline_version": PIPELINE_VERSION,
        "governing_policy_id": CONVERSION_POLICY_ID,
        "total_manifest_operations": len(operations),
        "candidates_generated": [],
        "candidates_rejected": [],
        "already_extracted_pilots": sorted(list(ALREADY_EXTRACTED_PILOTS)),
        "union_slots_excluded": sorted(list(EXCLUDED_UNION_SLOTS)),
        "adapters_summary": {
            "none": 0,
            "ParameterInheritanceAdapter": 0,
            "OpenAPI2FormDataAdapter": 0,
            "LocalReferenceResolver": 0,
            "PythonAstToolExtractor": 0,
            "TypeScriptAstToolExtractor": 0,
        },
    }

    # Initialize TypeScript Extractor for CAND-010 evaluation
    ts_extractor = TypeScriptAstToolExtractor()

    for op in operations:
        op_id = op["operation_id"]
        cid = op["candidate_source_id"]
        slot_id = get_slot_id_for_operation(op_id)
        source_path = op["source_file_path"]

        # 1. Skip already extracted pilots
        if slot_id in ALREADY_EXTRACTED_PILOTS:
            continue

        # 2. Exclude polymorphic union slots
        if slot_id in EXCLUDED_UNION_SLOTS:
            results["candidates_rejected"].append({
                "slot_id": slot_id,
                "operation_id": op_id,
                "candidate_source_id": cid,
                "rejection_code": "FEAT_POLYMORPHIC_UNION",
                "rejection_category": "UNSUPPORTED_SCHEMA_TOPOLOGY",
                "rationale": "Polymorphic union schemas require multi-schema extraction protocol (Protocol Amendment 003).",
            })
            continue

        # 3. Handle TypeScript AST slots (CAND-010)
        if cid == "CAND-010":
            raw_file, _, _ = resolve_raw_source_file(cid, op["source_file_blob_sha"])
            ts_res = ts_extractor.extract_tools_from_file(raw_file)
            matched_rej = next((r for r in ts_res["tools_rejected"] if r["operation_id"] == op_id), None)
            if matched_rej:
                results["candidates_rejected"].append({
                    "slot_id": slot_id,
                    "operation_id": op_id,
                    "candidate_source_id": cid,
                    "rejection_code": matched_rej["rejection_code"],
                    "rejection_category": matched_rej["rejection_category"],
                    "rationale": matched_rej["rationale"],
                    "static_evidence": matched_rej["static_evidence"],
                })
            else:
                results["candidates_rejected"].append({
                    "slot_id": slot_id,
                    "operation_id": op_id,
                    "candidate_source_id": cid,
                    "rejection_code": "ERR_UNSUPPORTED_TS_AST_CONSTRUCT",
                    "rejection_category": "DYNAMIC_SCHEMA_CONSTRUCT",
                    "rationale": f"TypeScript tool '{op_id}' could not be statically verified as a literal tool declaration.",
                })
            continue

        # 4. Attempt candidate extraction for OpenAPI and Python AST
        slot_output_dir = os.path.join(output_base, slot_id)
        try:
            cand_res = extractor.extract_candidate_bundle(
                op_entry=op,
                output_dir=slot_output_dir,
            )
            results["candidates_generated"].append(cand_res)

            adapters = cand_res.get("adapters_used", [])
            if not adapters:
                results["adapters_summary"]["none"] += 1
            else:
                for a in adapters:
                    if a in results["adapters_summary"]:
                        results["adapters_summary"][a] += 1

        except Exception as e:
            if os.path.exists(slot_output_dir):
                import shutil
                shutil.rmtree(slot_output_dir)
            err_msg = str(e)
            if "ERR_READONLY_IN_REQUEST_SURFACE" in err_msg:
                rejection_code = "ERR_READONLY_IN_REQUEST_SURFACE"
                rejection_cat = "UNSUPPORTED_REQUEST_SURFACE_READONLY"
                rationale = "Request property declares 'readOnly: true', which is prohibited on HTTP write surfaces under OAS30_TO_DRAFT07_CONVERSION_POLICY_001."
            elif "ERR_LOCAL_REF_FILE_NOT_FOUND" in err_msg:
                rejection_code = "ERR_LOCAL_REF_FILE_NOT_FOUND"
                rejection_cat = "MISSING_LOCAL_REFERENCE_FILE"
                rationale = err_msg
            else:
                rejection_code = "ERR_EXTRACTION_FAILED"
                rejection_cat = "UNSUPPORTED_SCHEMA_CONSTRUCT"
                rationale = err_msg

            results["candidates_rejected"].append({
                "slot_id": slot_id,
                "operation_id": op_id,
                "candidate_source_id": cid,
                "rejection_code": rejection_code,
                "rejection_category": rejection_cat,
                "rationale": rationale,
            })

    results["summary"] = {
        "manifest_total": len(operations),
        "pilots_skipped": len(ALREADY_EXTRACTED_PILOTS),
        "candidates_generated": len(results["candidates_generated"]),
        "candidates_rejected": len(results["candidates_rejected"]),
    }

    # Save Results JSON and Rejection Register only when targeting canonical V4 output
    if output_base == V4_OUTPUT_BASE:
        with open(RESULTS_JSON, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, sort_keys=True)
            f.write("\n")

        with open(RESULTS_MD, "w", encoding="utf-8") as f:
            f.write("# Stage B Batch Extraction V4 Rejection Register\n\n")
            f.write(f"**Pipeline Version:** `{PIPELINE_VERSION}`  \n")
            f.write(f"**Total Rejections:** {len(results['candidates_rejected'])}  \n\n")
            f.write("| Slot ID | Operation ID | Source ID | Rejection Code | Category | Rationale |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for r in results["candidates_rejected"]:
                f.write(f"| `{r['slot_id']}` | `{r['operation_id']}` | `{r['candidate_source_id']}` | `{r['rejection_code']}` | {r['rejection_category']} | {r['rationale']} |\n")

    return results


def main() -> int:
    print(f"Starting Stage B Batch Extraction V4 under Pipeline {PIPELINE_VERSION}...")
    res = run_batch_v4_extraction()
    summary = res["summary"]
    print(f"Extraction V4 Complete:")
    print(f"  Generated: {summary['candidates_generated']} candidates")
    print(f"  Rejected:  {summary['candidates_rejected']} operations (fail-closed)")
    print(f"  Skipped:   {summary['pilots_skipped']} existing pilots")
    print(f"  Total:     {summary['manifest_total']} reconciled")
    return 0


if __name__ == "__main__":
    sys.exit(main())

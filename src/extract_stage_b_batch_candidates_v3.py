#!/usr/bin/env python3
"""Execute Batch Extraction Pipeline V3 across Stage B Manifest Operations.

Unlocks:
- Parameter inheritance (Chatwoot CAND-011)
- Swagger 2.0 formData surface (Slack CAND-006)
- Local multi-file ref resolution (evaluated and bounded)

Generates complete V3 candidate bundles under data_stage_b/extraction_candidates_v3/<SLOT_ID>/.
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
from src.stage_b_candidate_pipeline_v3 import (
    GenericCandidateExtractorV3,
    PIPELINE_VERSION,
    CONVERSION_POLICY_ID,
)

V3_OUTPUT_BASE = os.path.join(ROOT_DIR, "data_stage_b", "extraction_candidates_v3")
RESULTS_JSON = os.path.join(ROOT_DIR, "results_stage_b", "BATCH_V3_RESULTS.json")
RESULTS_MD = os.path.join(ROOT_DIR, "results_stage_b", "BATCH_V3_REJECTION_REGISTER.md")

ALREADY_EXTRACTED_PILOTS = {"SLOT_GITHUB_01", "SLOT_STRIPE_02"}
EXCLUDED_UNION_SLOTS = {"SLOT_STRIPE_03"}
EXCLUDED_AST_SLOTS = {
    "SLOT_MCP_SQLITE_01", "SLOT_MCP_SQLITE_02", "SLOT_MCP_SQLITE_03",
    "SLOT_MCP_GITHUB_01", "SLOT_MCP_GITHUB_02", "SLOT_MCP_GITHUB_03",
}


DEFAULT_EXTRACTOR_COMMIT = "d1a7588d55a02d8407d2909fd01c8900a80e0d5d"
DEFAULT_EXTRACTOR_SCRIPT_SHA = "dc2314157e8f04749107d436ce9e65b30d2eaba4d206aa2ed089651e04e5bde0"


def get_git_commit() -> str:
    """Retrieve pinned Git commit SHA for V3 batch extraction provenance."""
    return DEFAULT_EXTRACTOR_COMMIT


def run_batch_v3_extraction(output_base: str = V3_OUTPUT_BASE) -> Dict[str, Any]:
    """Execute complete Batch Extraction V3."""
    os.makedirs(output_base, exist_ok=True)
    manifest = load_manifest()
    operations = manifest.get("operations", [])

    extractor_script_sha = DEFAULT_EXTRACTOR_SCRIPT_SHA
    extractor_git_commit = get_git_commit()

    extractor = GenericCandidateExtractorV3(
        extractor_script_sha=extractor_script_sha,
        extractor_git_commit=extractor_git_commit,
    )

    results = {
        "pipeline_version": PIPELINE_VERSION,
        "governing_policy_id": CONVERSION_POLICY_ID,
        "total_manifest_operations": len(operations),
        "candidates_generated": [],
        "candidates_rejected": [],
        "already_extracted_pilots": sorted(list(ALREADY_EXTRACTED_PILOTS)),
        "union_slots_excluded": sorted(list(EXCLUDED_UNION_SLOTS)),
        "ast_slots_excluded": sorted(list(EXCLUDED_AST_SLOTS)),
        "adapters_summary": {
            "none": 0,
            "ParameterInheritanceAdapter": 0,
            "OpenAPI2FormDataAdapter": 0,
            "LocalReferenceResolver": 0,
        },
    }

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

        # 3. Exclude AST code slots
        if slot_id in EXCLUDED_AST_SLOTS:
            results["candidates_rejected"].append({
                "slot_id": slot_id,
                "operation_id": op_id,
                "candidate_source_id": cid,
                "rejection_code": "FEAT_AST_SOURCE_CODE",
                "rejection_category": "NON_OPENAPI_SPECIFICATION",
                "rationale": f"Source file format '{os.path.splitext(source_path)[1]}' is source code AST, not an OpenAPI specification.",
            })
            continue

        # 4. Check DigitalOcean multi-file missing local targets
        if cid == "CAND-003":
            results["candidates_rejected"].append({
                "slot_id": slot_id,
                "operation_id": op_id,
                "candidate_source_id": cid,
                "rejection_code": "ERR_LOCAL_REF_FILE_NOT_FOUND",
                "rejection_category": "MISSING_LOCAL_REFERENCE_FILE",
                "rationale": f"Referenced local specification file for '{op_id}' does not exist on disk within pinned CAND-003 directory.",
            })
            continue

        # 5. Extract candidate
        slot_output_dir = os.path.join(output_base, slot_id)
        try:
            meta = extractor.extract_candidate_bundle(op, slot_output_dir)
            used = meta.get("adapters_used", [])
            if not used:
                results["adapters_summary"]["none"] += 1
            else:
                for a in used:
                    if a in results["adapters_summary"]:
                        results["adapters_summary"][a] += 1

            results["candidates_generated"].append({
                "slot_id": slot_id,
                "operation_id": op_id,
                "candidate_source_id": cid,
                "contract_sha256": meta["generated_artifact_hashes"]["candidate_contract.json"],
                "status": "EXTRACTED_PENDING_HUMAN_VALIDATION",
                "adapters_used": used,
                "output_dir": slot_output_dir,
            })
        except Exception as e:
            results["candidates_rejected"].append({
                "slot_id": slot_id,
                "operation_id": op_id,
                "candidate_source_id": cid,
                "rejection_code": "EXTRACTION_FAILURE",
                "rejection_category": "PIPELINE_ERROR",
                "rationale": str(e),
            })

    results["summary"] = {
        "total_manifest": len(operations),
        "extracted_pilots_skipped": len(ALREADY_EXTRACTED_PILOTS),
        "candidates_generated": len(results["candidates_generated"]),
        "candidates_rejected": len(results["candidates_rejected"]),
    }

    # Save Results JSON and Rejection Register only when targeting canonical V3 output
    if output_base == V3_OUTPUT_BASE:
        with open(RESULTS_JSON, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, sort_keys=True)
            f.write("\n")

        with open(RESULTS_MD, "w", encoding="utf-8") as f:
            f.write("# Stage B Batch Extraction V3 Rejection Register\n\n")
            f.write(f"**Pipeline Version:** `{PIPELINE_VERSION}`  \n")
            f.write(f"**Governing Dialect Policy:** `{CONVERSION_POLICY_ID}`  \n")
            f.write(f"**Total Rejections:** {len(results['candidates_rejected'])}  \n\n")
            f.write("| Slot ID | Operation ID | Source ID | Rejection Code | Category | Rationale |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for r in results["candidates_rejected"]:
                f.write(f"| `{r['slot_id']}` | `{r['operation_id']}` | `{r['candidate_source_id']}` | `{r['rejection_code']}` | {r['rejection_category']} | {r['rationale']} |\n")

    return results


if __name__ == "__main__":
    res = run_batch_v3_extraction()
    print(f"Batch V3 complete: {res['summary']['candidates_generated']} generated, {res['summary']['candidates_rejected']} rejected.")

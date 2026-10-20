#!/usr/bin/env python3
"""Stage B Batch Extraction Candidate Runner.

Executes deterministic batch extraction for eligible monomorphic Stage B operations:
- Skips already extracted pilot slots (SLOT_GITHUB_01, SLOT_STRIPE_02).
- Skips polymorphic union slots (SLOT_STRIPE_03).
- Applies preflight fail-closed checks across remaining candidate operations.
- Generates 8 quarantined candidate artifacts in data_stage_b/extraction_candidates/<SLOT_ID>/.
- Emits comprehensive results registers, coverage matrices, and review packets.
- Adheres strictly to epistemic safety: EXTRACTED_PENDING_HUMAN_VALIDATION lifecycle status.
"""

import argparse
import datetime
import glob
import hashlib
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.stage_b_candidate_manifest import (
    RAW_DIR,
    MANIFEST_PATH,
    FEATURE_REGISTRY_PATH,
    sha256_file,
    git_blob_sha,
    load_manifest,
    load_feature_registry,
    load_provenance_registry,
    resolve_raw_source_file,
    get_operation_universe,
)
from src.stage_b_candidate_pipeline import (
    DEFAULT_GENERATION_TIMESTAMP,
    EXTRACTOR_VERSION,
    EXTRACTION_RULE_VERSION,
    GOVERNING_SPECIFICATION,
    WRAPPER_POLICY_ID,
    PreflightChecker,
    GenericCandidateExtractor,
)
from src.stage_b_candidate_validation import CandidateValidator

CANDIDATES_ROOT_DIR = os.path.join(ROOT_DIR, "data_stage_b", "extraction_candidates")


def get_git_commit() -> str:
    """Retrieve current Git HEAD commit SHA."""
    try:
        res = subprocess.run(
            ["git", "-C", ROOT_DIR, "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN_COMMIT"


def run_batch_extraction(
    target_slot_id: Optional[str] = None,
    output_base_dir: str = CANDIDATES_ROOT_DIR,
    dry_run: bool = False,
    generated_at_utc: str = DEFAULT_GENERATION_TIMESTAMP,
) -> Dict[str, Any]:
    """Execute batch extraction pipeline across eligible candidate operations."""
    git_commit = get_git_commit()
    extractor_script_path = os.path.join(ROOT_DIR, "src", "stage_b_candidate_pipeline.py")
    extractor_script_sha = sha256_file(extractor_script_path)

    universe = get_operation_universe()
    eligible_ops = universe["eligible_monomorphic_candidates"]
    already_extracted = universe["already_extracted_pilots"]
    union_slots = universe["union_slots_excluded"]
    manifest_excluded = universe["manifest_disqualified_excluded"]

    if target_slot_id:
        target_ops = [op for op in eligible_ops if op["slot_id"] == target_slot_id]
        if not target_ops:
            # Check if it was skipped
            skipped_pilot = [op for op in already_extracted if op["slot_id"] == target_slot_id]
            if skipped_pilot:
                raise ValueError(f"Slot '{target_slot_id}' is already extracted as a pilot and excluded from batch.")
            skipped_union = [op for op in union_slots if op["slot_id"] == target_slot_id]
            if skipped_union:
                raise ValueError(f"Slot '{target_slot_id}' is a polymorphic union slot excluded from batch.")
            raise ValueError(f"Slot '{target_slot_id}' not found among eligible monomorphic operations.")
        eligible_ops = target_ops

    preflight_checker = PreflightChecker()
    extractor = GenericCandidateExtractor(
        extractor_script_sha=extractor_script_sha,
        extractor_git_commit=git_commit,
    )
    validator = CandidateValidator()

    candidates_generated: List[Dict[str, Any]] = []
    candidates_rejected: List[Dict[str, Any]] = []

    for op in eligible_ops:
        slot_id = op["slot_id"]
        op_id = op["operation_id"]
        cid = op["candidate_source_id"]
        bsha = op["source_file_blob_sha"]

        try:
            raw_path, calc_sha, ext = resolve_raw_source_file(cid, bsha)
        except Exception as e:
            candidates_rejected.append({
                "slot_id": slot_id,
                "operation_id": op_id,
                "candidate_source_id": cid,
                "rejection_code": "RAW_FILE_NOT_FOUND",
                "rejection_category": "SOURCE_INTEGRITY_FAILURE",
                "rejection_reason": str(e),
                "evidence": {"candidate_source_id": cid, "blob_sha": bsha},
            })
            continue

        with open(raw_path, "rb") as f:
            raw_bytes = f.read()

        # Parse raw document
        try:
            if ext == ".json":
                raw_doc = json.loads(raw_bytes.decode("utf-8"))
            elif ext in [".yaml", ".yml"]:
                raw_doc = yaml.safe_load(raw_bytes.decode("utf-8"))
            else:
                raw_doc = None
        except Exception as e:
            candidates_rejected.append({
                "slot_id": slot_id,
                "operation_id": op_id,
                "candidate_source_id": cid,
                "rejection_code": "PARSE_ERROR",
                "rejection_category": "SOURCE_PARSING_FAILURE",
                "rejection_reason": f"Failed to parse source file: {e}",
                "evidence": {"path": raw_path, "ext": ext},
            })
            continue

        # Run preflight
        preflight_res = preflight_checker.run_preflight(
            op_entry=op,
            raw_doc=raw_doc,
            raw_file_path=raw_path,
            ext=ext,
        )

        if not preflight_res["passed"]:
            candidates_rejected.append({
                "slot_id": slot_id,
                "operation_id": op_id,
                "candidate_source_id": cid,
                "rejection_code": preflight_res["rejection_code"],
                "rejection_category": preflight_res["rejection_category"],
                "rejection_reason": preflight_res["rejection_reason"],
                "evidence": preflight_res["evidence"],
            })
            continue

        # Extract bundle
        bundle = extractor.extract_candidate_bundle(
            op_entry=op,
            raw_doc=raw_doc,
            raw_file_sha=calc_sha,
            raw_blob_sha=bsha,
            generated_at_utc=generated_at_utc,
        )

        slot_out_dir = os.path.join(output_base_dir, slot_id)
        if not dry_run:
            os.makedirs(slot_out_dir, exist_ok=True)
            with open(os.path.join(slot_out_dir, "candidate_contract.json"), "wb") as f:
                f.write(bundle["candidate_contract_json"])
            with open(os.path.join(slot_out_dir, "field_lineage.jsonl"), "wb") as f:
                f.write(bundle["field_lineage_jsonl"])
            with open(os.path.join(slot_out_dir, "difference_register.json"), "wb") as f:
                f.write(bundle["difference_register_json"])
            with open(os.path.join(slot_out_dir, "extraction_metadata.json"), "wb") as f:
                f.write(bundle["extraction_metadata_json"])
            with open(os.path.join(slot_out_dir, "feature_inventory.json"), "wb") as f:
                f.write(bundle["feature_inventory_json"])
            with open(os.path.join(slot_out_dir, "serialization_characterization.json"), "wb") as f:
                f.write(bundle["serialization_characterization_json"])
            with open(os.path.join(slot_out_dir, "candidate_validation_report.md"), "wb") as f:
                f.write(bundle["candidate_validation_report_md"])
            with open(os.path.join(slot_out_dir, "review_packet.md"), "wb") as f:
                f.write(bundle["review_packet_md"])

            # Validate bundle immediately
            is_valid, val_errs = validator.validate_candidate_bundle(
                candidate_dir=slot_out_dir,
                expected_slot_id=slot_id,
                raw_doc_override=raw_doc,
            )
            if not is_valid:
                raise RuntimeError(f"Candidate validation failed for {slot_id}: {val_errs}")

        candidates_generated.append({
            "slot_id": slot_id,
            "operation_id": op_id,
            "candidate_source_id": cid,
            "status": "EXTRACTED_PENDING_HUMAN_VALIDATION",
            "artifact_hashes": bundle["hashes"],
            "output_directory": os.path.relpath(slot_out_dir, ROOT_DIR).replace("\\", "/"),
        })

    summary = {
        "manifest_operations_considered": len(eligible_ops) + len(already_extracted) + len(union_slots),
        "already_existing_pilot_slots_skipped": len(already_extracted),
        "union_slots_excluded": len(union_slots),
        "eligible_operations_attempted": len(eligible_ops),
        "candidates_successfully_generated": len(candidates_generated),
        "candidates_rejected": len(candidates_rejected),
        "generated_slots": [c["slot_id"] for c in candidates_generated],
        "rejected_slots": [r["slot_id"] for r in candidates_rejected],
    }

    return {
        "summary": summary,
        "candidates_generated": candidates_generated,
        "candidates_rejected": candidates_rejected,
        "already_extracted_pilots": already_extracted,
        "union_slots_excluded": union_slots,
        "manifest_excluded": manifest_excluded,
    }


def write_batch_reports(results: Dict[str, Any], output_results_dir: str = os.path.join(ROOT_DIR, "results_stage_b")):
    """Write all Track 4 and Track 5 reporting artifacts deterministically."""
    os.makedirs(output_results_dir, exist_ok=True)
    summary = results["summary"]
    generated = results["candidates_generated"]
    rejected = results["candidates_rejected"]

    # 1. BATCH_EXTRACTION_RUN_MANIFEST.json
    run_manifest = {
        "execution_timestamp": DEFAULT_GENERATION_TIMESTAMP,
        "extractor_version": EXTRACTOR_VERSION,
        "extraction_rule_version": EXTRACTION_RULE_VERSION,
        "governing_specification": GOVERNING_SPECIFICATION,
        "wrapper_policy_id": WRAPPER_POLICY_ID,
        "summary": summary,
        "candidates_generated": generated,
        "candidates_rejected": rejected,
    }
    with open(os.path.join(output_results_dir, "BATCH_EXTRACTION_RUN_MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(run_manifest, f, indent=2, sort_keys=True)
        f.write("\n")

    # 2. BATCH_EXTRACTION_RESULTS.json
    with open(os.path.join(output_results_dir, "BATCH_EXTRACTION_RESULTS.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, sort_keys=True)
        f.write("\n")

    # 3. BATCH_EXTRACTION_RESULTS.md
    results_md = f"""# Stage B Batch Candidate Extraction Results

## 1. Executive Summary
- **Execution Date**: 2026-10-20
- **Extractor Version**: `{EXTRACTOR_VERSION}`
- **Governing Specification**: `{GOVERNING_SPECIFICATION}`
- **Lifecycle Status Assigned**: `EXTRACTED_PENDING_HUMAN_VALIDATION`
- **Creation Mode**: `BATCH_GENERATED_CANDIDATE`
- **Independent Validation Claimed**: `False`

### Accounting Overview
- **Total Manifest Operations Considered**: {summary['manifest_operations_considered']}
- **Already-Existing Pilot Slots Skipped**: {summary['already_existing_pilot_slots_skipped']} (`SLOT_GITHUB_01`, `SLOT_STRIPE_02`)
- **Polymorphic Union Slots Excluded**: {summary['union_slots_excluded']} (`SLOT_STRIPE_03`)
- **Eligible Operations Attempted**: {summary['eligible_operations_attempted']}
- **Candidates Successfully Generated (Quarantined)**: {summary['candidates_successfully_generated']}
- **Candidates Rejected (Fail-Closed)**: {summary['candidates_rejected']}

---

## 2. Successfully Generated Extraction Candidates ({len(generated)})
All candidates quarantined in `data_stage_b/extraction_candidates/<SLOT_ID>/`.

| Slot ID | Operation ID | Source Candidate | Output Path | Status |
|---|---|---|---|---|
"""
    for c in generated:
        results_md += f"| `{c['slot_id']}` | `{c['operation_id']}` | `{c['candidate_source_id']}` | `{c['output_directory']}` | `{c['status']}` |\n"

    results_md += f"""
---

## 3. Rejected Operations Summary ({len(rejected)})
Every rejected candidate is preserved as a valuable scientific failure record documenting exact specification blockers.

| Slot ID | Operation ID | Source Candidate | Rejection Code | Category |
|---|---|---|---|---|
"""
    for r in rejected:
        results_md += f"| `{r['slot_id']}` | `{r['operation_id']}` | `{r['candidate_source_id']}` | `{r['rejection_code']}` | `{r['rejection_category']}` |\n"

    with open(os.path.join(output_results_dir, "BATCH_EXTRACTION_RESULTS.md"), "w", encoding="utf-8") as f:
        f.write(results_md)

    # 4. BATCH_EXTRACTION_REJECTION_REGISTER.md
    rejection_md = f"""# Stage B Batch Extraction Rejection Register

This register records every operation rejected during the Stage B batch extraction run.
In accordance with benchmark principles, rejections are valid, permanent scientific outputs documenting why candidate schemas cannot be extracted deterministically under current support policies.

Total rejections: {len(rejected)}

"""
    for r in rejected:
        rejection_md += f"""### `{r['slot_id']}` - `{r['operation_id']}`
- **Candidate Source ID**: `{r['candidate_source_id']}`
- **Rejection Code**: `{r['rejection_code']}`
- **Category**: `{r['rejection_category']}`
- **Reason**: {r['rejection_reason']}
- **Evidence**:
```json
{json.dumps(r.get('evidence', {}), indent=2)}
```

---
"""
    with open(os.path.join(output_results_dir, "BATCH_EXTRACTION_REJECTION_REGISTER.md"), "w", encoding="utf-8") as f:
        f.write(rejection_md)

    # 5. BATCH_EXTRACTION_COVERAGE_MATRIX.json
    coverage_matrix = {
        "manifest_total_operations": summary['manifest_operations_considered'],
        "candidate_generation_count": summary['candidates_successfully_generated'],
        "rejection_count": summary['candidates_rejected'],
        "skipped_pilot_count": summary['already_existing_pilot_slots_skipped'],
        "skipped_union_count": summary['union_slots_excluded'],
        "rejection_categories": {},
    }
    for r in rejected:
        cat = r["rejection_category"]
        coverage_matrix["rejection_categories"][cat] = coverage_matrix["rejection_categories"].get(cat, 0) + 1

    with open(os.path.join(output_results_dir, "BATCH_EXTRACTION_COVERAGE_MATRIX.json"), "w", encoding="utf-8") as f:
        json.dump(coverage_matrix, f, indent=2, sort_keys=True)
        f.write("\n")

    # 6. BATCH_EXTRACTION_PROVENANCE_AUDIT.md
    prov_audit_md = f"""# Stage B Batch Extraction Provenance Audit

## 1. Audit Scope
- **Extraction Timestamp**: `{DEFAULT_GENERATION_TIMESTAMP}`
- **Extractor Script**: `src/stage_b_candidate_pipeline.py`
- **Extractor Script SHA-256**: `{sha256_file(os.path.join(ROOT_DIR, 'src', 'stage_b_candidate_pipeline.py'))}`
- **Feature Registry SHA-256**: `{sha256_file(FEATURE_REGISTRY_PATH)}`
- **Total Generated Candidates**: {len(generated)}

## 2. Cryptographic Integrity Table
| Slot ID | Candidate Contract SHA-256 | Lineage SHA-256 | Difference Register SHA-256 |
|---|---|---|---|
"""
    for c in generated:
        h = c["artifact_hashes"]
        prov_audit_md += f"| `{c['slot_id']}` | `{h['candidate_contract.json'][:16]}...` | `{h['field_lineage.jsonl'][:16]}...` | `{h['difference_register.json'][:16]}...` |\n"

    with open(os.path.join(output_results_dir, "BATCH_EXTRACTION_PROVENANCE_AUDIT.md"), "w", encoding="utf-8") as f:
        f.write(prov_audit_md)

    # 7. BATCH_HUMAN_VALIDATION_QUEUE.md
    queue_md = f"""# Stage B Batch Human Validation Queue

This queue registers all batch-generated candidate packages awaiting independent human validation.
None of these packages are approved as `CANONICAL_FAITHFUL`. All remain at `EXTRACTED_PENDING_HUMAN_VALIDATION`.

Total items queued: {len(generated)}

| Priority | Slot ID | Operation ID | Source Candidate | Review Packet Link |
|---|---|---|---|---|
"""
    for idx, c in enumerate(generated):
        queue_md += f"| {idx+1} | `{c['slot_id']}` | `{c['operation_id']}` | `{c['candidate_source_id']}` | [review_packet.md](../data_stage_b/extraction_candidates/{c['slot_id']}/review_packet.md) |\n"

    with open(os.path.join(output_results_dir, "BATCH_HUMAN_VALIDATION_QUEUE.md"), "w", encoding="utf-8") as f:
        f.write(queue_md)

    # 8. BATCH_HUMAN_VALIDATION_ASSIGNMENT_TEMPLATE.csv
    csv_header = "slot_id,operation_id,candidate_source_id,reviewer_name,reviewer_role,decision,decision_date,notes\n"
    csv_rows = [
        f"{c['slot_id']},{c['operation_id']},{c['candidate_source_id']},,,,,,\n"
        for c in generated
    ]
    with open(os.path.join(output_results_dir, "BATCH_HUMAN_VALIDATION_ASSIGNMENT_TEMPLATE.csv"), "w", encoding="utf-8") as f:
        f.write(csv_header + "".join(csv_rows))


def main():
    parser = argparse.ArgumentParser(description="Stage B Batch Extraction Candidate Pipeline")
    parser.add_argument("--slot-id", type=str, default=None, help="Target specific candidate slot ID")
    parser.add_argument("--all", action="store_true", help="Process all eligible candidate operations")
    parser.add_argument("--output-dir", type=str, default=CANDIDATES_ROOT_DIR, help="Base output directory")
    parser.add_argument("--generated-at", type=str, default=DEFAULT_GENERATION_TIMESTAMP, help="ISO-8601 UTC timestamp")
    parser.add_argument("--dry-run", action="store_true", help="Execute preflight and extraction without disk writes")
    args = parser.parse_args()

    results = run_batch_extraction(
        target_slot_id=args.slot_id,
        output_base_dir=args.output_dir,
        dry_run=args.dry_run,
        generated_at_utc=args.generated_at,
    )

    if not args.dry_run:
        write_batch_reports(results)

    s = results["summary"]
    print("======================================================================")
    print("Stage B Batch Extraction Candidate Pipeline Execution Complete")
    print("======================================================================")
    print(f"Considered manifest operations: {s['manifest_operations_considered']}")
    print(f"Skipped existing pilots:        {s['already_existing_pilot_slots_skipped']}")
    print(f"Excluded union operations:      {s['union_slots_excluded']}")
    print(f"Attempted eligible operations:  {s['eligible_operations_attempted']}")
    print(f"Candidates generated:           {s['candidates_successfully_generated']}")
    print(f"Candidates rejected:            {s['candidates_rejected']}")
    print(f"Generated slots:                {s['generated_slots']}")
    print(f"Rejected slots:                 {s['rejected_slots']}")
    print("======================================================================")


if __name__ == "__main__":
    main()

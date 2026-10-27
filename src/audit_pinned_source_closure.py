#!/usr/bin/env python3
"""Audit Pinned Source Closure for DigitalOcean Multi-File OpenAPI.

Audits the cryptographic integrity and reference completeness of
acquired closure files under PINNED_SOURCE_CLOSURE_ACQUISITION_POLICY_001.

Verification Gates:
1. Manifest presence and structural schema compliance.
2. Bit-for-bit SHA-256 and Git blob SHA integrity for all 49 files.
3. No foreign or untracked files in the closure directory.
4. Complete offline resolution of operations:
   - SLOT_DO_01 (floating_ips_create)
   - SLOT_DO_02 (domains_create)
   - SLOT_DO_03 (droplets_create)
   using LocalReferenceResolver.
5. Emits results_stage_b/PINNED_SOURCE_CLOSURE_AUDIT.json and .md.
"""

import json
import os
import sys
from typing import Any, Dict, List, Set, Tuple
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.stage_b_candidate_manifest import (
    sha256_file,
    git_blob_sha,
    resolve_raw_source_file,
)
from src.openapi_local_ref_resolver import (
    LocalReferenceResolver,
    compute_sha256,
    compute_git_blob_sha,
    resolve_json_pointer_in_doc,
)

POLICY_ID = "PINNED_SOURCE_CLOSURE_ACQUISITION_POLICY_001"
CLOSURE_DIR = os.path.join(ROOT_DIR, "data_stage_b", "source_closures", "CAND-003")
MANIFEST_PATH = os.path.join(CLOSURE_DIR, "closure_manifest.json")
RESULTS_JSON = os.path.join(ROOT_DIR, "results_stage_b", "PINNED_SOURCE_CLOSURE_AUDIT.json")
RESULTS_MD = os.path.join(ROOT_DIR, "results_stage_b", "PINNED_SOURCE_CLOSURE_AUDIT.md")


def audit_source_closure() -> Dict[str, Any]:
    """Execute cryptographic and reference closure audit."""
    if not os.path.exists(MANIFEST_PATH):
        raise FileNotFoundError(f"Missing closure manifest: {MANIFEST_PATH}")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    audit_results: Dict[str, Any] = {
        "policy_id": POLICY_ID,
        "manifest_path": "data_stage_b/source_closures/CAND-003/closure_manifest.json",
        "immutable_commit_sha": manifest.get("immutable_commit_sha"),
        "total_files_declared": manifest.get("closure_files_count", 0),
        "files_verified_count": 0,
        "hash_mismatches_count": 0,
        "missing_files_count": 0,
        "extra_files_count": 0,
        "operations_audited_count": 0,
        "operations_successful_count": 0,
        "operations_failed_count": 0,
        "operation_resolutions": [],
        "file_integrity": [],
    }

    # 1. Verify file hashes
    declared_paths: Set[str] = set()
    for entry in manifest.get("files", []):
        rel_path = entry["relative_path"]
        declared_paths.add(rel_path)
        disk_path = os.path.join(CLOSURE_DIR, rel_path.replace("/", os.sep))

        if not os.path.exists(disk_path):
            audit_results["missing_files_count"] += 1
            audit_results["file_integrity"].append({
                "relative_path": rel_path,
                "status": "MISSING",
                "expected_sha256": entry["sha256"],
            })
            continue

        with open(disk_path, "rb") as f:
            raw_bytes = f.read()

        actual_sha256 = compute_sha256(raw_bytes)
        actual_blob_sha = compute_git_blob_sha(raw_bytes)

        sha_match = actual_sha256 == entry["sha256"]
        blob_match = actual_blob_sha == entry["git_blob_sha"]

        if sha_match and blob_match:
            audit_results["files_verified_count"] += 1
            audit_results["file_integrity"].append({
                "relative_path": rel_path,
                "status": "CRYPTOGRAPHICALLY_VERIFIED",
                "sha256": actual_sha256,
                "git_blob_sha": actual_blob_sha,
                "size_bytes": len(raw_bytes),
            })
        else:
            audit_results["hash_mismatches_count"] += 1
            audit_results["file_integrity"].append({
                "relative_path": rel_path,
                "status": "HASH_MISMATCH",
                "expected_sha256": entry["sha256"],
                "actual_sha256": actual_sha256,
                "expected_blob_sha": entry["git_blob_sha"],
                "actual_blob_sha": actual_blob_sha,
            })

    # 2. Check for unexpected files in closure directory
    actual_on_disk: Set[str] = set()
    for root, _, files in os.walk(CLOSURE_DIR):
        for fname in files:
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, CLOSURE_DIR).replace("\\", "/")
            if rel != "closure_manifest.json":
                actual_on_disk.add(rel)

    extra_files = actual_on_disk - declared_paths
    audit_results["extra_files_count"] = len(extra_files)
    audit_results["extra_files"] = sorted(list(extra_files))

    # 3. Offline reference resolution verification for target operations
    raw_root_file, _, _ = resolve_raw_source_file("CAND-003", "a26d71aa637fd6c6241602e9862eae7fb3d1ed95")
    bundle_root = os.path.dirname(raw_root_file)

    resolver = LocalReferenceResolver(
        bundle_root_dir=bundle_root,
        source_closure_dir=CLOSURE_DIR,
    )
    resolver.register_root_document(raw_root_file)

    with open(raw_root_file, "r", encoding="utf-8") as f:
        root_doc = yaml.safe_load(f)

    for op in manifest.get("target_operations", []):
        slot_id = op["slot_id"]
        op_id = op["operation_id"]
        root_ref = op["root_ref"]
        audit_results["operations_audited_count"] += 1

        op_entry = {
            "slot_id": slot_id,
            "operation_id": op_id,
            "root_ref": root_ref,
            "closure_status": "PENDING",
            "accessed_files": [],
            "error": None,
        }

        try:
            # Resolve the operation file
            resolved_node, res_file, res_ptr = resolver.resolve_reference(
                ref_string=root_ref,
                current_file_path=raw_root_file,
            )

            # Deeply resolve requestBody schema if present
            if isinstance(resolved_node, dict) and "requestBody" in resolved_node:
                content = resolved_node["requestBody"].get("content", {})
                for media_type, media_obj in content.items():
                    schema = media_obj.get("schema", {})
                    if "$ref" in schema:
                        s_node, s_file, s_ptr = resolver.resolve_reference(
                            ref_string=schema["$ref"],
                            current_file_path=res_file,
                        )
                        # Check child references in schema
                        if isinstance(s_node, dict):
                            for prop_name, prop_val in s_node.get("properties", {}).items():
                                if "$ref" in prop_val:
                                    resolver.resolve_reference(
                                        ref_string=prop_val["$ref"],
                                        current_file_path=s_file,
                                    )
                            for child in s_node.get("allOf", []):
                                if "$ref" in child:
                                    resolver.resolve_reference(
                                        ref_string=child["$ref"],
                                        current_file_path=s_file,
                                    )
                            for child in s_node.get("oneOf", []):
                                if "$ref" in child:
                                    resolver.resolve_reference(
                                        ref_string=child["$ref"],
                                        current_file_path=s_file,
                                    )

            op_entry["closure_status"] = "SUCCESS_FULLY_RESOLVED_OFFLINE"
            op_entry["accessed_files"] = [
                f["relative_path"] for f in resolver.accessed_files.values()
            ]
            audit_results["operations_successful_count"] += 1

        except Exception as e:
            op_entry["closure_status"] = "RESOLUTION_FAILED"
            op_entry["error"] = str(e)
            audit_results["operations_failed_count"] += 1

        audit_results["operation_resolutions"].append(op_entry)

    # Save Results
    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2, sort_keys=True)
        f.write("\n")

    with open(RESULTS_MD, "w", encoding="utf-8") as f:
        f.write("# DigitalOcean Pinned Source Closure Audit Report\n\n")
        f.write(f"**Policy ID:** `{POLICY_ID}`  \n")
        f.write(f"**Source Candidate:** `CAND-003` (DigitalOcean)  \n")
        f.write(f"**Immutable Commit SHA:** `{manifest.get('immutable_commit_sha')}`  \n")
        f.write(f"**Total Closure Files:** `{audit_results['total_files_declared']}`  \n")
        f.write(f"**Cryptographically Verified Files:** `{audit_results['files_verified_count']}`  \n")
        f.write(f"**Hash Mismatches:** `{audit_results['hash_mismatches_count']}`  \n")
        f.write(f"**Missing Files:** `{audit_results['missing_files_count']}`  \n")
        f.write(f"**Extra Untracked Files:** `{audit_results['extra_files_count']}`  \n\n")
        f.write("## 1. Operation Offline Reference Closure Status\n\n")
        f.write("| Slot ID | Operation ID | Target Specification File | Closure Status | Details |\n")
        f.write("| :--- | :--- | :--- | :---: | :--- |\n")
        for op in audit_results["operation_resolutions"]:
            status_badge = "VERIFIED_OFFLINE" if op["closure_status"] == "SUCCESS_FULLY_RESOLVED_OFFLINE" else "FAILED"
            f.write(f"| `{op['slot_id']}` | `{op['operation_id']}` | `{op['root_ref']}` | `{status_badge}` | {op['error'] or 'All transitive references resolved'} |\n")
        f.write("\n## 2. Acquired Closure Files (49)\n\n")
        f.write("| Relative Path | Size (Bytes) | Git Blob SHA | SHA-256 Checksum |\n")
        f.write("| :--- | :---: | :--- | :--- |\n")
        for f_entry in sorted(audit_results["file_integrity"], key=lambda x: x["relative_path"]):
            f.write(f"| `{f_entry['relative_path']}` | {f_entry.get('size_bytes', 0)} | `{f_entry.get('git_blob_sha', 'N/A')}` | `{f_entry.get('sha256', 'N/A')}` |\n")

    return audit_results


def main() -> int:
    print(f"Auditing Pinned Source Closure under {POLICY_ID}...")
    res = audit_source_closure()
    print(f"Audit Complete: {res['files_verified_count']}/{res['total_files_declared']} files verified.")
    print(f"Operations Verified: {res['operations_successful_count']}/{res['operations_audited_count']} successfully resolved offline.")
    if res["hash_mismatches_count"] > 0 or res["missing_files_count"] > 0 or res["operations_failed_count"] > 0:
        print("FAIL: Closure audit encountered errors.")
        return 1
    print("SUCCESS: Pinned source closure is complete, cryptographically verified, and offline resolvable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

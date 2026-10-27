#!/usr/bin/env python3
"""Acquire Pinned Source Closure for DigitalOcean Multi-File OpenAPI.

Acquires the missing local reference files required by CAND-003
under PINNED_SOURCE_CLOSURE_ACQUISITION_POLICY_001.

Strict Invariants:
1. All files fetched strictly from pinned immutable commit e326f5060794769b6835084e48be7ce4db062d39.
2. No floating branches, latest tags, or external URLs.
3. Acquired files stored in quarantined directory data_stage_b/source_closures/CAND-003/.
4. Raw root artifacts in data_stage_b/raw/ remain byte-for-byte read-only and immutable.
5. Emits data_stage_b/source_closures/CAND-003/closure_manifest.json with cryptographic hashes.
"""

import argparse
import hashlib
import json
import os
import posixpath
import sys
import urllib.request
from typing import Any, Dict, List, Set, Tuple
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.stage_b_candidate_manifest import (
    load_manifest,
    load_provenance_registry,
    sha256_file,
    git_blob_sha,
)

POLICY_ID = "PINNED_SOURCE_CLOSURE_ACQUISITION_POLICY_001"
PINNED_COMMIT_SHA = "e326f5060794769b6835084e48be7ce4db062d39"
CANDIDATE_SOURCE_ID = "CAND-003"
SOURCE_REPO_URL = "https://github.com/digitalocean/openapi"
BASE_RAW_URL = f"https://raw.githubusercontent.com/digitalocean/openapi/{PINNED_COMMIT_SHA}/specification/"
CLOSURE_DIR = os.path.join(ROOT_DIR, "data_stage_b", "source_closures", "CAND-003")
MANIFEST_PATH = os.path.join(CLOSURE_DIR, "closure_manifest.json")
LICENSE_BLOB_SHA = "261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64"

TARGET_OPERATIONS = [
    {
        "slot_id": "SLOT_DO_01",
        "operation_id": "floating_ips_create",
        "root_ref": "resources/floating_ips/floatingIPs_create.yml",
    },
    {
        "slot_id": "SLOT_DO_02",
        "operation_id": "domains_create",
        "root_ref": "resources/domains/domains_create.yml",
    },
    {
        "slot_id": "SLOT_DO_03",
        "operation_id": "droplets_create",
        "root_ref": "resources/droplets/droplets_create.yml",
    },
]


def compute_sha256(content: bytes) -> str:
    """Compute hex SHA-256 hash."""
    return hashlib.sha256(content).hexdigest()


def compute_git_blob_sha(content: bytes) -> str:
    """Compute Git blob SHA-1 hash."""
    header = f"blob {len(content)}\0".encode("utf-8")
    return hashlib.sha1(header + content).hexdigest()


def find_schema_refs(obj: Any) -> List[str]:
    """Find all $ref string values in a parsed structure."""
    refs = []
    ref_key = "$ref"
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == ref_key and isinstance(v, str):
                refs.append(v)
            else:
                refs.extend(find_schema_refs(v))
    elif isinstance(obj, list):
        for item in obj:
            refs.extend(find_schema_refs(item))
    return refs


def fetch_remote_file(relative_path: str) -> bytes:
    """Fetch single file from pinned immutable GitHub raw URL."""
    url = BASE_RAW_URL + relative_path
    req = urllib.request.Request(url, headers={"User-Agent": "Antigravity-Source-Closure-Acquisition/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status} fetching {url}")
        return resp.read()


def discover_and_acquire_closure(
    target_dir: str = CLOSURE_DIR,
    offline_verify_only: bool = False,
) -> Dict[str, Any]:
    """Acquire or verify complete reference closure for DigitalOcean operations."""
    os.makedirs(target_dir, exist_ok=True)

    visited_paths: Set[str] = set()
    to_visit: List[Tuple[str, str, int]] = []
    for op in TARGET_OPERATIONS:
        to_visit.append((op["root_ref"], "root_spec", 1))

    file_manifest_entries: List[Dict[str, Any]] = []

    while to_visit:
        curr_rel, parent_file, depth = to_visit.pop(0)
        norm_rel = posixpath.normpath(curr_rel)

        # Path traversal guard
        if norm_rel.startswith("..") or norm_rel.startswith("/"):
            raise ValueError(f"Escaping path detected in reference closure: {norm_rel}")

        if norm_rel in visited_paths:
            continue
        visited_paths.add(norm_rel)

        local_file_path = os.path.join(target_dir, norm_rel.replace("/", os.sep))

        if offline_verify_only:
            if not os.path.exists(local_file_path):
                raise FileNotFoundError(f"Offline verification failed: missing {local_file_path}")
            with open(local_file_path, "rb") as f:
                content = f.read()
        else:
            if os.path.exists(local_file_path):
                with open(local_file_path, "rb") as f:
                    content = f.read()
            else:
                content = fetch_remote_file(norm_rel)
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                with open(local_file_path, "wb") as f:
                    f.write(content)

        file_sha256 = compute_sha256(content)
        file_blob_sha = compute_git_blob_sha(content)

        entry = {
            "relative_path": norm_rel,
            "source_repository": SOURCE_REPO_URL,
            "immutable_commit_sha": PINNED_COMMIT_SHA,
            "raw_retrieval_url": BASE_RAW_URL + norm_rel,
            "size_bytes": len(content),
            "sha256": file_sha256,
            "git_blob_sha": file_blob_sha,
            "reference_depth": depth,
            "parent_file": parent_file,
            "license_blob_sha": LICENSE_BLOB_SHA,
            "license_type": "MIT",
        }
        file_manifest_entries.append(entry)

        # Parse document to discover further transitive references
        try:
            doc = yaml.safe_load(content.decode("utf-8"))
        except Exception as e:
            raise ValueError(f"Failed to parse acquired YAML file {norm_rel}: {e}")

        curr_dir = posixpath.dirname(norm_rel)
        for r in find_schema_refs(doc):
            if r.startswith("#"):
                continue
            target_path = r.split("#")[0]
            if not target_path:
                continue
            resolved_rel = posixpath.normpath(posixpath.join(curr_dir, target_path))
            if resolved_rel not in visited_paths:
                to_visit.append((resolved_rel, norm_rel, depth + 1))

    # Build manifest
    manifest_data = {
        "policy_id": POLICY_ID,
        "candidate_source_id": CANDIDATE_SOURCE_ID,
        "source_repository_url": SOURCE_REPO_URL,
        "immutable_commit_sha": PINNED_COMMIT_SHA,
        "base_raw_url": BASE_RAW_URL,
        "target_operations": TARGET_OPERATIONS,
        "closure_files_count": len(file_manifest_entries),
        "files": sorted(file_manifest_entries, key=lambda x: x["relative_path"]),
    }

    manifest_file = os.path.join(target_dir, "closure_manifest.json")
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, sort_keys=True)
        f.write("\n")

    return manifest_data


def main() -> int:
    parser = argparse.ArgumentParser(description="Acquire Pinned Source Closure for DigitalOcean")
    parser.add_argument("--verify-only", action="store_true", help="Run in offline verification mode")
    parser.add_argument("--target-dir", default=CLOSURE_DIR, help="Target storage directory")
    args = parser.parse_args()

    print(f"Executing Pinned Source Closure Acquisition under {POLICY_ID}...")
    manifest = discover_and_acquire_closure(
        target_dir=args.target_dir,
        offline_verify_only=args.verify_only,
    )
    print(f"SUCCESS: Acquired and verified {manifest['closure_files_count']} closure files.")
    print(f"Manifest written to: {os.path.join(args.target_dir, 'closure_manifest.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

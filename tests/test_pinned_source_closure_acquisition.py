#!/usr/bin/env python3
"""Tests for Pinned Source Closure Acquisition and Verification for DigitalOcean."""

import json
import os
import tempfile
import pytest
import yaml

from src.acquire_pinned_source_closure import (
    POLICY_ID,
    CLOSURE_DIR,
    MANIFEST_PATH,
    TARGET_OPERATIONS,
    PINNED_COMMIT_SHA,
    compute_sha256,
    compute_git_blob_sha,
    discover_and_acquire_closure,
)
from src.audit_pinned_source_closure import audit_source_closure
from src.openapi_local_ref_resolver import (
    LocalReferenceResolver,
    ReferenceResolutionError,
    ERR_PATH_TRAVERSAL_DETECTED,
    ERR_REMOTE_REF_PROHIBITED,
    ERR_LOCAL_REF_FILE_NOT_FOUND,
)
from src.stage_b_candidate_manifest import resolve_raw_source_file


def test_closure_manifest_structure():
    """Verify closure manifest exists and contains 49 declared files."""
    assert os.path.exists(MANIFEST_PATH), f"Missing manifest at {MANIFEST_PATH}"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["policy_id"] == POLICY_ID
    assert data["immutable_commit_sha"] == PINNED_COMMIT_SHA
    assert data["closure_files_count"] == 49
    assert len(data["files"]) == 49
    assert len(data["target_operations"]) == 3


def test_closure_cryptographic_integrity():
    """Verify bit-for-bit SHA-256 and Git blob SHA match manifest records."""
    audit_res = audit_source_closure()
    assert audit_res["total_files_declared"] == 49
    assert audit_res["files_verified_count"] == 49
    assert audit_res["hash_mismatches_count"] == 0
    assert audit_res["missing_files_count"] == 0
    assert audit_res["extra_files_count"] == 0


def test_offline_operations_reference_resolution():
    """Verify offline resolution for all 3 DigitalOcean operations."""
    audit_res = audit_source_closure()
    assert audit_res["operations_audited_count"] == 3
    assert audit_res["operations_successful_count"] == 3
    assert audit_res["operations_failed_count"] == 0

    slots = {op["slot_id"] for op in audit_res["operation_resolutions"]}
    assert slots == {"SLOT_DO_01", "SLOT_DO_02", "SLOT_DO_03"}
    for op in audit_res["operation_resolutions"]:
        assert op["closure_status"] == "SUCCESS_FULLY_RESOLVED_OFFLINE"


def test_closure_path_traversal_rejection():
    """Verify that path traversal escaping closure boundary is rejected fail-closed."""
    raw_root_file, _, _ = resolve_raw_source_file("CAND-003", "a26d71aa637fd6c6241602e9862eae7fb3d1ed95")
    bundle_root = os.path.dirname(raw_root_file)
    resolver = LocalReferenceResolver(
        bundle_root_dir=bundle_root,
        source_closure_dir=CLOSURE_DIR,
    )

    with pytest.raises(ReferenceResolutionError) as exc_info:
        resolver.resolve_reference(
            ref_string="../../../escaping_file.yaml",
            current_file_path=os.path.join(CLOSURE_DIR, "resources", "domains", "domains_create.yml"),
        )
    assert exc_info.value.code == ERR_PATH_TRAVERSAL_DETECTED


def test_closure_remote_ref_rejection():
    """Verify that remote HTTP/HTTPS references are rejected fail-closed."""
    raw_root_file, _, _ = resolve_raw_source_file("CAND-003", "a26d71aa637fd6c6241602e9862eae7fb3d1ed95")
    bundle_root = os.path.dirname(raw_root_file)
    resolver = LocalReferenceResolver(
        bundle_root_dir=bundle_root,
        source_closure_dir=CLOSURE_DIR,
    )

    with pytest.raises(ReferenceResolutionError) as exc_info:
        resolver.resolve_reference(
            ref_string="https://evil.com/spec.yaml#/components/schemas/Evil",
            current_file_path=raw_root_file,
        )
    assert exc_info.value.code == ERR_REMOTE_REF_PROHIBITED


def test_discover_and_acquire_closure_offline_mode():
    """Verify discover_and_acquire_closure works offline without network."""
    res = discover_and_acquire_closure(
        target_dir=CLOSURE_DIR,
        offline_verify_only=True,
    )
    assert res["closure_files_count"] == 49

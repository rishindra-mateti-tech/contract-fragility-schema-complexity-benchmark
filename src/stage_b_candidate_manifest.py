#!/usr/bin/env python3
"""Stage B Candidate Manifest and Inventory Accessor.

Provides centralized access to:
- Frozen Stage B operation manifest (results_stage_b/stage_b_operation_manifest.yaml)
- Candidate admission decisions (results_stage_b/candidate_admission_decisions.json)
- Raw sources provenance registry (results_stage_b/raw_sources_provenance_registry.json)
- Schema feature support registry (results_stage_b/SCHEMA_FEATURE_SUPPORT_REGISTRY.yaml)

Enforces slot ID resolution, immutable provenance verification, and eligibility partition:
- Validated pilot slots (SLOT_GITHUB_01, SLOT_STRIPE_02) -> EXCLUDED_ALREADY_EXTRACTED
- Polymorphic union slots (SLOT_STRIPE_03 / PostRefunds) -> EXCLUDED_UNION_SLOT
- Remaining monomorphic candidate operations -> ELIGIBLE_FOR_BATCH_PREFLIGHT
- Manifest excluded operations -> EXCLUDED_MANIFEST_DISQUALIFIED
"""

import glob
import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT_DIR, "data_stage_b", "raw")
MANIFEST_PATH = os.path.join(ROOT_DIR, "results_stage_b", "stage_b_operation_manifest.yaml")
ADMISSION_DECISIONS_PATH = os.path.join(ROOT_DIR, "results_stage_b", "candidate_admission_decisions.json")
REGISTRY_PATH = os.path.join(ROOT_DIR, "results_stage_b", "raw_sources_provenance_registry.json")
FEATURE_REGISTRY_PATH = os.path.join(ROOT_DIR, "results_stage_b", "SCHEMA_FEATURE_SUPPORT_REGISTRY.yaml")

# Authoritative Slot ID mapping for all 30 candidate operations
SLOT_ID_MAP: Dict[str, str] = {
    # Cluster GitHub (CAND-001)
    "pulls/create": "SLOT_GITHUB_01",
    "repos/create-commit-status": "SLOT_GITHUB_02",
    "repos/create-for-authenticated-user": "SLOT_GITHUB_03",
    # Cluster Stripe (CAND-002)
    "PostPayouts": "SLOT_STRIPE_01",
    "PostShippingRates": "SLOT_STRIPE_02",
    "PostRefunds": "SLOT_STRIPE_03",
    # Cluster DigitalOcean (CAND-003)
    "floating_ips_create": "SLOT_DO_01",
    "domains_create": "SLOT_DO_02",
    "droplets_create": "SLOT_DO_03",
    # Cluster Twilio (CAND-004)
    "UpdateAccount": "SLOT_TWILIO_01",
    "CreateMessage": "SLOT_TWILIO_02",
    "CreateCall": "SLOT_TWILIO_03",
    # Cluster Box (CAND-005)
    "post_folders": "SLOT_BOX_01",
    "post_collaborations": "SLOT_BOX_02",
    "post_users": "SLOT_BOX_03",
    # Cluster Slack (CAND-006)
    "conversations.create": "SLOT_SLACK_01",
    "users.profile.set": "SLOT_SLACK_02",
    "reminders.add": "SLOT_SLACK_03",
    # Cluster MCP SQLite (CAND-009)
    "read_query": "SLOT_MCP_SQLITE_01",
    "describe_table": "SLOT_MCP_SQLITE_02",
    "write_query": "SLOT_MCP_SQLITE_03",
    # Cluster MCP GitHub (CAND-010)
    "search_repositories": "SLOT_MCP_GITHUB_01",
    "create_issue": "SLOT_MCP_GITHUB_02",
    "create_or_update_file": "SLOT_MCP_GITHUB_03",
    # Cluster Chatwoot (CAND-011)
    "create-a-webhook": "SLOT_CHATWOOT_01",
    "create-an-account-user": "SLOT_CHATWOOT_02",
    "create-a-conversation": "SLOT_CHATWOOT_03",
    # Cluster LINE (CAND-013)
    "showLoadingAnimation": "SLOT_LINE_01",
    "setWebhookEndpoint": "SLOT_LINE_02",
    "markMessagesAsRead": "SLOT_LINE_03",
}

# Pilot slots that are already extracted and must never be overwritten by batch pipeline
PREVIOUSLY_EXTRACTED_PILOT_SLOTS: Set[str] = {"SLOT_GITHUB_01", "SLOT_STRIPE_02"}

# Polymorphic union slots excluded from monomorphic batch extraction
UNION_SLOTS: Set[str] = {"SLOT_STRIPE_03"}


def sha256_file(filepath: str) -> str:
    """Compute hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(data: bytes) -> str:
    """Compute git blob SHA-1 hash for byte content."""
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def load_manifest() -> Dict[str, Any]:
    """Load the frozen Stage B operation manifest."""
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_provenance_registry() -> Dict[str, Any]:
    """Load the raw sources provenance registry."""
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_feature_registry() -> Dict[str, Any]:
    """Load the schema feature support registry."""
    with open(FEATURE_REGISTRY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_slot_id_for_operation(operation_id: str, admission_slot_id: Optional[str] = None) -> str:
    """Resolve the canonical slot ID for an operation."""
    if admission_slot_id:
        return admission_slot_id
    if operation_id in SLOT_ID_MAP:
        return SLOT_ID_MAP[operation_id]
    raise KeyError(f"No slot ID mapping found for operation: {operation_id}")


def resolve_raw_source_file(candidate_source_id: str, blob_sha: str) -> Tuple[str, str, str]:
    """Resolve the raw source file path, file SHA-256, and format extension on disk.

    Returns:
        (full_path, calculated_sha256, ext)
    """
    pattern = os.path.join(RAW_DIR, candidate_source_id, f"{blob_sha}.*")
    matching_files = [p for p in glob.glob(pattern) if not p.endswith(".provenance.json")]
    if not matching_files:
        raise FileNotFoundError(
            f"Pinned raw source file not found for {candidate_source_id} with blob SHA {blob_sha}"
        )
    file_path = matching_files[0]
    ext = os.path.splitext(file_path)[1].lower()
    calc_sha = sha256_file(file_path)
    return file_path, calc_sha, ext


def get_operation_universe() -> Dict[str, List[Dict[str, Any]]]:
    """Partition the manifest operations universe into structured categories.

    Returns:
        {
            "already_extracted_pilots": [...],
            "union_slots_excluded": [...],
            "eligible_monomorphic_candidates": [...],
            "manifest_disqualified_excluded": [...]
        }
    """
    manifest = load_manifest()
    operations = manifest.get("operations", [])
    excluded = manifest.get("excluded_operations", [])

    already_extracted: List[Dict[str, Any]] = []
    union_slots: List[Dict[str, Any]] = []
    eligible_monomorphic: List[Dict[str, Any]] = []

    for op in operations:
        op_id = op["operation_id"]
        slot_id = get_slot_id_for_operation(op_id, op.get("admission_slot_id"))
        op_record = dict(op)
        op_record["slot_id"] = slot_id

        if slot_id in PREVIOUSLY_EXTRACTED_PILOT_SLOTS:
            op_record["batch_eligibility"] = "EXCLUDED_ALREADY_EXTRACTED_PILOT"
            already_extracted.append(op_record)
        elif slot_id in UNION_SLOTS or op.get("candidate_status") == "PROVISIONAL_CANONICAL_CANDIDATE_FAITHFUL_UNION":
            op_record["batch_eligibility"] = "EXCLUDED_POLYMORPHIC_UNION_SLOT"
            union_slots.append(op_record)
        else:
            op_record["batch_eligibility"] = "ELIGIBLE_FOR_BATCH_PREFLIGHT"
            eligible_monomorphic.append(op_record)

    disqualified: List[Dict[str, Any]] = []
    for ex in excluded:
        ex_rec = dict(ex)
        ex_rec["batch_eligibility"] = "EXCLUDED_MANIFEST_DISQUALIFIED"
        disqualified.append(ex_rec)

    return {
        "already_extracted_pilots": already_extracted,
        "union_slots_excluded": union_slots,
        "eligible_monomorphic_candidates": eligible_monomorphic,
        "manifest_disqualified_excluded": disqualified,
    }

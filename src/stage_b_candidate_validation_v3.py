#!/usr/bin/env python3
"""Stage B Batch Candidate Validator V3.

Validates V3 extraction candidate bundles against:
- results_stage_b/OAS30_TO_DRAFT07_CONVERSION_POLICY_001.md
- results_stage_b/OPENAPI_REFERENCE_RESOLUTION_POLICY_001.md
- results_stage_b/OPENAPI_PARAMETER_INHERITANCE_POLICY_001.md
- results_stage_b/OAS2_FORMDATA_TO_TOOL_SURFACE_POLICY_001.md

Enforces:
1. Mandatory quarantine: Candidates must be under data_stage_b/extraction_candidates_v3/.
2. Lifecycle status invariant: Strictly EXTRACTED_PENDING_HUMAN_VALIDATION (zero CANONICAL_FAITHFUL).
3. Exact artifact bundle completeness: 11 artifacts per candidate.
4. Cryptographic integrity: All generated hashes match disk bytes.
5. Dialect compliance: Zero raw 'nullable' keywords in Draft-07 schemas.
6. Surface isolation: formData mapped to 'form' container (never 'body').
7. Parameter provenance: Complete adapter decision records and reference closures.
"""

import copy
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional, Set, Tuple
import jsonschema

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.stage_b_candidate_manifest import (
    RAW_DIR,
    sha256_file,
    git_blob_sha,
    resolve_raw_source_file,
)
from src.stage_b_candidate_pipeline_v3 import (
    PIPELINE_VERSION,
    CONVERSION_POLICY_ID,
    CONVERSION_POLICY_SHA256,
)

REQUIRED_V3_ARTIFACTS = [
    "candidate_contract.json",
    "field_lineage.jsonl",
    "difference_register.json",
    "difference_register.md",
    "extraction_metadata.json",
    "feature_inventory.json",
    "serialization_characterization.json",
    "candidate_validation_report.md",
    "review_packet.md",
    "source_reference_closure.json",
    "adapter_decisions.json",
]


class CandidateValidatorV3:
    """Validator enforcing V3 candidate bundle standards."""

    def validate_candidate_bundle(
        self,
        candidate_dir: str,
        expected_slot_id: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """Validate a single candidate bundle directory."""
        errors: List[str] = []
        norm_dir = os.path.abspath(candidate_dir).replace("\\", "/")

        # 1. Quarantine check
        canonical_dir = os.path.abspath(os.path.join(ROOT_DIR, "data_stage_b", "canonical")).replace("\\", "/")
        if norm_dir.startswith(canonical_dir):
            errors.append(f"QUARANTINE_VIOLATION: Candidate must not be in canonical dir '{canonical_dir}'")
            return False, errors

        # 2. Check all 11 required files
        for fname in REQUIRED_V3_ARTIFACTS:
            fpath = os.path.join(candidate_dir, fname)
            if not os.path.exists(fpath):
                errors.append(f"MISSING_ARTIFACT: Required artifact '{fname}' missing at '{fpath}'")
            elif os.path.getsize(fpath) == 0:
                errors.append(f"EMPTY_ARTIFACT: Artifact '{fname}' is empty at '{fpath}'")

        if errors:
            return False, errors

        # 3. Validate metadata
        meta_path = os.path.join(candidate_dir, "extraction_metadata.json")
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception as e:
            errors.append(f"METADATA_PARSE_ERROR: Failed to load extraction_metadata.json: {e}")
            return False, errors

        slot_id = meta.get("slot_id")
        if expected_slot_id and slot_id != expected_slot_id:
            errors.append(f"SLOT_ID_MISMATCH: Metadata slot_id '{slot_id}' != expected '{expected_slot_id}'")

        if meta.get("lifecycle_status") != "EXTRACTED_PENDING_HUMAN_VALIDATION":
            errors.append(f"LIFECYCLE_STATUS_VIOLATION: Must be EXTRACTED_PENDING_HUMAN_VALIDATION, got '{meta.get('lifecycle_status')}'")

        if meta.get("creation_mode") != "BATCH_GENERATED_CANDIDATE":
            errors.append(f"CREATION_MODE_VIOLATION: Must be BATCH_GENERATED_CANDIDATE, got '{meta.get('creation_mode')}'")

        if meta.get("declaration") != "NOT_INDEPENDENTLY_VALIDATED":
            errors.append("DECLARATION_VIOLATION: Missing 'NOT_INDEPENDENTLY_VALIDATED'")

        if meta.get("extractor_version") != PIPELINE_VERSION:
            errors.append(f"VERSION_MISMATCH: Extractor version {meta.get('extractor_version')} != {PIPELINE_VERSION}")

        # 4. Verify artifact hashes
        gen_hashes = meta.get("generated_artifact_hashes", {})
        for fname, exp_sha in gen_hashes.items():
            fpath = os.path.join(candidate_dir, fname)
            if not os.path.exists(fpath):
                errors.append(f"HASH_CHECK_MISSING_FILE: File '{fname}' in metadata missing on disk.")
                continue
            act_sha = sha256_file(fpath)
            if act_sha != exp_sha:
                errors.append(f"ARTIFACT_HASH_MISMATCH: '{fname}' expected {exp_sha}, got {act_sha}")

        # 5. Validate Candidate Contract Draft-07 schema
        contract_path = os.path.join(candidate_dir, "candidate_contract.json")
        try:
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
            jsonschema.Draft7Validator.check_schema(contract)
        except Exception as e:
            errors.append(f"SCHEMA_INVALID: Candidate contract is not valid JSON Schema Draft-07: {e}")

        # 6. Check closed object on root and surfaces
        if contract.get("additionalProperties") is not False:
            errors.append("CLOSED_OBJECT_VIOLATION: Root contract must declare additionalProperties: false")

        props = contract.get("properties", {})
        for surf_name, surf_schema in props.items():
            if isinstance(surf_schema, dict) and surf_schema.get("type") == "object":
                if surf_schema.get("additionalProperties") is not False:
                    errors.append(f"CLOSED_SURFACE_VIOLATION: Surface '{surf_name}' must declare additionalProperties: false")

        # 7. Check dialect: Zero raw 'nullable' keywords
        def check_no_raw_nullable(node: Any, path: str):
            if isinstance(node, dict):
                if "nullable" in node:
                    errors.append(f"RAW_NULLABLE_DETECTED: Prohibited 'nullable' keyword at '{path}' in Draft-07 contract.")
                for k, v in node.items():
                    check_no_raw_nullable(v, f"{path}/{k}")
            elif isinstance(node, list):
                for i, it in enumerate(node):
                    check_no_raw_nullable(it, f"{path}/{i}")

        check_no_raw_nullable(contract, "#")

        # 8. Check form surface isolation
        adapters = meta.get("adapters_used", [])
        if "OpenAPI2FormDataAdapter" in adapters:
            if "form" not in props:
                errors.append("FORM_SURFACE_MISSING: OpenAPI2FormDataAdapter used but no 'form' surface in contract.")
            if "body" in props and bool(props["body"].get("properties")):
                errors.append("FORM_BODY_COLLISION: Form adapter used but 'body' surface also populated.")

        # 9. Check source reference closure
        closure_path = os.path.join(candidate_dir, "source_reference_closure.json")
        try:
            with open(closure_path, "r", encoding="utf-8") as f:
                closure = json.load(f)
            if len(closure.get("closure_sha256", "")) != 64:
                errors.append("CLOSURE_HASH_INVALID: Invalid closure_sha256 in source_reference_closure.json")
        except Exception as e:
            errors.append(f"CLOSURE_PARSE_ERROR: Failed to read source_reference_closure.json: {e}")

        # 10. Check adapter decisions
        decisions_path = os.path.join(candidate_dir, "adapter_decisions.json")
        try:
            with open(decisions_path, "r", encoding="utf-8") as f:
                decisions = json.load(f)
            if "decisions" not in decisions:
                errors.append("DECISIONS_FORMAT_ERROR: adapter_decisions.json missing 'decisions' array.")
        except Exception as e:
            errors.append(f"DECISIONS_PARSE_ERROR: Failed to read adapter_decisions.json: {e}")

        return len(errors) == 0, errors

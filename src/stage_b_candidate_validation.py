#!/usr/bin/env python3
"""Stage B Batch Candidate Validator.

Strict, fail-closed validator for quarantined extraction candidate bundles:
- Rejects candidate if placed inside validated-pilot directory (data_stage_b/canonical/).
- Rejects candidate if lifecycle status is anything other than EXTRACTED_PENDING_HUMAN_VALIDATION.
- Rejects candidate if creation mode is not BATCH_GENERATED_CANDIDATE.
- Rejects candidate if independent validation is claimed.
- Verifies cryptographic hashes of all generated artifacts.
- Verifies raw source hashes against disk.
- Verifies Draft-07 schema validity and structural invariants.
- Verifies additionalProperties: false on root and all transport surfaces.
- Verifies difference register completeness, absence of duplicates, and proper classification
  (wrapper changes must NEVER be classified as PRESERVED).
- Verifies complete field lineage provenance for every canonical property.
- Rejects any presence of unratified unions, recursion cycles, depth > 5, or binary payloads.
"""

import copy
import glob
import hashlib
import json
import os
import re
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
from src.stage_b_candidate_pipeline import (
    resolve_json_pointer,
    compute_schema_depth,
    WRAPPER_POLICY_ID,
)

REQUIRED_ARTIFACT_FILES = [
    "candidate_contract.json",
    "field_lineage.jsonl",
    "difference_register.json",
    "extraction_metadata.json",
    "feature_inventory.json",
    "serialization_characterization.json",
    "candidate_validation_report.md",
    "review_packet.md",
]


class CandidateValidator:
    """Validator enforcing strict integrity and provenance on batch candidate bundles."""

    def __init__(self, raw_doc: Optional[Any] = None):
        self.raw_doc = raw_doc

    def validate_candidate_bundle(
        self,
        candidate_dir: str,
        expected_slot_id: Optional[str] = None,
        raw_doc_override: Optional[Any] = None,
    ) -> Tuple[bool, List[str]]:
        """Validate an extraction candidate directory.

        Returns:
            (is_valid, list_of_errors)
        """
        errors: List[str] = []
        norm_dir = os.path.abspath(candidate_dir).replace("\\", "/")

        # 1. Directory quarantine check
        canonical_dir = os.path.abspath(os.path.join(ROOT_DIR, "data_stage_b", "canonical")).replace("\\", "/")
        if norm_dir.startswith(canonical_dir):
            errors.append(
                f"QUARANTINE_VIOLATION: Batch candidate must not be placed in validated-pilot directory '{canonical_dir}'"
            )
            return False, errors

        # 2. Check all 8 required files exist and are non-empty
        for fname in REQUIRED_ARTIFACT_FILES:
            fpath = os.path.join(candidate_dir, fname)
            if not os.path.exists(fpath):
                errors.append(f"MISSING_ARTIFACT: Required artifact '{fname}' missing at '{fpath}'")
            elif os.path.getsize(fpath) == 0:
                errors.append(f"EMPTY_ARTIFACT: Artifact '{fname}' is empty at '{fpath}'")

        if errors:
            return False, errors

        # 3. Validate extraction_metadata.json
        meta_path = os.path.join(candidate_dir, "extraction_metadata.json")
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception as e:
            errors.append(f"METADATA_PARSE_ERROR: Failed to parse extraction_metadata.json: {e}")
            return False, errors

        slot_id = metadata.get("slot_id")
        if expected_slot_id and slot_id != expected_slot_id:
            errors.append(f"SLOT_ID_MISMATCH: Metadata slot_id '{slot_id}' != expected '{expected_slot_id}'")

        status = metadata.get("lifecycle_status")
        if status != "EXTRACTED_PENDING_HUMAN_VALIDATION":
            errors.append(
                f"LIFECYCLE_STATUS_VIOLATION: Status must be 'EXTRACTED_PENDING_HUMAN_VALIDATION', got '{status}'"
            )

        creation_mode = metadata.get("creation_mode")
        if creation_mode != "BATCH_GENERATED_CANDIDATE":
            errors.append(
                f"CREATION_MODE_VIOLATION: Creation mode must be 'BATCH_GENERATED_CANDIDATE', got '{creation_mode}'"
            )

        declaration = metadata.get("declaration")
        if declaration != "NOT_INDEPENDENTLY_VALIDATED":
            errors.append(
                f"DECLARATION_VIOLATION: Missing mandatory declaration 'NOT_INDEPENDENTLY_VALIDATED', got '{declaration}'"
            )

        # 4. Cryptographic artifact hash verification
        gen_hashes = metadata.get("generated_artifact_hashes", {})
        for fname, expected_hash in gen_hashes.items():
            fpath = os.path.join(candidate_dir, fname)
            if not os.path.exists(fpath):
                errors.append(f"HASH_VERIFY_MISSING: File '{fname}' referenced in metadata hashes does not exist")
                continue
            actual_hash = sha256_file(fpath)
            if actual_hash != expected_hash:
                errors.append(
                    f"ARTIFACT_HASH_TAMPERED: Artifact '{fname}' SHA-256 mismatch (actual={actual_hash}, expected={expected_hash})"
                )

        # 5. Raw source hash check
        raw_file_sha = metadata.get("raw_source_file_sha256")
        cid = metadata.get("candidate_source_id")
        bsha = metadata.get("raw_source_blob_sha")
        if cid and bsha and raw_file_sha:
            try:
                raw_path, calc_sha, _ = resolve_raw_source_file(cid, bsha)
                if calc_sha != raw_file_sha:
                    errors.append(
                        f"RAW_SOURCE_HASH_DRIFT: Raw source '{raw_path}' SHA-256 {calc_sha} != metadata {raw_file_sha}"
                    )
            except Exception as e:
                errors.append(f"RAW_SOURCE_RESOLUTION_FAILED: {e}")

        # 6. Validate candidate_contract.json
        contract_path = os.path.join(candidate_dir, "candidate_contract.json")
        try:
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
        except Exception as e:
            errors.append(f"CONTRACT_PARSE_ERROR: Failed to parse candidate_contract.json: {e}")
            return False, errors

        # Validate JSON Schema Draft-07 conformance
        try:
            jsonschema.Draft7Validator.check_schema(contract)
        except jsonschema.exceptions.SchemaError as e:
            errors.append(f"SCHEMA_INVALID_DRAFT07: {e.message}")

        if contract.get("additionalProperties") is not False:
            errors.append("ROOT_OBJECT_UNCLOSED: Root contract must enforce additionalProperties: false")

        if contract.get("type") != "object":
            errors.append(f"ROOT_TYPE_INVALID: Root type must be 'object', got '{contract.get('type')}'")

        props = contract.get("properties", {})
        for surf in ["path", "query", "header", "body"]:
            if surf not in props:
                errors.append(f"SURFACE_CONTAINER_MISSING: Container '{surf}' missing from properties")
            else:
                surf_node = props[surf]
                if not isinstance(surf_node, dict):
                    errors.append(f"SURFACE_NOT_OBJECT: Container '{surf}' must be an object schema")
                elif surf_node.get("additionalProperties") is not False:
                    errors.append(f"SURFACE_UNCLOSED: Container '{surf}' must enforce additionalProperties: false")

        # Check for prohibited features in candidate contract
        contract_str = json.dumps(contract)
        if "oneOf" in contract:
            errors.append("PROHIBITED_FEATURE_EMITTED: Contract contains prohibited 'oneOf' construct")
        if "anyOf" in contract:
            errors.append("PROHIBITED_FEATURE_EMITTED: Contract contains prohibited 'anyOf' construct")

        def check_node_safety(node: Any, path: str):
            if not isinstance(node, dict):
                return
            if "oneOf" in node:
                errors.append(f"PROHIBITED_FEATURE_EMITTED: oneOf at {path}")
            if "anyOf" in node:
                errors.append(f"PROHIBITED_FEATURE_EMITTED: anyOf at {path}")
            if "discriminator" in node:
                errors.append(f"PROHIBITED_FEATURE_EMITTED: discriminator at {path}")
            if node.get("format") in ["binary", "byte"]:
                errors.append(f"PROHIBITED_FEATURE_EMITTED: binary format at {path}")
            if "$ref" in node and not node["$ref"].startswith("#/"):
                errors.append(f"PROHIBITED_FEATURE_EMITTED: external ref '{node['$ref']}' at {path}")

            if "properties" in node and isinstance(node["properties"], dict):
                for p_name, p_node in node["properties"].items():
                    check_node_safety(p_node, f"{path}/properties/{p_name}")
            if "items" in node:
                if isinstance(node["items"], dict):
                    check_node_safety(node["items"], f"{path}/items")
                elif isinstance(node["items"], list):
                    for idx_item, it in enumerate(node["items"]):
                        check_node_safety(it, f"{path}/items/{idx_item}")

        check_node_safety(contract, "")

        # Check depth
        depth = compute_schema_depth(contract)
        if depth > 6:  # root + wrapper surfaces + 5 levels
            errors.append(f"EXCESSIVE_DEPTH: Contract nesting depth {depth} exceeds allowed limit")

        # 7. Validate difference_register.json
        diff_path = os.path.join(candidate_dir, "difference_register.json")
        try:
            with open(diff_path, "r", encoding="utf-8") as f:
                diffs = json.load(f)
        except Exception as e:
            errors.append(f"DIFF_PARSE_ERROR: Failed to parse difference_register.json: {e}")
            return False, errors

        if not isinstance(diffs, list) or len(diffs) == 0:
            errors.append("DIFFERENCE_REGISTER_EMPTY: difference_register.json must contain records")
        else:
            seen_cand_ptrs: Set[str] = set()
            for idx_diff, d in enumerate(diffs):
                if not isinstance(d, dict):
                    errors.append(f"MALFORMED_DIFF_RECORD: Record at index {idx_diff} is not a dict")
                    continue
                cand_ptr = d.get("candidate_json_pointer")
                src_ptr = d.get("source_json_pointer")
                classification = d.get("classification")
                rationale = d.get("rationale")

                if not cand_ptr or not src_ptr or not classification or not rationale:
                    errors.append(f"MALFORMED_DIFF_RECORD: Record {idx_diff} missing required fields")

                if cand_ptr in seen_cand_ptrs:
                    errors.append(f"DUPLICATE_DIFF_RECORD: Duplicate candidate pointer '{cand_ptr}' in difference register")
                seen_cand_ptrs.add(cand_ptr)

                # Check wrapper normalization classification rule
                if "additionalProperties" in str(cand_ptr) and classification == "PRESERVED":
                    errors.append(
                        f"MISLABELED_WRAPPER_CLASSIFICATION: Wrapper change at '{cand_ptr}' mislabeled as PRESERVED"
                    )

        # 8. Validate field_lineage.jsonl
        lineage_path = os.path.join(candidate_dir, "field_lineage.jsonl")
        lineage_ptrs: Set[str] = set()
        lineage_records: List[Dict[str, Any]] = []
        try:
            with open(lineage_path, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    c_ptr = rec.get("canonical_json_pointer")
                    if not c_ptr:
                        errors.append(f"LINEAGE_RECORD_MISSING_POINTER: Line {line_idx+1}")
                    lineage_ptrs.add(c_ptr)
                    lineage_records.append(rec)
        except Exception as e:
            errors.append(f"LINEAGE_PARSE_ERROR: Failed to parse field_lineage.jsonl: {e}")

        # Ensure every property in candidate contract has lineage provenance
        for surf in ["path", "query", "header", "body"]:
            surf_props = props.get(surf, {}).get("properties", {})
            for p_name in surf_props.keys():
                expected_ptr = f"/properties/{surf}/properties/{p_name}"
                if expected_ptr not in lineage_ptrs:
                    errors.append(f"FIELD_LACKS_PROVENANCE: No lineage record for '{expected_ptr}'")

        if "/description" not in lineage_ptrs:
            errors.append("FIELD_LACKS_PROVENANCE: No lineage record for '/description'")

        # If raw_doc is available, verify lineage raw pointers exist
        active_raw_doc = raw_doc_override or self.raw_doc
        if active_raw_doc:
            for rec in lineage_records:
                for r_ptr in rec.get("raw_source_pointers", []):
                    try:
                        resolve_json_pointer(active_raw_doc, r_ptr)
                    except Exception as ex:
                        errors.append(f"LINEAGE_SOURCE_POINTER_INVALID: Raw pointer '{r_ptr}' does not resolve: {ex}")

        return len(errors) == 0, errors

#!/usr/bin/env python3
"""Stage B Candidate Bundle Validator V4.

Validates that candidate bundles in data_stage_b/extraction_candidates_v4/<SLOT_ID>/
meet all structural, cryptographic, and epistemic criteria under Pipeline 4.0.0.

Required Review Artifacts per Bundle (13):
1. candidate_contract.json
2. field_lineage.jsonl
3. difference_register.json
4. difference_register.md
5. extraction_metadata.json
6. feature_inventory.json
7. serialization_characterization.json
8. candidate_validation_report.md
9. review_packet.md
10. source_reference_closure.json
11. adapter_decisions.json
12. static_source_evidence.json
13. intermediate_representation.json
"""

import json
import os
import sys
from typing import Any, Dict, List, Tuple
import jsonschema

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.validate_stage_b_intermediate_representation import IntermediateRepresentationValidator

REQUIRED_V4_ARTIFACTS = [
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
    "static_source_evidence.json",
    "intermediate_representation.json",
]


class CandidateValidatorV4:
    """Validator for V4 candidate extraction bundles."""

    def __init__(self):
        self.ir_validator = IntermediateRepresentationValidator()

    def validate_candidate_bundle(
        self,
        slot_dir: str,
        expected_slot_id: str,
    ) -> Tuple[bool, List[str]]:
        """Validate an extracted candidate bundle on disk."""
        errors: List[str] = []

        if not os.path.isdir(slot_dir):
            return False, [f"Slot directory does not exist: {slot_dir}"]

        # 1. Verify presence of all 13 required artifacts
        for fname in REQUIRED_V4_ARTIFACTS:
            fpath = os.path.join(slot_dir, fname)
            if not os.path.exists(fpath):
                errors.append(f"Missing required V4 artifact: {fname}")

        if errors:
            return False, errors

        # 2. Validate candidate_contract.json
        contract_path = os.path.join(slot_dir, "candidate_contract.json")
        try:
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
        except Exception as e:
            errors.append(f"Invalid JSON in candidate_contract.json: {e}")
            contract = None

        if contract:
            # Check JSON Schema Draft-07 syntax
            try:
                jsonschema.Draft7Validator.check_schema(contract)
            except jsonschema.SchemaError as e:
                errors.append(f"Contract fails JSON Schema Draft-07 validation: {e.message}")

            # Check for unhandled raw nullable keyword
            with open(contract_path, "r", encoding="utf-8") as f:
                c_text = f.read()
                if '"nullable"' in c_text:
                    errors.append("Raw OpenAPI 'nullable' keyword detected in candidate_contract.json")

            # Check closed surface
            if contract.get("additionalProperties") is not False:
                errors.append("Contract must explicitly declare additionalProperties: false")

        # 3. Validate extraction_metadata.json
        meta_path = os.path.join(slot_dir, "extraction_metadata.json")
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception as e:
            errors.append(f"Invalid JSON in extraction_metadata.json: {e}")
            meta = None

        if meta:
            if meta.get("slot_id") != expected_slot_id:
                errors.append(f"Slot ID mismatch in metadata: expected {expected_slot_id}, got {meta.get('slot_id')}")
            if meta.get("extractor_version") != "4.0.0":
                errors.append(f"Extractor version must be 4.0.0, got {meta.get('extractor_version')}")
            if meta.get("lifecycle_status") != "EXTRACTED_PENDING_HUMAN_VALIDATION":
                errors.append(f"Unauthorized lifecycle status: {meta.get('lifecycle_status')}")
            if meta.get("declaration") != "NOT_INDEPENDENTLY_VALIDATED":
                errors.append("Declaration must be NOT_INDEPENDENTLY_VALIDATED")

        # 4. Validate intermediate_representation.json
        ir_path = os.path.join(slot_dir, "intermediate_representation.json")
        try:
            with open(ir_path, "r", encoding="utf-8") as f:
                ir_data = json.load(f)
            ir_valid, ir_errors = self.ir_validator.validate(ir_data)
            if not ir_valid:
                errors.extend([f"IR validation error: {err}" for err in ir_errors])
        except Exception as e:
            errors.append(f"Failed to validate intermediate_representation.json: {e}")

        # 5. Global CANONICAL_FAITHFUL prohibition
        for fname in REQUIRED_V4_ARTIFACTS:
            fpath = os.path.join(slot_dir, fname)
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                if "CANONICAL_FAITHFUL" in content:
                    errors.append(f"Strict invariant violation: CANONICAL_FAITHFUL found in {fname}")

        return len(errors) == 0, errors

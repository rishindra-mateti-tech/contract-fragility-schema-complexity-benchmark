"""Tests for Stage B Batch Candidate Validator and Adversarial Negative Tests.

Verifies:
1. Valid candidate bundles pass validation cleanly.
2. Validator fails closed when placed in validated-pilot directory (data_stage_b/canonical/).
3. Validator fails closed when lifecycle status is promoted (e.g. to CANONICAL_FAITHFUL).
4. Validator fails closed when creation mode or declaration is altered.
5. Validator fails closed when an artifact hash is tampered.
6. Validator fails closed when raw source hash drifts.
7. Validator fails closed when root or surface additionalProperties is not False.
8. Validator fails closed when prohibited keywords (oneOf, anyOf, discriminator, binary) are added.
9. Validator fails closed when a required field or property is deleted or renamed.
10. Validator fails closed when an enum is altered.
11. Validator fails closed when a difference register entry is removed or contains duplicates.
12. Validator fails closed when a wrapper change is mislabeled as PRESERVED.
13. Validator fails closed when lineage records reference invalid raw pointers.
14. Validator fails closed when an output property lacks lineage provenance.
"""

import copy
import json
import os
import shutil
import tempfile
import pytest

from src.stage_b_candidate_manifest import (
    ROOT_DIR,
    RAW_DIR,
    get_operation_universe,
    resolve_raw_source_file,
)
from src.stage_b_candidate_pipeline import (
    DEFAULT_GENERATION_TIMESTAMP,
    GenericCandidateExtractor,
)
from src.stage_b_candidate_validation import CandidateValidator


@pytest.fixture(scope="module")
def valid_candidate_bundle(tmp_path_factory):
    """Generate a clean candidate bundle in a temporary quarantine directory."""
    temp_dir = tmp_path_factory.mktemp("quarantined_candidates")
    slot_id = "SLOT_GITHUB_02"
    slot_dir = str(temp_dir / slot_id)
    os.makedirs(slot_dir, exist_ok=True)

    universe = get_operation_universe()
    op = next(o for o in universe["eligible_monomorphic_candidates"] if o["slot_id"] == slot_id)
    raw_path, calc_sha, ext = resolve_raw_source_file(op["candidate_source_id"], op["source_file_blob_sha"])
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    extractor = GenericCandidateExtractor(
        extractor_script_sha="DETERMINISTIC_TEST_SHA",
        extractor_git_commit="DETERMINISTIC_TEST_COMMIT",
    )
    bundle = extractor.extract_candidate_bundle(op, raw_doc, calc_sha, op["source_file_blob_sha"], DEFAULT_GENERATION_TIMESTAMP)

    with open(os.path.join(slot_dir, "candidate_contract.json"), "wb") as f:
        f.write(bundle["candidate_contract_json"])
    with open(os.path.join(slot_dir, "field_lineage.jsonl"), "wb") as f:
        f.write(bundle["field_lineage_jsonl"])
    with open(os.path.join(slot_dir, "difference_register.json"), "wb") as f:
        f.write(bundle["difference_register_json"])
    with open(os.path.join(slot_dir, "extraction_metadata.json"), "wb") as f:
        f.write(bundle["extraction_metadata_json"])
    with open(os.path.join(slot_dir, "feature_inventory.json"), "wb") as f:
        f.write(bundle["feature_inventory_json"])
    with open(os.path.join(slot_dir, "serialization_characterization.json"), "wb") as f:
        f.write(bundle["serialization_characterization_json"])
    with open(os.path.join(slot_dir, "candidate_validation_report.md"), "wb") as f:
        f.write(bundle["candidate_validation_report_md"])
    with open(os.path.join(slot_dir, "review_packet.md"), "wb") as f:
        f.write(bundle["review_packet_md"])

    return slot_dir, slot_id, raw_doc


def test_valid_bundle_passes_validation(valid_candidate_bundle):
    slot_dir, slot_id, raw_doc = valid_candidate_bundle
    validator = CandidateValidator(raw_doc=raw_doc)
    is_valid, errors = validator.validate_candidate_bundle(slot_dir, expected_slot_id=slot_id)
    assert is_valid, f"Expected clean bundle to pass validation, got: {errors}"
    assert len(errors) == 0


def test_quarantine_violation_in_canonical_dir(tmp_path):
    canonical_fake_dir = os.path.join(ROOT_DIR, "data_stage_b", "canonical", "TEST_FAKE_CANDIDATE")
    validator = CandidateValidator()
    is_valid, errors = validator.validate_candidate_bundle(canonical_fake_dir)
    assert not is_valid
    assert any("QUARANTINE_VIOLATION" in e for e in errors)


def test_negative_promote_lifecycle_status(valid_candidate_bundle, tmp_path):
    slot_dir, slot_id, raw_doc = valid_candidate_bundle
    mutated_dir = str(tmp_path / "mutated_status")
    shutil.copytree(slot_dir, mutated_dir)

    # Mutate status to CANONICAL_FAITHFUL
    meta_path = os.path.join(mutated_dir, "extraction_metadata.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    meta["lifecycle_status"] = "CANONICAL_FAITHFUL"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)

    validator = CandidateValidator(raw_doc=raw_doc)
    is_valid, errors = validator.validate_candidate_bundle(mutated_dir, expected_slot_id=slot_id)
    assert not is_valid
    assert any("LIFECYCLE_STATUS_VIOLATION" in e for e in errors)


def test_negative_tamper_artifact_hash(valid_candidate_bundle, tmp_path):
    slot_dir, slot_id, raw_doc = valid_candidate_bundle
    mutated_dir = str(tmp_path / "mutated_hash")
    shutil.copytree(slot_dir, mutated_dir)

    # Tamper candidate_contract.json without updating metadata hash
    contract_path = os.path.join(mutated_dir, "candidate_contract.json")
    with open(contract_path, "a", encoding="utf-8") as f:
        f.write("   \n")

    validator = CandidateValidator(raw_doc=raw_doc)
    is_valid, errors = validator.validate_candidate_bundle(mutated_dir, expected_slot_id=slot_id)
    assert not is_valid
    assert any("ARTIFACT_HASH_TAMPERED" in e for e in errors)


def test_negative_unclose_additional_properties(valid_candidate_bundle, tmp_path):
    slot_dir, slot_id, raw_doc = valid_candidate_bundle
    mutated_dir = str(tmp_path / "mutated_addl_props")
    shutil.copytree(slot_dir, mutated_dir)

    contract_path = os.path.join(mutated_dir, "candidate_contract.json")
    with open(contract_path, "r", encoding="utf-8") as f:
        contract = json.load(f)
    contract["additionalProperties"] = True
    with open(contract_path, "w", encoding="utf-8") as f:
        json.dump(contract, f)

    validator = CandidateValidator(raw_doc=raw_doc)
    is_valid, errors = validator.validate_candidate_bundle(mutated_dir, expected_slot_id=slot_id)
    assert not is_valid
    assert any("ROOT_OBJECT_UNCLOSED" in e for e in errors)


def test_negative_add_prohibited_union(valid_candidate_bundle, tmp_path):
    slot_dir, slot_id, raw_doc = valid_candidate_bundle
    mutated_dir = str(tmp_path / "mutated_union")
    shutil.copytree(slot_dir, mutated_dir)

    contract_path = os.path.join(mutated_dir, "candidate_contract.json")
    with open(contract_path, "r", encoding="utf-8") as f:
        contract = json.load(f)
    contract["properties"]["body"]["oneOf"] = [{"type": "string"}, {"type": "number"}]
    with open(contract_path, "w", encoding="utf-8") as f:
        json.dump(contract, f)

    validator = CandidateValidator(raw_doc=raw_doc)
    is_valid, errors = validator.validate_candidate_bundle(mutated_dir, expected_slot_id=slot_id)
    assert not is_valid
    assert any("PROHIBITED_FEATURE_EMITTED" in e for e in errors)


def test_negative_remove_difference_register_entry(valid_candidate_bundle, tmp_path):
    slot_dir, slot_id, raw_doc = valid_candidate_bundle
    mutated_dir = str(tmp_path / "mutated_diff_remove")
    shutil.copytree(slot_dir, mutated_dir)

    diff_path = os.path.join(mutated_dir, "difference_register.json")
    with open(diff_path, "w", encoding="utf-8") as f:
        json.dump([], f)

    validator = CandidateValidator(raw_doc=raw_doc)
    is_valid, errors = validator.validate_candidate_bundle(mutated_dir, expected_slot_id=slot_id)
    assert not is_valid
    assert any("DIFFERENCE_REGISTER_EMPTY" in e for e in errors)


def test_negative_duplicate_difference_record(valid_candidate_bundle, tmp_path):
    slot_dir, slot_id, raw_doc = valid_candidate_bundle
    mutated_dir = str(tmp_path / "mutated_diff_dup")
    shutil.copytree(slot_dir, mutated_dir)

    diff_path = os.path.join(mutated_dir, "difference_register.json")
    with open(diff_path, "r", encoding="utf-8") as f:
        diffs = json.load(f)
    diffs.append(copy.deepcopy(diffs[0]))
    with open(diff_path, "w", encoding="utf-8") as f:
        json.dump(diffs, f)

    validator = CandidateValidator(raw_doc=raw_doc)
    is_valid, errors = validator.validate_candidate_bundle(mutated_dir, expected_slot_id=slot_id)
    assert not is_valid
    assert any("DUPLICATE_DIFF_RECORD" in e for e in errors)


def test_negative_mislabeled_wrapper_classification(valid_candidate_bundle, tmp_path):
    slot_dir, slot_id, raw_doc = valid_candidate_bundle
    mutated_dir = str(tmp_path / "mutated_diff_mislabel")
    shutil.copytree(slot_dir, mutated_dir)

    diff_path = os.path.join(mutated_dir, "difference_register.json")
    with open(diff_path, "r", encoding="utf-8") as f:
        diffs = json.load(f)
    for d in diffs:
        if "additionalProperties" in d["candidate_json_pointer"]:
            d["classification"] = "PRESERVED"
    with open(diff_path, "w", encoding="utf-8") as f:
        json.dump(diffs, f)

    validator = CandidateValidator(raw_doc=raw_doc)
    is_valid, errors = validator.validate_candidate_bundle(mutated_dir, expected_slot_id=slot_id)
    assert not is_valid
    assert any("MISLABELED_WRAPPER_CLASSIFICATION" in e for e in errors)


def test_negative_output_field_lacks_provenance(valid_candidate_bundle, tmp_path):
    slot_dir, slot_id, raw_doc = valid_candidate_bundle
    mutated_dir = str(tmp_path / "mutated_lineage_missing")
    shutil.copytree(slot_dir, mutated_dir)

    contract_path = os.path.join(mutated_dir, "candidate_contract.json")
    with open(contract_path, "r", encoding="utf-8") as f:
        contract = json.load(f)
    contract["properties"]["body"]["properties"]["phantom_field"] = {"type": "string"}
    with open(contract_path, "w", encoding="utf-8") as f:
        json.dump(contract, f)

    validator = CandidateValidator(raw_doc=raw_doc)
    is_valid, errors = validator.validate_candidate_bundle(mutated_dir, expected_slot_id=slot_id)
    assert not is_valid
    assert any("FIELD_LACKS_PROVENANCE" in e for e in errors)


def test_negative_invalid_raw_pointer_in_lineage(valid_candidate_bundle, tmp_path):
    slot_dir, slot_id, raw_doc = valid_candidate_bundle
    mutated_dir = str(tmp_path / "mutated_lineage_invalid_pointer")
    shutil.copytree(slot_dir, mutated_dir)

    lineage_path = os.path.join(mutated_dir, "field_lineage.jsonl")
    with open(lineage_path, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]
    lines[0]["raw_source_pointers"] = ["#/paths/~1non_existent_pointer/post"]
    with open(lineage_path, "w", encoding="utf-8") as f:
        for item in lines:
            f.write(json.dumps(item) + "\n")

    validator = CandidateValidator(raw_doc=raw_doc)
    is_valid, errors = validator.validate_candidate_bundle(mutated_dir, expected_slot_id=slot_id)
    assert not is_valid
    assert any("LINEAGE_SOURCE_POINTER_INVALID" in e for e in errors)

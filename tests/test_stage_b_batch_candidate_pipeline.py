"""Tests for Stage B Generic Batch Candidate Extraction Pipeline.

Verifies:
1. Operation universe partitioning (pilots skipped, unions excluded, eligible monomorphic isolated).
2. Slot ID resolution and metadata integrity.
3. Preflight gates fail-closed behavior:
   - External refs rejected (DigitalOcean).
   - Non-spec code rejected (MCP Python and TypeScript).
   - Swagger 2.0 formData rejected (Slack).
   - Uninherited path-level parameters rejected (Chatwoot 02, 03).
   - Clean monomorphic operations pass preflight.
4. Determinism of candidate extraction (identical hashes across multiple runs).
5. Schema structural invariants:
   - Draft-07 schema valid.
   - Root additionalProperties: false enforced under WRAPPER_CLOSED_OBJECT_POLICY_001.
   - All 4 transport surfaces present and closed.
   - Lifecycle status strictly EXTRACTED_PENDING_HUMAN_VALIDATION.
   - Creation mode is BATCH_GENERATED_CANDIDATE.
   - Independent validation is NOT claimed.
"""

import json
import os
import pytest
import yaml

from src.stage_b_candidate_manifest import (
    ROOT_DIR,
    RAW_DIR,
    PREVIOUSLY_EXTRACTED_PILOT_SLOTS,
    UNION_SLOTS,
    load_manifest,
    load_provenance_registry,
    load_feature_registry,
    get_slot_id_for_operation,
    get_operation_universe,
    resolve_raw_source_file,
)
from src.stage_b_candidate_pipeline import (
    DEFAULT_GENERATION_TIMESTAMP,
    EXTRACTOR_VERSION,
    WRAPPER_POLICY_ID,
    PreflightChecker,
    GenericCandidateExtractor,
)


def test_operation_universe_partition():
    """Verify exact partition of the 30 manifest operations and 7 excluded operations."""
    universe = get_operation_universe()
    already_extracted = universe["already_extracted_pilots"]
    union_slots = universe["union_slots_excluded"]
    eligible_monomorphic = universe["eligible_monomorphic_candidates"]
    manifest_excluded = universe["manifest_disqualified_excluded"]

    # Manifest totals check
    assert len(already_extracted) == 2, f"Expected 2 already-extracted pilots, found {len(already_extracted)}"
    assert {op["slot_id"] for op in already_extracted} == PREVIOUSLY_EXTRACTED_PILOT_SLOTS

    assert len(union_slots) == 1, f"Expected 1 union slot, found {len(union_slots)}"
    assert {op["slot_id"] for op in union_slots} == UNION_SLOTS
    assert union_slots[0]["operation_id"] == "PostRefunds"

    assert len(eligible_monomorphic) == 27, f"Expected 27 eligible monomorphic candidates, found {len(eligible_monomorphic)}"
    assert len(manifest_excluded) == 7, f"Expected 7 manifest excluded operations, found {len(manifest_excluded)}"

    total_provisional = len(already_extracted) + len(union_slots) + len(eligible_monomorphic)
    assert total_provisional == 30, f"Total provisional operations must equal 30, got {total_provisional}"


def test_slot_id_mapping_coverage():
    """Verify every operation in the manifest maps to a unique canonical slot ID."""
    manifest = load_manifest()
    operations = manifest.get("operations", [])
    assert len(operations) == 30

    slots = [get_slot_id_for_operation(op["operation_id"], op.get("admission_slot_id")) for op in operations]
    assert len(slots) == len(set(slots)), "All slot IDs across the 30 operations must be unique"


def test_preflight_rejections_external_refs():
    """Verify DigitalOcean operations fail preflight due to external file references."""
    universe = get_operation_universe()
    do_ops = [op for op in universe["eligible_monomorphic_candidates"] if op["candidate_source_id"] == "CAND-003"]
    assert len(do_ops) == 3

    checker = PreflightChecker()
    for op in do_ops:
        raw_path, _, ext = resolve_raw_source_file(op["candidate_source_id"], op["source_file_blob_sha"])
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_doc = yaml.safe_load(f)
        res = checker.run_preflight(op, raw_doc, raw_path, ext)
        assert not res["passed"]
        assert res["rejection_code"] == "FEAT_REF_EXTERNAL_FILE"
        assert "external file reference" in res["rejection_reason"].lower()


def test_preflight_rejections_non_spec_code():
    """Verify MCP SQLite and MCP GitHub fail preflight due to non-OpenAPI code format (.py/.ts)."""
    universe = get_operation_universe()
    mcp_ops = [
        op for op in universe["eligible_monomorphic_candidates"]
        if op["candidate_source_id"] in ["CAND-009", "CAND-010"]
    ]
    assert len(mcp_ops) == 6

    checker = PreflightChecker()
    for op in mcp_ops:
        raw_path, _, ext = resolve_raw_source_file(op["candidate_source_id"], op["source_file_blob_sha"])
        res = checker.run_preflight(op, None, raw_path, ext)
        assert not res["passed"]
        assert res["rejection_code"] == "NON_OPENAPI_SPEC_SOURCE_CODE"
        assert res["rejection_category"] == "UNSUPPORTED_SPEC_FORMAT"


def test_preflight_rejections_swagger_form_data():
    """Verify Slack operations fail preflight due to Swagger 2.0 in:formData parameters."""
    universe = get_operation_universe()
    slack_ops = [op for op in universe["eligible_monomorphic_candidates"] if op["candidate_source_id"] == "CAND-006"]
    assert len(slack_ops) == 3

    checker = PreflightChecker()
    for op in slack_ops:
        raw_path, _, ext = resolve_raw_source_file(op["candidate_source_id"], op["source_file_blob_sha"])
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_doc = json.load(f)
        res = checker.run_preflight(op, raw_doc, raw_path, ext)
        assert not res["passed"]
        assert res["rejection_code"] == "FEAT_SWAGGER_FORM_DATA_UNSUPPORTED"


def test_preflight_rejections_uninherited_path_params():
    """Verify Chatwoot 02 and 03 fail preflight due to uninherited path-level parameters."""
    universe = get_operation_universe()
    cw_ops = [
        op for op in universe["eligible_monomorphic_candidates"]
        if op["operation_id"] in ["create-an-account-user", "create-a-conversation"]
    ]
    assert len(cw_ops) == 2

    checker = PreflightChecker()
    for op in cw_ops:
        raw_path, _, ext = resolve_raw_source_file(op["candidate_source_id"], op["source_file_blob_sha"])
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_doc = json.load(f)
        res = checker.run_preflight(op, raw_doc, raw_path, ext)
        assert not res["passed"]
        assert res["rejection_code"] == "UNINHERITED_PATH_PARAMETERS"


def test_eligible_candidates_pass_preflight_and_extract():
    """Verify eligible clean operations pass preflight and produce valid candidate bundles."""
    universe = get_operation_universe()
    # Test a sample of eligible operations across different domains and spec formats
    sample_slot_ids = ["SLOT_GITHUB_02", "SLOT_TWILIO_01", "SLOT_BOX_01", "SLOT_STRIPE_01", "SLOT_CHATWOOT_01", "SLOT_LINE_01"]
    sample_ops = [op for op in universe["eligible_monomorphic_candidates"] if op["slot_id"] in sample_slot_ids]
    assert len(sample_ops) == 6

    checker = PreflightChecker()
    extractor = GenericCandidateExtractor(
        extractor_script_sha="DETERMINISTIC_TEST_SHA",
        extractor_git_commit="DETERMINISTIC_TEST_COMMIT",
    )

    for op in sample_ops:
        raw_path, calc_sha, ext = resolve_raw_source_file(op["candidate_source_id"], op["source_file_blob_sha"])
        with open(raw_path, "rb") as f:
            raw_bytes = f.read()
        raw_doc = json.loads(raw_bytes.decode("utf-8")) if ext == ".json" else yaml.safe_load(raw_bytes.decode("utf-8"))

        res = checker.run_preflight(op, raw_doc, raw_path, ext)
        assert res["passed"], f"Expected {op['slot_id']} to pass preflight, got rejection: {res.get('rejection_reason')}"

        bundle = extractor.extract_candidate_bundle(
            op_entry=op,
            raw_doc=raw_doc,
            raw_file_sha=calc_sha,
            raw_blob_sha=op["source_file_blob_sha"],
            generated_at_utc=DEFAULT_GENERATION_TIMESTAMP,
        )

        contract = json.loads(bundle["candidate_contract_json"].decode("utf-8"))
        assert contract["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert contract["additionalProperties"] is False
        assert set(contract["properties"].keys()) == {"path", "query", "header", "body"}

        for surf in ["path", "query", "header", "body"]:
            assert contract["properties"][surf]["additionalProperties"] is False

        meta = contract["x-benchmark-metadata"]
        assert meta["status"] == "EXTRACTED_PENDING_HUMAN_VALIDATION"
        assert meta["creation_mode"] == "BATCH_GENERATED_CANDIDATE"
        assert meta["independent_validation_claimed"] is False
        assert meta["wrapper_normalization_policy"]["policy_id"] == WRAPPER_POLICY_ID

        # Verify difference register contains wrapper normalizations
        diffs = json.loads(bundle["difference_register_json"].decode("utf-8"))
        wrapper_diffs = [d for d in diffs if d["classification"] == "WRAPPER_NORMALIZATION"]
        assert len(wrapper_diffs) >= 5, "Must have wrapper normalization records for root and 4 surfaces"

        # Verify lineage contains records
        lineage_lines = bundle["field_lineage_jsonl"].decode("utf-8").strip().split("\n")
        assert len(lineage_lines) >= 5, "Must have lineage records for surfaces and description"


def test_extraction_determinism():
    """Verify extraction is 100% deterministic (identical hashes across separate executions)."""
    universe = get_operation_universe()
    op = next(o for o in universe["eligible_monomorphic_candidates"] if o["slot_id"] == "SLOT_GITHUB_02")

    raw_path, calc_sha, ext = resolve_raw_source_file(op["candidate_source_id"], op["source_file_blob_sha"])
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_doc = json.load(f)

    extractor = GenericCandidateExtractor(
        extractor_script_sha="DETERMINISTIC_TEST_SHA",
        extractor_git_commit="DETERMINISTIC_TEST_COMMIT",
    )

    b1 = extractor.extract_candidate_bundle(op, raw_doc, calc_sha, op["source_file_blob_sha"], DEFAULT_GENERATION_TIMESTAMP)
    b2 = extractor.extract_candidate_bundle(op, raw_doc, calc_sha, op["source_file_blob_sha"], DEFAULT_GENERATION_TIMESTAMP)

    assert b1["hashes"] == b2["hashes"]
    assert b1["candidate_contract_json"] == b2["candidate_contract_json"]
    assert b1["field_lineage_jsonl"] == b2["field_lineage_jsonl"]
    assert b1["difference_register_json"] == b2["difference_register_json"]

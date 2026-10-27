"""Tests for Stage C Semantic Oracle (Track 2).

Verifies exact match, semantic equivalence, schema violation detection,
missing slot detection, value corruption detection, hallucinated slot detection,
and abstention task evaluation.
"""

import json
from pathlib import Path
import pytest

from src.stage_c_latent_intent import LatentIntent, LatentSlot
from src.stage_c_intent_codec import StageCIntentCodec
from src.stage_c_semantic_oracle import StageCSemanticOracle


REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_CONTRACTS_DIR = REPO_ROOT / "data_stage_c" / "base_contracts"


@pytest.fixture
def sample_contract():
    with open(BASE_CONTRACTS_DIR / "BASE_SYNTH_001.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def sample_intent(sample_contract):
    gold = sample_contract["gold_examples"][0]
    return StageCIntentCodec.create_intent_from_contract_and_args(
        contract=sample_contract,
        arguments=gold,
        intent_id="INTENT_TEST_BASE_001"
    )


def test_oracle_exact_match(sample_contract, sample_intent):
    oracle = StageCSemanticOracle()
    tool_name = sample_contract["tool_name"]
    gold_args = sample_contract["gold_examples"][0]

    result = oracle.evaluate_invocation(
        expected_intent=sample_intent,
        target_contract=sample_contract,
        candidate_tool_name=tool_name,
        candidate_arguments=gold_args
    )

    assert result.is_success is True
    assert result.classification == "EXACT_MATCH"
    assert result.tool_correct is True
    assert result.schema_valid is True
    assert result.slot_precision == 1.0
    assert result.slot_recall == 1.0
    assert result.slot_f1 == 1.0


def test_oracle_tool_selection_error(sample_contract, sample_intent):
    oracle = StageCSemanticOracle()
    gold_args = sample_contract["gold_examples"][0]

    result = oracle.evaluate_invocation(
        expected_intent=sample_intent,
        target_contract=sample_contract,
        candidate_tool_name="incorrect_tool_name",
        candidate_arguments=gold_args
    )

    assert result.is_success is False
    assert result.classification == "TOOL_SELECTION_ERROR"
    assert result.tool_correct is False


def test_oracle_schema_violation(sample_contract, sample_intent):
    oracle = StageCSemanticOracle()
    tool_name = sample_contract["tool_name"]
    # Provide an invalid type for ttl_seconds (string instead of integer)
    invalid_args = dict(sample_contract["gold_examples"][0])
    invalid_args["ttl_seconds"] = "not_an_integer"

    result = oracle.evaluate_invocation(
        expected_intent=sample_intent,
        target_contract=sample_contract,
        candidate_tool_name=tool_name,
        candidate_arguments=invalid_args
    )

    assert result.is_success is False
    assert result.classification == "SCHEMA_VIOLATION"
    assert result.schema_valid is False
    assert len(result.schema_errors) > 0


def test_oracle_missing_required_slot(sample_contract, sample_intent):
    oracle = StageCSemanticOracle()
    tool_name = sample_contract["tool_name"]
    # Remove required key "key"
    args = dict(sample_contract["gold_examples"][0])
    del args["key"]

    result = oracle.evaluate_invocation(
        expected_intent=sample_intent,
        target_contract=sample_contract,
        candidate_tool_name=tool_name,
        candidate_arguments=args
    )

    # Note that removing required property fails schema validation too
    assert result.is_success is False
    assert result.classification in ["SCHEMA_VIOLATION", "MISSING_REQUIRED_SLOT"]


def test_oracle_value_corruption(sample_contract, sample_intent):
    oracle = StageCSemanticOracle()
    tool_name = sample_contract["tool_name"]
    corrupted_args = dict(sample_contract["gold_examples"][0])
    corrupted_args["value"] = "totally_corrupted_value_123"

    result = oracle.evaluate_invocation(
        expected_intent=sample_intent,
        target_contract=sample_contract,
        candidate_tool_name=tool_name,
        candidate_arguments=corrupted_args
    )

    assert result.is_success is False
    assert result.classification == "VALUE_CORRUPTION"
    assert "value" in result.corrupted_slots


def test_oracle_hallucinated_slot(sample_contract, sample_intent):
    oracle = StageCSemanticOracle()
    tool_name = sample_contract["tool_name"]
    extra_args = dict(sample_contract["gold_examples"][0])
    extra_args["unauthorized_hallucinated_param"] = "bad_data"

    result = oracle.evaluate_invocation(
        expected_intent=sample_intent,
        target_contract=sample_contract,
        candidate_tool_name=tool_name,
        candidate_arguments=extra_args
    )

    # In contracts with additionalProperties: false, this will be SCHEMA_VIOLATION or HALLUCINATED_SLOT
    assert result.is_success is False
    assert result.classification in ["SCHEMA_VIOLATION", "HALLUCINATED_SLOT"]


def test_oracle_abstention_evaluation():
    oracle = StageCSemanticOracle()

    # Case 1: Model correctly abstained (no tool call or ABSTAIN)
    res_abstain = oracle.evaluate_invocation(
        expected_intent=None,
        target_contract=None,
        candidate_tool_name=None,
        candidate_arguments=None,
        is_abstention_task=True
    )
    assert res_abstain.is_success is True
    assert res_abstain.classification == "CORRECT_ABSTENTION"

    # Case 2: Model wrongly invoked a tool on an unfulfillable task
    res_false_exec = oracle.evaluate_invocation(
        expected_intent=None,
        target_contract=None,
        candidate_tool_name="unwarranted_tool",
        candidate_arguments={"param": "value"},
        is_abstention_task=True
    )
    assert res_false_exec.is_success is False
    assert res_false_exec.classification == "FALSE_EXECUTION_UNWARRANTED"

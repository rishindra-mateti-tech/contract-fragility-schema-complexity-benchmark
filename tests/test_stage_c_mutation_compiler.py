"""Tests for Stage C Mutation Compiler (Track 3).

Verifies that all 5 mutation families compile correctly with expected
structural modifications, valid schemas, and accurate mapping specs.
"""

import json
from pathlib import Path
import pytest

from src.stage_c_mutation_compiler import StageCMutationCompiler


REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_CONTRACTS_DIR = REPO_ROOT / "data_stage_c" / "base_contracts"


@pytest.fixture
def base_contracts():
    contracts = []
    for cf in sorted(BASE_CONTRACTS_DIR.glob("BASE_SYNTH_*.json")):
        with open(cf, "r", encoding="utf-8") as f:
            contracts.append(json.load(f))
    return contracts


def test_compiler_canonical_family(base_contracts):
    compiler = StageCMutationCompiler()
    base = base_contracts[0]

    res = compiler.compile_mutation(base, family="CANONICAL", variant="default")
    assert res.family == "CANONICAL"
    assert res.mutated_contract["schema"] == base["schema"]
    assert res.mapping_spec["intent_to_arg_path"]["key"] == "key"
    assert res.complexity_delta["depth_delta"] == 0


def test_compiler_nested_hierarchy_family(base_contracts):
    compiler = StageCMutationCompiler()
    base = base_contracts[0]

    res = compiler.compile_mutation(base, family="NESTED_HIERARCHY", variant="default")
    assert res.family == "NESTED_HIERARCHY"

    mutated_schema = res.mutated_contract["schema"]
    properties = mutated_schema["properties"]
    assert "payload_parameters" in properties
    assert properties["payload_parameters"]["type"] == "object"
    assert properties["payload_parameters"]["additionalProperties"] is False

    # Check mapping spec
    assert "intent_to_arg_path" in res.mapping_spec
    paths = list(res.mapping_spec["intent_to_arg_path"].values())
    assert any(p.startswith("payload_parameters.") for p in paths)


def test_compiler_optionality_bloat_family(base_contracts):
    compiler = StageCMutationCompiler()
    base = base_contracts[0]

    res = compiler.compile_mutation(base, family="OPTIONALITY_BLOAT", variant="default")
    assert res.family == "OPTIONALITY_BLOAT"

    orig_count = len(base["schema"]["properties"])
    mutated_count = len(res.mutated_contract["schema"]["properties"])
    assert mutated_count > orig_count
    assert res.complexity_delta["properties_delta"] > 0

    # Injected fields must NOT be in required list
    mutated_required = res.mutated_contract["schema"].get("required", [])
    for bloat_key in res.mapping_spec["injected_optional_properties"]:
        assert bloat_key not in mutated_required


def test_compiler_ambiguous_identifiers_family(base_contracts):
    compiler = StageCMutationCompiler()
    base = base_contracts[0]  # BASE_SYNTH_001 has "key", "value", etc.

    res = compiler.compile_mutation(base, family="AMBIGUOUS_IDENTIFIERS", variant="default")
    assert res.family == "AMBIGUOUS_IDENTIFIERS"

    properties = res.mutated_contract["schema"]["properties"]
    assert "entry_identifier" in properties  # "key" mapped to "entry_identifier"
    assert "payload_content" in properties   # "value" mapped to "payload_content"
    assert "key" not in properties

    assert res.mapping_spec["intent_to_arg_path"]["key"] == "entry_identifier"
    assert res.mapping_spec["arg_to_intent_slot"]["entry_identifier"] == "key"


def test_compiler_distractor_set_complexity_family(base_contracts):
    compiler = StageCMutationCompiler()
    base = base_contracts[0]

    res = compiler.compile_mutation(
        base,
        family="DISTRACTOR_SET_COMPLEXITY",
        variant="default",
        all_contracts=base_contracts
    )
    assert res.family == "DISTRACTOR_SET_COMPLEXITY"
    assert len(res.distractor_tools) == 4
    for d in res.distractor_tools:
        assert d["contract_id"] != base["contract_id"]
        assert "tool_name" in d
        assert "schema" in d

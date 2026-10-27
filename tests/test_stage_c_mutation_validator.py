"""Tests for Stage C Mutation Validator (Track 3).

Verifies validation on all 200 compiled mutations in the registry,
ensuring Draft-07 compliance, additionalProperties constraints,
and reversibility.
"""

import json
from pathlib import Path
import pytest

from src.stage_c_mutation_compiler import MutationResult
from src.stage_c_mutation_validator import StageCMutationValidator


REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_CONTRACTS_DIR = REPO_ROOT / "data_stage_c" / "base_contracts"
MUTATIONS_DIR = REPO_ROOT / "data_stage_c" / "mutation_manifests"
REGISTRY_PATH = REPO_ROOT / "results_stage_c" / "MUTATION_REGISTRY.json"


def test_registry_manifest_and_counts():
    assert REGISTRY_PATH.is_file(), f"Registry file missing at {REGISTRY_PATH}"
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    assert registry["registry_version"] == "1.0.0"
    assert registry["total_mutations"] == 200
    assert registry["base_contracts_covered"] == 40

    distribution = registry["family_distribution"]
    assert distribution.get("CANONICAL") == 40
    assert distribution.get("NESTED_HIERARCHY") == 40
    assert distribution.get("OPTIONALITY_BLOAT") == 40
    assert distribution.get("AMBIGUOUS_IDENTIFIERS") == 40
    assert distribution.get("DISTRACTOR_SET_COMPLEXITY") == 40

    manifest_files = list(MUTATIONS_DIR.glob("MUT_*.json"))
    assert len(manifest_files) == 200


def test_all_persisted_mutations_pass_validation():
    validator = StageCMutationValidator()

    # Load base contracts for ground truth comparison
    base_contracts = {}
    for cf in BASE_CONTRACTS_DIR.glob("BASE_SYNTH_*.json"):
        with open(cf, "r", encoding="utf-8") as f:
            data = json.load(f)
            base_contracts[data["contract_id"]] = data

    manifest_files = sorted(MUTATIONS_DIR.glob("MUT_*.json"))
    assert len(manifest_files) == 200

    for mf in manifest_files:
        with open(mf, "r", encoding="utf-8") as f:
            m_dict = json.load(f)

        mutation_res = MutationResult(
            mutation_id=m_dict["mutation_id"],
            base_contract_id=m_dict["base_contract_id"],
            family=m_dict["family"],
            variant=m_dict["variant"],
            mutated_contract=m_dict["mutated_contract"],
            mapping_spec=m_dict["mapping_spec"],
            distractor_tools=m_dict.get("distractor_tools", []),
            complexity_delta=m_dict.get("complexity_delta", {}),
            provenance_statement=m_dict.get("provenance_statement", "")
        )

        base_contract = base_contracts[mutation_res.base_contract_id]
        is_valid, errors = validator.validate_mutation(mutation_res, base_contract)
        assert is_valid is True, f"Mutation {mf.name} failed validation: {errors}"

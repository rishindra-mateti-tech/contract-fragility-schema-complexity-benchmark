"""Tests for Stage C Synthetic Base Contract Corpus (Track 1).

Verifies contract counts, stratum distribution, schema validity, gold/counterexample
satisfaction, and deterministic generation.
"""

import json
from pathlib import Path
import pytest
import jsonschema

from src.stage_c_contract_validator import StageCContractValidator
from src.stage_c_synthetic_contract_generator import build_synthetic_base_corpus


REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_CONTRACTS_DIR = REPO_ROOT / "data_stage_c" / "base_contracts"
MANIFEST_PATH = REPO_ROOT / "data_stage_c" / "base_contract_manifest.json"
AUDIT_PATH = REPO_ROOT / "results_stage_c" / "BASE_CONTRACT_CORPUS_AUDIT.md"


def test_base_contract_count_and_manifest():
    assert MANIFEST_PATH.is_file(), f"Manifest missing at {MANIFEST_PATH}"
    assert AUDIT_PATH.is_file(), f"Audit missing at {AUDIT_PATH}"

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest.get("manifest_version") == "1.0.0"
    assert manifest.get("total_contracts") == 40
    assert len(manifest.get("contracts", [])) == 40

    contract_files = list(BASE_CONTRACTS_DIR.glob("BASE_SYNTH_*.json"))
    assert len(contract_files) == 40, f"Expected 40 files, got {len(contract_files)}"


def test_stratum_and_domain_distribution():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    contracts = manifest["contracts"]
    stratum_counts = {}
    domain_counts = {}

    for c in contracts:
        st = c["stratum"]
        dm = c["domain"]
        stratum_counts[st] = stratum_counts.get(st, 0) + 1
        domain_counts[dm] = domain_counts.get(dm, 0) + 1

    assert stratum_counts.get("SIMPLE_FLAT") == 12
    assert stratum_counts.get("MEDIUM_ARRAYS_ENUMS") == 16
    assert stratum_counts.get("NESTED_OBJECTS_SURFACES") == 12

    assert len(domain_counts) == 5
    for domain, count in domain_counts.items():
        assert count == 8, f"Expected 8 contracts in domain {domain}, found {count}"


def test_all_contracts_validate_via_validator():
    validator = StageCContractValidator()
    contract_files = sorted(BASE_CONTRACTS_DIR.glob("BASE_SYNTH_*.json"))

    for cf in contract_files:
        with open(cf, "r", encoding="utf-8") as f:
            data = json.load(f)
        is_valid, errors = validator.validate_contract(data)
        assert is_valid is True, f"Contract {cf.name} validation failed: {errors}"


def test_gold_and_counterexamples():
    contract_files = sorted(BASE_CONTRACTS_DIR.glob("BASE_SYNTH_*.json"))

    for cf in contract_files:
        with open(cf, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema = data["schema"]
        gold_examples = data["gold_examples"]
        counterexamples = data["counterexamples"]

        assert len(gold_examples) >= 2, f"{cf.name} has fewer than 2 gold examples"
        assert len(counterexamples) >= 2, f"{cf.name} has fewer than 2 counterexamples"

        for idx, gold in enumerate(gold_examples):
            try:
                jsonschema.validate(gold, schema)
            except jsonschema.ValidationError as err:
                pytest.fail(f"{cf.name} gold example {idx} failed schema validation: {err.message}")

        for idx, ce in enumerate(counterexamples):
            with pytest.raises(jsonschema.ValidationError):
                jsonschema.validate(ce, schema)


def test_regeneration_determinism():
    fresh_contracts = build_synthetic_base_corpus()
    assert len(fresh_contracts) == 40

    for contract in fresh_contracts:
        contract_id = contract["contract_id"]
        disk_path = BASE_CONTRACTS_DIR / f"{contract_id}.json"
        assert disk_path.is_file(), f"Missing file for {contract_id}"

        with open(disk_path, "r", encoding="utf-8") as f:
            disk_contract = json.load(f)

        assert contract == disk_contract, f"Determinism mismatch for {contract_id}"


def test_no_em_dash_or_forbidden_patterns_in_track1():
    files_to_check = [
        REPO_ROOT / "src" / "stage_c_contract_validator.py",
        REPO_ROOT / "src" / "stage_c_synthetic_contract_generator.py",
        REPO_ROOT / "results_stage_c" / "BASE_CONTRACT_CORPUS_AUDIT.md",
    ]
    for p in files_to_check:
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        assert "\u2014" not in content, f"Em dash found in {p.name}"
        assert "\u2013" not in content, f"En dash found in {p.name}"

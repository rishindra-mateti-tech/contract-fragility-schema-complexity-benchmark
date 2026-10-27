#!/usr/bin/env python3
"""Tests for Stage C Protocol, Preregistration, and Scope Freeze Invariants (Track 0)."""

import json
import os
import sys
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

PROTOCOL_MD = os.path.join(ROOT_DIR, "STAGE_C_PROTOCOL.md")
SCOPE_FREEZE_MD = os.path.join(ROOT_DIR, "results_stage_c", "STAGE_C_SCOPE_FREEZE.md")
PREREG_JSON = os.path.join(ROOT_DIR, "results_stage_c", "STAGE_C_PREREGISTRATION.json")
THREATS_MD = os.path.join(ROOT_DIR, "results_stage_c", "STAGE_C_THREATS_TO_VALIDITY.md")

EXPECTED_STARTING_SHA = "57ee369f00b3fd03621f92b879abdc286e66bce2"
RESEARCH_QUESTION = "Under controlled synthetic task conditions, how do specified schema transformations affect structured tool-use task completion?"


def test_protocol_document_exists_and_declares_core_elements():
    """Verify STAGE_C_PROTOCOL.md exists and articulates all mandatory protocol structures."""
    assert os.path.exists(PROTOCOL_MD), "Missing STAGE_C_PROTOCOL.md"
    with open(PROTOCOL_MD, "r", encoding="utf-8") as f:
        text = f.read()

    # Research Question as explicit question
    assert RESEARCH_QUESTION in text

    # Three primary task categories
    assert "Argument Construction" in text
    assert "Tool Selection Among Distractors" in text
    assert "Abstention When No Valid Tool Applies" in text

    # Five mutation families
    assert "CANONICAL" in text
    assert "NESTED_HIERARCHY" in text
    assert "OPTIONALITY_BLOAT" in text
    assert "AMBIGUOUS_IDENTIFIERS" in text
    assert "DISTRACTOR_SET_COMPLEXITY" in text

    # Primary outcomes
    assert "Tool-Name Exact Match" in text
    assert "Syntax-Valid Argument Rate" in text
    assert "Semantic Argument Exact Match" in text
    assert "Abstention Precision" in text

    # Epistemic distinction
    assert "Synthetic Latent-Intent vs Real APIs" in text or "internal task equivalence" in text


def test_scope_freeze_document_integrity():
    """Verify STAGE_C_SCOPE_FREEZE.md documents starting state and strict boundaries."""
    assert os.path.exists(SCOPE_FREEZE_MD), "Missing STAGE_C_SCOPE_FREEZE.md"
    with open(SCOPE_FREEZE_MD, "r", encoding="utf-8") as f:
        text = f.read()

    assert EXPECTED_STARTING_SHA in text
    assert "Protocol Version: `1.0.0`" in text or "Protocol Version: 1.0.0" in text or "`1.0.0`" in text
    assert "INFRASTRUCTURE_DESIGN_ONLY" in text

    # Invariant boundaries
    assert "Zero LLM / Model Inference" in text
    assert "Stage B raw sources" in text or "Stage B candidates" in text
    assert "Zero Result Fabrication" in text


def test_preregistration_json_schema_and_invariants():
    """Verify STAGE_C_PREREGISTRATION.json is structurally sound and adheres to pre-registration constraints."""
    assert os.path.exists(PREREG_JSON), "Missing STAGE_C_PREREGISTRATION.json"
    with open(PREREG_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["preregistration_version"] == "1.0.0"
    assert data["protocol_version"] == "1.0.0"
    assert data["empirical_results_state"] == "NO_EMPIRICAL_RESULTS_PRESENT"
    assert data["research_question"] == RESEARCH_QUESTION
    assert data["master_random_seed"] == 42
    assert "master_seed * 1000 + contract_index" in data["subseed_derivation_rule"]

    # Categories
    cat_ids = [c["category_id"] for c in data["task_categories"]]
    assert "ARGUMENT_CONSTRUCTION" in cat_ids
    assert "TOOL_SELECTION" in cat_ids
    assert "ABSTENTION" in cat_ids

    # Mutation families
    fam_ids = [m["family_id"] for m in data["mutation_families"]]
    assert "CANONICAL" in fam_ids
    assert "NESTED_HIERARCHY" in fam_ids
    assert "OPTIONALITY_BLOAT" in fam_ids
    assert "AMBIGUOUS_IDENTIFIERS" in fam_ids
    assert "DISTRACTOR_SET_COMPLEXITY" in fam_ids

    # Targets
    assert data["sample_targets"]["minimum_base_contracts"] >= 40
    assert data["sample_targets"]["minimum_task_instances"] >= 300

    # Declarations
    assert data["declarations"]["zero_model_execution_in_stage_c"] is True
    assert data["declarations"]["zero_unvalidated_stage_b_data_used"] is True
    assert data["declarations"]["no_claim_of_production_api_equivalence"] is True


def test_threats_to_validity_coverage():
    """Verify STAGE_C_THREATS_TO_VALIDITY.md systematically addresses all validity dimensions."""
    assert os.path.exists(THREATS_MD), "Missing STAGE_C_THREATS_TO_VALIDITY.md"
    with open(THREATS_MD, "r", encoding="utf-8") as f:
        text = f.read()

    assert "Construct Validity" in text
    assert "Internal Validity" in text
    assert "External Validity" in text
    assert "Statistical Conclusion Validity" in text
    assert "Prompt Leakage" in text
    assert "Multiple Hypothesis Testing Inflation" in text


def test_strict_punctuation_and_anti_ai_invariants():
    """Verify that Stage C Track 0 documents strictly adhere to anti-AI style and punctuation rules."""
    stage_c_files = [PROTOCOL_MD, SCOPE_FREEZE_MD, THREATS_MD]
    for fpath in stage_c_files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        assert "—" not in content, f"Forbidden em dash in {fpath}"
        assert "–" not in content, f"Forbidden en dash in {fpath}"
        assert "CANONICAL_FAITHFUL" not in content, f"Forbidden CANONICAL_FAITHFUL token in {fpath}"

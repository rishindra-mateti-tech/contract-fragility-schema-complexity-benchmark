"""Tests for Stage C Release 1 Finding Adjudication Engine (Track 0).

Verifies that all 654 Release 1 diagnostic findings are categorized into the four
preregistered adjudication categories with complete scientific justification.
"""

from pathlib import Path
import json
import pytest

from src.adjudicate_stage_c_release1_findings import (
    StageCRelease1Adjudicator,
    AdjudicatedFinding,
    OUTPUT_JSON,
    OUTPUT_MD
)

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_adjudication_completeness():
    adj = StageCRelease1Adjudicator()
    payload = adj.adjudicate_all()

    assert payload["total_findings_adjudicated"] == 654
    assert payload["remediation_required_count"] > 0
    assert OUTPUT_JSON.is_file()
    assert OUTPUT_MD.is_file()


def test_adjudication_category_partition():
    adj = StageCRelease1Adjudicator()
    payload = adj.adjudicate_all()
    dist = payload["category_distribution"]

    expected_categories = {
        "TRUE_CONSTRUCT_VALIDITY_DEFECT",
        "INTENTIONAL_PAIRED_DESIGN_REUSE",
        "AUDIT_RULE_FALSE_POSITIVE",
        "REQUIRES_HUMAN_JUDGMENT"
    }

    assert set(dist.keys()) == expected_categories
    assert sum(dist.values()) == 654
    assert dist["TRUE_CONSTRUCT_VALIDITY_DEFECT"] > 0
    assert dist["INTENTIONAL_PAIRED_DESIGN_REUSE"] == 100
    assert dist["AUDIT_RULE_FALSE_POSITIVE"] > 0


def test_tool_name_ac_adjudication():
    adj = StageCRelease1Adjudicator()
    payload = adj.adjudicate_all()

    ac_tool_findings = [
        a for a in payload["adjudications"]
        if a["audit_dimension"] == "TOOL_NAME_EXACT_LEAK" and a["category"] == "ARGUMENT_CONSTRUCTION"
    ]

    assert len(ac_tool_findings) == 100
    for f in ac_tool_findings:
        assert f["adjudicated_category"] == "AUDIT_RULE_FALSE_POSITIVE"
        assert f["remediation_required"] is True


def test_intent_conflict_adjudication():
    adj = StageCRelease1Adjudicator()
    payload = adj.adjudicate_all()

    intent_findings = [
        a for a in payload["adjudications"]
        if a["audit_dimension"] == "INTENT_CONFLICT"
    ]

    assert len(intent_findings) == 100
    for f in intent_findings:
        assert f["adjudicated_category"] == "INTENTIONAL_PAIRED_DESIGN_REUSE"
        assert f["remediation_required"] is True
        assert "paired_group_id" in f["remediation_strategy"]


def test_payload_parameters_wrapper_adjudication():
    adj = StageCRelease1Adjudicator()
    payload = adj.adjudicate_all()

    wrapper_findings = [
        a for a in payload["adjudications"]
        if a["audit_dimension"] == "CONSTRUCTION_OMITTED_GOLD_VALUE"
        and "payload_parameters" in a["release1_evidence"]
    ]

    assert len(wrapper_findings) == 25
    for f in wrapper_findings:
        assert f["adjudicated_category"] == "AUDIT_RULE_FALSE_POSITIVE"


def test_distractor_ambiguity_adjudication():
    adj = StageCRelease1Adjudicator()
    payload = adj.adjudicate_all()

    distractor_findings = [
        a for a in payload["adjudications"]
        if a["audit_dimension"] == "DISTRACTOR_SEMANTIC_AMBIGUITY"
    ]

    assert len(distractor_findings) == 3
    for f in distractor_findings:
        assert f["adjudicated_category"] == "TRUE_CONSTRUCT_VALIDITY_DEFECT"
        assert f["remediation_required"] is True

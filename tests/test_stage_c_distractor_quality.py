"""Tests for Stage C Distractor Quality and Task Ambiguity Audit (Track 2).

Verifies overlap heuristics, distractor proximity scoring, signature collision detection,
and ambiguity register generation.
"""

from pathlib import Path
import json
import pytest

from src.stage_c_semantic_overlap import StageCSemanticOverlap
from src.audit_stage_c_distractor_quality import StageCDistractorQualityAuditor


REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_JSON = REPO_ROOT / "results_stage_c" / "DISTRACTOR_QUALITY_AUDIT_RELEASE1.json"
REPORT_MD = REPO_ROOT / "results_stage_c" / "DISTRACTOR_QUALITY_AUDIT_RELEASE1.md"
AMBIGUITY_MD = REPO_ROOT / "results_stage_c" / "TASK_AMBIGUITY_REGISTER.md"


def test_semantic_overlap_heuristics():
    set_a = {"user", "cache", "key"}
    set_b = {"user", "data", "value"}

    jaccard = StageCSemanticOverlap.jaccard_similarity(set_a, set_b)
    assert 0.15 < jaccard < 0.25  # 1/5 = 0.20

    text_sim = StageCSemanticOverlap.text_similarity("get user cache", "fetch user cache entry")
    assert text_sim > 0.3


def test_schema_overlap_computation():
    schema1 = {
        "properties": {"user_id": {"type": "string"}, "ttl": {"type": "integer"}},
        "required": ["user_id"]
    }
    schema2 = {
        "properties": {"user_id": {"type": "string"}, "status": {"type": "string"}},
        "required": ["user_id"]
    }

    res = StageCSemanticOverlap.compute_schema_overlap(schema1, schema2)
    assert "user_id" in res["shared_properties"]
    assert res["identical_required_signature"] is True
    assert res["type_match_ratio"] == 1.0


def test_distractor_proximity_evaluation():
    target = {
        "tool_name": "update_user_status",
        "description": "Updates account status in database.",
        "schema": {"properties": {"user_id": {"type": "string"}}, "required": ["user_id"]}
    }
    distractor = {
        "tool_name": "delete_user_record",
        "description": "Deletes account record permanently.",
        "schema": {"properties": {"user_id": {"type": "string"}}, "required": ["user_id"]}
    }

    eval_res = StageCSemanticOverlap.evaluate_distractor_proximity(target, distractor)
    assert eval_res["distractor_name"] == "delete_user_record"
    assert eval_res["composite_proximity"] > 0.2
    assert eval_res["identical_required"] is True
    assert eval_res["is_duplicate_identity"] is False


def test_audit_reports_exist_and_cover_selection_and_abstention():
    assert REPORT_JSON.is_file(), f"Missing report JSON at {REPORT_JSON}"
    assert REPORT_MD.is_file(), f"Missing report markdown at {REPORT_MD}"
    assert AMBIGUITY_MD.is_file(), f"Missing ambiguity register at {AMBIGUITY_MD}"

    with open(REPORT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_tasks_audited"] == 200  # 100 TS + 100 AB
    assert data["category_counts"]["TOOL_SELECTION"] == 100
    assert data["category_counts"]["ABSTENTION"] == 100

    pos_dist = data["positional_distribution"]
    assert len(pos_dist) >= 4  # Positions distributed across index 0, 1, 2, 3, 4


def test_strict_punctuation_in_track_2():
    for p in [REPORT_MD, AMBIGUITY_MD]:
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        assert "\u2014" not in content, f"Em dash found in {p.name}"
        assert "\u2013" not in content, f"En dash found in {p.name}"

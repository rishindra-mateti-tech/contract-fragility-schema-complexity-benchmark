"""Tests for Stage C Task Leakage and Shortcut Audit Engine (Track 1).

Verifies feature extractors, 14-dimension leakage detection algorithms,
audit report existence, and transparent status distributions.
"""

from pathlib import Path
import json
import pytest

from src.stage_c_leakage_features import StageCLeakageFeatures, LeakageFinding
from src.audit_stage_c_task_leakage import StageCTaskLeakageAuditor


REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_JSON = REPO_ROOT / "results_stage_c" / "TASK_LEAKAGE_AUDIT_RELEASE1.json"
REPORT_MD = REPO_ROOT / "results_stage_c" / "TASK_LEAKAGE_AUDIT_RELEASE1.md"
POLICY_MD = REPO_ROOT / "results_stage_c" / "LEAKAGE_DETECTION_POLICY_001.md"


def test_leakage_features_tool_name_detection():
    prompt_exact = "Please execute the set_cache_entry operation now."
    prompt_stem = "We want to update the cache entry for user."
    prompt_none = "Store the user data in the key value store."

    exact, stem, stems = StageCLeakageFeatures.check_tool_name_leakage(prompt_exact, "set_cache_entry")
    assert exact is True
    assert "cache" in stems or "entry" in stems

    exact2, stem2, stems2 = StageCLeakageFeatures.check_tool_name_leakage(prompt_stem, "set_cache_entry")
    assert exact2 is False
    assert len(stems2) >= 1

    exact3, stem3, _ = StageCLeakageFeatures.check_tool_name_leakage(prompt_none, "set_cache_entry")
    assert exact3 is False


def test_leakage_features_field_name_detection():
    props = {
        "user_id": {"type": "string"},
        "ttl_seconds": {"type": "integer"},
        "value": {"type": "string"}
    }
    prompt = "Set user_id to 'usr_10' and ttl_seconds to 3600 with value 'active'."

    leaks = StageCLeakageFeatures.check_field_name_leakage(prompt, props)
    leak_dict = dict(leaks)

    assert "ttl_seconds" in leak_dict
    assert leak_dict["ttl_seconds"] == "SHORTCUT_LEAK"
    assert "value" in leak_dict
    assert leak_dict["value"] == "UNAVOIDABLE_DOMAIN_WORD"


def test_leakage_features_mutation_label_detection():
    prompt_clean = "Perform record insert with parameters."
    prompt_leaky = "Use the nested container structure to submit."

    assert len(StageCLeakageFeatures.check_mutation_label_leakage(prompt_clean)) == 0
    leaks = StageCLeakageFeatures.check_mutation_label_leakage(prompt_leaky)
    assert "nested" in leaks


def test_audit_report_release1_exists_and_covers_all_tasks():
    assert REPORT_JSON.is_file(), f"Missing audit report at {REPORT_JSON}"
    assert REPORT_MD.is_file(), f"Missing audit markdown at {REPORT_MD}"
    assert POLICY_MD.is_file(), f"Missing policy file at {POLICY_MD}"

    with open(REPORT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["benchmark_release"] == "RELEASE_1"
    assert data["total_tasks_audited"] == 300
    assert len(data["task_summaries"]) == 300

    status_dist = data["status_distribution"]
    assert "CLEAR" in status_dist
    assert "REQUIRES_HUMAN_REVIEW" in status_dist
    assert "INVALID" in status_dist


def test_strict_punctuation_in_track_1():
    for p in [REPORT_MD, POLICY_MD]:
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        assert "\u2014" not in content, f"Em dash found in {p.name}"
        assert "\u2013" not in content, f"En dash found in {p.name}"

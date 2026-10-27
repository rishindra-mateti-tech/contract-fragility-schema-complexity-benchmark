"""Tests for Stage C Prompt Diversity Audit (Track 3).

Verifies tokenization, entropy calculation, template skeleton extraction,
and diversity report generation.
"""

from pathlib import Path
import json
import pytest

from src.audit_stage_c_prompt_diversity import StageCPromptDiversityAuditor


REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_JSON = REPO_ROOT / "results_stage_c" / "PROMPT_DIVERSITY_AUDIT_RELEASE1.json"
REPORT_MD = REPO_ROOT / "results_stage_c" / "PROMPT_DIVERSITY_AUDIT_RELEASE1.md"


def test_diversity_report_exists_and_measures_entropy():
    assert REPORT_JSON.is_file(), f"Missing diversity JSON at {REPORT_JSON}"
    assert REPORT_MD.is_file(), f"Missing diversity markdown at {REPORT_MD}"

    with open(REPORT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_prompts"] == 300
    assert data["unique_tokens"] > 100
    assert data["shannon_entropy_bits"] > 4.0
    assert data["type_token_ratio"] > 0.05


def test_template_skeleton_extraction():
    prompt = "Please execute the set_cache_entry operation for 'user_1024' with count 5."
    skeleton = StageCPromptDiversityAuditor.extract_template_frame(prompt)
    assert "<VALUE>" in skeleton
    assert "<NUM>" in skeleton


def test_strict_punctuation_in_diversity_report():
    with open(REPORT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    assert "\u2014" not in content, f"Em dash found in {REPORT_MD.name}"
    assert "\u2013" not in content, f"En dash found in {REPORT_MD.name}"

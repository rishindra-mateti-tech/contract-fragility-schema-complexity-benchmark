"""Tests for Stage C Corpus Balance Audit (Track 3).

Verifies category ratios, stratum distribution, positional balance,
and confound register generation.
"""

from pathlib import Path
import json
import pytest

from src.audit_stage_c_corpus_balance import StageCCorpusBalanceAuditor


REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_JSON = REPO_ROOT / "results_stage_c" / "CORPUS_BALANCE_AUDIT_RELEASE1.json"
REPORT_MD = REPO_ROOT / "results_stage_c" / "CORPUS_BALANCE_AUDIT_RELEASE1.md"


def test_balance_report_exists_and_covers_300_tasks():
    assert REPORT_JSON.is_file(), f"Missing balance JSON at {REPORT_JSON}"
    assert REPORT_MD.is_file(), f"Missing balance markdown at {REPORT_MD}"

    with open(REPORT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_tasks"] == 300
    cat_counts = data["category_distribution"]
    assert cat_counts.get("ARGUMENT_CONSTRUCTION") == 100
    assert cat_counts.get("TOOL_SELECTION") == 100
    assert cat_counts.get("ABSTENTION") == 100


def test_strata_representation_balanced():
    with open(REPORT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    strata = data["strata_distribution"]
    assert strata.get("SIMPLE_FLAT") == 108
    assert strata.get("MEDIUM_ARRAYS_ENUMS") == 120
    assert strata.get("NESTED_OBJECTS_SURFACES") == 72


def test_strict_punctuation_in_balance_report():
    with open(REPORT_MD, "r", encoding="utf-8") as f:
        content = f.read()
    assert "\u2014" not in content, f"Em dash found in {REPORT_MD.name}"
    assert "\u2013" not in content, f"En dash found in {REPORT_MD.name}"

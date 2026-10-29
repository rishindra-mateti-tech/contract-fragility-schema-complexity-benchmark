"""Tests for Stage C Release 2 Audits (Track 3).

Verifies that the Release 2 leakage, distractor quality, corpus balance, and prompt
diversity audits pass all preregistered quality gates with zero invalid tasks.
"""

from pathlib import Path
import json
import pytest

from src.audit_stage_c_release2_leakage import StageCRelease2LeakageAuditor, TASKS_DIR, REPORT_JSON as LEAK_JSON
from src.audit_stage_c_release2_distractors import StageCRelease2DistractorAuditor, REPORT_JSON as DIST_JSON, AMBIGUITY_REGISTER_MD
from src.audit_stage_c_release2_balance import StageCRelease2BalanceAuditor, BASE_DIR, REPORT_JSON as BAL_JSON
from src.audit_stage_c_release2_prompt_diversity import StageCRelease2PromptDiversityAuditor, REPORT_JSON as DIV_JSON


@pytest.fixture(scope="module")
def release2_tasks():
    task_files = sorted(TASKS_DIR.glob("TASK_R2_*.json"))
    tasks = []
    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            tasks.append(json.load(f))
    return tasks


@pytest.fixture(scope="module")
def base_contracts():
    contracts = {}
    for cf in sorted(BASE_DIR.glob("BASE_SYNTH_*.json")):
        with open(cf, "r", encoding="utf-8") as f:
            c = json.load(f)
            contracts[c["contract_id"]] = c
    return contracts


def test_release2_leakage_audit_zero_invalid(release2_tasks):
    auditor = StageCRelease2LeakageAuditor()
    report = auditor.audit_all_tasks(release2_tasks)

    dist = report["status_distribution"]
    assert dist.get("INVALID") == 0, f"Found {dist.get('INVALID')} INVALID tasks in Release 2"
    assert dist.get("AMBIGUOUS") == 0, f"Found {dist.get('AMBIGUOUS')} AMBIGUOUS tasks in Release 2"
    assert dist.get("CLEAR") == 300
    assert LEAK_JSON.is_file()


def test_release2_distractor_audit_uniformity(release2_tasks):
    auditor = StageCRelease2DistractorAuditor()
    report = auditor.audit_tasks(release2_tasks)

    assert report["total_tasks_audited"] == 200
    assert report["ambiguity_items_count"] == 0

    pos_dist = report["positional_distribution"]
    for p in range(5):
        assert pos_dist.get(str(p)) == 20, f"Positional skew at index {p}: {pos_dist}"

    assert DIST_JSON.is_file()
    assert AMBIGUITY_REGISTER_MD.is_file()
    reg_text = AMBIGUITY_REGISTER_MD.read_text(encoding="utf-8")
    assert "Total Ambiguity Items Registered: `0`" in reg_text


def test_release2_corpus_balance(release2_tasks, base_contracts):
    auditor = StageCRelease2BalanceAuditor()
    report = auditor.audit_corpus(release2_tasks, base_contracts)

    assert report["total_tasks"] == 300
    assert report["balance_invariants_passed"] is True
    assert report["category_distribution"]["ARGUMENT_CONSTRUCTION"] == 100
    assert report["category_distribution"]["TOOL_SELECTION"] == 100
    assert report["category_distribution"]["ABSTENTION"] == 100
    assert BAL_JSON.is_file()


def test_release2_prompt_diversity(release2_tasks):
    auditor = StageCRelease2PromptDiversityAuditor()
    report = auditor.audit_diversity(release2_tasks)

    assert report["diversity_passed"] is True
    assert report["shannon_entropy_bits"] >= 4.0
    assert report["unique_tokens"] >= 250
    assert DIV_JSON.is_file()

"""Tests for Stage C Benchmark Audit (Track 7).

Verifies that the comprehensive benchmark audit passes all checks and
that all generated audit artifacts exist and adhere to standards.
"""

from pathlib import Path
import json

from src.audit_stage_c_benchmark import run_comprehensive_stage_c_audit


REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "results_stage_c"


def test_comprehensive_audit_passes():
    audit_data = run_comprehensive_stage_c_audit()
    assert audit_data["status"] == "PASS", f"Audit failed: {audit_data['errors']}"
    assert audit_data["base_contracts_audited"] == 40
    assert audit_data["mutations_audited"] == 200
    assert audit_data["tasks_audited"] == 300
    assert len(audit_data["errors"]) == 0


def test_audit_artifacts_exist():
    artifacts = [
        RESULTS_DIR / "STAGE_C_BENCHMARK_AUDIT.md",
        RESULTS_DIR / "STAGE_C_REPRODUCIBILITY_AUDIT.md",
        RESULTS_DIR / "STAGE_C_CLAIM_EVIDENCE_LEDGER.md",
    ]
    for art in artifacts:
        assert art.is_file(), f"Missing audit artifact {art.name}"
        with open(art, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 100
        assert "\u2014" not in content, f"Em dash found in {art.name}"
        assert "\u2013" not in content, f"En dash found in {art.name}"

"""
test_stage_b_paper_readiness.py - Unit and Regression Tests for Paper Readiness & Methodology Traceability.

Verifies:
1. All 4 paper readiness and methodology documents exist and are non-empty.
2. The 8 publication dimensions are classified with honest status (unexecuted phases NOT marked READY).
3. The 5 empirical execution prerequisites are documented and mandate execution lock.
4. The 4 threats to validity categories (Construct, Internal, External, Conclusion) are detailed.
5. All 4 core research questions (RQ1-RQ4) are mapped and held at NOT_YET_EXECUTED.
6. Strictly zero em/en dashes across all documents.
"""

import re
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DOC_PATHS = [
    REPO_ROOT / "results_stage_b" / "PAPER_READINESS_GAP_ANALYSIS.md",
    REPO_ROOT / "results_stage_b" / "EMPIRICAL_EXECUTION_PREREQUISITES.md",
    REPO_ROOT / "results_stage_b" / "THREATS_TO_VALIDITY_REGISTER.md",
    REPO_ROOT / "results_stage_b" / "RESEARCH_QUESTION_TRACEABILITY_MATRIX.md",
]


def test_paper_readiness_documents_exist_and_non_empty():
    """Asserts that all 4 paper readiness documents exist and are non-empty."""
    for p in DOC_PATHS:
        assert p.exists(), f"Missing document: {p}"
        assert p.stat().st_size > 1000, f"Document too small or empty: {p}"


def test_readiness_dimensions_unexecuted_phases_honest():
    """Asserts that empirical dimensions are not falsely marked READY."""
    text = (REPO_ROOT / "results_stage_b" / "PAPER_READINESS_GAP_ANALYSIS.md").read_text(encoding="utf-8")
    assert "READY" in text
    assert "IN_PROGRESS" in text
    assert "NOT_STARTED" in text
    # Verify that multi-model evaluation and statistical significance are NOT marked READY
    assert "| **5. Multi-Model Evaluation** | `NOT_STARTED` |" in text
    assert "| **6. Statistical Power & Significance** | `NOT_STARTED` |" in text


def test_empirical_prerequisites_documented():
    """Asserts that all 5 prerequisite gates are specified with clear verification criteria."""
    text = (REPO_ROOT / "results_stage_b" / "EMPIRICAL_EXECUTION_PREREQUISITES.md").read_text(encoding="utf-8")
    assert "Prerequisite 1" in text
    assert "Prerequisite 2" in text
    assert "Prerequisite 3" in text
    assert "Prerequisite 4" in text
    assert "Prerequisite 5" in text
    assert "LIVE_MODEL_EVALUATION_LOCKED" in text


def test_threats_to_validity_categories_covered():
    """Asserts that all 4 validity categories are present in the threats register."""
    text = (REPO_ROOT / "results_stage_b" / "THREATS_TO_VALIDITY_REGISTER.md").read_text(encoding="utf-8")
    assert "Construct Validity" in text
    assert "Internal Validity" in text
    assert "External Validity" in text
    assert "Statistical Conclusion Validity" in text
    assert "THREAT_CON_01" in text
    assert "THREAT_INT_01" in text
    assert "THREAT_EXT_01" in text
    assert "THREAT_STA_01" in text


def test_research_questions_traceability():
    """Asserts that RQ1 through RQ4 are defined and held at NOT_YET_EXECUTED."""
    text = (REPO_ROOT / "results_stage_b" / "RESEARCH_QUESTION_TRACEABILITY_MATRIX.md").read_text(encoding="utf-8")
    assert "RQ1: Structural Complexity" in text
    assert "RQ2: Mutation Fragility" in text
    assert "RQ3: Transport Surface Isolation" in text
    assert "RQ4: Vendor Masking Confounding" in text
    assert "NOT_YET_EXECUTED" in text
    assert "N = 6,000" in text or "6,000" in text


def test_zero_em_en_dashes_in_paper_readiness_docs():
    """Asserts strictly zero em/en dashes across all paper readiness documents."""
    for p in DOC_PATHS:
        text = p.read_text(encoding="utf-8")
        dashes = re.findall(r"[\u2014\u2013—–]", text)
        assert len(dashes) == 0, f"Found {len(dashes)} em/en dashes in {p.name}"

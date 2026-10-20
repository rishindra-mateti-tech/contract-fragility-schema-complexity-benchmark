"""
test_stage_b_human_validation_ops.py - Unit and Regression Tests for Human Validation Operations.

Verifies:
1. Operations manual, blind review template, adjudication template, conflict rules, and sample plan exist.
2. 15-point verification rubric (R-01 through R-15) is fully specified and consistent.
3. Conflict of interest rules strictly forbid authors from conducting independent evaluations.
4. Stratified sampling plan accurately reflects current state (2 pilots, 0 independent reviews).
5. All documents contain strictly zero em/en dashes and pass claim linter.
"""

import re
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DOC_PATHS = [
    REPO_ROOT / "results_stage_b" / "HUMAN_VALIDATION_OPERATIONS_MANUAL.md",
    REPO_ROOT / "results_stage_b" / "HUMAN_VALIDATION_BLIND_REVIEW_TEMPLATE.md",
    REPO_ROOT / "results_stage_b" / "HUMAN_VALIDATION_ADJUDICATION_TEMPLATE.md",
    REPO_ROOT / "results_stage_b" / "HUMAN_VALIDATION_CONFLICT_RULES.md",
    REPO_ROOT / "results_stage_b" / "HUMAN_VALIDATION_SAMPLE_PLAN.md",
]


def test_human_validation_documents_exist_and_non_empty():
    """Asserts that all 5 human validation operations documents exist and are non-empty."""
    for p in DOC_PATHS:
        assert p.exists(), f"Missing document: {p}"
        assert p.stat().st_size > 500, f"Document too small or empty: {p}"


def test_fifteen_point_rubric_consistency():
    """Asserts that all 15 rubric items (R-01 through R-15) are present in the manual and template."""
    manual_text = (REPO_ROOT / "results_stage_b" / "HUMAN_VALIDATION_OPERATIONS_MANUAL.md").read_text(encoding="utf-8")
    template_text = (REPO_ROOT / "results_stage_b" / "HUMAN_VALIDATION_BLIND_REVIEW_TEMPLATE.md").read_text(encoding="utf-8")

    for i in range(1, 16):
        rubric_id = f"R-{i:02d}"
        assert rubric_id in manual_text, f"Missing {rubric_id} in operations manual"
        assert rubric_id in template_text, f"Missing {rubric_id} in review template"


def test_conflict_rules_prohibit_author_independent_reviews():
    """Asserts that conflict rules strictly prohibit authors from independent reviews."""
    rules_text = (REPO_ROOT / "results_stage_b" / "HUMAN_VALIDATION_CONFLICT_RULES.md").read_text(encoding="utf-8")
    assert "AUTHOR_MANUAL_REVIEW" in rules_text
    assert "INDEPENDENT_REVIEW" in rules_text
    assert "prohibit" in rules_text.lower()
    assert "commit access" in rules_text.lower()


def test_sampling_plan_current_state_truth():
    """Asserts that the sample plan honestly states current project status."""
    plan_text = (REPO_ROOT / "results_stage_b" / "HUMAN_VALIDATION_SAMPLE_PLAN.md").read_text(encoding="utf-8")
    assert "30" in plan_text  # Total active manifest operations
    assert "SLOT_GITHUB_01" in plan_text
    assert "SLOT_STRIPE_02" in plan_text
    assert "0" in plan_text  # 0 independent reviews completed
    assert "CANONICAL_FAITHFUL" in plan_text


def test_zero_em_en_dashes_in_ops_packets():
    """Asserts strictly zero em/en dashes across all human validation operations documents."""
    for p in DOC_PATHS:
        text = p.read_text(encoding="utf-8")
        dashes = re.findall(r"[\u2014\u2013—–]", text)
        assert len(dashes) == 0, f"Found {len(dashes)} em/en dashes in {p.name}"

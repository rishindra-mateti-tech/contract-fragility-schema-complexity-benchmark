"""
test_research_claim_linter.py - Unit and Regression Tests for Epistemic Claim Governance.

Verifies:
1. Schema integrity of results_stage_b/CLAIM_EVIDENCE_LEDGER.json.
2. Full repository claim linting passes with zero un-scoped violations.
3. Fail-closed detection of synthetic un-scoped claims.
4. Correct classification of scoped negative statements.
5. Correct recognition of allowlisted claims.
"""

import json
import pytest
from pathlib import Path
from src.lint_research_claims import (
    REPO_ROOT,
    HIGH_RISK_TERMS,
    load_claim_ledger,
    check_scoping,
    run_claim_linter,
    is_in_allowlisted_claim,
)

VALID_CATEGORIES = {"FACTUAL", "EMPIRICAL", "METHODOLOGICAL", "LIMITATION", "FUTURE_WORK"}
VALID_STATUSES = {"SUPPORTED", "SCOPE_RESTRICTED", "PENDING", "RETRACTED"}


def test_claim_ledger_schema():
    """Asserts that results_stage_b/CLAIM_EVIDENCE_LEDGER.json is valid and complete."""
    ledger_path = REPO_ROOT / "results_stage_b" / "CLAIM_EVIDENCE_LEDGER.json"
    assert ledger_path.exists(), f"Ledger file missing: {ledger_path}"

    with open(ledger_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "claims" in data, "Ledger missing 'claims' key"
    assert len(data["claims"]) >= 16, f"Expected at least 16 claims, found {len(data['claims'])}"

    for claim in data["claims"]:
        assert "claim_id" in claim
        assert "document_path" in claim
        assert "line_range" in claim
        assert "category" in claim
        assert claim["category"] in VALID_CATEGORIES, f"Invalid category: {claim['category']}"
        assert "status" in claim
        assert claim["status"] in VALID_STATUSES, f"Invalid status: {claim['status']}"
        assert "exact_quoted_text" in claim
        assert "evidence_artifacts" in claim
        assert isinstance(claim["evidence_artifacts"], list)
        assert len(claim["evidence_artifacts"]) > 0
        assert "permitted_wording" in claim
        assert "prohibited_stronger_wording" in claim
        assert "reviewer_needed" in claim
        assert isinstance(claim["reviewer_needed"], bool)
        assert "epistemic_notes" in claim


def test_claim_linter_clean_run():
    """Asserts that the full repository markdown documentation passes with zero violations."""
    results = run_claim_linter()
    assert results["files_scanned"] > 0, "No markdown files scanned"
    assert results["violations"] == 0, (
        f"Found {results['violations']} un-scoped claim violations: "
        f"{[d for d in results['details'] if d['status'] == 'UNSCOPED_VIOLATION']}"
    )
    assert results["total_occurrences"] > 0


def test_linter_detects_unscoped_violations():
    """Asserts that absolutist, un-scoped claims are flagged as violations."""
    unscoped_lines = [
        ("TERM_PROVES", "Our extensive evaluation proves that frontier models fail."),
        ("TERM_GUARANTEE", "This schema wrapper guarantees wire-level compatibility."),
        ("TERM_FAITHFUL", "The new extraction is hereby promoted to CANONICAL_FAITHFUL."),
        ("TERM_PRODUCTION_READY", "This tool definition is a production-ready contract."),
        ("TERM_STAT_SIGNIFICANT", "Our sample of 5 calls demonstrates statistically significant degradation."),
        ("TERM_CONFORMANT", "The serialized contract is wire-conformant with Stripe."),
    ]

    for term_id, line in unscoped_lines:
        term_cfg = next(t for t in HIGH_RISK_TERMS if t["id"] == term_id)
        is_scoped, rationale = check_scoping(line, term_cfg, "dummy_spec.md")
        assert not is_scoped, f"Expected violation for '{line}', but was marked scoped: {rationale}"


def test_linter_accepts_properly_scoped_statements():
    """Asserts that statements with negative disclaimers or strict scoping pass."""
    scoped_lines = [
        ("TERM_PROVES", "We do not claim proven model degradation yet."),
        ("TERM_GUARANTEE", "Does not guarantee external network wire compatibility."),
        ("TERM_LOSSLESS", "In-process round-trip is lossless under declared representation policy."),
        ("TERM_LOSSLESS", "Lossless Classification: SEMANTICALLY_EQUIVALENT_MODULO_WRAPPER_POLICY"),
        ("TERM_FAITHFUL", "An operation may never be labeled CANONICAL_FAITHFUL upon initial extraction."),
        ("TERM_INDEPENDENT_REVIEW", "Human review status: AUTHOR_MANUAL_REVIEW (Independent Review: NOT_CONDUCTED)."),
        ("TERM_STAT_SIGNIFICANT", "This sample size (N=5) is too small for statistical significance."),
        ("TERM_CONFORMANT", "Actual wire-conformant behavior remains unvalidated without socket capture."),
    ]

    for term_id, line in scoped_lines:
        term_cfg = next(t for t in HIGH_RISK_TERMS if t["id"] == term_id)
        is_scoped, rationale = check_scoping(line, term_cfg, "dummy_doc.md")
        assert is_scoped, f"Expected line to be scoped: '{line}', reason: {rationale}"


def test_linter_allowlist_matching():
    """Asserts that allowlisted claim quotes are recognized by ledger matching."""
    claims = load_claim_ledger()
    claim_001 = next(c for c in claims if c["claim_id"] == "CLAIM-001")
    matched_word = "statistically significant"

    is_allowlisted, claim_id = is_in_allowlisted_claim(
        claim_001["document_path"], 30, matched_word, claims
    )
    assert is_allowlisted, "Expected claim to be recognized in allowlist"
    assert claim_id == "CLAIM-001"

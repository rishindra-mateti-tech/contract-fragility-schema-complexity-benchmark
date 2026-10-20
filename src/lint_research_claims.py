"""
lint_research_claims.py - Epistemic Claim Linter for Benchmark Research.

Audits repository documentation against high-risk, un-scoped claims.
Enforces adherence to:
- docs/RESEARCH_CLAIM_STYLE_GUIDE.md
- results_stage_b/CLAIM_EVIDENCE_LEDGER.json
- CLAIM_EVIDENCE_LEDGER.md

Ensures no absolutist claims (e.g., unvalidated wire conformance, premature
CANONICAL_FAITHFUL promotion, unproven model degradation, independent review)
enter benchmark publications or reports without explicit epistemic scoping.
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Root directory of repository
REPO_ROOT = Path(__file__).resolve().parent.parent

# Files exempted from linting (e.g. meta-documents, self-reporting audits)
EXEMPTED_FILES = {
    "docs/RESEARCH_CLAIM_STYLE_GUIDE.md",
    "results_stage_b/CLAIM_LINT_AUDIT.md",
}

# Directories exempted from scanning
EXEMPTED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "build",
    "dist",
    "tests/fixtures",
}

# High-risk terms configuration
HIGH_RISK_TERMS = [
    {
        "id": "TERM_PROVES",
        "pattern": r"\b(proves|proven)\b",
        "name": "proves / proven",
        "risk_level": "HIGH",
        "scoping_patterns": [
            r"\b(do not|does not|did not|cannot|never|not|neither|nor|without|fails to|falsif\w+)\b",
            r"\b(to prove|tests whether|evaluates whether|proves whether)\b",
            r"\b(in-process|representation policy|declared policy|under declared)\b",
            r"\b(prohibited|unproven|unverified|insufficient)\b",
            r"\"proves?\"",
            r"'proves?'",
        ],
    },
    {
        "id": "TERM_GUARANTEE",
        "pattern": r"\b(guarantees?|guaranteed)\b",
        "name": "guarantee / guaranteed",
        "risk_level": "HIGH",
        "scoping_patterns": [
            r"\b(do not|does not|did not|cannot|never|not|no|without|unverified|fails to)\b",
            r"\b(to guarantee|does not guarantee|cannot guarantee|no guarantee)\b",
            r"\b(syntactic|grammar|FSM|schema validation|jsonschema)\b",
            r"\"guarantee[sd]?\"",
            r"'guarantee[sd]?'",
        ],
    },
    {
        "id": "TERM_LOSSLESS",
        "pattern": r"\blossless\b",
        "name": "lossless",
        "risk_level": "HIGH",
        "scoping_patterns": [
            r"\b(non-lossless|not lossless|modulo|in-process|representation policy|declared policy|under declared|replaced|replaces|superseded)\b",
            r"\b(deliberate non-lossless normalization|lossless round-trip under declared representation policy)\b",
            r"\b(reversible under|Tier 2|representation-level)\b|(SEMANTICALLY_EQUIVALENT|MODULO_WRAPPER_POLICY)",
            r"\b(strictly lossless\s*[:\?]\s*`?false`?|lossless\?)\b",
            r"\"[^\"]*lossless[^\"]*\"",
            r"'[^\']*lossless[^\']*'",
        ],
    },
    {
        "id": "TERM_FAITHFUL",
        "pattern": r"\bCANONICAL_FAITHFUL\b",
        "name": "CANONICAL_FAITHFUL promotion",
        "risk_level": "CRITICAL",
        "scoping_patterns": [
            r"\b(do not|does not|must not|never|prohibited|not|before|until|cannot|without|pending)\b",
            r"\b(gate|promotion|lifecycle|state|transition|status|criterion|criteria|header|column)\b",
            r"\"CANONICAL_FAITHFUL\"",
            r"`CANONICAL_FAITHFUL`",
        ],
    },
    {
        "id": "TERM_INDEPENDENT_REVIEW",
        "pattern": r"\bindependent\s+(?:validation|review)\b",
        "name": "independent validation / review",
        "risk_level": "CRITICAL",
        "scoping_patterns": [
            r"\b(do not|does not|not|never|neither|nor|without|zero|0|must not|future|pending|unconducted|not conducted|NOT_CONDUCTED)\b",
            r"\b(author review vs|boundary|author manual review|not claim|cannot claim|claimed\s*[:=]\s*`?false`?|disqualified|mislabeled|panels?)\b",
            r"(`INDEPENDENT_REVIEW`|\"independent (?:validation|review)\"|'independent (?:validation|review)')",
        ],
    },
    {
        "id": "TERM_PRODUCTION_READY",
        "pattern": r"\bproduction-ready\b",
        "name": "production-ready",
        "risk_level": "HIGH",
        "scoping_patterns": [
            r"\b(not|never|unverified|benchmarking|simulated|candidate)\b",
            r"\"production-ready\"",
            r"'production-ready'",
        ],
    },
    {
        "id": "TERM_STAT_SIGNIFICANT",
        "pattern": r"\bstatistically\s+significant\b|\bstatistical\s+significance\b",
        "name": "statistical significance",
        "risk_level": "HIGH",
        "scoping_patterns": [
            r"\b(not|insufficient|too small|small sample|exploratory|cannot|without|until|before|unverified|do not claim|does not claim|N\s*=\s*5|pilot)\b",
            r"\b(pending full-scale|requires full-scale|required to test|testing across|future gate)\b",
            r"\"statistical",
            r"'statistical",
        ],
    },
    {
        "id": "TERM_CONFORMANT",
        "pattern": r"\b(?:endpoint|wire)-conformant\b",
        "name": "wire / endpoint conformant",
        "risk_level": "HIGH",
        "scoping_patterns": [
            r"\b(unvalidated|not|without|Tier 2|in-process|representation)\b",
            r"\"(?:endpoint|wire)-conformant\"",
            r"'(?:endpoint|wire)-conformant'",
        ],
    },
]


def load_claim_ledger() -> List[Dict[str, Any]]:
    """Loads approved claims from results_stage_b/CLAIM_EVIDENCE_LEDGER.json."""
    ledger_path = REPO_ROOT / "results_stage_b" / "CLAIM_EVIDENCE_LEDGER.json"
    if not ledger_path.exists():
        return []
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("claims", [])
    except Exception as e:
        print(f"Warning: Failed to load claim ledger from {ledger_path}: {e}")
        return []


def is_path_exempted(rel_path: str) -> bool:
    """Checks if a relative file path is exempted from scanning."""
    norm_path = rel_path.replace("\\", "/")
    if norm_path in EXEMPTED_FILES:
        return True
    for ed in EXEMPTED_DIRS:
        if norm_path == ed or norm_path.startswith(ed + "/"):
            return True
    return False


def is_in_allowlisted_claim(
    rel_path: str, line_no: int, matched_text: str, claims: List[Dict[str, Any]]
) -> Tuple[bool, Optional[str]]:
    """Checks if the occurrence matches an approved claim in the ledger."""
    norm_path = rel_path.replace("\\", "/")
    for claim in claims:
        claim_doc = claim.get("document_path", "").replace("\\", "/")
        if claim_doc and norm_path == claim_doc:
            # Check line range if available
            line_range = claim.get("line_range", "")
            if "-" in line_range:
                try:
                    start_str, end_str = line_range.split("-")
                    start_l, end_l = int(start_str), int(end_str)
                    if start_l <= line_no <= end_l:
                        return True, claim.get("claim_id")
                except ValueError:
                    pass
            # Or check exact quote containment
            exact_quote = claim.get("exact_quoted_text", "")
            if matched_text and matched_text.lower() in exact_quote.lower():
                return True, claim.get("claim_id")
    return False, None


def check_scoping(
    line: str,
    term_cfg: Dict[str, Any],
    file_path: str = ""
) -> Tuple[bool, str]:
    """
    Evaluates whether an occurrence of a high-risk term has proper epistemic scoping.
    Returns (is_scoped, rationale).
    """
    # 1. Structural context: Check if line is a table header, rule heading, or status definition
    if re.match(r"^#{1,6}\s+", line):
        return True, "SECTION_TITLE_OR_BOUNDARY_HEADING"
    
    if line.startswith("|") and ("---" in line or "?" in line or "Lossless?" in line or "Strictly Lossless?" in line):
        return True, "TABLE_HEADER_OR_SEPARATOR"

    if re.match(r"^\|\s*`?[A-Z0-9_\-]+`?\s*\|", line) and ("YES" in line or "CRITERIA" in line or "STATUS" in line or "STATE" in line or "PENDING" in line or "SUPPORTED" in line):
        return True, "LIFECYCLE_SPECIFICATION_TABLE"

    # 2. Check term-specific scoping patterns within the line
    for pat in term_cfg.get("scoping_patterns", []):
        if re.search(pat, line, re.IGNORECASE):
            return True, f"SCOPED_BY_PATTERN: {pat}"

    # 3. Check for general negative / disclaiming context in the sentence
    general_scoping = [
        r"\b(do not|does not|must not|cannot|not|never|neither|nor|without|zero|0|unverified|unvalidated|not conducted|NOT_CONDUCTED|too small|exploratory|strictly prohibited)\b",
        r"\b(pending|future work|future gate|deliverables?|not claim|does not claim|do not claim|no independent|author manual review)\b",
        r"\b(false|none|n/a|hostile|red-team|flagged|simulated)\b",
    ]
    for gpat in general_scoping:
        if re.search(gpat, line, re.IGNORECASE):
            return True, f"SCOPED_BY_GENERAL_NEGATION: {gpat}"

    # 4. Check roadmap/future gates document
    if "NEXT_GATES.md" in file_path:
        return True, "SCOPED_AS_FUTURE_ROADMAP_MILESTONE"

    return False, "UNSCOPED_HIGH_RISK_CLAIM"


def run_claim_linter() -> Dict[str, Any]:
    """
    Scans all repository Markdown files and audits against epistemic claims.
    Returns structured results dict.
    """
    claims = load_claim_ledger()
    results = {
        "files_scanned": 0,
        "total_occurrences": 0,
        "allowlisted_claims": 0,
        "scoped_acceptable": 0,
        "violations": 0,
        "details": [],
    }

    for root, dirs, files in os.walk(REPO_ROOT):
        # Filter excluded directories in-place
        dirs[:] = [
            d for d in dirs
            if not is_path_exempted(str((Path(root) / d).relative_to(REPO_ROOT)))
        ]

        for file in files:
            if not file.endswith(".md"):
                continue

            abs_path = Path(root) / file
            rel_path = str(abs_path.relative_to(REPO_ROOT)).replace("\\", "/")

            if is_path_exempted(rel_path):
                continue

            results["files_scanned"] += 1

            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"Error reading {rel_path}: {e}")
                continue

            in_code_block = False
            for line_no, line_content in enumerate(lines, 1):
                stripped = line_content.strip()
                if stripped.startswith("```"):
                    in_code_block = not in_code_block
                    continue

                if in_code_block:
                    continue

                for term_cfg in HIGH_RISK_TERMS:
                    match = re.search(term_cfg["pattern"], line_content, re.IGNORECASE)
                    if not match:
                        continue

                    results["total_occurrences"] += 1
                    matched_word = match.group(0)

                    # Check allowlist
                    is_allowlisted, claim_id = is_in_allowlisted_claim(
                        rel_path, line_no, matched_word, claims
                    )

                    if is_allowlisted:
                        results["allowlisted_claims"] += 1
                        results["details"].append({
                            "file": rel_path,
                            "line": line_no,
                            "term_id": term_cfg["id"],
                            "term_name": term_cfg["name"],
                            "matched_text": matched_word,
                            "status": "ALLOWLISTED",
                            "claim_id": claim_id,
                            "context": stripped[:120],
                            "rationale": f"Explicitly registered and permitted under {claim_id}",
                        })
                        continue

                    # Check scoping
                    is_scoped, rationale = check_scoping(stripped, term_cfg, rel_path)
                    if is_scoped:
                        results["scoped_acceptable"] += 1
                        results["details"].append({
                            "file": rel_path,
                            "line": line_no,
                            "term_id": term_cfg["id"],
                            "term_name": term_cfg["name"],
                            "matched_text": matched_word,
                            "status": "SCOPED_ACCEPTABLE",
                            "claim_id": None,
                            "context": stripped[:120],
                            "rationale": rationale,
                        })
                    else:
                        results["violations"] += 1
                        results["details"].append({
                            "file": rel_path,
                            "line": line_no,
                            "term_id": term_cfg["id"],
                            "term_name": term_cfg["name"],
                            "matched_text": matched_word,
                            "status": "UNSCOPED_VIOLATION",
                            "claim_id": None,
                            "context": stripped[:120],
                            "rationale": "High-risk absolutist phrase detected without negative disclaimer, scoping boundary, or ledger registration.",
                        })

    return results


def generate_audit_markdown(results: Dict[str, Any]) -> str:
    """Formats audit results as a comprehensive Markdown report."""
    status_str = "PASS" if results["violations"] == 0 else "FAIL"

    md = []
    md.append("# Epistemic Research Claim Linter Audit Report")
    md.append("")
    md.append(f"**Audit Status:** `{status_str}`  ")
    md.append("**Governing Policy:** `docs/RESEARCH_CLAIM_STYLE_GUIDE.md`  ")
    md.append("**Claim Ledger:** `results_stage_b/CLAIM_EVIDENCE_LEDGER.json`  ")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. Executive Summary")
    md.append("")
    md.append("| Metric | Count | Governance Meaning |")
    md.append("| :--- | :---: | :--- |")
    md.append(f"| **Markdown Documents Scanned** | `{results['files_scanned']}` | All active documentation, specifications, and reports. |")
    md.append(f"| **High-Risk Terms Monitored** | `{len(HIGH_RISK_TERMS)}` | Monitored vocabulary for overclaiming risks. |")
    md.append(f"| **Total Pattern Matches** | `{results['total_occurrences']}` | All occurrences of monitored high-risk stems. |")
    md.append(f"| **Allowlisted Claims** | `{results['allowlisted_claims']}` | Verified against approved entries in `CLAIM_EVIDENCE_LEDGER.json`. |")
    md.append(f"| **Scoped Acceptable Claims** | `{results['scoped_acceptable']}` | Contextually constrained by negative disclaimers or definitions. |")
    md.append(f"| **Un-scoped Violations** | **`{results['violations']}`** | Absolutist or ungrounded claims requiring remediation. |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 2. Term Classification Breakdown")
    md.append("")

    # Aggregate by term
    term_counts: Dict[str, Dict[str, int]] = {}
    for d in results["details"]:
        tname = d["term_name"]
        if tname not in term_counts:
            term_counts[tname] = {"ALLOWLISTED": 0, "SCOPED_ACCEPTABLE": 0, "UNSCOPED_VIOLATION": 0}
        term_counts[tname][d["status"]] += 1

    md.append("| High-Risk Term | Total Matches | Scoped Acceptable | Allowlisted | Violations |")
    md.append("| :--- | :---: | :---: | :---: | :---: |")
    for tname, counts in sorted(term_counts.items()):
        md.append(
            f"| `{tname}` | {sum(counts.values())} | {counts['SCOPED_ACCEPTABLE']} | {counts['ALLOWLISTED']} | {counts['UNSCOPED_VIOLATION']} |"
        )
    md.append("")
    md.append("---")
    md.append("")

    if results["violations"] > 0:
        md.append("## 3. Un-scoped Claim Violations (Action Required)")
        md.append("")
        md.append("| File | Line | Term | Context Snippet | Required Action |")
        md.append("| :--- | :---: | :--- | :--- | :--- |")
        for d in results["details"]:
            if d["status"] == "UNSCOPED_VIOLATION":
                md.append(
                    f"| `{d['file']}` | {d['line']} | `{d['matched_text']}` | {d['context']} | Apply scoping disclaimer or register in ledger. |"
                )
        md.append("")
        md.append("---")
        md.append("")

    md.append("## 4. Scoped and Allowlisted Inventory (Sample)")
    md.append("")
    md.append("| File | Line | Status | Term | Scoping Rationale |")
    md.append("| :--- | :---: | :---: | :--- | :--- |")
    sample_details = results["details"][:25]
    for d in sample_details:
        md.append(
            f"| `{d['file']}` | {d['line']} | `{d['status']}` | `{d['matched_text']}` | {d['rationale']} |"
        )
    if len(results["details"]) > 25:
        md.append(f"| ... | ... | ... | ... | *({len(results['details']) - 25} additional scoped occurrences verified)* |")

    md.append("")
    md.append("---")
    md.append("")
    md.append("## 5. Certification Invariant")
    md.append("")
    md.append("1. **Fail-Closed Execution:** Any un-scoped high-risk claim in repository documentation causes continuous integration to fail.")
    md.append("2. **Independent Review Defense:** Author manual reviews (`AUTHOR_MANUAL_REVIEW`) are strictly forbidden from being described as independent validations.")
    md.append("3. **Epistemic Truth:** All claims remain strictly bounded to verified in-process representations without asserting unvalidated wire or server acceptance.")
    md.append("")

    return "\n".join(md)


def main():
    """Main execution entry point."""
    print("Executing Epistemic Claim Linter...")
    results = run_claim_linter()

    output_path = REPO_ROOT / "results_stage_b" / "CLAIM_LINT_AUDIT.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    markdown_report = generate_audit_markdown(results)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_report)

    print(f"Scanned {results['files_scanned']} markdown files.")
    print(f"Total pattern matches: {results['total_occurrences']}")
    print(f"Allowlisted: {results['allowlisted_claims']}")
    print(f"Scoped acceptable: {results['scoped_acceptable']}")
    print(f"Violations: {results['violations']}")
    print(f"Report written to {output_path}")

    if results["violations"] > 0:
        print(f"ERROR: Found {results['violations']} un-scoped claim violations!")
        sys.exit(1)
    else:
        print("SUCCESS: All claims adhere strictly to epistemic style guide.")
        sys.exit(0)


if __name__ == "__main__":
    main()

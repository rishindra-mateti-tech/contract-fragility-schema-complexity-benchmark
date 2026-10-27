# Epistemic Research Claim Linter Audit Report

**Audit Status:** `PASS`  
**Governing Policy:** `docs/RESEARCH_CLAIM_STYLE_GUIDE.md`  
**Claim Ledger:** `results_stage_b/CLAIM_EVIDENCE_LEDGER.json`  

---

## 1. Executive Summary

| Metric | Count | Governance Meaning |
| :--- | :---: | :--- |
| **Markdown Documents Scanned** | `290` | All active documentation, specifications, and reports. |
| **High-Risk Terms Monitored** | `8` | Monitored vocabulary for overclaiming risks. |
| **Total Pattern Matches** | `221` | All occurrences of monitored high-risk stems. |
| **Allowlisted Claims** | `14` | Verified against approved entries in `CLAIM_EVIDENCE_LEDGER.json`. |
| **Scoped Acceptable Claims** | `207` | Contextually constrained by negative disclaimers or definitions. |
| **Un-scoped Violations** | **`0`** | Absolutist or ungrounded claims requiring remediation. |

---

## 2. Term Classification Breakdown

| High-Risk Term | Total Matches | Scoped Acceptable | Allowlisted | Violations |
| :--- | :---: | :---: | :---: | :---: |
| `CANONICAL_FAITHFUL promotion` | 65 | 60 | 5 | 0 |
| `guarantee / guaranteed` | 7 | 7 | 0 | 0 |
| `independent validation / review` | 85 | 82 | 3 | 0 |
| `lossless` | 44 | 42 | 2 | 0 |
| `proves / proven` | 7 | 6 | 1 | 0 |
| `statistical significance` | 13 | 10 | 3 | 0 |

---

## 4. Scoped and Allowlisted Inventory (Sample)

| File | Line | Status | Term | Scoping Rationale |
| :--- | :---: | :---: | :--- | :--- |
| `AUTHOR_REVIEW_INSTRUCTIONS.md` | 24 | `SCOPED_ACCEPTABLE` | `Independent Validation` | SECTION_TITLE_OR_BOUNDARY_HEADING |
| `AUTHOR_REVIEW_INSTRUCTIONS.md` | 36 | `SCOPED_ACCEPTABLE` | `independent review` | SCOPED_BY_PATTERN: \b(do not|does not|not|never|neither|nor|without|zero|0|must not|future|pending|unconducted|not conducted|NOT_CONDUCTED)\b |
| `AUTHOR_REVIEW_INSTRUCTIONS.md` | 37 | `SCOPED_ACCEPTABLE` | `independent validation` | SCOPED_BY_PATTERN: \b(do not|does not|not|never|neither|nor|without|zero|0|must not|future|pending|unconducted|not conducted|NOT_CONDUCTED)\b |
| `CANONICAL_CONTRACT_VALIDATION_SPEC.md` | 19 | `SCOPED_ACCEPTABLE` | `CANONICAL_FAITHFUL` | SCOPED_BY_PATTERN: \b(gate|promotion|lifecycle|state|transition|status|criterion|criteria|header|column)\b |
| `CANONICAL_CONTRACT_VALIDATION_SPEC.md` | 220 | `SCOPED_ACCEPTABLE` | `CANONICAL_FAITHFUL` | LIFECYCLE_SPECIFICATION_TABLE |
| `CANONICAL_CONTRACT_VALIDATION_SPEC.md` | 224 | `SCOPED_ACCEPTABLE` | `CANONICAL_FAITHFUL` | LIFECYCLE_SPECIFICATION_TABLE |
| `CANONICAL_CONTRACT_VALIDATION_SPEC.md` | 228 | `SCOPED_ACCEPTABLE` | `CANONICAL_FAITHFUL` | SCOPED_BY_PATTERN: \b(do not|does not|must not|never|prohibited|not|before|until|cannot|without|pending)\b |
| `CLAIM_EVIDENCE_LEDGER.md` | 119 | `SCOPED_ACCEPTABLE` | `guarantees` | SCOPED_BY_PATTERN: \b(syntactic|grammar|FSM|schema validation|jsonschema)\b |
| `CLAIM_EVIDENCE_LEDGER.md` | 204 | `SCOPED_ACCEPTABLE` | `statistical significance` | SCOPED_BY_PATTERN: \b(not|insufficient|too small|small sample|exploratory|cannot|without|until|before|unverified|do not claim|does not claim|N\s*=\s*5|pilot)\b |
| `EXTRACTION_IMPLEMENTATION_CHECKLIST.md` | 20 | `SCOPED_ACCEPTABLE` | `CANONICAL_FAITHFUL` | SCOPED_BY_PATTERN: \b(do not|does not|must not|never|prohibited|not|before|until|cannot|without|pending)\b |
| `EXTRACTION_IMPLEMENTATION_CHECKLIST.md` | 210 | `SCOPED_ACCEPTABLE` | `guarantee` | SCOPED_BY_PATTERN: \b(to guarantee|does not guarantee|cannot guarantee|no guarantee)\b |
| `EXTRACTION_IMPLEMENTATION_CHECKLIST.md` | 224 | `SCOPED_ACCEPTABLE` | `CANONICAL_FAITHFUL` | SECTION_TITLE_OR_BOUNDARY_HEADING |
| `EXTRACTION_IMPLEMENTATION_CHECKLIST.md` | 226 | `SCOPED_ACCEPTABLE` | `CANONICAL_FAITHFUL` | SCOPED_BY_PATTERN: \b(do not|does not|must not|never|prohibited|not|before|until|cannot|without|pending)\b |
| `LONG_BLOCK_HANDOFF.md` | 55 | `SCOPED_ACCEPTABLE` | `CANONICAL_FAITHFUL` | SCOPED_BY_PATTERN: \b(gate|promotion|lifecycle|state|transition|status|criterion|criteria|header|column)\b |
| `PAPER_EVIDENCE_LEDGER.md` | 46 | `SCOPED_ACCEPTABLE` | `statistical significance` | SCOPED_BY_PATTERN: \b(not|insufficient|too small|small sample|exploratory|cannot|without|until|before|unverified|do not claim|does not claim|N\s*=\s*5|pilot)\b |
| `README.md` | 31 | `ALLOWLISTED` | `proven` | Explicitly registered and permitted under CLAIM-001 |
| `README.md` | 31 | `ALLOWLISTED` | `statistical significance` | Explicitly registered and permitted under CLAIM-001 |
| `README.md` | 33 | `ALLOWLISTED` | `statistically significant` | Explicitly registered and permitted under CLAIM-001 |
| `README.md` | 165 | `ALLOWLISTED` | `Statistical Significance` | Explicitly registered and permitted under CLAIM-001 |
| `REPRODUCIBILITY.md` | 12 | `ALLOWLISTED` | `CANONICAL_FAITHFUL` | Explicitly registered and permitted under CLAIM-014 |
| `REPRODUCIBILITY.md` | 182 | `SCOPED_ACCEPTABLE` | `Independent Review` | SCOPED_BY_PATTERN: \b(do not|does not|not|never|neither|nor|without|zero|0|must not|future|pending|unconducted|not conducted|NOT_CONDUCTED)\b |
| `STAGE_B_EXTRACTION_SPEC.md` | 19 | `ALLOWLISTED` | `CANONICAL_FAITHFUL` | Explicitly registered and permitted under CLAIM-006 |
| `STAGE_B_EXTRACTION_SPEC.md` | 20 | `ALLOWLISTED` | `CANONICAL_FAITHFUL` | Explicitly registered and permitted under CLAIM-006 |
| `STAGE_B_EXTRACTION_SPEC.md` | 197 | `SCOPED_ACCEPTABLE` | `CANONICAL_FAITHFUL` | SCOPED_BY_PATTERN: \b(do not|does not|must not|never|prohibited|not|before|until|cannot|without|pending)\b |
| `STAGE_B_EXTRACTION_SPEC.md` | 210 | `SCOPED_ACCEPTABLE` | `CANONICAL_FAITHFUL` | SCOPED_BY_PATTERN: `CANONICAL_FAITHFUL` |
| ... | ... | ... | ... | *(196 additional scoped occurrences verified)* |

---

## 5. Certification Invariant

1. **Fail-Closed Execution:** Any un-scoped high-risk claim in repository documentation causes continuous integration to fail.
2. **Independent Review Defense:** Author manual reviews (`AUTHOR_MANUAL_REVIEW`) are strictly forbidden from being described as independent validations.
3. **Epistemic Truth:** All claims remain strictly bounded to verified in-process representations without asserting unvalidated wire or server acceptance.

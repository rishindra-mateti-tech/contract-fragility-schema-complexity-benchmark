# Stage B Human Validation Conflict of Interest and Integrity Rules

**Document Type:** Epistemic Governance & Conflict of Interest Policy  
**Document Status:** `RATIFIED_POLICY`  
**Governing Manual:** `results_stage_b/HUMAN_VALIDATION_OPERATIONS_MANUAL.md`  
**Associated Guide:** `docs/RESEARCH_CLAIM_STYLE_GUIDE.md`  

---

## 1. Core Epistemic Imperative

In empirical benchmark science, internal authors are inherently biased toward finding that their extraction algorithms and evaluation harnesses are correct. Self-certification of experimental ground truth without independent verification degrades benchmark credibility.

Therefore, this benchmark strictly prohibits project authors, code contributors, and primary investigators from presenting internal manual reviews as independent empirical validations.

---

## 2. Reviewer Role Taxonomy and Privileges

| Reviewer Role | Permitted Actors | Permitted Determinations | Status Elevation Authority |
| :--- | :--- | :--- | :--- |
| **`AUTHOR_MANUAL_REVIEW`** | Project authors, repository committers, core engineers | Preliminary sanity check, wrapper policy approval, bug triage | May elevate to `CANONICAL_VALIDATED_WITH_EXPLICIT_WRAPPER_POLICY`. Strictly **prohibited** from elevating to `CANONICAL_FAITHFUL`. |
| **`INDEPENDENT_REVIEW`** | External qualified engineers/researchers with zero project involvement | Formal double-blind rubric evaluation (R-01 through R-15) | Dual independent sign-offs may elevate an operation to `CANONICAL_FAITHFUL`. |
| **`SENIOR_PROTOCOL_REFEREE`** | Designated independent arbitrator | Dispute arbitration, kappa reconciliation, protocol clarification | Authority to adjudicate split independent decisions. |

---

## 3. Disqualification Criteria for Independent Review Panels

An individual is strictly disqualified from serving as an `INDEPENDENT_REVIEW` panelist if any of the following conditions hold:
1. **Commit History & Repository Access:** Contributed any Git commit, pull request, or holds commit access to this benchmark repository.
2. **Collaborative Association:** Co-authored any scientific paper, technical report, or funding grant with benchmark authors within the preceding 36 calendar months.
3. **Supervisory Conflict:** Serves as direct supervisor, manager, academic advisor, or advisee of any benchmark author.
4. **Financial Conflict:** Employed by, receives consulting fees from, or holds equity in an organization directly funding this benchmark project.
5. **Upstream Author Conflict:** Primary creator or maintainer of an evaluated raw OpenAPI specification (to avoid defensive bias).

---

## 4. Mandatory Disclosure and Attribution Rules

Every public artifact, dashboard, manuscript, and release report must adhere to three disclosure invariants:
1. **Explicit Role Labeling:** Any review performed by a project contributor must be labeled `AUTHOR_MANUAL_REVIEW`.
2. **Mandatory Negative Disclaimer:** Every author review document must prominently include the disclaimer:
   `Document Status: AUTHOR_MANUAL_REVIEW_COMPLETED (Independent Review: NOT_CONDUCTED)`
3. **No Aggregate Claims:** Benchmark summary metrics must report `Independent Reviews Completed: 0/30` until external panels have completed the protocol.

---

## 5. Violation Remediation and Retraction Protocol

If an un-scoped or mislabeled claim of independent review is detected:
1. **Automated CI Failure:** The repository claim linter (`src/lint_research_claims.py`) flags the violation and blocks merge.
2. **Immediate Retraction:** The misattributed claim is retracted in `CLAIM_EVIDENCE_LEDGER.md` under `RETRACTED` status with an explanatory note.
3. **Public Reversion:** Any affected candidate status is downgraded to `EXTRACTED_PENDING_HUMAN_VALIDATION`.

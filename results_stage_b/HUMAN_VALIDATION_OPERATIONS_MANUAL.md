# Stage B Human Validation Operations Manual

**Document Type:** Standard Operating Procedure (SOP)  
**Document Status:** `ACTIVE_OPERATIONS_SPECIFICATION`  
**Governing Specification:** `STAGE_B_EXTRACTION_SPEC.md`  
**Associated Policies:** `results_stage_b/HUMAN_VALIDATION_CONFLICT_RULES.md`, `docs/RESEARCH_CLAIM_STYLE_GUIDE.md`  
**Current Lifecycle State:** `OPERATIONAL_FRAMEWORK_ESTABLISHED` (Independent Reviews: `0/30 CONDUCTED`)  

---

## 1. Purpose and Epistemic Boundaries

This operations manual governs all human-in-the-loop review processes for Stage B canonical contract extraction, mock runtime execution, and benchmark ground-truth validation.

### Epistemic Reviewer Boundary
To preserve scientific integrity, this protocol enforces an immutable distinction between two review tiers:
1. **Author Manual Review (`AUTHOR_MANUAL_REVIEW`):** Conducted by project contributors, repository authors, or primary benchmark architects. Author reviews serve solely as internal sanity checks, structural debugging, and preliminary quality assurance. Author reviews must **never** be cited as independent empirical validation or peer-reviewed certification.
2. **Independent Review (`INDEPENDENT_REVIEW`):** Conducted by external subject-matter experts possessing no repository commit access, no supervisory or financial conflict of interest, and complete independence from benchmark author teams. Only dual independent review sign-offs permit promotion to `CANONICAL_FAITHFUL`.

---

## 2. Reviewer Recruitment and Qualifications

### Independent Reviewer Criteria
Independent reviewers recruited for Gate 4 validation must satisfy all of the following requirements:
- **Technical Competence:** Minimum of 3 years production software engineering experience with REST/OpenAPI architectures, or a graduate degree in Computer Science with published research in program analysis, API design, or software engineering.
- **JSON Schema Fluency:** Demonstrated familiarity with JSON Schema Draft-07, RFC 6901 JSON Pointers, and OpenAPI 3.0/3.1 transport specifications.
- **No Conflict of Interest:** Zero contributions to this benchmark repository, zero co-authorships with benchmark leads within the preceding 36 months, and no financial dependency.

---

## 3. Calibration and Qualification Benchmark

Before reviewing production benchmark operations, every prospective reviewer must complete a 3-case calibration benchmark:
1. **Calibration Case A (Clean Identity):** Perfectly preserved monomorphic endpoint. Reviewer must correctly identify all 8 fields as `IDENTITY` or `SURFACE_WRAPPING`.
2. **Calibration Case B (Controlled Semantic Loss):** Schema with a dropped required field. Reviewer must detect the omission and reject the contract.
3. **Calibration Case C (Wrapper Normalization):** Schema enforcing `additionalProperties: false` on synthetic envelopes. Reviewer must classify as `APPROVE_WITH_WRAPPER_POLICY` rather than claiming raw equivalence.

Reviewers achieving less than 100% agreement on calibration cases are disqualified from independent review panels.

---

## 4. Blinding Protocol and Anonymization Pipeline

To eliminate confirmation bias, independent reviews are executed double-blind:
- **Identifier Stripping:** Candidate names and source repository URLs are masked with synthetic anonymous tokens (e.g. `SERVICE_ALPHA_OPERATION_01`).
- **Extractor Metadata Blinding:** Git commit hashes, extractor timestamps, and author annotations are stripped from model-facing review sheets.
- **Randomized Pairing:** Raw OpenAPI spec snippets and extracted canonical contracts are displayed in randomized left/right orientations.

---

## 5. 15-Point Semantic Verification Rubric

Every reviewer must evaluate each operation against 15 discrete criteria:

| Rubric Item | Dimension | Verification Standard | Failure Threshold |
| :--- | :--- | :--- | :--- |
| **R-01** | Property Count | Total derived properties match raw spec. | Any missing property |
| **R-02** | Requiredness | All required parameters remain required. | Any dropped required property |
| **R-03** | Primitive Types | `string`, `integer`, `number`, `boolean` exact match. | Type widening or coercion |
| **R-04** | Enum Constraints | Exact string/numeric enum set preserved. | Pruned or altered enum set |
| **R-05** | Numeric Bounds | `minimum`, `maximum`, `multipleOf` preserved. | Dropped numeric constraint |
| **R-06** | String Bounds | `minLength`, `maxLength`, `pattern` preserved. | Dropped regex or string bound |
| **R-07** | Descriptions | Raw parameter documentation retained. | Stripped documentation |
| **R-08** | Defaults | Raw default values mapped without alteration. | Invented or altered defaults |
| **R-09** | Nullability | Nullable states mapped cleanly without loss. | Nullable dropped or widened |
| **R-10** | Array Structure | Array items schema matches upstream type. | Converted to unconstrained list |
| **R-11** | Object Recursion | Nested properties preserved up to depth 5. | Truncated child properties |
| **R-12** | Reference Expansion | `$ref` components resolved to exact target node. | Broken pointer or unresolved URI |
| **R-13** | Transport Surfaces | Separated into `path`, `query`, `header`, `body`. | Cross-surface contamination |
| **R-14** | Wrapper Normalization | Closed wrapper objects acknowledged as policy. | Misrepresenting closed objects as raw |
| **R-15** | Guesswork Check | Zero invented fields, fallbacks, or synthetic `{}`. | Any unevidenced field injection |

---

## 6. Inter-Rater Reliability and Adjudication

### Panel Sizing
Every sampled operation receives independent evaluations from two distinct reviewers ($R_1, R_2$).

### Statistical Agreement Standard
- **Inter-Rater Agreement Metric:** Cohen's kappa ($\kappa$) calculated across all 15 rubric items.
- **Acceptance Threshold:** $\kappa \ge 0.85$ required for automatic approval.
- **Arbitration Trigger:** If $\kappa < 0.85$ or if $R_1$ and $R_2$ reach divergent binary decisions (e.g. `APPROVE` vs `REQUEST_CORRECTION`), the review is escalated to a Senior Protocol Referee using `results_stage_b/HUMAN_VALIDATION_ADJUDICATION_TEMPLATE.md`.

---

## 7. Cryptographic Record Recording

Every completed review packet must record immutable Git provenance:
- Reviewed raw spec Git blob SHA.
- Canonical contract SHA-256 digest.
- Exact Git commit of the reviewed packet snapshot.
- Cryptographic GPG or SSH signature of the reviewer.
- Sign-offs are committed in isolated, single-purpose commits to maintain auditable Git history.

---

## 8. Non-Elevation Invariants

1. **Zero Premature Promotions:** No operation may be elevated to `CANONICAL_FAITHFUL` based solely on author review.
2. **Zero Mislabeled Reviews:** Any review conducted by an author must be explicitly titled `AUTHOR_MANUAL_REVIEW`.
3. **Public Disclaimers:** All research papers, dashboards, and README files must explicitly report that independent validation is pending future execution.

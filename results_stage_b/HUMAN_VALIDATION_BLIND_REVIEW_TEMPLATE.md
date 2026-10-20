# Stage B Double-Blind Human Validation Review Template

**Document Type:** Independent Reviewer Record Template  
**Governing Manual:** `results_stage_b/HUMAN_VALIDATION_OPERATIONS_MANUAL.md`  
**Governing Policy:** `results_stage_b/HUMAN_VALIDATION_CONFLICT_RULES.md`  

---

## 1. Review Identification and Cryptographic Provenance

| Provenance Field | Recorded Value | Evidentiary Standard |
| :--- | :--- | :--- |
| **Blinded Operation Token** | `[e.g. OP_BLIND_7A92]` | Anonymized operation identifier |
| **Reviewer Unique ID** | `[e.g. REV_EXT_04]` | External reviewer credential identifier |
| **Reviewer Role** | `INDEPENDENT_REVIEW` | Must NOT be author or committer |
| **Review Date (UTC)** | `[YYYY-MM-DD]` | Evaluation completion timestamp |
| **Raw Spec Git Blob SHA** | `[40-char SHA]` | Bit-level hash of reviewed raw spec |
| **Canonical Contract SHA-256** | `[64-char SHA-256]` | Bit-level digest of emitted contract |
| **Reviewed Snapshot Git Commit** | `[40-char SHA]` | Exact commit containing review artifacts |

---

## 2. 15-Point Semantic Preservation Checklist

| Rubric Item | Dimension Evaluated | Evaluation (PASS / FAIL) | Observations & Evidence |
| :--- | :--- | :---: | :--- |
| **R-01** | Property Count Integrity | `[PASS / FAIL]` | Verify total property counts match upstream. |
| **R-02** | Requiredness Preservation | `[PASS / FAIL]` | Verify no required properties were dropped. |
| **R-03** | Primitive Type Mapping | `[PASS / FAIL]` | Verify string/int/number/bool match exactly. |
| **R-04** | Enum Constraint Fidelity | `[PASS / FAIL]` | Verify exact enum sets are preserved. |
| **R-05** | Numeric Range Bounds | `[PASS / FAIL]` | Verify min/max/multipleOf constraints match. |
| **R-06** | String Constraints & Regex | `[PASS / FAIL]` | Verify minLength/maxLength/pattern match. |
| **R-07** | Parameter Descriptions | `[PASS / FAIL]` | Verify documentation strings are retained. |
| **R-08** | Default Parameter Values | `[PASS / FAIL]` | Verify default literals are unperturbed. |
| **R-09** | Nullable Type Representation | `[PASS / FAIL]` | Verify nullable semantics mapped without loss. |
| **R-10** | Array Items Schema | `[PASS / FAIL]` | Verify array item schemas match upstream. |
| **R-11** | Object Nesting Recursion | `[PASS / FAIL]` | Verify deep child objects are preserved ($d \le 5$). |
| **R-12** | Reference Expansion ($ref) | `[PASS / FAIL]` | Verify RFC 6901 pointers resolved cleanly. |
| **R-13** | Transport Surface Envelopes | `[PASS / FAIL]` | Verify clean path/query/header/body surfaces. |
| **R-14** | Wrapper Closed Objects | `[PASS / FAIL]` | Verify additionalProperties: false is policy. |
| **R-15** | Absence of Guesswork | `[PASS / FAIL]` | Verify zero invented fields or synthetic `{}`. |

---

## 3. Transformation and Normalization Review

### WRAPPER_CLOSED_OBJECT_POLICY_001 Review
The extractor enforces `additionalProperties: false` across synthetic root and transport wrapper containers (`body`, `path`, `query`, `header`) to ensure strict LLM tool argument formulation.
- **Reviewer Finding:**
  - `[ ]` I confirm that closing object schemas on wrapper containers is an explicit benchmark evaluation normalization, NOT raw-source equivalence.
  - `[ ]` I reject this normalization for the reviewed operation.

---

## 4. Final Reviewer Determination

Select exactly one decision:
- `[ ] APPROVE_FAITHFUL`: Contract is semantically identical to raw source across all parameters.
- `[ ] APPROVE_WITH_WRAPPER_POLICY`: Contract is semantically equivalent modulo documented closed wrapper normalization.
- `[ ] REQUEST_CORRECTION`: Specific reversible defects identified; requires re-extraction.
- `[ ] REJECT_EXTRACTION`: Structural or protocol incompatibility; operation must be disqualified.

---

## 5. Reviewer Sign-Off and Epistemic Declaration

- **Reviewer Name:** `[Full Name]`
- **Affiliation / Organization:** `[Institution / Company]`
- **Conflict of Interest Declaration:**
  *"I declare that I have no financial, personal, or employment conflict of interest with the authors of this benchmark. I have made zero code or documentation contributions to this benchmark repository, hold no commit access, and have performed this evaluation independently."*
- **Cryptographic Signature / GPG Key ID:** `[GPG Key ID / Commit Signature]`
- **Signature Timestamp:** `[ISO-8601 Timestamp]`

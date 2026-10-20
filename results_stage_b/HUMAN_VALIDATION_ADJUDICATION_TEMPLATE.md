# Stage B Human Validation Inter-Rater Adjudication Template

**Document Type:** Formal Dispute Resolution and Adjudication Protocol  
**Governing Manual:** `results_stage_b/HUMAN_VALIDATION_OPERATIONS_MANUAL.md`  
**Escalation Trigger:** Inter-Rater Reliability $\kappa < 0.85$ or Split Binary Review Decision  

---

## 1. Case Identification and Discrepancy Metadata

| Case Dimension | Primary Record |
| :--- | :--- |
| **Blinded Operation Token** | `[e.g. OP_BLIND_7A92]` |
| **Target Slot / Operation ID** | `[Unblinded Slot ID after review completion]` |
| **Reviewer 1 (R1) ID & Decision** | `[e.g. REV_EXT_01]`: `[APPROVE_WITH_WRAPPER_POLICY]` |
| **Reviewer 2 (R2) ID & Decision** | `[e.g. REV_EXT_02]`: `[REQUEST_CORRECTION]` |
| **Observed Rubric Agreement ($P_o$)** | `[e.g. 0.80 (12/15 items agreed)]` |
| **Expected Chance Agreement ($P_e$)** | `[e.g. 0.50]` |
| **Calculated Cohen's Kappa ($\\kappa$)** | `[e.g. 0.60]` (Requires adjudication if $\kappa < 0.85$) |
| **Date Escalated to Referee** | `[YYYY-MM-DD]` |

---

## 2. Discrepancy Breakdown by Rubric Item

Document every rubric item where Reviewer 1 and Reviewer 2 reached divergent assessments:

| Item ID | Dimension | Reviewer 1 Assessment & Rationale | Reviewer 2 Assessment & Rationale | Root Cause of Divergence |
| :--- | :--- | :--- | :--- | :--- |
| **`R-XX`** | `[e.g. Array Structure]` | `[R1 passed: items matches string]` | `[R2 failed: tuple syntax ambiguity]` | `[Interpretation of openapi 3.0 items array]` |
| **`R-YY`** | `[e.g. Default Values]` | `[R1 passed: default retained]` | `[R2 failed: boolean default coerced]` | `[Coercion vs identity mapping]` |

---

## 3. Protocol Referee Hearing and Deliberation

The Senior Protocol Referee conducts a direct independent inspection of the raw OpenAPI specification node, the canonical contract, and the deterministic lineage ledger.

### Technical Analysis of Divergent Points
`[Referee records detailed technical analysis comparing the competing rater arguments against RFC 6901, JSON Schema Draft-07, and STAGE_B_EXTRACTION_SPEC.md.]`

---

## 4. Final Adjudication Determination

Select exactly one authoritative determination:
- `[ ] UPHOLD_REVIEWER_1_DECISION`: Reviewer 1 interpretation verified against protocol standards.
- `[ ] UPHOLD_REVIEWER_2_DECISION`: Reviewer 2 defect identification verified; remediation required.
- `[ ] DIRECTED_REMEDIATION`: Clarify specification and execute deterministic re-extraction under updated rule.
- `[ ] DISQUALIFY_OPERATION`: Irreconcilable ambiguity in raw upstream OpenAPI contract; exclude from benchmark cohort.

---

## 5. Required Action Items and Implementation Mandates

1. **Extractor Updates (if required):** `[Specify code modification or state 'None']`
2. **Lineage Ledger Updates:** `[Specify lineage corrections or state 'None']`
3. **Re-Review Requirements:** `[Specify whether dual re-review is mandatory or state 'None']`

---

## 6. Senior Protocol Referee Sign-Off

- **Referee Name:** `[Full Name]`
- **Role:** `SENIOR_PROTOCOL_REFEREE`
- **Institution / Affiliation:** `[Institution]`
- **Conflict of Interest Declaration:**
  *"I declare that I have evaluated this inter-rater dispute impartially according to published protocol specifications, holding no personal interest in the outcome."*
- **Cryptographic Signature / GPG Key:** `[GPG Signature]`
- **Timestamp:** `[ISO-8601 Timestamp]`

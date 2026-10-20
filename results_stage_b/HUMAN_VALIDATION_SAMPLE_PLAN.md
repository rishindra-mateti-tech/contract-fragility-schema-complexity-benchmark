# Stage B Human Validation Stratified Sampling Plan

**Document Type:** Statistical Sampling Strategy & Operational Protocol  
**Document Status:** `ACTIVE_PLANNING_SPECIFICATION`  
**Governing Manual:** `results_stage_b/HUMAN_VALIDATION_OPERATIONS_MANUAL.md`  
**Current Lifecycle State:** `PILOT_PHASE` (2 Extracted Pilots; 0 Independent Reviews Completed)  

---

## 1. Executive Summary and Sampling Architecture

To balance statistical rigor against the high cost of double-blind expert review, this protocol implements a stratified sampling plan across the 30 active manifest operations.

### Core Sampling Rules
1. **100% Census Strata (High-Complexity / Union Cohort):** All operations involving object-level unions (e.g. Stripe `PostRefunds` under Protocol Amendment 003) or deep nesting ($d = 5$) undergo mandatory 100% double-blind human review.
2. **Minimum 20% Stratified Strata (Monomorphic Cohort):** Clean monomorphic operations are sampled at a minimum 20% rate, stratified across all 10 clusters (ensuring at least 1 operation per cluster is reviewed).
3. **Double Reviewer Assignment:** Every sampled operation is independently evaluated by two distinct external reviewers ($R_1, R_2$).
4. **Current Execution Baseline:** Currently, only 2 operations have been extracted (`SLOT_GITHUB_01`, `SLOT_STRIPE_02`). Exactly 0 independent reviews have been conducted to date.

---

## 2. Stratified Population Allocation

The 30 active manifest operations partition into three evaluation strata:

| Stratum ID | Stratum Definition | Total Operations | Required Sample Rate | Minimum Sample Size | Reviewer Assignments |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **STRAT_01** | **Faithful Object Unions** (Stripe PostRefunds) | 1 | 100% | 1 operation | 2 independent reviews |
| **STRAT_02** | **Deep Nesting Cohort** ($d = 4$ or $5$) | 6 | 100% | 6 operations | 12 independent reviews |
| **STRAT_03** | **Standard Monomorphic Cohort** ($d \le 3$) | 23 | ~30% (min 20%) | 7 operations | 14 independent reviews |
| **TOTAL** | **Full Benchmark Cohort** | **30** | **46.7% overall** | **14 operations** | **28 independent reviews** |

> **Cluster Balance Invariant:** The sampled 14 operations must include at least one operation from each of the 10 source clusters (GitHub, Stripe, DigitalOcean, Twilio, Box, Slack, Chatwoot, LINE, MCP SQLite, MCP GitHub).

---

## 3. Current Project State Truth Table

| Dimension | Realized Status as of October 2026 | Governing Policy |
| :--- | :---: | :--- |
| **Total Active Manifest Operations** | `30` | Defined in `stage_b_operation_manifest.yaml` |
| **Canonical Contracts Extracted** | `2` | `SLOT_GITHUB_01` (pulls/create) and `SLOT_STRIPE_02` (PostShippingRates) |
| **Author Manual Reviews Completed** | `1` | `SLOT_GITHUB_01` (Rishindra Mateti, AUTHOR_MANUAL_REVIEW) |
| **Operations Pending Human Validation** | `1` | `SLOT_STRIPE_02` (held strictly pending validation) |
| **Unextracted Manifest Operations** | `28` | Awaiting scheduled extractor capability expansion |
| **Independent Reviews Completed** | **`0`** | **Strictly 0; independent review remains a future gate** |
| **Operations Labeled CANONICAL_FAITHFUL** | **`0`** | **Strictly 0; non-elevation invariant strictly enforced** |

---

## 4. Sampling Selection Methodology

When Gate 4 execution commences:
1. **Deterministic Random Seed:** Operations for Stratum 3 are selected using a cryptographically published seed (`SHA256(origin/master HEAD commit SHA)`).
2. **Stratification Constraint:** Selection algorithm enforces the rule: `len(set(op.cluster for op in sample)) == 10`.
3. **Replacement Handling:** If an operation is disqualified during review, an alternate operation from the same cluster is selected deterministically.

---

## 5. Execution Prerequisites and Milestones

Human validation panels will be convened only after clearing the following technical milestones:
- **Milestone A:** Extraction engine expanded to support all 30 manifest operations without exceptions.
- **Milestone B:** Automated validator and lineage audit passing 100% across all 30 canonical contracts.
- **Milestone C:** Reviewer panel recruited, COI disclosures signed, and 3-case calibration completed.
- **Milestone D:** Double-blind review packets generated and assigned to external evaluators.

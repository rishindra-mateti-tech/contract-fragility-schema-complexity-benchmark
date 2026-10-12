# Paper Evidence Ledger & Claim Boundary Controls

**Document Role:** Empirical Claim Verification Ledger & Overclaim Prevention Protocol  
**Date (UTC):** October 12, 2026  
**Status:** ACTIVE_RESEARCH_LEDGER  
**Governing Phase:** Phase 4 Paper Evidence Ledger  

---

## 1. Executive Protocol & Boundary Guardrails

This ledger enforces strict empirical integrity between claims planned for the research paper and the tangible artifacts committed to this repository. In scientific benchmarking, claims of performance, robustness, fragility, or adherence are scientifically invalid unless backed by byte-stable, reproducible code, frozen data, and audit records.

### 1.1 Status Definitions
- **`AVAILABLE`**: The claim is fully substantiated by immutable, committed repository artifacts (e.g., frozen raw schemas, verified hashes, ratified protocols, pre-screen audit logs, or candidate inventories).
- **`PENDING`**: The claim is theoretically formulated and structurally specified, but the required empirical phase (extraction engine, mutation generator, mock executor, or model evaluation) has not yet been authorized or executed.
- **`BLOCKED`**: The claim depends on unresolved protocol gates, unselected candidate slots, or missing external author approval.

### 1.2 Absolute Invariants & Prohibitions
1. **Stage B Empirical Invariance**: Absolutely NO claim that Stage B empirical results, model rankings, fragility curves, or execution error rates exist may be made. Stage B extraction, mutation, and evaluation have NOT begun.
2. **Canonical Cohort Status**: Absolutely NO claim that 28 or 30 real-world operations are "approved", "finalized", or "canonical" may be made. Currently:
   - **Clean Monomorphic Provisional Candidates**: 24 operations.
   - **Faithful-Union Provisional Candidates**: 1 operation (`Stripe PostRefunds`).
   - **Excluded Operations**: 7 operations (`EXCLUDE_PENDING`).
   - **Replacement Slots Required**: 5 slots (inventoried, but zero final selections admitted).
   - **Canonical Faithful Admitted**: **0 operations**.
3. **Stage A Frozen State**: Stage A results and artifacts are permanently frozen. Stage B work cannot retroactively alter Stage A numbers or claims.
4. **Zero Fluff & Anti-AI Tone**: Research claims must use precise mathematical and empirical terminology. Vague claims of "superior performance", "industry-standard accuracy", or "revolutionary methodology" are prohibited.

---

## 2. Master Paper Claims Ledger

| Claim ID | Planned Paper Section | Planned Paper Claim | Required Evidence Artifact | Status | Exact Repo Path to Evidence | Prohibited Overclaim Language |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **CLM-01** | Abstract / Intro | "We benchmark LLM tool calling across real-world API schemas with controlled complexity and mutations." | Frozen raw sources, Stage B extraction spec, mutation plan | **AVAILABLE** (Design & Corpus Level) | `STAGE_B_EXTRACTION_SPEC.md`, `PROTOCOL_AMENDMENT_003.md` | Do NOT claim model evaluations or rankings have been completed. |
| **CLM-02** | Corpus / Methodology | "Real-world schemas are sourced from 10 diverse ecosystem clusters and cryptographically pinned." | Pinned Git blob SHAs and raw files in `data_stage_b/raw/` | **AVAILABLE** | `data_stage_b/raw/`, `results_stage_b/stage_b_operation_manifest.yaml` | Do NOT claim all candidate operations are admitted into canonical cohort. |
| **CLM-03** | Corpus / Integrity | "The canonical cohort enforces strict structural bounds: no cycles, depth $\le 5$, no binary uploads." | Static pre-screen auditor script, JSON/MD reports, regression tests | **AVAILABLE** | `src/audit_stage_b_candidate_prescreen.py`, `results_stage_b/pre_extraction_candidate_audit.json` | Do NOT claim rejected operations can be admitted without protocol amendments. |
| **CLM-04** | Corpus / Unions | "Finite source-faithful object unions are preserved without heuristic pruning under ratified Amendment 003." | Ratified protocol amendment, union test plan specification | **AVAILABLE** (Spec Level) | `PROTOCOL_AMENDMENT_003.md`, `UNION_VALIDATION_TEST_PLAN.md` | Do NOT claim union test suites have been executed or that wide unions are permitted. |
| **CLM-05** | Corpus / Slots | "Open replacement slots are inventoried from frozen raw sources across 15 audited candidate operations." | Replacement candidate inventory draft (JSON and MD) | **AVAILABLE** (Draft Inventory) | `results_stage_b/replacement_candidate_inventory_draft.json`, `results_stage_b/replacement_candidate_inventory_draft.md` | Do NOT claim replacements are finalized or admitted to the manifest. |
| **CLM-06** | Extraction / Architecture | "All input surfaces (`path`, `query`, `header`, `body`) are faithfully extracted into uniform transport contracts." | Stage B extraction engine, extracted canonical schemas, field lineage log | **PENDING** | To be generated in future authorized phase | Do NOT claim extraction has been executed or contracts exist. |
| **CLM-07** | Extraction / Lineage | "Every extracted canonical field maintains byte-verifiable cryptographic lineage to raw source pointers." | `canonical_field_lineage.jsonl` | **PENDING** | To be generated in future authorized phase | Do NOT claim lineage verification has passed prior to extraction. |
| **CLM-08** | Mutations / Fragility | "Systematic syntactic and semantic mutations reveal non-linear model contract fragility." | Mutation engine, mutated contract fixtures, mutation manifest | **PENDING** | To be generated in future authorized phase | Do NOT claim fragility curves or mutation failure modes are known. |
| **CLM-09** | Execution / Grounding | "Model tool calls are validated offline against hermetic, deterministic local mock executors." | Mock execution engine, state machines, response fixtures | **PENDING** | To be generated in future authorized phase | Do NOT claim execution grounding is active or mock tests pass. |
| **CLM-10** | Empirical Evaluation | "Model adherence degrades sharply as schema recursion depth increases beyond depth 2." | Model inference transcripts, scoring logs, statistical summary tables | **PENDING** | To be generated in future authorized phase | Do NOT claim any model (OpenAI, Claude, Gemini, etc.) has been evaluated. |
| **CLM-11** | Empirical Evaluation | "Models exhibit severe error rate increases under transport-level surface restructuring." | Evaluation runner outputs, confusion matrices, statistical significance tests | **PENDING** | To be generated in future authorized phase | Do NOT claim specific model vulnerability numbers or error percentages. |
| **CLM-12** | Related Work | "Existing benchmarks rely primarily on flat (depth 1) synthetic or scraped schemas lacking mutation testing." | Related work evidence matrix, verified BibTeX, source verification log | **AVAILABLE** | `literature/RELATED_WORK_EVIDENCE_MATRIX.md`, `literature/RELATED_WORK_BIBLIOGRAPHY.bib`, `literature/RELATED_WORK_SOURCE_LOG.md` | Do NOT claim superiority or novelty until empirical evaluations are complete. |
| **CLM-13** | Threats to Validity | "Data contamination is mitigated by cryptographic blob freezing and synthetic mutation divergence." | Contamination analysis, source commit hashes, mutation divergence logs | **PENDING** (Methodology specified; empirical run pending) | `STAGE_B_EXTRACTION_SPEC.md` | Do NOT claim zero contamination without empirical memorization audit. |

---

## 3. Section-by-Section Evidence Requirements

### 3.1 Abstract & Introduction
- **Permitted Claims**:
  - Research objective: Investigating LLM tool-calling contract fragility under structural complexity.
  - Identification of literature gaps: Current benchmarks focus on flat, unmutated schemas.
  - Benchmark protocol design: Dual-cohort structure (real production schemas + synthetic controls).
- **Prohibited Claims**:
  - Quantitative benchmark scores (e.g. *"GPT-4 achieves 72% accuracy"*).
  - Claims that the benchmark is complete, fully extracted, or evaluated.

### 3.2 Benchmark Design & Corpus Curation
- **Permitted Claims**:
  - 10 frozen real-world clusters pinned by immutable Git blob hashes (`a91fa76a...`, `f1cedf38...`, etc.).
  - Formal 7-rule pre-screen audit establishing 24 clean monomorphic candidates, 1 faithful-union candidate, and 7 exclusions.
  - Draft inventory of 15 candidate operations for 5 open replacement slots.
- **Prohibited Claims**:
  - *"30 operations are approved and ready."* (Only 25 provisional candidates exist; 5 slots remain open).
  - *"Slack chat.postMessage and LINE pushMessage are included."* (Both are permanently `EXCLUDE_PENDING`).

### 3.3 Extraction Specification & Field Lineage
- **Permitted Claims**:
  - Deterministic transport contract representation: uniform nested surfaces (`path`, `query`, `header`, `body`).
  - Zero-pruning rule for canonical cohort; depth bounded at $5$.
  - Ratified Amendment 003 protocol for finite object unions.
- **Prohibited Claims**:
  - Any claim referencing extracted canonical JSON Schema files on disk.
  - Any claim of completed field-lineage verification.

### 3.4 Mutation Calculus & Execution Grounding
- **Permitted Claims**:
  - Theoretical specification of mutation operators (syntactic renaming, type loosening, surface restructuring).
  - Design specification for offline local mock executors and Draft-07 validator enforcement.
- **Prohibited Claims**:
  - Claims that mutations have been generated or validated against models.
  - Claims that mock executors have executed live model payloads.

### 3.5 Results & Discussion
- **Permitted Claims**:
  - None for Stage B.
- **Prohibited Claims**:
  - All empirical claims regarding model accuracy, fragility degradation, syntax failure rates, or leaderboard rankings for Stage B.

---

## 4. Claims Not Yet Permitted (Explicit Freeze List)

The following statements are **STRICTLY PROHIBITED** from appearing in any paper draft, documentation, conference abstract, or commit message until their specific gating conditions are satisfied:

1. ❌ *"The Stage B benchmark contains 30 validated real-world API schemas."*  
   *Condition Required:* Extraction engine executed, 5 replacement slots formally admitted, automated validation passed, and manual review signed off.
2. ❌ *"Model tool-calling accuracy drops by X% under schema mutations."*  
   *Condition Required:* Mutation generation engine completed, model inference execution runs finished, scoring verified.
3. ❌ *"Stripe PostCustomers and PostPaymentIntents are evaluated in the benchmark."*  
   *Condition Required:* Independent depth-limit amendment proposed, reviewed, and approved (currently prohibited under frozen $MAX\_RECURSION\_DEPTH = 5$).
4. ❌ *"We evaluate Frontier LLMs (GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro) on enterprise contracts."*  
   *Condition Required:* Benchmark runner authorization, API call execution, raw transcript preservation.
5. ❌ *"Our benchmark eliminates data contamination."*  
   *Condition Required:* Memorization probing empirical tests conducted and documented in `results_stage_b/`.
6. ❌ *"Field lineage verification has confirmed 100% fidelity across all real schemas."*  
   *Condition Required:* Extraction executed and `canonical_field_lineage.jsonl` validated by automated lineage auditor.

---

## 5. Audit & Maintenance Protocol

Any proposed promotion of a claim from `PENDING` or `BLOCKED` to `AVAILABLE` requires:
1. Direct inspection of the supporting file path in the repository.
2. Verification of cryptographic hashes and automated test pass records.
3. Updating this ledger in a dedicated documentation commit.

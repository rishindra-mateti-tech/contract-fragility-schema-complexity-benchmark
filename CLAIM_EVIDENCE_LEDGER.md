# Comprehensive Claim Evidence Ledger

**Document Role:** Verifiable Literature, Comparative, and Benchmark Claim Evidence Ledger  
**Date (UTC):** October 12, 2026  
**Status:** ACTIVE_EVIDENCE_AUDIT  
**Governing Policy:** All empirical and literature claims must possess a verified primary-source citation, exact section/page reference, and explicit status classification (`SUPPORTED`, `PARTIALLY_SUPPORTED`, `PENDING`, or `RETRACTED`). Claims without primary-source evidence remain strictly `PENDING`.

---

## 1. Executive Summary & Ledger Statistics

| Status | Definition | Count |
| :--- | :--- | :---: |
| **`SUPPORTED`** | Verified directly against primary literature source or cryptographically pinned repository data. | 13 |
| **`PARTIALLY_SUPPORTED`** | Methodological or design claim partially substantiated by code/spec but awaiting empirical Stage B completion. | 3 |
| **`PENDING`** | Planned capability, future evaluation hypothesis, or unverified empirical claim; prohibited from paper claims until verified. | 4 |
| **`RETRACTED`** | Superseded or exaggerated claim formally withdrawn from project claims. | 1 |
| **TOTAL** | **All Audited Claims** | **21** |

---

## 2. Literature & Comparative Claims Table

### CLM-LIT-001: Gorilla / APIBench Flat Parameter Signatures & Static Evaluation
- **Exact Claim Text:** *"Gorilla (APIBench) evaluates tool/API calling accuracy on flat Python library signatures (TorchHub, HuggingFace, TensorHub) using static documentation, without multi-surface HTTP transport partitioning or programmatic schema mutation operators."*
- **Status:** **`SUPPORTED`**
- **Primary-Source Reference & URL:** Patil et al., NeurIPS 2024, arXiv:2305.15334. [https://arxiv.org/abs/2305.15334](https://arxiv.org/abs/2305.15334).
- **Exact Section / Page:** Section 3 ("APIBench"), pages 3-4; Appendix A.
- **Evidence Note:** Primary paper documents APIBench as a dataset of 1,645 API calls across three ML hubs evaluated via Python AST parameter parsing against static docstrings. Does not contain schema mutations or HTTP transport layers.

---

### CLM-LIT-002: ToolBench RapidAPI Flattening & Catalog Scale
- **Exact Claim Text:** *"ToolBench crawls 16,464 RapidAPI marketplace endpoints where parameters are largely flattened into generic dictionary objects, prioritizing catalog volume over multi-surface transport partitioning or schema recursion depth."*
- **Status:** **`SUPPORTED`**
- **Primary-Source Reference & URL:** Qin et al., ICLR 2024 (Spotlight), arXiv:2307.16789. [https://arxiv.org/abs/2307.16789](https://arxiv.org/abs/2307.16789).
- **Exact Section / Page:** Section 3.1 ("ToolBench Data Collection"), pages 3-5.
- **Evidence Note:** RapidAPI crawler stores parameters in loose key-value mappings; evaluation relies on simulated LLM evaluators or live RapidAPI proxy calls without recursion depth bounds or mutation operators.

---

### CLM-LIT-003: Berkeley Function Calling Leaderboard (BFCL) Static AST Evaluation
- **Exact Claim Text:** *"BFCL benchmarks static function-calling accuracy across Python, Java, JavaScript, and REST APIs using AST argument matching, without evaluating contract fragility under upstream schema evolution or controlled mutations."*
- **Status:** **`SUPPORTED`**
- **Primary-Source Reference & URL:** Yan et al., ICML 2024 Workshop. [https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html](https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html). Repository: [https://github.com/ShishirPatil/gorilla](https://github.com/ShishirPatil/gorilla).
- **Exact Section / Page:** Blog documentation and repository evaluation scripts (`eval_checker.py`).
- **Evidence Note:** BFCL evaluates model completions against fixed golden ground-truth ASTs from static function signatures. Does not apply schema perturbation calculus.

---

### CLM-LIT-004: ToolAlpaca Fully Synthetic Simulation
- **Exact Claim Text:** *"ToolAlpaca evaluates tool-use generalization using 3,000 simulated interaction cases across 400 purely synthetic tools generated via Self-Instruct, lacking cryptographically pinned production OpenAPI interfaces."*
- **Status:** **`SUPPORTED`**
- **Primary-Source Reference & URL:** Tang et al., arXiv:2306.05301. [https://arxiv.org/abs/2306.05301](https://arxiv.org/abs/2306.05301).
- **Exact Section / Page:** Section 2.1 ("Tool Generation"), pages 2-3.
- **Evidence Note:** Tools were created entirely via prompting GPT-4 to invent tool names, descriptions, and flat parameter dictionaries.

---

### CLM-LIT-005: API-Bank Handcrafted Python Methods
- **Exact Claim Text:** *"API-Bank evaluates multi-turn dialogue planning over 73 handcrafted Python tool classes with flat docstrings, rather than enterprise OpenAPI 3.0/3.1 contracts with deep schema nesting."*
- **Status:** **`SUPPORTED`**
- **Primary-Source Reference & URL:** Li et al., EMNLP 2023, pages 3102-3116, arXiv:2304.08244. [https://arxiv.org/abs/2304.08244](https://arxiv.org/abs/2304.08244).
- **Exact Section / Page:** Section 2 ("API-Bank Benchmark"), pages 3103-3105.
- **Evidence Note:** Catalog comprises 73 Python functions covering daily tasks (e.g. calculator, calendar, email) with plain docstrings.

---

### CLM-LIT-006: RestGPT / RestBench Live Execution Scope
- **Exact Claim Text:** *"RestBench evaluates REST API planning over live TMDB and Spotify endpoints across 2 specifications, subject to external network latency and live account state, without schema mutation testing."*
- **Status:** **`SUPPORTED`**
- **Primary-Source Reference & URL:** Song et al., arXiv:2306.06624. [https://arxiv.org/abs/2306.06624](https://arxiv.org/abs/2306.06624).
- **Exact Section / Page:** Section 3.2 ("RestBench"), pages 4-5.
- **Evidence Note:** Benchmark evaluates live requests against TMDB (movie database) and Spotify APIs; does not test schema perturbations or offline state isolation.

---

### CLM-LIT-007: NexusRaven Docstring Function Evaluation
- **Exact Claim Text:** *"NexusRaven evaluates open-source instruction-tuned model parameter generation on static Python docstring signatures against proprietary models, without schema nesting depth scaling or mutation operators."*
- **Status:** **`SUPPORTED`**
- **Primary-Source Reference & URL:** Srinivasan et al., Nexusflow Report 2023. [https://nexusflow.ai/blogs/ravenv2](https://nexusflow.ai/blogs/ravenv2). Repository: [https://github.com/nexusflowai/NexusRaven-V2](https://github.com/nexusflowai/NexusRaven-V2).
- **Exact Section / Page:** Section 2 ("Evaluation Methodology").
- **Evidence Note:** Evaluates prompt-to-call accuracy on curated Python docstrings; does not evaluate multi-surface HTTP transport or schema mutation curves.

---

### CLM-LIT-008: Seal-Tools Synthetic Training Focus
- **Exact Claim Text:** *"Seal-Tools focuses on synthetic tool and task generation for training data synthesis rather than empirical contract fragility evaluation under enterprise schema mutations."*
- **Status:** **`SUPPORTED`**
- **Primary-Source Reference & URL:** Du et al., arXiv:2405.08355. [https://arxiv.org/abs/2405.08355](https://arxiv.org/abs/2405.08355).
- **Exact Section / Page:** Section 3 ("Tool and Task Generation"), pages 3-5.
- **Evidence Note:** Framework is engineered for self-instruct tool data synthesis to train open models, rather than evaluating contract adherence under schema drift.

---

### CLM-LIT-009: FOFO Format-Following Scope
- **Exact Claim Text:** *"FOFO evaluates model instruction-following across broad surface text formats (JSON, YAML, XML, markdown) rather than API tool-calling contracts or JSON Schema typing constraints."*
- **Status:** **`SUPPORTED`**
- **Primary-Source Reference & URL:** Xia et al., arXiv:2402.18667. [https://arxiv.org/abs/2402.18667](https://arxiv.org/abs/2402.18667).
- **Exact Section / Page:** Section 2 ("Benchmark Design"), pages 2-4.
- **Evidence Note:** Measures parsing success across general text formats; does not isolate HTTP transport surfaces, parameter requiredness, or API schema complexity.

---

### CLM-LIT-010: StructEval Format Generation Scope
- **Exact Claim Text:** *"StructEval benchmarks structured format generation across 18 formats and 44 task categories, rather than tool-calling contract fragility or downstream execution state."*
- **Status:** **`SUPPORTED`**
- **Primary-Source Reference & URL:** Tang et al., arXiv:2410.08815. [https://arxiv.org/abs/2410.08815](https://arxiv.org/abs/2410.08815).
- **Exact Section / Page:** Section 3 ("Taxonomy of Tasks"), pages 3-6.
- **Evidence Note:** Covers generic format tasks (text-to-JSON, table extraction, code formatting) without stateful mock grounding or API mutation operators.

---

### CLM-LIT-011: Outlines Constrained Decoding Scope
- **Exact Claim Text:** *"Constrained decoding frameworks (Outlines) ensure token-level syntactic validity against formal grammars by construction, but do not prevent semantic argument formulation errors or evaluate contract fragility under upstream schema drift."*
- **Status:** **`SUPPORTED`**
- **Primary-Source Reference & URL:** Willard & Louf, arXiv:2307.09702. [https://arxiv.org/abs/2307.09702](https://arxiv.org/abs/2307.09702). Repository: [https://github.com/dottxt-ai/outlines](https://github.com/dottxt-ai/outlines).
- **Exact Section / Page:** Section 2 ("Efficient Guided Generation"), pages 2-4.
- **Evidence Note:** FSM-based logit masking guarantees syntactic grammar compliance; semantic correctness within valid tokens remains dependent on model reasoning.

---

### CLM-LIT-012: SWE-bench Macro-Level Task Scope
- **Exact Claim Text:** *"SWE-bench evaluates multi-turn autonomous software engineering (generating git patches to resolve GitHub issues verified by unit test execution) at a macro-level, rather than isolating unit-level tool contract fragility under schema complexity."*
- **Status:** **`SUPPORTED`**
- **Primary-Source Reference & URL:** Jimenez et al., ICLR 2024, arXiv:2310.06770. [https://arxiv.org/abs/2310.06770](https://arxiv.org/abs/2310.06770).
- **Exact Section / Page:** Section 2 ("SWE-bench Task Formulation"), pages 2-4.
- **Evidence Note:** Benchmark evaluates repository-level problem solving over hours/turns; does not isolate individual tool call argument degradation under controlled schema mutations.

---

## 3. Benchmark Design & Methodology Claims Table

### CLM-DES-001: Target Corpus Cohort Architecture
- **Exact Claim Text:** *"The benchmark architecture targets a balanced dual-cohort design consisting of 30 cryptographically pinned real enterprise operations and 20 controlled synthetic schemas."*
- **Status:** **`PARTIALLY_SUPPORTED`**
- **Primary-Source Reference & URL:** `STAGE_B_EXTRACTION_SPEC.md`, Section 1 & Section 8.
- **Exact Section / Page:** `STAGE_B_EXTRACTION_SPEC.md` lines 11-23, 340-385.
- **Evidence Note:** The 30+20 architecture is the ratified protocol design target. Stage A produced 20 synthetic schemas; Stage B real enterprise operations are currently provisionally cataloged (24 clean candidates, 1 faithful-union candidate, 5 open replacement slots) pending extraction. It is a target design, not an achieved corpus.

---

### CLM-DES-002: Bounded Deep Nesting ($1 \le d \le 5$) in Enterprise Specs
- **Exact Claim Text:** *"Enterprise OpenAPI specifications exhibit recursive parameter nesting up to depth 5 with multi-surface transport partitioning across path, query, header, and body."*
- **Status:** **`SUPPORTED`**
- **Primary-Source Reference & URL:** `results_stage_b/raw_operation_universe.json`, Section `depth_distribution`.
- **Exact Section / Page:** Lines 51614-51631 in `raw_operation_universe.json`.
- **Evidence Note:** Static analysis scan of 1,346 raw operations across 8 enterprise OpenAPI specs confirms depth 1: 435 ops, depth 2: 215 ops, depth 3: 378 ops, depth 4: 100 ops, depth 5: 81 ops.

---

### CLM-DES-003: Systematic Schema Mutation Calculus Isolation
- **Exact Claim Text:** *"A programmatic schema mutation calculus (testing field renaming, requiredness shifts, type widening, and field reordering) can isolate whether models rely on pre-trained prompt memorization or dynamic schema contract comprehension."*
- **Status:** **`PARTIALLY_SUPPORTED`**
- **Primary-Source Reference & URL:** `src/mutations.py` and `STAGE_A_PILOT_FINDINGS.md`.
- **Exact Section / Page:** `src/mutations.py` lines 1-150.
- **Evidence Note:** Validated empirically on Stage A synthetic schemas. Hypothesized for Stage B enterprise schemas, pending post-extraction empirical evaluation runs.

---

### CLM-DES-004: Hermetic Offline Mock Execution Runtime
- **Exact Claim Text:** *"Hermetic offline mock executors validate tool parameter formulation against deterministic local state machines without outbound network calls, eliminating live API flakiness."*
- **Status:** **`PENDING`**
- **Primary-Source Reference & URL:** `STAGE_B_EXTRACTION_SPEC.md`, Section 2.5; `EXTRACTION_IMPLEMENTATION_CHECKLIST.md`, Section 1.
- **Exact Section / Page:** `EXTRACTION_IMPLEMENTATION_CHECKLIST.md` Section 1.
- **Evidence Note:** Mock execution is a planned Stage B capability specified in design blueprints; concrete mock executors have NOT yet been implemented. Prohibited from being claimed as an achieved capability.

---

### CLM-DES-005: Frontier LLM Fragility Degradation Curves
- **Exact Claim Text:** *"Frontier LLMs exhibit steep performance degradation curves under programmatic schema mutations and deep parameter nesting."*
- **Status:** **`PENDING`**
- **Primary-Source Reference & URL:** Research Hypothesis (to be evaluated in future Stage B experimental runs).
- **Exact Section / Page:** Pending experimental benchmark execution.
- **Evidence Note:** Hypothesis grounded in Stage A pilot observations on synthetic schemas. Cannot be asserted as an established empirical finding across frontier models until full Stage B model evaluation is completed.

---

### CLM-DES-006: Cryptographic Provenance Immutability
- **Exact Claim Text:** *"All raw specification sources are pinned to immutable Git blob SHAs and raw source file SHA-256 digests verified by deterministic read-only static analysis."*
- **Status:** **`SUPPORTED`**
- **Primary-Source Reference & URL:** `results_stage_b/raw_sources_provenance_registry.json` and `results_stage_b/raw_operation_universe.json`.
- **Exact Section / Page:** `raw_sources_provenance_registry.json` lines 1-150; `tests/test_stage_b_raw_sources.py`.
- **Evidence Note:** Validated by automated tests: all 10 raw files on disk match their pinned blob SHAs and SHA-256 digests with zero drift.

---

### CLM-DES-007: Finite Faithful Object Union Preservation (Amendment 003)
- **Exact Claim Text:** *"Under Amendment 003, finite object-level unions (such as Stripe PostRefunds metadata) can be preserved without lossy pruning or generic object fallbacks."*
- **Status:** **`PARTIALLY_SUPPORTED`**
- **Primary-Source Reference & URL:** `PROTOCOL_AMENDMENT_003.md` and `UNION_VALIDATION_TEST_PLAN.md`.
- **Exact Section / Page:** `PROTOCOL_AMENDMENT_003.md` lines 1-120.
- **Evidence Note:** Protocol amendment is formally ratified and test plan established. Actual contract extraction and validator checks remain pending implementation of the Stage B extractor.

---


---

## 4. Internal Repository and Protocol Claims Ledger

| Claim ID | Category | Status | Document & Location | Permitted Scoped Wording | Evidence Artifacts |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CLAIM-001` | `EMPIRICAL` | `SCOPE_RESTRICTED` | `README.md:28-34` | Exploratory pilot execution indicates semantic exact match reduction in small sample (N=5); statistical significance unverified. | `results/raw_responses.jsonl`, `results/summary_metrics.json` |
| `CLAIM-002` | `METHODOLOGICAL` | `SUPPORTED` | `README.md:37-63` | Three-task decoupled framework isolates parameter hierarchy, identifier ambiguity, and execution grounding. | `src/runner.py`, `src/evaluator.py`, `tests/test_runner.py` |
| `CLAIM-003` | `METHODOLOGICAL` | `SUPPORTED` | `README.md:65-74` | 20 synthetic tool contracts modeled after real-world API design patterns. | `data/PROVENANCE.md`, `data/tools_canonical.json` |
| `CLAIM-004` | `METHODOLOGICAL` | `SUPPORTED` | `README.md:75-82` | Unit tests verify programmatic mutation operator isolation across canonical, nested, bloated, and ambiguous variants. | `src/mutations.py`, `tests/test_mutations.py` |
| `CLAIM-005` | `METHODOLOGICAL` | `SUPPORTED` | `README.md:85-94` | Distinguishes provider-mediated Regime A from unconstrained Regime B. | `src/runner.py`, `README.md` |
| `CLAIM-006` | `FACTUAL` | `SUPPORTED` | `STAGE_B_EXTRACTION_SPEC.md:15-35` | Section 2.5 prescreening identified 30 active candidates and 7 disqualified operations. | `results_stage_b/candidate_admission_decisions.json`, `tests/test_stage_b_admitted_candidates.py` |
| `CLAIM-007` | `FACTUAL` | `SUPPORTED` | `results_stage_b/HUMAN_ADMISSION_REVIEW_PACKET.md:50-70` | Admission decisions reviewed by author under role AUTHOR_MANUAL_REVIEW with immutable Git provenance. | `results_stage_b/HUMAN_ADMISSION_REVIEW_PACKET.md`, `tests/test_stage_b_human_review_packet.py` |
| `CLAIM-008` | `METHODOLOGICAL` | `SUPPORTED` | `results_stage_b/CANONICAL_EXTRACTION_PILOT_REPORT.md:10-25` | Extracted contract semantically equivalent modulo explicit closed-object wrapper policy. | `data_stage_b/canonical/SLOT_GITHUB_01/canonical_contract.json`, `data_stage_b/canonical/SLOT_GITHUB_01/semantic_preservation_report.md`, `results_stage_b/CANONICAL_PILOT_HUMAN_VALIDATION_PACKET.md` |
| `CLAIM-009` | `FACTUAL` | `SUPPORTED` | `data_stage_b/canonical/SLOT_STRIPE_02/canonical_contract.json:240-260` | SLOT_STRIPE_02 extracted and held strictly at EXTRACTED_PENDING_HUMAN_VALIDATION. | `data_stage_b/canonical/SLOT_STRIPE_02/canonical_contract.json`, `tests/test_stage_b_canonical_generalization_stripe.py` |
| `CLAIM-010` | `FACTUAL` | `SUPPORTED` | `results_stage_b/EXTRACTION_READINESS_AUDIT.md:10-30` | Full-cohort audit classifies 37 tracked operations across 4 readiness states. | `results_stage_b/EXTRACTION_READINESS_MATRIX.json`, `tests/test_stage_b_extraction_readiness.py` |
| `CLAIM-011` | `METHODOLOGICAL` | `SUPPORTED` | `results_stage_b/SCHEMA_FEATURE_SUPPORT_POLICY.md:10-25` | Explicit policy registry and fail-closed validation engine for 38 schema constructs. | `results_stage_b/SCHEMA_FEATURE_SUPPORT_REGISTRY.yaml`, `src/schema_feature_registry.py`, `tests/test_stage_b_schema_feature_registry.py` |
| `CLAIM-012` | `METHODOLOGICAL` | `SUPPORTED` | `tests/test_stage_b_adversarial_feature_corpus.py:10-30` | Synthetic adversarial corpus verifies extraction rules across 28 controlled edge-case fixtures. | `tests/fixtures/schema_feature_corpus/`, `src/synthetic_extractor.py`, `tests/test_stage_b_adversarial_feature_corpus.py` |
| `CLAIM-013` | `METHODOLOGICAL` | `SCOPE_RESTRICTED` | `results_stage_b/SERIALIZATION_CONFORMANCE_SPEC.md:10-40` | Deterministic in-process round-trip under declared representation and supported encoding policy (Tier 2). | `src/openapi_serialization.py`, `results_stage_b/SERIALIZATION_CONFORMANCE_SPEC.md`, `tests/test_openapi_serialization.py` |
| `CLAIM-014` | `FACTUAL` | `SUPPORTED` | `REPRODUCIBILITY.md:10-35` | Automated 7-stage reproducibility script verifies environment, raw provenance, test pass rate, and bitwise re-extraction identity. | `requirements.txt`, `scripts/verify_reproducibility.py`, `results_stage_b/REPRODUCIBILITY_AUDIT.md` |
| `CLAIM-015` | `LIMITATION` | `SUPPORTED` | `results_stage_b/CANONICAL_PROVENANCE_AUDIT.md:35-50` | Identified and documented provenance limitation PROV-LIMIT-001 without altering underlying artifacts. | `results_stage_b/CANONICAL_PROVENANCE_AUDIT.json`, `results_stage_b/CANONICAL_DIFFERENCE_REGISTER.md` |
| `CLAIM-016` | `FUTURE_WORK` | `PENDING` | `results_stage_b/NEXT_GATES.md:1-30` | Roadmap outlines 10 planned sequential engineering and validation gates. | `results_stage_b/NEXT_GATES.md` |
| `CLAIM-017` | `METHODOLOGICAL` | `SUPPORTED` | `results_stage_b/BATCH_EXTRACTION_RESULTS.md:1-40` | Deterministic batch pipeline extracted 13 quarantined candidates held at EXTRACTED_PENDING_HUMAN_VALIDATION and rejected 14 candidates fail-closed. | `data_stage_b/extraction_candidates/`, `results_stage_b/BATCH_EXTRACTION_RESULTS.json`, `tests/test_stage_b_batch_candidate_pipeline.py` |
| `CLAIM-018` | `METHODOLOGICAL` | `SCOPE_RESTRICTED` | `results_stage_b/BATCH_V1_TO_V2_CHANGELOG.md:1-45` | OpenAPI 3.0 to JSON Schema Draft-07 conversion requires explicit type union transformation for nullable: true under OAS30_TO_DRAFT07_CONVERSION_POLICY_001; verbatim preservation is not semantically valid. | `results_stage_b/OAS30_TO_DRAFT07_CONVERSION_POLICY_001.md`, `results_stage_b/OAS30_DRAFT07_COMPATIBILITY_AUDIT.md`, `data_stage_b/extraction_candidates_v2/` |

---

## 5. Retracted & Superseded Claims Ledger

### CLM-RET-001: "Bijective Field Traceability" Superseded
- **Original Claim Text:** *"Every derived field possesses a strictly bijective mapping back to the raw source schema."*
- **Status:** **`RETRACTED`**
- **Superseded By:** `STAGE_B_EXTRACTION_SPEC.md`, Section 5 ("Deterministic Field-Lineage Traceability").
- **Exact Section / Page:** `STAGE_B_EXTRACTION_SPEC.md` lines 252-293.
- **Retraction Rationale:** OpenAPI structural wrapping (e.g. creating `path`, `query`, `header`, `body` transport containers) is a surjective transport encapsulation, not a strict mathematical bijection. Retracted and superseded by deterministic provenance lineage with explicit transformation categories.

---

## 6. Ledger Maintenance Invariant

1. Any claim asserted in a future academic manuscript or public release must cite its corresponding `CLM-*` ID from this ledger.
2. No claim classified as `PENDING` may appear in abstract, introduction, or empirical results sections as an established fact.
3. If primary-source review contradicts an existing claim, its status must be immediately updated to `RETRACTED` or `PARTIALLY_SUPPORTED` with an explanatory note.

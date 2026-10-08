# Contract Fragility Benchmark: Stage B Expansion Plan

## 1. Stage B Protocol
Stage B transitions the benchmark from an exploratory pilot (Stage A) into a fully-scaled, pre-registered causal ablation study measuring how specific schema complexities degrade Large Language Model (LLM) tool-use reliability. Stage A remains strictly frozen and unchanged; Stage B utilizes a new dataset version, new protocol, new manifest, new run IDs, and structurally separated results/analysis directories.

**Core Additions:**
*   **Decoupling Generative from Execution Testing:** While Tasks 1 and 2 (argument syntax and selection) are directly measured off model generation, Stage B officially implements **Task 3: Execution Semantics**. This requires executing the generated JSON against safe, local deterministic simulators (e.g., SQLite databases, mocked HTTP servers) to verify if a structurally valid call induces the intended state change.
*   **Adversarial Rigor:** Stage B formally injects adversarial distractor schemas, near-neighbor function names, deep-nested optionality clutter, underspecified queries, and explicit "no-tool-needed" (abstention) control questions to evaluate whether structural friction forces models into unsafe extrapolations.
*   **Pre-registration:** Before any Stage B API calls are made, the full 50-100 schema dataset, prompt hashes, and analysis pipeline must be committed and cryptographically frozen in `results_stage_b/stage_b_manifest.json`.

## 2. Dataset and Source Plan
The Stage B dataset will expand to 50-100 total schemas, strictly isolated into two reportable sub-datasets:
*   **Synthetic Corpus (Stage A Heritage):** 20 highly controlled synthetic schemas isolating specific parameter permutations.
*   **Real-World Corpus (New for Stage B):** 30-80 schemas directly ingested from production environments.
    *   **OpenAPI Specs:** Sampled from real REST APIs (e.g., GitHub, Stripe, Twilio).
    *   **MCP-Style Specs:** Modern Model Context Protocol (MCP) tool schemas.
*   **Taxonomy & Metadata:** Every schema will be annotated with a rigorous taxonomy: `domain`, `parameter_count`, `nesting_depth`, `optional_field_ratio`, `enum_density`, `identifier_ambiguity_score`, `description_length`, and `token_length`.
*   **Strict Source-Admission Policy:** We will not blindly ingest or assume public specifications are redistributable. Every real-world schema must strictly record:
    1. Source URL
    2. Repository commit or version tag
    3. License file URL and License compatibility (e.g., MIT, Apache 2.0)
    4. Source SHA-256
    5. Provenance date
    6. Exact transformation record (what was truncated/modified to fit the harness)
    7. Exclusion reason (if a candidate schema is rejected)

## 3. Literature-Gap Matrix
The Contract Fragility Benchmark differs fundamentally from existing tool-use benchmarks by focusing on **causal degradation** (ablation) due to schema design choices, rather than overall functional capacity.

| Benchmark | Primary Focus | Methodology | Gap Addressed by Contract Fragility |
| :--- | :--- | :--- | :--- |
| **BFCL (Berkeley Function Calling Leaderboard)** | Broad capability ranking | Assesses execution across diverse programming APIs | Does not control for schema structure; cannot isolate *why* an LLM failed. |
| **ToolSandbox** | Stateful, multi-step execution | Evaluates agent traversal of complex environments | Too macroscopic; conflates planning failure with schema extraction failure. |
| **API-Bank** | Conversational integration | Focuses on multi-turn API usage | Lacks specific schema mutation ablation (e.g., nesting vs. optionality). |
| **ToolBench** | Massive scale OpenAPI | Tests generalization across thousands of real APIs | Focuses on breadth, lacking isolated causal controls on tool descriptions. |
| **Contract Fragility** | **Causal Ablation** | **Controlled structural mutations on identical targets** | **Proves whether poor API contract design directly degrades a capable LLM.** |

*Novelty Statement:* The Contract Fragility Benchmark is a controlled causal ablation of tool-contract properties. It is not a replacement for broad real-world tool-use capability benchmarks; rather, it is a specialized diagnostic instrument that proves how specific engineering choices (e.g., deep object nesting, identifier ambiguity) degrade LLM alignment, isolating structural friction from general intelligence.

## 4. Provider Preflight and Track Plan
To ensure fair and rigorous model evaluation, Track A (Provider-Mediated native tool-calling) and Track B (Raw JSON Unconstrained) will be strictly separated.

**No models are hard-coded or assumed.** A read-only provider preflight script (`src/stage_b_preflight.py`) will execute to dynamically generate the model matrix. The final model list will only be frozen *after* the preflight validates access.
The preflight script must record:
- Provider
- Exact available model ID queried from the API
- Track/Interface (Native vs Raw JSON)
- Native tool calling support confirmation
- Current API quota/error result (ensuring zero-cost tier access is alive)
- Timestamp
- Model-list snapshot SHA-256 hash

Telemetry for real execution will expand to capture token usage and exact API error categories.

## 5. Statistical Analysis Plan
*   **Schema-Level Analysis:** Results will be aggregated at the schema level. We will use bootstrap confidence intervals over the *schemas* (resampling schemas with replacement) to estimate the robustness of findings across different API domains.
*   **Multiple Hypothesis Correction:** Because we test multiple mutation vectors against the Canonical baseline, we will apply the **Holm-Bonferroni correction** to all $p$-values derived from McNemar paired exact tests to strictly control the Family-Wise Error Rate (FWER).
*   **Stratified Human Validation:** We will mandate blinded human validation for **at least 20 schemas or 20% of the Stage B dataset** (whichever is larger). This sample will stratify across synthetic vs. real sources and explicitly cover every mutation family. Validation will utilize two independent reviewers, formally reporting inter-reviewer agreement and the adjudication protocol for edge cases.

## 6. Calculated Call Budget and Safety Guards
To prevent runaway background execution and respect zero-cost tiers, the exact call budget is calculated from the combinatorial design.

**Base Call Calculation Formula:**
`Schemas (S) × Variants (4) × Tasks (T) × Repeats (3) × Models (M) + Distractor/Abstention/Retries`

*Task Scope Definitions:*
- Task 1 (Argument Construction): 1 call
- Task 2 (Tool Selection with Distractors): 1 call
- Task 3 (Execution Semantics): 0 calls (Evaluates Task 1 output locally)
- Task 4 (Adversarial Abstention/No-Tool): 1 call
*(Total $T = 3$ API calls per schema/variant/repeat)*

Assuming a dataset of $S=80$ schemas and exactly $M=3$ models validated by preflight:
`80 × 4 × 3 × 3 × 3 = 8,640 base calls.`

**Strict Maximum-Call Safety Guard:**
To accommodate potential API retries (503s, 429s), the runner will inject a strict `MAX_CALLS` guard at 110% of the theoretical baseline. Execution will immediately halt if this threshold is breached. Zero-cost feasibility is explicitly verified empirically via the preflight gate rather than assumed.

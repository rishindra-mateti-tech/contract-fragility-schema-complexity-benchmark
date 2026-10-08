# Contract Fragility Benchmark: Stage B Expansion Plan

## 1. Stage B Protocol
Stage B transitions the benchmark from an exploratory pilot (Stage A) into a fully-scaled, pre-registered causal ablation study measuring how specific schema complexities degrade Large Language Model (LLM) tool-use reliability. 

**Core Additions:**
*   **Decoupling Generative from Execution Testing:** While Tasks 1 and 2 (argument syntax and selection) are directly measured off model generation, Stage B officially implements **Task 3: Execution Semantics**. This requires executing the generated JSON against safe, local deterministic simulators (e.g., SQLite databases, mocked HTTP servers) to verify if a structurally valid call induces the intended state change.
*   **Adversarial Rigor:** Stage B formally injects adversarial distractor schemas, near-neighbor function names, deep-nested optionality clutter, underspecified queries, and explicit "no-tool-needed" (abstention) control questions to evaluate whether structural friction forces models into unsafe extrapolations.
*   **Pre-registration:** Before any Stage B API calls are made, the full 50–100 schema dataset, prompt hashes, and analysis pipeline must be committed and cryptographically frozen as `stage_b_manifest.json`.

## 2. Dataset and Source Plan
The Stage B dataset will expand to 50–100 total schemas, strictly isolated into two reportable sub-datasets:
*   **Synthetic Corpus (Stage A Heritage):** 20 highly controlled synthetic schemas that isolate specific parameter permutations (used primarily to test extreme boundaries).
*   **Real-World Corpus (New for Stage B):** 30–80 schemas directly ingested from production environments.
    *   **OpenAPI Specs:** Sampled from the ToolBench dataset (e.g., subset of GitHub, Stripe, and Twilio APIs).
    *   **MCP-Style Specs:** Modern Model Context Protocol (MCP) tool schemas.
*   **Taxonomy & Metadata:** Every schema will be annotated with a rigorous taxonomy: `domain`, `parameter_count`, `nesting_depth`, `optional_field_ratio`, `enum_density`, `identifier_ambiguity_score`, `description_length`, and `token_length`.
*   **Licensing & Provenance:** Real-world schemas will strictly include original source URLs, license metadata (e.g., MIT, Apache 2.0), source hashes, and documentation of any truncations required to fit the evaluation harness.

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

## 4. Exact Model and Track Plan
To ensure fair and rigorous model evaluation, Track A and Track B will be strictly separated, and results will never be directly compared as cross-model rankings due to differing execution interfaces.

*   **Track A (Provider-Mediated native tool-calling):**
    *   `gemini-1.5-flash` (Google GenAI)
    *   `gemini-1.5-pro` (Google GenAI)
    *   `gpt-4o-mini` (OpenAI - *if zero-cost/tier allows, otherwise excluded to preserve zero-cost constraints*)
*   **Track B (Raw JSON Unconstrained):**
    *   `llama-3-70b-versatile` (via Groq)
    *   `command-r-plus-08-2024` (via Cohere)
    *   `mixtral-8x7b-32768` (via Groq)
*   **Telemetry Logs:** Every call will log exact model IDs, provider configuration, prompt hashes, timestamp, retries, output structure, token usage (where exposed by the free tier), and strict API error categories.

## 5. Statistical Analysis Plan
Stage B abandons treating repeated calls as purely independent samples, acknowledging the underlying schema as the true statistical unit.
*   **Schema-Level Analysis:** Results will be aggregated at the schema level. We will use bootstrap confidence intervals over the *schemas* (resampling schemas with replacement) to estimate the robustness of findings across different API domains.
*   **Multiple Hypothesis Correction:** Because we test multiple mutation vectors (e.g., Nested, Bloated, Ambiguous) against the Canonical baseline, we will apply the **Holm-Bonferroni correction** to all $p$-values derived from McNemar paired exact tests to strictly control the Family-Wise Error Rate (FWER).
*   **Human Validation:** A randomly selected 5% sample of the transformed schemas and their gold arguments will undergo blinded human validation to ensure mutations did not unintentionally alter the semantic meaning of the task.

## 6. Estimated Calls and Zero-Cost Feasibility
*   **Expected Matrix:** 80 schemas $\times$ 4 variants $\times$ 3 repeats $\times$ 6 models = **5,760 total API calls**.
*   **Zero-Cost Feasibility:** Highly feasible using existing infrastructure. 
    *   Gemini Free Tier allows 15 Requests Per Minute (RPM).
    *   Groq Free Tier allows 30 RPM.
    *   Cohere Free Tier permits sufficient background polling.
*   **Execution Time:** By running a rate-aware background daemon with exponential backoff (e.g., 6–10 second staggered sleeps per model track), the entire 5,760-call execution can seamlessly complete asynchronously over a 24- to 36-hour period strictly utilizing $0 API credits.

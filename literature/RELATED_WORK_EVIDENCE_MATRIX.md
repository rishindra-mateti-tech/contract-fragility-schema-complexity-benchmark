# Related Work Evidence & Benchmark Gap Matrix

**Document Role:** Systematic Literature & Benchmark Gap Analysis  
**Date (UTC):** October 12, 2026  
**Status:** EVIDENCE_MAPPING_COMPLETE  
**Governing Protocol:** Phase 3 Literature and Benchmark Gap Map  

---

## 1. Executive Comparison Matrix

The table below maps existing function calling, tool use, and structured generation benchmarks across six structural and empirical dimensions:
1. **Schema Origin**: Real-world production APIs vs. automated synthetic generation vs. scraped marketplace wrappers.
2. **Nesting Depth**: Maximum object recursion depth captured in evaluation schemas.
3. **Mutation Robustness**: Systematic stress testing under contract changes (syntactic, semantic, transport restructuring).
4. **Execution Grounding**: How tool calls are evaluated (Live endpoints, local mock engines, AST syntax match, or string match).
5. **Contamination Vulnerability**: Risk of evaluation instances leaking into model pre-training corpora.
6. **Schema Complexity Dimensions**: Explicit quantification of property counts, multi-surface partitioning (path/query/body), and union/polymorphism handling.

| Benchmark / Work | Primary Citation | Schema Origin | Max Nesting Depth | Mutation Robustness | Execution Grounding | Contamination Vulnerability | Schema Complexity Metrics Reported |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Gorilla / APIBench** | Patil et al. (NeurIPS 2024) | Scraped documentation (TorchHub, HuggingFace, TensorHub) | Depth 1 (Flat) | None | AST argument match | High (Static public dataset in web crawl) | Argument count, hallucination rate |
| **ToolBench / ToolLLM** | Qin et al. (ICLR 2024) | Scraped RapidAPI marketplace listings (16K APIs) | Depth 1–2 (Shallow) | None | Live RapidAPI execution + simulated pass | High (Scraped public web APIs) | Number of tools, tool category distribution |
| **ToolAlpaca** | Tang et al. (arXiv 2023) | 100% Synthetic (Self-Instruct LLM simulation) | Depth 1 (Flat) | None | Simulated multi-agent environment | Medium-High (Generated from GPT-3.5/4 prompts) | Tool count, instance count |
| **BFCL (Berkeley Function Calling Leaderboard)** | Yan et al. (ICML 2024 / Live) | Curated developer functions (Python, Java, REST) | Depth 1–2 | Ad-hoc (Parallel, multi-turn, irrelevance) | AST match + live execution (partial) | Medium (Continuously updated v2/v3, but static prompt sets) | Function count, language split, turn count |
| **NexusRaven-V2** | Srinivasan et al. (Nexusflow 2023) | Curated & synthetic Python docstrings | Depth 1 (Flat) | None | AST match | High (Public synthetic benchmarks) | Zero-shot call accuracy |
| **API-Bank** | Li et al. (EMNLP 2023) | Handcrafted Python tool classes (73 tools) | Depth 1 (Flat) | None | Local Python mock execution | High (Static public repository) | API count, dialogue turns |
| **RestGPT / RestBench** | Song et al. (arXiv 2023) | Real-world OpenAPI (TMDB, Spotify) | Depth 2–3 | None | Live REST API calls | Medium-High (Public OpenAPI documentation) | Multi-step path length, gold path overlap |
| **Seal-Tools** | Du et al. (arXiv 2024) | 100% Synthetic (Auto-generated tools & tasks) | Depth 1–2 | None | Simulated sandbox | High (Synthetic public dataset) | Generated tool counts, task complexity |
| **FOFO (Follow the Format)** | Xia et al. (arXiv 2024) | Synthetic formatting tasks (JSON, YAML, XML) | Depth 1–2 | Ad-hoc format perturbations | Format parsing validation | Medium (Synthetic text prompts) | Format adherence rate |
| **StructEval** | Tang et al. (arXiv 2024) | Synthetic multi-format generation (18 formats) | Depth 1–3 | None | Syntactic parser validation | Medium (Public synthetic instances) | Format accuracy, semantic correctness |
| **Guided Decoding / Outlines** | Willard & Louf (arXiv 2023) | Grammar-constrained decoding (Regex, CFG) | Arbitrary (Constrained) | None (Enforces valid token transitions) | FSA / Regex masking | N/A (Inference-time decoding engine) | Token latency, grammar compliance |

---

## 2. Dimensional Deep-Dive & Empirical Findings

### 2.1 Schema Origin: Production Fidelity vs. Synthetic Artifacts
- **Current Landscape**:
  - The majority of tool-use datasets rely on either **fully synthetic tools** generated via LLM self-instruct (e.g. ToolAlpaca, Seal-Tools) or **scraped marketplace wrappers** (e.g. ToolBench using RapidAPI).
  - RapidAPI endpoints scraped in ToolBench predominantly flatten complex parameters into generic top-level string or query parameters to fit the marketplace interface. As a consequence, models are trained and evaluated on simplified key-value forms rather than the nested, highly constrained structures required by enterprise APIs.
  - Benchmarks using real OpenAPI specifications (e.g. RestBench) are restricted to narrow domains (TMDB, Spotify) and do not preserve immutable cryptographic provenance back to frozen raw upstream sources.

### 2.2 Nesting Depth & Structural Complexity
- **Current Landscape**:
  - Across Gorilla, BFCL, API-Bank, and ToolAlpaca, the overwhelming majority of function calls operate at **Depth 1** (flat keyword arguments, e.g. `func(a=1, b="text")`).
  - Real-world production contracts (as documented in Stripe, Box, Twilio, and GitHub) regularly reach nesting depths of 3 to 5 levels, incorporating nested sub-objects, parameter structures, and arrays of objects.
  - When benchmarks encounter depth $> 2$, they typically flatten parameters into single-string concatenations or drop nested object structures, obscuring model fragility when navigating deep object hierarchies.

### 2.3 Contract Fragility & Mutation Robustness
- **Current Landscape**:
  - Existing benchmarks evaluate models exclusively against **static, immutable schemas**.
  - No current benchmark systematically evaluates **contract mutation robustness**—i.e., how model tool-calling accuracy degrades when a schema undergoes controlled syntactic changes (e.g. property renaming, requiredness shifts, enum casing adjustments) or semantic transport restructuring (e.g. wrapping path parameters vs body objects).
  - While BFCL introduces "irrelevance detection" (evaluating whether a model avoids calling an irrelevant tool), this tests tool selection rather than schema contract resilience or argument fragility.

### 2.4 Execution Grounding & Evaluation Mechanics
- **Current Landscape**:
  - Evaluation in existing benchmarks splits into three main paradigms:
    1. **AST Matching** (Gorilla, BFCL): Compares the model-generated call against a canonical Python AST. This penalizes valid alternative representations and cannot evaluate behavioral side effects.
    2. **Live API Execution** (ToolBench, RestGPT): Highly fragile over time due to external API deprecation, quota exhaustion, network latency, and required secret authentication keys.
    3. **Simulated Sandbox** (ToolAlpaca, Seal-Tools): Relies on LLM-based simulation judges, introducing self-evaluation bias and non-deterministic scoring.
  - Missing from current literature is a **hermetic, deterministic local mock execution engine** paired with standard JSON Schema validator enforcement (e.g. Draft-07 validation) that operates completely offline without live internet dependencies.

### 2.5 Contamination Vulnerability & Provenance Tracking
- **Current Landscape**:
  - As highlighted by Golchin & Surdeanu (ICLR 2024) and Sainz et al. (EACL 2024), open-source static benchmarks published on GitHub and HuggingFace suffer from rapid pre-training contamination.
  - When models are evaluated on static API documentation that exists in Common Crawl (e.g. standard GitHub or Stripe documentation), high evaluation accuracy often reflects **training memory** rather than genuine schema-following reasoning.
  - Existing benchmarks do not incorporate cryptographic blob pinning (Git blob SHA-1 and SHA-256) or programmatic schema mutations to isolate memorization from in-context contract adherence.

### 2.6 Schema Complexity Metrics & Multi-Surface Transport
- **Current Landscape**:
  - Tool-use benchmarks routinely report only aggregate counts: total number of tools, total number of categories, or average argument count.
  - They lack formal structural metrics capturing:
    - **Multi-surface partitioning**: Explicit separation and validation across `path`, `query`, `header`, and `body` transport surfaces.
    - **Union complexity**: Formal tracking of monomorphic vs. polymorphic unions (`oneOf`, `anyOf`, discriminators).
    - **Constraint density**: Number of enums, regex patterns, type assertions, and requiredness ratios per contract.

---

## 3. Objective Gap Map (Literature Boundaries)

This analysis establishes four specific, uncontested empirical boundaries in existing published benchmarks:

1. **Gap 1: Absence of Systematic Contract Mutation Stress-Testing**:
   Existing tool benchmarks assess static schema matching. None provide a formal calculus of schema mutations (syntactic perturbations, enum shifts, structural depth changes) to measure model contract fragility.

2. **Gap 2: Disconnect Between Flat Function Calling and Multi-Surface Enterprise Contracts**:
   Existing function-calling benchmarks (BFCL, Gorilla, ToolBench) prioritize flat Python-style signatures or flattened RapidAPI inputs. Real-world OpenAPI schemas with partitioned `path`, `query`, and `body` surfaces and nesting depths of 3–5 remain largely unrepresented in systematic evaluation.

3. **Gap 3: Live Flakiness vs. AST Rigidity in Execution Grounding**:
   The evaluation literature oscillates between fragile live web calls (subject to drift and rate limits) and rigid AST syntax comparison. Hermetic, reproducible, local mock executors driven by strict JSON Schema validators are absent from wide-scale tool benchmarks.

4. **Gap 4: Lack of Cryptographic Provenance & Contamination Isolation**:
   No tool benchmark currently binds its raw real-world sources to immutable cryptographic blob hashes and byte-stable audit logs while employing controlled mutations to disentangle model memorization from dynamic schema adherence.

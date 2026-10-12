# Comprehensive Benchmark Comparison Matrix

**Document Role:** Systematic Literature & Benchmark Contrast Matrix  
**Date (UTC):** October 12, 2026  
**Status:** PEER_REVIEW_READY  
**Governing Phase:** Phase 3 Benchmark Design Evidence Map  

---

## 1. Executive Protocol & Comparative Methodology

This matrix compares the **Contract Fragility & Schema Complexity Benchmark** against twelve prominent benchmarks across tool use, function calling, REST APIs, JSON Schema adherence, structured decoding, and agent execution.

For every benchmark, this matrix defines:
1. **Target of External Measurement**: The concrete empirical tasks, metrics, and ground-truth mechanisms of the external work.
2. **Distinctive Target of Our Project**: The specific structural, mutation, transport, or grounding divergence in our benchmark design.
3. **Distinction Status**: Classified strictly as **`CONFIRMED`**, **`UNCERTAIN`**, or **`CONTRADICTED`**.
4. **Primary Citation & Repository**: Immutable link to original archival publication and official repository.
5. **Safe Wording for Paper Claims**: Approved, precise academic phrasing for eventual paper manuscripts.
6. **Prohibited Exaggerated Wording**: Banned marketing rhetoric, puffed claims, and unproven superlatives.

---

## 2. Systematic Benchmark Comparison Matrix

### 1. Gorilla / APIBench (NeurIPS 2024)
- **What External Work Measures**: Accuracy of generating Python API calls for ML model hubs (TorchHub, HuggingFace, TensorHub) in response to natural language prompts. Evaluates argument hallucination rate and AST parameter matching against static documentation.
- **What Our Project Measures Differently**: Systematic contract fragility under programmatic schema mutations (renaming, type loosening, requiredness shifting); multi-surface HTTP transport partitioning (`path`, `query`, `header`, `body`); recursion depth scaling ($1 \le d \le 5$); and offline mock execution against real-world enterprise OpenAPI specs (Stripe, GitHub, Box, Twilio).
- **Distinction Status**: **`CONFIRMED`** (APIBench schemas are flat single-layer Python signatures; it contains zero schema mutation calculus and zero HTTP transport surface partitioning).
- **Exact Citation & Source**: Patil et al., NeurIPS 2024, arXiv:2305.15334. Repository: [https://github.com/ShishirPatil/gorilla](https://github.com/ShishirPatil/gorilla).
- **Safe Wording**: *"Whereas APIBench assesses model hallucination in flat Python library calls under static documentation, our benchmark investigates contract fragility across multi-surface HTTP schemas subjected to controlled structural mutations."*
- **Prohibited Exaggerated Wording**: *"Our benchmark makes Gorilla obsolete"*; *"Gorilla fails completely on real APIs"*; *"We solve the problems Gorilla ignored"*.

---

### 2. ToolBench / ToolLLM (ICLR 2024)
- **What External Work Measures**: Multi-step tool retrieval, planning, and execution across 16,464 RapidAPI marketplace endpoints. Evaluates win rate and pass rate via simulated LLM judges or live RapidAPI proxy calls.
- **What Our Project Measures Differently**: Deep structural schema adherence and contract sensitivity. ToolBench schemas crawled from RapidAPI flatten parameters into generic key-value dictionaries. Our project maintains frozen cryptographic byte provenance, enforces strict single-column transport fidelity, preserves finite object unions without heuristic degradation, and evaluates robustness under controlled schema perturbations.
- **Distinction Status**: **`CONFIRMED`** (ToolBench prioritizes massive tool count breadth over structural schema depth, parameter typing rigor, or contract mutation testing).
- **Exact Citation & Source**: Qin et al., ICLR 2024 (Spotlight), arXiv:2307.16789. Repository: [https://github.com/OpenBMB/ToolBench](https://github.com/OpenBMB/ToolBench).
- **Safe Wording**: *"While ToolBench scales evaluation breadth across thousands of flattened RapidAPI listings, our work isolates structural depth, typing complexity, and contract mutation fragility across cryptographically pinned enterprise schemas."*
- **Prohibited Exaggerated Wording**: *"ToolBench data is invalid/worthless"*; *"We provide the first real tool benchmark"*; *"Our approach is infinitely more rigorous"*.

---

### 3. Berkeley Function Calling Leaderboard - BFCL (ICML 2024 / Live)
- **What External Work Measures**: Real-world function-calling accuracy across Python, Java, JavaScript, and REST functions. Evaluates single-turn, multi-turn, parallel, and irrelevant tool calls using Abstract Syntax Tree (AST) argument comparison.
- **What Our Project Measures Differently**: Fragility under upstream schema evolution and mutation; multi-surface transport partitioning (`path`, `query`, `header`, `body`); and hermetic local state-machine mock execution. BFCL tests whether a model calls the correct function from a static catalog; our benchmark tests whether the model's contract adherence collapses when the schema's syntactic or transport structure shifts.
- **Distinction Status**: **`CONFIRMED`** (BFCL uses static function definitions and does not perform controlled schema mutations or evaluate transport partitioning).
- **Exact Citation & Source**: Yan et al., ICML 2024 Workshop, [gorilla.cs.berkeley.edu](https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html). Repository: [https://github.com/ShishirPatil/gorilla](https://github.com/ShishirPatil/gorilla).
- **Safe Wording**: *"BFCL establishes a prominent leaderboard for static function routing and AST argument matching; our benchmark complements this by measuring sensitivity to schema structural variations, deep nesting, and transport restructuring."*
- **Prohibited Exaggerated Wording**: *"BFCL is flawed"*; *"We replace BFCL with superior testing"*; *"Our benchmark is better than Berkeley's"*.

---

### 4. ToolAlpaca (arXiv 2023)
- **What External Work Measures**: Generalization of language models to unseen tools using 3,000 simulated multi-agent interaction cases across 400 automatically generated synthetic tools.
- **What Our Project Measures Differently**: Real-world enterprise schema fidelity and structural depth. ToolAlpaca relies 100% on synthetic tools generated via Self-Instruct, which produce shallow, flat schemas lacking production typing constraints. Our benchmark evaluates a balanced dual-cohort of 30 cryptographically pinned real enterprise operations and 20 controlled synthetic schemas.
- **Distinction Status**: **`CONFIRMED`** (ToolAlpaca tools are entirely LLM-generated simulations; our project grounds evaluation in frozen production OpenAPI specs from major software ecosystems).
- **Exact Citation & Source**: Tang et al., arXiv:2306.05301. Repository: [https://github.com/tangqiaoyu/ToolAlpaca](https://github.com/tangqiaoyu/ToolAlpaca).
- **Safe Wording**: *"Unlike ToolAlpaca's fully synthetic multi-agent simulation corpus, our benchmark couples cryptographically pinned real-world enterprise specifications with synthetic controls to assess real-to-synthetic transferability."*
- **Prohibited Exaggerated Wording**: *"Synthetic tools are useless"*; *"ToolAlpaca is completely unrealistic"*; *"Only our benchmark uses real data"*.

---

### 5. API-Bank (EMNLP 2023)
- **What External Work Measures**: Three-level capability of tool-augmented LLMs: API call planning, API retrieval, and API call generation across 73 manually written Python tool classes in multi-turn dialogues.
- **What Our Project Measures Differently**: Schema complexity at scale (nesting depth 1–5, property counts 5–45), standard JSON Schema Draft-07 validation, and contract mutation robustness. API-Bank's 73 tools are handcrafted Python methods with flat docstrings; our benchmark tests production OpenAPI 3.0/3.1 transport specifications.
- **Distinction Status**: **`CONFIRMED`** (API-Bank uses a small catalog of 73 handcrafted tools without OpenAPI transport partitioning or schema mutation operators).
- **Exact Citation & Source**: Li et al., EMNLP 2023, pages 3102–3116, arXiv:2304.08244. Repository: [https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/api-bank](https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/api-bank).
- **Safe Wording**: *"API-Bank pioneers multi-turn dialogue planning with handcrafted Python tool wrappers; our benchmark focuses on structural contract adherence under complex OpenAPI schemas and syntactic perturbations."*
- **Prohibited Exaggerated Wording**: *"API-Bank is too small to be useful"*; *"Handcrafted tools have zero value"*.

---

### 6. RestGPT / RestBench (arXiv 2023)
- **What External Work Measures**: Multi-step RESTful API task decomposition, coarse-to-fine planning, and live API execution across two real OpenAPI specifications (TMDB and Spotify).
- **What Our Project Measures Differently**: Scope (10 enterprise source clusters across 1,361 candidate operations vs. 2 API specs); systematic schema mutation testing; cryptographic source immutability; and hermetic local mock grounding that avoids live endpoint rate limits, account credentials, and network flakiness.
- **Distinction Status**: **`CONFIRMED`** (RestBench is restricted to 2 live consumer media APIs and does not include mutation testing or multi-cluster breadth).
- **Exact Citation & Source**: Song et al., arXiv:2306.06624. Repository: [https://github.com/Yifan-Song793/RestGPT](https://github.com/Yifan-Song793/RestGPT).
- **Safe Wording**: *"RestBench demonstrated LLM planning over live TMDB and Spotify APIs; our benchmark expands real-source diversity across 10 enterprise domains while introducing offline mock grounding and systematic contract fragility analysis."*
- **Prohibited Exaggerated Wording**: *"RestGPT cannot handle real APIs"*; *"Live API benchmarks are fundamentally broken"*.

---

### 7. NexusRaven / NexusRaven-V2 (2023)
- **What External Work Measures**: Zero-shot function calling accuracy of a specialized 13B open-source model against OpenAI GPT-4 on curated function call prompts with Python docstring interfaces.
- **What Our Project Measures Differently**: Structural schema depth, OpenAPI transport modeling, and contract sensitivity. NexusRaven evaluates static Python docstrings; our benchmark tests model argument formulation under OpenAPI JSON Schema contracts, testing both monomorphic and faithful polymorphic object unions.
- **Distinction Status**: **`CONFIRMED`** (NexusRaven is a model release and evaluation against static docstring benchmarks, without schema complexity scaling or mutation operators).
- **Exact Citation & Source**: Srinivasan et al., Nexusflow Technical Report 2023, [nexusflow.ai/blogs/ravenv2](https://nexusflow.ai/blogs/ravenv2). Repository: [https://github.com/nexusflowai/NexusRaven-V2](https://github.com/nexusflowai/NexusRaven-V2).
- **Safe Wording**: *"NexusRaven establishes that instruction-tuned models can match proprietary function-calling accuracy on Python signatures; our benchmark evaluates how such models respond to deep enterprise schemas and structural contract mutations."*
- **Prohibited Exaggerated Wording**: *"NexusRaven only works on trivial functions"*; *"Docstrings are inadequate for evaluation"*.

---

### 8. Seal-Tools (arXiv 2024)
- **What External Work Measures**: Self-instruct tool learning via automatically generated tools, tasks, and simulated execution environments, focusing on training data generation.
- **What Our Project Measures Differently**: Evaluates production contract fidelity rather than synthetic tool synthesis. Seal-Tools uses synthetic generators to maximize data scale; our benchmark uses immutable real enterprise contracts to uncover authentic production failure modes.
- **Distinction Status**: **`CONFIRMED`** (Seal-Tools is a synthetic training synthesis framework; our work is an empirical evaluation benchmark grounded in frozen real specs).
- **Exact Citation & Source**: Du et al., arXiv:2405.08355. Repository: [https://github.com/OpenBMB/Seal-Tools](https://github.com/OpenBMB/Seal-Tools).
- **Safe Wording**: *"While Seal-Tools generates scalable synthetic data for tool learning, our benchmark provides an empirical testbed grounded in cryptographically verified production APIs to evaluate real-world transferability."*
- **Prohibited Exaggerated Wording**: *"Self-instruct tools produce fake data"*; *"Seal-Tools lacks rigor"*.

---

### 9. FOFO: Follow the Format (arXiv 2024)
- **What External Work Measures**: Ability of LLMs to follow formatting instructions across diverse textual formats (JSON, YAML, XML, markdown tables, shell commands). Evaluates syntactic validity using format parsers.
- **What Our Project Measures Differently**: Domain-specific API tool calling contracts. FOFO evaluates general text formatting; our benchmark specifically isolates HTTP transport contracts, parameter requiredness, schema typing constraints, nesting depth ($1 \le d \le 5$), and semantic mutation drift in tool execution.
- **Distinction Status**: **`CONFIRMED`** (FOFO tests generic text formatting; our benchmark evaluates API tool argument formulation under formal JSON Schema constraints).
- **Exact Citation & Source**: Xia et al., arXiv:2402.18667.
- **Safe Wording**: *"FOFO evaluates format-following across broad surface representations; our work isolates the specific structured interface constraints of API tool calling, measuring parameter formulation accuracy under varying schema depth and mutations."*
- **Prohibited Exaggerated Wording**: *"FOFO is too simple"*; *"Formatting benchmarks do not test intelligence"*.

---

### 10. StructEval (arXiv 2024)
- **What External Work Measures**: Comprehensive format-following capability across 18 structured formats and 44 task types, covering generation, transformation, and extraction.
- **What Our Project Measures Differently**: Evaluates functional tool invocation and downstream execution side effects, rather than standalone format generation. Our project couples structured JSON Schema Draft-07 validation with deterministic mock state execution and measures degradation curves under controlled schema mutations.
- **Distinction Status**: **`CONFIRMED`** (StructEval benchmarks format syntax across task categories; our benchmark benchmarks tool calling contract fragility and mock execution grounding).
- **Exact Citation & Source**: Tang et al., arXiv:2410.08815.
- **Safe Wording**: *"StructEval provides an extensive taxonomy of format generation tasks; our benchmark specifically examines tool-calling contract adherence and execution side-effects under mutating API contracts."*
- **Prohibited Exaggerated Wording**: *"StructEval misses the point of tools"*; *"Our schema benchmark is more realistic than StructEval"*.

---

### 11. Guided Decoding / Outlines (arXiv 2023)
- **What External Work Measures**: Inference-time token masking using finite-state machines (FSMs) derived from regular expressions or context-free grammars (CFGs), guaranteeing syntactic validity of generated tokens.
- **What Our Project Measures Differently**: Guided decoding guarantees *syntactic* validity of tokens against a fixed grammar at generation time. Our benchmark measures *semantic* argument correctness, parameter selection, and contract fragility when schemas change. Furthermore, guided decoding does not prevent semantic hallucinations (e.g. providing an invalid UUID or mathematically incorrect amount) within syntactically valid fields.
- **Distinction Status**: **`CONFIRMED`** (Guided decoding is an inference-time decoding constraint algorithm, not a benchmark of contract fragility or semantic tool execution).
- **Exact Citation & Source**: Willard & Louf, arXiv:2307.09702. Repository: [https://github.com/dottxt-ai/outlines](https://github.com/dottxt-ai/outlines).
- **Safe Wording**: *"Constrained decoding frameworks such as Outlines ensure syntactic validity by construction; our benchmark evaluates semantic adherence and measures contract fragility when upstream schemas mutate, highlighting failure modes that constrained decoding cannot resolve."*
- **Prohibited Exaggerated Wording**: *"Constrained decoding fails on schemas"*; *"Outlines is insufficient for production"*.

---

### 12. SWE-bench & AgentBench (ICLR 2024)
- **What External Work Measures**: End-to-end multi-turn autonomous software engineering (SWE-bench: resolving real GitHub issues via git patch generation evaluated by unit test execution) and multi-environment agent reasoning (AgentBench: OS, DB, Web, Knowledge).
- **What Our Project Measures Differently**: Unit-level tool calling contract adherence vs. macro-level repository problem solving. SWE-bench evaluates whether an agent can fix complex codebases over multi-hour turns with dozens of shell interactions. Our benchmark provides a fine-grained, controlled laboratory instrument to isolate why and how individual tool calls fail when API schemas exhibit structural complexity or contract drift.
- **Distinction Status**: **`CONFIRMED`** (SWE-bench and AgentBench are macro-level agent benchmarks; our project is a micro-level contract adherence and schema complexity benchmark).
- **Exact Citation & Source**: Jimenez et al., ICLR 2024, arXiv:2310.06770 (SWE-bench); Liu et al., ICLR 2024, arXiv:2308.03688 (AgentBench).
- **Safe Wording**: *"While macro-benchmarks like SWE-bench measure end-to-end autonomous problem solving across complex repositories, our benchmark isolates the specific micro-level failure modes of tool parameter formulation and schema contract adherence under structural mutations."*
- **Prohibited Exaggerated Wording**: *"SWE-bench is uninterpretable"*; *"Our benchmark is better than SWE-bench for evaluating agents"*.

---

## 3. Summary of Confirmed Differentiators

Across all twelve comparative benchmarks, our benchmark's confirmed empirical differentiators are:

| Differentiator | Current Literature Status | Our Project's Position | Confirmation Status |
| :--- | :--- | :--- | :---: |
| **Systematic Schema Mutation Calculus** | Non-existent in tool benchmarks; models evaluated solely on static schemas. | Introduces formal syntactic and semantic mutation operators to test contract fragility. | **CONFIRMED** |
| **Multi-Surface Transport Partitioning** | Parameters predominantly flattened into single dictionaries or flat Python args. | Enforces strict uniform nesting: `path`, `query`, `header`, `body`. | **CONFIRMED** |
| **Bounded Deep Nesting ($1 \le d \le 5$)** | Bounded at depth 1–2; deeper objects pruned or flattened. | Evaluates full production depth up to 5 levels across enterprise OpenAPI specs. | **CONFIRMED** |
| **Cryptographic Provenance Immutability** | Datasets distributed as static JSONs without Git blob SHA binding. | Pinned Git blob SHAs and byte-stable read-only audit reports. | **CONFIRMED** |
| **Hermetic Offline Mock Grounding** | Either fragile live API calls or rigid AST parsing. | Offline stateful mock execution verifying business invariants without network calls. | **CONFIRMED** |
| **Finite Faithful Union Handling** | Object unions pruned to untyped objects or omitted entirely. | Preserves finite `anyOf`/`oneOf` variant schemas without heuristic degradation. | **CONFIRMED** |

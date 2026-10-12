# Novelty Claim Boundaries & Defensible Scope Specification

**Document Role:** Academic Novelty Boundaries and Defensible Scope Statement  
**Date (UTC):** October 12, 2026  
**Status:** DRAFT_INTERNAL_CLAIM_BOUNDARIES — evidence audit pending  
**Governing Phase:** Phase 3 Benchmark Design Evidence Map  
**Companion Evidence Ledger:** [CLAIM_EVIDENCE_LEDGER.md](file:///c:/Users/rishi/OneDrive/Desktop/Education/contract-fragility-schema-complexity-benchmark/CLAIM_EVIDENCE_LEDGER.md)

---

## 1. Executive Protocol & Scientific Humility

Scientific credibility in empirical machine learning requires precise demarcation of what a benchmark measures, what it demonstrates, and—crucially—what it does **not** claim. Overclaiming novelty, asserting supremacy over prior benchmarks, or using vague marketing superlatives damages peer-review standing and obscures legitimate scientific contributions.

This document establishes internal working boundaries for all publications, manuscripts, release notes, and documentation derived from the **Contract Fragility & Schema Complexity Benchmark**. 

Every contributor and co-author must adhere strictly to these boundaries. Any manuscript draft or presentation that violates these guidelines will be rejected at internal review prior to submission.

---

## 2. Hypothesized Differentiated Empirical Signal Dimensions

Our benchmark explores five specific dimensions of experimental focus relative to existing tool-use literature:

### Dimension 1: Systematic Schema Mutation Calculus
- **Hypothesized Focus:** This work investigates a deterministic schema mutation calculus that subjects API contracts to controlled structural perturbations (e.g., parameter renaming, requiredness loosening/tightening, type widening, and field reordering).
- **Scientific Rationale:** Seeks to measure the degradation curve (contract fragility) of LLM tool invocation under upstream API schema drift, separating memorized API usage from dynamic schema comprehension.
- **Literature Context:** Published tool benchmarks (Gorilla, ToolBench, BFCL) predominantly evaluate models on static, unperturbed function definitions.

### Dimension 2: Bounded Enterprise OpenAPI Depth & Multi-Surface Transport Partitioning
- **Hypothesized Focus:** We evaluate a uniform four-surface transport wrapper (`path`, `query`, `header`, `body`) across enterprise OpenAPI 3.0/3.1 specifications and examine structured parameter nesting bounded at recursion depth $d \le 5$.
- **Scientific Rationale:** Explores how models handle realistic HTTP transport semantics and nested object structures, contrasting flat function-call representations with production-grade enterprise interfaces.
- **Literature Context:** Prior tool datasets predominantly flatten parameters into single key-value dictionaries or flat argument lists, leaving transport surface distinctions largely unpartitioned.

### Dimension 3: Finite Faithful Object Union Preservation
- **Hypothesized Focus:** Under Amendment 003, we explore preserving finite object-level polymorphism (`anyOf` / `oneOf` unions) where variants can be evaluated without heuristic pruning or lossy flattening.
- **Scientific Rationale:** Evaluates whether models can discern and formulate variant-specific object arguments according to discriminant properties or variant schemas in enterprise contracts.
- **Literature Context:** Published benchmarks often either prune polymorphic unions to unconstrained `object` types or omit polymorphic endpoints from evaluation.

### Dimension 4: Cryptographic Provenance Immutability & Reproducibility
- **Methodological Standard:** All raw OpenAPI specifications and source files are pinned to immutable Git blob SHAs and raw source file SHA-256 hashes, paired with deterministic, byte-stable read-only audit tools.
- **Scientific Value:** Aims to mitigate dataset drift, undocumented scraper churn, and silent spec modifications that can affect live web-crawled tool corpora.
- **Literature Context:** Web-crawled collections (such as RapidAPI dumps) can exhibit shifting upstream endpoints, undocumented deprecations, and unpinned snapshots.

### Dimension 5: Planned Offline Hermetic Mock Execution
- **Planned Stage B Capability:** Tool invocations are intended to be validated against deterministic, offline, stateful mock executors verifying schema constraints, required invariants, and state transitions without outbound network calls.
- **Scientific Value:** Intended to provide reproducible execution environments unaffected by rate limits, API key authentication failures, billing caps, or network latency.
- **Status Clarification:** Hermetic offline mock execution is a **planned Stage B capability**, currently in protocol and test planning; it is not yet an implemented or validated execution runtime.

---

## 3. Explicit Boundaries of Non-Novelty (What We Do NOT Claim)

To prevent unscientific inflation, the following negative assertions are formally binding across all project communications:

### 1. We Do NOT Claim to Be the "First" Tool Use or Function Calling Benchmark
- **Prior Art Acknowledgment:** Tool-augmented LLM evaluation was pioneered by Gorilla / APIBench (Patil et al., 2023), ToolBench (Qin et al., 2023), API-Bank (Li et al., 2023), ToolAlpaca (Tang et al., 2023), and the Berkeley Function Calling Leaderboard (Yan et al., 2024).
- **Prohibited Claim:** *"We propose the first benchmark for evaluating LLM tool calling capabilities."*
- **Accurate Framing:** *"We propose a benchmark specifically targeting contract fragility and schema structural complexity under controlled mutations, addressing a dimension less explored in static tool evaluation literature."*

### 2. We Do NOT Claim the "Largest" or "Most Comprehensive" API Catalog
- **Prior Art Acknowledgment:** ToolBench evaluates over 16,000 RapidAPI endpoints; Gorilla evaluates thousands of ML model hub APIs.
- **Prohibited Claim:** *"Our benchmark is the most comprehensive API dataset ever created."*
- **Accurate Framing:** *"Our benchmark adopts a target design of a bounded cohort (targeting 30 cryptographically pinned enterprise operations and 20 controlled synthetic schemas) to permit exhaustive structural validation and deterministic mock grounding."*

### 3. We Do NOT Claim to Evaluate General Autonomous Agent Reasoning
- **Prior Art Acknowledgment:** Multi-step autonomous agent reasoning, interactive task planning, and environment feedback are the domain of macro-benchmarks such as SWE-bench (Jimenez et al., 2024), AgentBench (Liu et al., 2024), and WebArena (Zhou et al., 2023).
- **Prohibited Claim:** *"Our benchmark proves whether an AI model can act as a fully autonomous software engineering agent."*
- **Accurate Framing:** *"Our benchmark isolates the unit-level capability of tool calling contract adherence under schema complexity, providing complementary micro-level diagnostic signal for agent architectures."*

### 4. We Do NOT Claim to Eliminate Training Data Contamination
- **Prior Art Acknowledgment:** Major enterprise APIs (Stripe, GitHub, Box, Twilio) are publicly documented and present in web crawl corpora used to pre-train leading foundation models.
- **Prohibited Claim:** *"Our benchmark is 100% contamination-free because models cannot have seen our tests."*
- **Accurate Framing:** *"While base enterprise schemas are likely represented in pre-training corpora, our systematic mutation calculus tests whether models rely on pre-trained memorization or dynamically adhere to perturbed interface contracts."*

### 5. We Do NOT Claim Full HTTP Network or Transport Emulation
- **Prior Art Acknowledgment:** Real-world API integration involves TLS handshakes, streaming responses, chunked transfer encoding, socket timeouts, and complex header negotiation.
- **Prohibited Claim:** *"Our benchmark provides an end-to-end simulation of real-world internet networking."*
- **Accurate Framing:** *"Our benchmark isolates the structural transport contract (partitioning inputs into `path`, `query`, `header`, and `body` schemas) to evaluate structured parameter formulation without introducing network-level flakiness."*

---

## 4. Phrasing Governance: Safe vs. Prohibited Language

| Section | Prohibited Wording (Banned) | Approved Safe Wording |
| :--- | :--- | :--- |
| **Abstract** | *"We introduce a revolutionary benchmark that solves the fundamental flaws of existing tool benchmarks."* | *"We present a benchmark designed to evaluate LLM tool contract fragility and adherence under varying schema complexity and programmatic mutations."* |
| **Abstract** | *"Current benchmarks like BFCL and ToolBench are unrealistic and fail to measure real performance."* | *"While prominent benchmarks evaluate static tool selection and argument generation, contract fragility under structural schema changes remains less explored."* |
| **Introduction** | *"Our benchmark makes Gorilla and ToolBench obsolete by providing real enterprise APIs."* | *"Complementing prior work focused on tool catalog scale (ToolBench) or library routing (Gorilla), this work investigates deep schema nesting and mutation sensitivity."* |
| **Related Work** | *"Previous benchmarks rely on flawed, trivial synthetic tools that have zero practical relevance."* | *"Prior benchmarks primarily study flat parameter signatures; in contrast, enterprise OpenAPI contracts feature deep nesting, transport partitioning, and polymorphic types."* |
| **Results** | *"We prove that all leading LLMs are fundamentally incompetent at tool use."* | *"Initial synthetic results suggest that model argument accuracy degrades as schema nesting depth increases and under field renaming mutations."* |
| **Conclusion** | *"Our benchmark establishes the definitive gold standard for all future agent research."* | *"Our benchmark provides a controlled diagnostic instrument for measuring contract adherence and fragility in tool-augmented models."* |

---

## 5. Peer-Review Defense Protocol

When addressing reviewer questions regarding novelty and relationship to prior art, use the following defense frameworks:

### Defense Case 1: "Why another tool benchmark when BFCL exists?"
- **Response Framework:** Acknowledge BFCL as a cornerstone for static function calling accuracy and AST matching. Clarify that BFCL does not measure contract fragility under upstream schema evolution, does not partition multi-surface HTTP transport, and does not systematically evaluate deep JSON Schema nesting up to recursion depth 5. Our benchmark serves as a stress-testing complement, not a replacement.

### Defense Case 2: "Why 50 operations instead of 10,000 like ToolBench?"
- **Response Framework:** Acknowledge the breadth value of ToolBench. Explain that ToolBench's scale requires flattening parameters and relying on unverified RapidAPI endpoints or LLM judges. In contrast, our cohort target size permits 100% cryptographic source pinning, exhaustive Draft-07 validator verification, full union preservation without heuristics, and planned stateful offline mock execution.

### Defense Case 3: "Isn't schema mutation testing artificial?"
- **Response Framework:** Demonstrate that API contract changes (deprecation, field renaming, requiredness tightening, version drift) are pervasive in software engineering. Programmatic mutation calculus provides a controlled, reproducible method to measure whether models exhibit fragile prompt-memorization or robust contract parsing.

---

## 6. Document Sign-Off & Verification

This specification is an internal working draft subject to empirical verification.

- **Status:** `DRAFT_INTERNAL_CLAIM_BOUNDARIES — evidence audit pending`
- **Literature Alignment:** Verified against claims in `CLAIM_EVIDENCE_LEDGER.md`.

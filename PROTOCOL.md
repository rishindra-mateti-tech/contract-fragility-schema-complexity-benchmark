# Preregistered Experimental Protocol: Contract Fragility & Schema Repair

**Document Status:** FROZEN (Pre-Execution)  
**Date:** October 2026  

## 1. Experimental Objectives and Hypotheses
This study shifts from demonstrating general fragility to predictive modeling and automated repair of LLM tool-calling contracts.

*   **Hypothesis 1 (Predictive Fragility):** Measurable JSON Schema parameters—specifically maximum nesting depth, optionality density, and identifier string distance—inversely predict semantic tool-call exact match rates, even when syntactic generation remains 100% valid.
*   **Hypothesis 2 (Automated Repair):** Automated schema transformations (flattening nested structures, grouping/stripping optional bloat, and disambiguating identifiers) significantly increase semantic exact match rates compared to the fragile baseline, without altering the underlying execution logic.

## 2. Experimental Conditions and Schema Mutations
The benchmark isolates specific structural properties using 4 controlled conditions per base schema:
1.  **Canonical:** The baseline schema following standard REST/MCP practices.
2.  **Nested Hierarchy:** Encapsulating root parameters into 3-level deep sub-objects.
3.  **Optionality Bloat:** Injecting 15 highly distracting, overlapping enterprise metadata fields (e.g., `tags`, `correlation_id`).
4.  **Ambiguous Identifiers:** Obfuscating tool names/parameters and removing docstrings to simulate poor enterprise naming conventions.

## 3. Model Configurations
To ensure reproducible, deterministic evaluation across different inference engines, the following parameters are strictly locked:
*   **Temperature:** `0.0` (greedy decoding for maximum determinism).
*   **Models:** 
    *   *Provider-Mediated:* `gemini-3.1-flash-lite-preview` (via Google API)
    *   *Open-Weights:* `meta-llama-3.3-70b-instruct` (via SambaNova/Groq APIs)
*   **System Prompts:** Native defaults; no custom framework-level injections beyond the schema payload.

## 4. Execution Parameters & Exclusion Rules
To adapt to free-tier constraints while preserving scientific integrity:
*   **Retry Logic:** Exponential backoff (starting at 6s) up to 4 maximum retries for HTTP 429 (Too Many Requests) or 503 (Service Unavailable).
*   **Exclusion Rule (Availability vs Capability):** Any call that exhausts retries with an infrastructure error (400, 429, 404, 503) is logged as an *Availability Failure* and is **strictly excluded** from the capability denominator. Capability metrics (Syntax, Selection, Semantics) are calculated solely over successfully terminated HTTP requests.
*   **Data Integrity:** Every run generates a unique `run_manifest.json` recording the Git commit SHA, timestamp, prompt hashes, and exact model string to prevent commingling of data.

## 5. Phased Execution Plan
*   **Stage A (Pilot):** 8 base schemas $\times$ 4 variants $\times$ 3 models $\times$ 1 repeat. Used to validate the protocol and pipeline stability without burning quota.
*   **Stage B (Repair & Holdout Verification):** If Stage A confirms the degradation effect, Stage B will introduce the `SchemaFragilityLinter` repair module, evaluating the canonical vs. repaired schemas across the full 20-schema dataset plus 3 real-world MCP/OpenAPI holdout schemas.

## 6. Planned Statistical Tests
*   **Paired Differences:** McNemar's exact test will evaluate differences in Boolean success rates (e.g., Syntax Pass/Fail, Semantic Exact Match Pass/Fail) between paired schema conditions (Canonical vs. Variant, Fragile vs. Repaired).
*   **Confidence Intervals:** Wilson score intervals will be reported for all single proportion metrics.
*   **Disclaimer:** All claims of fragility or repair efficacy apply strictly to the schema architectures and models tested in this protocol.

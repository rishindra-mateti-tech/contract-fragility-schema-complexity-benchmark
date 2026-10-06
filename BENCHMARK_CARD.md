# Contract Fragility Benchmark Card

## 1. Model Details
**Name:** Contract Fragility: Schema Complexity Benchmark
**Version:** 1.0 (Active Protocol)
**Type:** Empirical Evaluation Protocol & Synthetic Dataset
**License:** Apache 2.0

## 2. Intended Use
**Primary Use Cases:**
- Evaluating the robustness of Large Language Models (LLMs) to structural variations in JSON Schema tool contracts.
- Isolating specific failure modes (e.g., parameter omission, hallucination) caused by object nesting, optionality bloat, and identifier ambiguity.
- Comparing provider-mediated tool calling architectures (e.g., Gemini Function Calling vs. raw JSON schema generation) on equal footing.

**Non-Intended Use Cases:**
- This benchmark is **not** intended to evaluate general domain knowledge or reasoning capabilities of LLMs.
- It is **not** a ranking leaderboard for overall API capabilities; it specifically measures degradation under structural stress.

## 3. Data & Provenance
**Synthetic Nature:** 
The primary evaluation corpus consists of 20 synthetic, API-inspired schemas (e.g., Cloud, CRM, Fintech). These schemas are deliberately constructed to mirror the complexity of real-world REST and MCP contracts without exposing models to operational security risks, live PII, or destructive endpoint mutations.

**Real API Baseline:**
A small secondary baseline (`data/real_api_baseline.json`) containing real-world API schemas (e.g., Stripe, GitHub) is provided to validate that findings from the synthetic corpus generalize to actual production contracts.

## 4. Limitations & Risks
- **Synthetic Distribution Shift:** Because the schemas are synthetic, models that heavily memorize public OpenAPI specifications (like Stripe's or GitHub's real specs) might perform differently on this benchmark than they would in the wild.
- **Provider-Mediated Interference:** When evaluating through proprietary APIs (e.g., OpenAI, Anthropic, Google), the vendor's intermediate parsing layers, grammar masks, and system prompt injections mask the raw attention mechanism of the model. 
- **Cost & Rate Limiting:** Executing the full multi-provider sweep requires significant API quota.

## 5. Evaluation Regimes
This benchmark uniquely decouples evaluation into two distinct regimes to ensure fairness:
- **Regime A (Provider-Mediated):** Evaluates models via their native, first-class function-calling endpoints.
- **Regime B (Raw Unconstrained):** Evaluates models by injecting raw JSON Schema Draft-07 directly into the system prompt and expecting raw JSON text completion, bypassing vendor middleware.

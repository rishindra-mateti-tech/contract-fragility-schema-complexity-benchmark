# Benchmark Telemetry & Evaluation Protocol

This directory contains execution telemetry, statistical summaries, human evaluation audit records, and publication-ready LaTeX tables produced by the Contract Fragility benchmark harness.

---

## 1. Directory Structure

```
results/
├── raw_benchmark_results.json       # Granular per-call telemetry (timestamps, prompts, retry counts, latencies, tokens)
├── summary_metrics.json             # Aggregated Wilson 95% CIs, McNemar paired tests, and availability rates
├── human_evaluation_audit.json      # Ground-truth fulfillability and argument hallucination audit logs
├── tables/                          # Automated publication-ready LaTeX tables
│   ├── table1_syntactic_pass.tex
│   ├── table2_tool_selection.tex
│   └── table3_execution_semantics.tex
└── README.md                        # Telemetry manifest and experimental disclosures
```

---

## 2. Telemetry Schema & Granular Fields

Every executed call in `raw_benchmark_results.json` records granular, auditable parameters:

| Field | Type | Description |
| :--- | :--- | :--- |
| `timestamp` | String | ISO execution timestamp (`YYYY-MM-DD HH:MM:SS`) |
| `model` | String | Target model identifier (e.g., `gemini-3.1-flash-lite-preview`) |
| `base_id` | String | Unique synthetic base schema identifier (e.g., `stripe_create_refund`) |
| `mutation_type` | String | Experimental condition (`canonical`, `nested_hierarchy`, `optionality_bloat`, `ambiguous_identifiers`) |
| `prompt` | String | Frozen user query text providing task requirements |
| `retry_count` | Integer | Number of exponential backoff retry attempts triggered by 429/503 |
| `infrastructure_error` | Boolean | Whether an upstream HTTP network/quota error occurred |
| `tool_called` | Boolean | Whether the model produced a structured function call |
| `syntax_valid` | Boolean | Whether arguments strictly validate against JSON Schema Draft-07 |
| `error_category` | String | Machine-readable failure category (`MISSING_REQUIRED_FIELD`, `TYPE_MISMATCH`, etc.) |
| `latency` | Float | End-to-end request latency in seconds |
| `prompt_tokens` | Integer | Prompt token count measured via vendor usage metadata |
| `completion_tokens` | Integer | Completion token count measured via vendor usage metadata |
| `generated_args` | Object | Full payload dictionary emitted by the model |
| `expected_args` | Object | Ground-truth argument dictionary |

---

## 3. Reproduction Commands

To explicitly reproduce the current committed results (and scale the experiment), use the following documented commands:

**Smoke Test (Current Committed Data):**
```bash
python -u src/benchmark_runner.py --model gemini-3.1-flash-lite-preview --max-suites 1 --delay 4.0
python src/stats_analyzer.py
python src/human_eval_auditor.py --interactive
```

**Full Benchmark Sweep (Planned):**
```bash
# Regime A (Provider-Mediated):
python -u src/benchmark_runner.py --model gemini-3.1-flash-lite-preview --max-suites 20 --delay 4.0

# Regime B (Raw Unconstrained) - Planned implementation:
python -u src/benchmark_runner.py --model gemini-3.1-flash-lite-preview --max-suites 20 --delay 4.0 --raw-mode
```

---

## 4. Pipeline Smoke Test Disclosure

> [!IMPORTANT]
> **Status: Pipeline Verification / Smoke Test Only**  
> The baseline records currently committed in `raw_benchmark_results.json` and `summary_metrics.json` reflect an initial single-suite pipeline smoke test ($N = 1$ suite, 6 API calls on `gemini-3.1-flash-lite-preview`).
>
> While all conditions in this smoke test passed syntactic and semantic validation, the resulting 95% Wilson score confidence intervals are wide ($[20.7\%, 100.0\%]$) and McNemar tests yield $p = 1.0$ due to lack of discordant pairs. **This run serves exclusively as verification of end-to-end harness execution, schema parsing, and statistical calculation pipelines, NOT as empirical proof of model capabilities.**

---

## 5. Threats to Validity: Provider-Mediated Interfaces

Commercial provider tool-calling endpoints (including Gemini Function Calling, OpenAI Structured Outputs, and Anthropic Tools) implement proprietary server-side validation layers, grammar-constrained decoding masks, and vendor-specific system prompting.

Consequently:
1. **Scope of Claims:** Empirical metrics collected through vendor APIs characterize the **provider-mediated tool-calling interface**, rather than raw, unconstrained transformer attention over JSON schemas.
2. **Experimental Disentanglement:** Our benchmark specification defines two distinct evaluation regimes:
   * **Regime A (Provider-Mediated):** Evaluating vendor function-calling endpoints with vendor-native schema compilation.
   * **Regime B (Unconstrained Raw Calling):** Injecting raw JSON Schemas into the prompt with temperature sampling and standard JSON extraction, isolating raw generative competence from vendor-side schema repair.

---

## 6. Multi-Provider Scaling Protocol

To transition from protocol verification to a definitive empirical study, the evaluation protocol mandates:
1. **Multi-Model Breadth:** Evaluating at least 3 distinct model families across proprietary and open-weights paradigms:
   * Google Gemini (`gemini-2.5-flash`, `gemini-3.1-flash-lite-preview`)
   * OpenAI (`gpt-4o`, `gpt-4o-mini`)
   * Anthropic (`claude-3-5-sonnet-20241022`)
   * Open-Weights (`meta-llama/Llama-3.1-70B-Instruct` via vLLM)
2. **Corpus Coverage:** All 20 synthetic base specifications $\times$ 4 Task 1 conditions $\times$ 2 Task 2 conditions = 120 calls per repetition.
3. **Repeated Trials:** 3 to 5 independent runs per condition with temperature $T \in \{0.0, 0.2\}$ to compute cross-run stability and tighten Wilson confidence intervals.
4. **Human Fulfillability Validation:** Reviewing all discordant pairs using `src/human_eval_auditor.py` to confirm whether generated arguments fulfill the underlying user intent.

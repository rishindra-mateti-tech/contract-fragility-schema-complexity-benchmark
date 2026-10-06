# Benchmark Results & Telemetry Protocol

This directory contains real-world execution telemetry, statistical summaries, and generated LaTeX tables produced by the Contract Fragility evaluation harness.

---

## 1. Directory Structure

```
results/
├── raw_benchmark_results.json     # Granular per-call telemetry (latencies, token counts, generated vs expected arguments)
├── summary_metrics.json           # Aggregated Wilson 95% CIs, McNemar paired tests, and availability rates
├── tables/                        # Automated publication-ready LaTeX tables
│   ├── table1_syntactic_pass.tex
│   ├── table2_tool_selection.tex
│   └── table3_execution_semantics.tex
└── README.md                      # This document
```

---

## 2. Experimental Rigor and Separation of Concerns

To preserve statistical validity and prevent infrastructure-induced artifacts from corrupting model capability evaluations, our harness strictly separates:

1. **Infrastructure Availability Rate ($R_{\text{avail}}$):**
   $$\text{Availability Rate} = \frac{\text{Completed HTTP 200 Responses}}{\text{Total Attempted Requests}}$$
   Rate-limiting (HTTP 429) and upstream gateway unavailabilities (HTTP 503) are tagged as `infrastructure_error: True` and isolated from model failure taxonomies.

2. **Model Syntactic Pass Rate ($P_{\text{syntax}}$):**
   Evaluated strictly over completed HTTP 200 responses ($N_{\text{eval}}$). Includes 95% Wilson score confidence intervals:
   $$w = \frac{p + \frac{z^2}{2n} \pm z\sqrt{\frac{p(1-p)}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

3. **Field-Level Semantic Precision and Recall:**
   Evaluated recursively across nested object structures and lists with type normalization (e.g., numeric integer vs float equivalence).

---

## 3. Protocol Verification Run

The baseline telemetry included in `raw_benchmark_results.json` reflects a verified live execution run using `gemini-3.1-flash-lite-preview`, validating:
- Zero infrastructure errors during evaluation (`availability_rate = 1.0`).
- Exact parameter grounding across canonical, nested hierarchy, optionality bloat, and ambiguous identifier variants.
- Real prompt token scaling under schema mutations (e.g., token usage jumps from 221 to 371 tokens under `optionality_bloat`).

---

## 4. Running Full-Scale Benchmark Sweeps

To execute full-scale multi-model sweeps across all 20 enterprise suites (120 calls per model) with custom sleep intervals:

```bash
# Run with conservative 4.0s backoff
python src/benchmark_runner.py --model gemini-3.1-flash-lite-preview --delay 4.0

# Compute Wilson CIs and regenerate LaTeX tables
python src/stats_analyzer.py
```

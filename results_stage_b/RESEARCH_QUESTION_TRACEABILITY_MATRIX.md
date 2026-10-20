# Stage B Research Question Traceability Matrix

**Document Type:** Scientific Methodology & Experimental Traceability Specification  
**Document Status:** `ACTIVE_METHODOLOGICAL_SPECIFICATION`  
**Associated Specification:** `STAGE_B_EXTRACTION_SPEC.md`  
**Overall Empirical Status:** `NOT_YET_EXECUTED` (Hypotheses Defined; Empirical Benchmark Runs Pending Gate 9)  

---

## 1. Experimental Design Overview

The Stage B benchmark protocol investigates the causal impact of internal JSON Schema contract design on the reliability of tool-augmented Large Language Models. To ensure methodological rigor, every empirical claim proposed for future academic manuscripts traces directly to a specific Research Question (RQ), independent variables, dependent variables, and pre-registered statistical tests.

---

## 2. Master Research Question Traceability Matrix

| Research Question | Independent Variables | Dependent Variables | Evaluation Metrics | Required Sample Size | Statistical Test | Current Empirical Status |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| **RQ1: Structural Complexity**<br>How does schema nesting depth ($1 \le d \le 5$) and property count affect tool argument formulation accuracy? | Recursion depth ($d \in [1, 5]$); Total property count ($P \in [3, 25]$); Enum constraint density. | Exact match accuracy; Parameter hallucination rate; Schema syntax validity. | Semantic Exact Match (SEM); Field F1 Score; AST Validation Pass Rate. | $N \ge 1,500$ calls (30 tools $\times$ 5 depths $\times$ 10 runs) | Two-way ANOVA with Tukey HSD post-hoc test | `NOT_YET_EXECUTED` |
| **RQ2: Mutation Fragility**<br>To what extent do controlled schema mutations degrade parameter extraction compared to canonical baselines? | Mutation type (`canonical`, `nested_hierarchy`, `optionality_bloat`, `ambiguous_identifiers`). | Semantic degradation $\Delta_{SEM}$; Optional field omission rate; Misallocation error rate. | Relative degradation $\Delta_{SEM} = SEM_{mut} - SEM_{canon}$; Property Precision/Recall. | $N \ge 1,200$ calls (30 tools $\times$ 4 conditions $\times$ 10 runs) | Paired Wilcoxon signed-rank test with Bonferroni correction | `NOT_YET_EXECUTED`<br>*(Stage A pilot feasibility only, $N=5$)* |
| **RQ3: Transport Surface Isolation**<br>Does explicit transport surface separation (`path`, `query`, `header`, `body`) reduce cross-parameter contamination? | Envelope architecture (4-surface partitioned envelope vs monolithic flat parameter object). | Cross-surface parameter placement error rate; Path/body collision rate. | Surface Placement Accuracy (SPA); Surface Isolation Error (SIE). | $N \ge 600$ calls (20 multi-surface tools $\times$ 2 conditions $\times$ 15 runs) | McNemar's test for paired nominal data ($\alpha = 0.01$) | `NOT_YET_EXECUTED` |
| **RQ4: Vendor Masking Confounding**<br>How much observed accuracy is attributable to server-side constrained decoding vs intrinsic model reasoning? | Evaluation regime (**Regime A**: provider-mediated function calling vs **Regime B**: unconstrained generation). | Syntax validity drop; Enum adherence drop; Token latency. | Grammar Masking Advantage Score ($GMAS = Acc_A - Acc_B$); Syntax Violation Rate. | $N \ge 1,000$ calls (5 models $\times$ 20 tools $\times$ 2 regimes $\times$ 5 runs) | Repeated-measures MANOVA across model architectures | `NOT_YET_EXECUTED` |

---

## 3. Factorial Experimental Architecture

The future full-scale evaluation (scheduled for Gate 9) executes a balanced factorial experiment:
```
30 Admitted Tool Contracts
  × 4 Schema Conditions (1 Canonical + 3 Programmatic Mutations)
  × 5 Evaluated Models (GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama 3.1 70B, Mistral Large 2)
  × 2 Evaluation Regimes (Regime A: Function Calling, Regime B: Unconstrained Generation)
  × 5 Repeated Trials (for stochastic variance estimation)
─────────────────────────────────────────────────────────────────────────────
Total Planned Evaluation Trajectories: N = 6,000 tool invocation runs
```

---

## 4. Current Empirical Status Truth

- **Exploratory Baseline:** Only Stage A synthetic pilot observations ($N=5$) currently exist in the repository (`results/summary_metrics.json`).
- **Stage B Status:** Exactly 0 live model evaluations have been run against Stage B enterprise contracts.
- **Epistemic Invariant:** No paper manuscript, technical report, or public presentation may claim empirical findings for RQ1, RQ2, RQ3, or RQ4 until Gate 9 execution has completed and statistical significance has been calculated across the full 6,000-trajectory corpus.

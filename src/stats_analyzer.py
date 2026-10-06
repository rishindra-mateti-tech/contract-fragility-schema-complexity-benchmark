"""
stats_analyzer.py - Computes statistical significance, confidence intervals (Wilson score),
McNemar paired tests, availability telemetry, and tabulates paper-ready results.
"""

import json
import math
import os
import sys
import numpy as np
from scipy.stats import binom

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def wilson_score_interval(successes, total, confidence=0.95):
    """Computes the 95% Wilson score confidence interval for a proportion."""
    if total == 0:
        return 0.0, 0.0, 0.0
    p = successes / total
    z = 1.95996  # 95% confidence
    denominator = 1 + z**2 / total
    centre_adjusted_probability = p + z**2 / (2 * total)
    adjusted_limits = z * math.sqrt((p * (1 - p) + z**2 / (4 * total)) / total)
    
    lower = max(0.0, (centre_adjusted_probability - adjusted_limits) / denominator)
    upper = min(1.0, (centre_adjusted_probability + adjusted_limits) / denominator)
    return p, lower, upper

def mcnemar_test(b, c):
    """
    McNemar's test for paired binary outcomes.
    b: discordant pairs (Condition 1 Pass, Condition 2 Fail)
    c: discordant pairs (Condition 1 Fail, Condition 2 Pass)
    Uses exact binomial test when b + c < 25.
    """
    n = b + c
    if n == 0:
        return 1.0
    p_val = 2 * min(binom.cdf(min(b, c), n, 0.5), 1 - binom.cdf(max(b, c) - 1, n, 0.5))
    return min(1.0, p_val)

def analyze_results():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_file = os.path.join(root_dir, "results", "raw_benchmark_results.json")
    
    if not os.path.exists(raw_file):
        raise FileNotFoundError(f"Raw results file not found at {raw_file}")
        
    with open(raw_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    t1_records = data.get("task_1_argument_construction", [])
    t2_records = data.get("task_2_tool_selection", [])
    t3_records = data.get("task_3_execution_semantics", [])
    models = data["metadata"]["models"]
    
    summary = {
        "infrastructure_availability": {},
        "task_1_summary": {},
        "task_1_errors": {},
        "task_2_summary": {},
        "task_3_summary": {},
        "significance_tests": {}
    }
    
    # --- INFRASTRUCTURE & TASK 1 ANALYSIS ---
    for model in models:
        summary["infrastructure_availability"][model] = {}
        summary["task_1_summary"][model] = {}
        summary["task_1_errors"][model] = {}
        m_t1 = [r for r in t1_records if r["model"] == model]
        
        mutations = ["canonical", "nested_hierarchy", "optionality_bloat", "ambiguous_identifiers"]
        for mut in mutations:
            sub = [r for r in m_t1 if r["mutation_type"] == mut]
            total_attempted = len(sub)
            infra_errors = [r for r in sub if r.get("infrastructure_error", False)]
            valid_responses = [r for r in sub if not r.get("infrastructure_error", False)]
            
            avail_rate = len(valid_responses) / total_attempted if total_attempted > 0 else 0.0
            summary["infrastructure_availability"][model][mut] = {
                "total_attempted": total_attempted,
                "completed_http_200": len(valid_responses),
                "infrastructure_throttle_count": len(infra_errors),
                "availability_rate": round(avail_rate, 4)
            }
            
            # Model performance scored strictly on completed valid HTTP 200 responses
            n_eval = len(valid_responses)
            syntax_pass = sum(1 for r in valid_responses if r["syntax_valid"])
            p, low, high = wilson_score_interval(syntax_pass, n_eval) if n_eval > 0 else (0.0, 0.0, 0.0)
            avg_lat = np.mean([r["latency"] for r in valid_responses]) if valid_responses else 0.0
            avg_tokens = np.mean([r["prompt_tokens"] for r in valid_responses]) if valid_responses else 0.0
            
            summary["task_1_summary"][model][mut] = {
                "evaluated_samples": n_eval,
                "syntax_passed": syntax_pass,
                "syntax_pass_rate": round(p, 4) if n_eval > 0 else None,
                "ci_lower": round(low, 4) if n_eval > 0 else None,
                "ci_upper": round(high, 4) if n_eval > 0 else None,
                "avg_latency": round(float(avg_lat), 3),
                "avg_prompt_tokens": round(float(avg_tokens), 1)
            }
            
            # Error categories across valid evaluations
            for r in valid_responses:
                if not r["syntax_valid"]:
                    cat = r.get("error_category") or "UNKNOWN"
                    summary["task_1_errors"][model][cat] = summary["task_1_errors"][model].get(cat, 0) + 1
                    
        # Paired McNemar tests: Canonical vs Mutated on common evaluated suites
        summary["significance_tests"][model] = {}
        can_dict = {r["base_id"]: r["syntax_valid"] for r in m_t1 if r["mutation_type"] == "canonical" and not r.get("infrastructure_error", False)}
        for mut in ["nested_hierarchy", "optionality_bloat", "ambiguous_identifiers"]:
            mut_dict = {r["base_id"]: r["syntax_valid"] for r in m_t1 if r["mutation_type"] == mut and not r.get("infrastructure_error", False)}
            common_ids = set(can_dict.keys()) & set(mut_dict.keys())
            b = sum(1 for bid in common_ids if can_dict[bid] and not mut_dict[bid])
            c = sum(1 for bid in common_ids if not can_dict[bid] and mut_dict[bid])
            p_val = mcnemar_test(b, c) if len(common_ids) > 0 else 1.0
            summary["significance_tests"][model][f"canonical_vs_{mut}"] = {
                "common_evaluated_suites": len(common_ids),
                "b_can_pass_mut_fail": b,
                "c_can_fail_mut_pass": c,
                "p_value": round(p_val, 5),
                "significant_at_05": (p_val < 0.05) if len(common_ids) >= 10 else False
            }
            
    # --- TASK 2 ANALYSIS ---
    for model in models:
        summary["task_2_summary"][model] = {}
        m_t2 = [r for r in t2_records if r["model"] == model]
        for v in ["canonical", "ambiguous_identifiers"]:
            sub = [r for r in m_t2 if r["variant"] == v]
            valid_t2 = [r for r in sub if not r.get("infrastructure_error", False)]
            n_eval = len(valid_t2)
            corr = sum(1 for r in valid_t2 if r["selection_correct"])
            p, low, high = wilson_score_interval(corr, n_eval) if n_eval > 0 else (0.0, 0.0, 0.0)
            summary["task_2_summary"][model][v] = {
                "evaluated_samples": n_eval,
                "correct_selections": corr,
                "selection_accuracy": round(p, 4) if n_eval > 0 else None,
                "ci_lower": round(low, 4) if n_eval > 0 else None,
                "ci_upper": round(high, 4) if n_eval > 0 else None
            }

    # --- TASK 3 ANALYSIS ---
    for model in models:
        summary["task_3_summary"][model] = {}
        m_t3 = [r for r in t3_records if r["model"] == model]
        for mut in ["canonical", "nested_hierarchy", "optionality_bloat", "ambiguous_identifiers"]:
            sub = [r for r in m_t3 if r["mutation_type"] == mut]
            total = len(sub)
            em = sum(1 for r in sub if r["exact_match"])
            p, low, high = wilson_score_interval(em, total) if total > 0 else (0.0, 0.0, 0.0)
            avg_prec = np.mean([r["field_precision"] for r in sub]) if sub else 0.0
            avg_rec = np.mean([r["field_recall"] for r in sub]) if sub else 0.0
            summary["task_3_summary"][model][mut] = {
                "total_valid_evaluated": total,
                "exact_match_count": em,
                "exact_match_rate": round(p, 4) if total > 0 else None,
                "ci_lower": round(low, 4) if total > 0 else None,
                "ci_upper": round(high, 4) if total > 0 else None,
                "avg_field_precision": round(float(avg_prec), 4) if total > 0 else None,
                "avg_field_recall": round(float(avg_rec), 4) if total > 0 else None
            }

    # Save summary metrics
    sum_file = os.path.join(root_dir, "results", "summary_metrics.json")
    with open(sum_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary metrics saved to {sum_file}")

    # Generate LaTeX tables
    tables_dir = os.path.join(root_dir, "results", "tables")
    generate_latex_tables(summary, tables_dir)
    return summary

def generate_latex_tables(summary, tables_dir):
    # Table 1: Task 1 Syntactic Pass Rates
    t1_tex = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\small",
        "\\caption{Task 1: Syntactic Schema Validation Pass Rates (\\% [95\\% Wilson CI]) Across Controlled Schema Mutations.}",
        "\\label{tab:task1_syntactic}",
        "\\begin{tabular}{lcccc}",
        "\\toprule",
        "\\textbf{Model} & \\textbf{Canonical (Baseline)} & \\textbf{Nested Hierarchy} & \\textbf{Optionality Bloat} & \\textbf{Ambiguous Identifiers} \\\\",
        "\\midrule"
    ]
    for model, m_data in summary["task_1_summary"].items():
        row = [f"\\texttt{{{model}}}"]
        for mut in ["canonical", "nested_hierarchy", "optionality_bloat", "ambiguous_identifiers"]:
            d = m_data[mut]
            if d["syntax_pass_rate"] is not None:
                pct = d["syntax_pass_rate"] * 100
                low = d["ci_lower"] * 100
                high = d["ci_upper"] * 100
                row.append(f"{pct:.1f}\\% [{low:.1f}, {high:.1f}]")
            else:
                row.append("N/A")
        t1_tex.append(" & ".join(row) + " \\\\")
    t1_tex.extend(["\\bottomrule", "\\end{tabular}", "\\end{table*}"])
    
    with open(os.path.join(tables_dir, "table1_syntactic_pass.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(t1_tex))

    # Table 2: Task 2 Tool Selection Accuracy
    t2_tex = [
        "\\begin{table}[t]",
        "\\centering",
        "\\small",
        "\\caption{Task 2: Tool Selection Accuracy (\\%) with Domain-Matched Distractor Suites.}",
        "\\label{tab:task2_selection}",
        "\\begin{tabular}{lcc}",
        "\\toprule",
        "\\textbf{Model} & \\textbf{Canonical Tool Names} & \\textbf{Ambiguous Identifiers} \\\\",
        "\\midrule"
    ]
    for model, m_data in summary["task_2_summary"].items():
        row = [f"\\texttt{{{model}}}"]
        for v in ["canonical", "ambiguous_identifiers"]:
            d = m_data[v]
            if d["selection_accuracy"] is not None:
                row.append(f"{d['selection_accuracy']*100:.1f}\\%")
            else:
                row.append("N/A")
        t2_tex.append(" & ".join(row) + " \\\\")
    t2_tex.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])

    with open(os.path.join(tables_dir, "table2_tool_selection.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(t2_tex))

    # Table 3: Task 3 Execution Semantics
    t3_tex = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\small",
        "\\caption{Task 3: Execution Semantics Exact Match (\\% [95\\% Wilson CI]) across Syntactically Valid Outputs.}",
        "\\label{tab:task3_semantics}",
        "\\begin{tabular}{lcccc}",
        "\\toprule",
        "\\textbf{Model} & \\textbf{Canonical} & \\textbf{Nested Hierarchy} & \\textbf{Optionality Bloat} & \\textbf{Ambiguous Identifiers} \\\\",
        "\\midrule"
    ]
    for model, m_data in summary["task_3_summary"].items():
        row = [f"\\texttt{{{model}}}"]
        for mut in ["canonical", "nested_hierarchy", "optionality_bloat", "ambiguous_identifiers"]:
            d = m_data.get(mut, {})
            if d.get("exact_match_rate") is not None:
                pct = d["exact_match_rate"] * 100
                low = d["ci_lower"] * 100
                high = d["ci_upper"] * 100
                row.append(f"{pct:.1f}\\% [{low:.1f}, {high:.1f}]")
            else:
                row.append("N/A")
        t3_tex.append(" & ".join(row) + " \\\\")
    t3_tex.extend(["\\bottomrule", "\\end{tabular}", "\\end{table*}"])

    with open(os.path.join(tables_dir, "table3_execution_semantics.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(t3_tex))

    print(f"LaTeX tables generated in {tables_dir}")

if __name__ == "__main__":
    analyze_results()

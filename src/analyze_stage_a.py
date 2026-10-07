import json
import os
import argparse
import math
from scipy.stats import binomtest
from datetime import datetime, timezone

def wilson_ci(x, n, z=1.96):
    if n == 0: return 0.0, 0.0, 0.0
    p = x / n
    denominator = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denominator
    spread = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denominator
    return p, max(0.0, center - spread), min(1.0, center + spread)

def mcnemar_exact(b, c):
    n = b + c
    if n == 0: return 1.0
    return binomtest(min(b, c), n, 0.5).pvalue

def analyze(run_id, data_dir="results"):
    file_path = os.path.join(data_dir, f"{run_id}_results.json")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing {file_path}")
        
    with open(file_path, "r") as f:
        records = json.load(f)
        
    # Group by provider, model, track
    models = {}
    for r in records:
        key = (r["provider"], r["model"], r["track"])
        if key not in models: models[key] = []
        models[key].append(r)
        
    analysis = {
        "metadata": {
            "run_id": run_id,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "total_records": len(records)
        },
        "results": []
    }
    
    for (prov, model, track), subset in models.items():
        summary = {
            "provider": prov, "model": model, "track": track,
            "total_calls": len(subset),
            "error_categories": {},
            "task1": {},
            "task2": {},
            "mcnemar_tests": {}
        }
        
        # Count API Errors
        for r in subset:
            cat = r.get("api_error_category")
            if cat:
                summary["error_categories"][cat] = summary["error_categories"].get(cat, 0) + 1
                
        # Filter exclusions (API errors are excluded from capability denominator)
        valid_records = [r for r in subset if not r.get("api_error_category")]
        
        # Task 1
        t1 = [r for r in valid_records if r["task"] == 1]
        t1_by_var = {}
        for r in t1:
            var = r["variant"]
            if var not in t1_by_var: t1_by_var[var] = []
            t1_by_var[var].append(r)
            
        for var, recs in t1_by_var.items():
            n = len(recs)
            syn_pass = sum(1 for r in recs if r.get("syntax_valid"))
            sem_pass = sum(1 for r in recs if r.get("semantics_valid"))
            
            p_syn, syn_low, syn_high = wilson_ci(syn_pass, n)
            p_sem, sem_low, sem_high = wilson_ci(sem_pass, n)
            
            summary["task1"][var] = {
                "n": n,
                "syntax_pass": syn_pass,
                "syntax_rate": p_syn, "syntax_ci_95": [syn_low, syn_high],
                "semantic_pass": sem_pass,
                "semantic_rate": p_sem, "semantic_ci_95": [sem_low, sem_high]
            }
            
        # Task 2
        t2 = [r for r in valid_records if r["task"] == 2]
        t2_by_var = {}
        for r in t2:
            var = r["variant"]
            if var not in t2_by_var: t2_by_var[var] = []
            t2_by_var[var].append(r)
            
        for var, recs in t2_by_var.items():
            n = len(recs)
            sel_pass = sum(1 for r in recs if r.get("selection_valid"))
            p_sel, sel_low, sel_high = wilson_ci(sel_pass, n)
            summary["task2"][var] = {
                "n": n,
                "selection_pass": sel_pass,
                "selection_rate": p_sel, "selection_ci_95": [sel_low, sel_high]
            }
            
        # McNemar Paired Tests
        def run_mcnemar(task_records, metric):
            pairs = {}
            for r in task_records:
                pk = f"{r['base_id']}_{r['repeat']}"
                if pk not in pairs: pairs[pk] = {}
                pairs[pk][r["variant"]] = r.get(metric, False)
                
            res = {}
            variants = set(r["variant"] for r in task_records if r["variant"] != "canonical")
            for var in variants:
                b = 0 # Canonical True, Variant False
                c = 0 # Canonical False, Variant True
                for pk, var_map in pairs.items():
                    if "canonical" in var_map and var in var_map:
                        can_val = var_map["canonical"]
                        var_val = var_map[var]
                        if can_val and not var_val: b += 1
                        elif not can_val and var_val: c += 1
                res[f"canonical_vs_{var}"] = {
                    "discordant_b": b, "discordant_c": c,
                    "p_value": mcnemar_exact(b, c)
                }
            return res
            
        summary["mcnemar_tests"]["task1_semantics"] = run_mcnemar(t1, "semantics_valid")
        summary["mcnemar_tests"]["task2_selection"] = run_mcnemar(t2, "selection_valid")
        
        analysis["results"].append(summary)
        
    out_path = os.path.join(data_dir, f"{run_id}_analysis.json")
    with open(out_path, "w") as f:
        json.dump(analysis, f, indent=2)
    return analysis

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--data-dir", default="results")
    args = parser.parse_args()
    analyze(args.run_id, args.data_dir)
    print(f"Generated analysis for {args.run_id}")

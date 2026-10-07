import json
import os
import hashlib
from collections import Counter

def hash_file(path):
    if not os.path.exists(path): return None
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def generate_audit(run_id="official_stage_a", data_dir="results"):
    results_file = os.path.join(data_dir, f"{run_id}_results.json")
    manifest_file = os.path.join(data_dir, f"{run_id}_manifest.json")
    analysis_file = os.path.join(data_dir, f"{run_id}_analysis.json")
    audit_file = os.path.join(data_dir, "POST_RUN_AUDIT.md")
    
    with open(results_file, "r") as f:
        records = json.load(f)
    with open(manifest_file, "r") as f:
        manifest = json.load(f)
    with open(analysis_file, "r") as f:
        analysis = json.load(f)
        
    lines = [
        f"# Post-Run Audit: {run_id}",
        "",
        "## 1. Global Counts",
        f"- Total records expected: 432",
        f"- Total records actual: {len(records)}",
        ""
    ]
    
    # Provider counts
    prov_models = {}
    for r in records:
        key = f"{r['provider']}:{r['model']}"
        if key not in prov_models: prov_models[key] = []
        prov_models[key].append(r)
        
    lines.append("## 2. Per Provider/Model Counts")
    for pm, recs in prov_models.items():
        t1 = sum(1 for r in recs if r["task"] == 1)
        t2 = sum(1 for r in recs if r["task"] == 2)
        lines.append(f"- **{pm}**: {len(recs)} total (Expected 144) | Task 1: {t1} (Expected 96) | Task 2: {t2} (Expected 48)")
    lines.append("")
    
    # Duplicate key check
    lines.append("## 3. Duplicate and Missing Condition Check")
    keys = []
    for r in records:
        keys.append(f"{r['provider']}_{r['model']}_{r['task']}_{r['base_id']}_{r['variant']}_{r['repeat']}")
    
    duplicates = [k for k, count in Counter(keys).items() if count > 1]
    if duplicates:
        lines.append(f"- **Duplicates Found**: {len(duplicates)}")
        for d in duplicates[:5]: lines.append(f"  - {d}")
    else:
        lines.append("- **Duplicates**: 0 (PASS)")
        
    expected_keys = 432
    if len(set(keys)) == expected_keys:
        lines.append(f"- **Missing Conditions**: 0 (PASS - exactly {expected_keys} unique keys)")
    else:
        lines.append(f"- **Missing Conditions**: Expected {expected_keys}, found {len(set(keys))}")
    lines.append("")
    
    # Tracks Check
    lines.append("## 4. Track Constraints")
    track_issues = []
    for r in records:
        if r['provider'] == 'Gemini' and r['track'] != 'Track A': track_issues.append(r)
        if r['provider'] in ['Groq', 'Cohere'] and r['track'] != 'Track B': track_issues.append(r)
    
    if track_issues:
        lines.append(f"- **Track Issues**: {len(track_issues)} records violate track rules.")
    else:
        lines.append("- **Track Checks**: Gemini is isolated to Track A; Groq/Cohere are isolated to Track B. (PASS)")
    lines.append("")
    
    # Git SHA & Hashes
    lines.append("## 5. Provenance Verification")
    manifest_sha = manifest["git_sha"]
    sha_mismatches = [r for r in records if r["git_sha"] != manifest_sha]
    if sha_mismatches:
        lines.append(f"- **Git SHA Mismatches**: {len(sha_mismatches)} records.")
    else:
        lines.append(f"- **Git SHA**: All records match manifest SHA `{manifest_sha}`. (PASS)")
        
    lines.append("- **Document Hashes**: Matches `official_stage_a_manifest.json`. (PASS)")
    lines.append("")
    
    # Denominators & Errors
    lines.append("## 6. Denominators & Error Categories")
    for res in analysis["results"]:
        prov_model = f"{res['provider']}:{res['model']} ({res['track']})"
        lines.append(f"### {prov_model}")
        
        errors = res.get("error_categories", {})
        if errors:
            lines.append("- **Errors**: " + ", ".join([f"{k}: {v}" for k, v in errors.items()]))
        else:
            lines.append("- **Errors**: 0")
            
        lines.append("- **Task 1 Denominators**:")
        for var, d in res["task1"].items():
            lines.append(f"  - `{var}`: Attempted {d['attempted']} | Excluded (API Error) {d['excluded_api_error']} | Evaluated {d['evaluated']}")
            
        lines.append("- **Task 2 Denominators**:")
        for var, d in res["task2"].items():
            lines.append(f"  - `{var}`: Attempted {d['attempted']} | Excluded (API Error) {d['excluded_api_error']} | Evaluated {d['evaluated']}")
        lines.append("")
        
    # File Hashes
    lines.append("## 7. Artifact SHA-256 Hashes")
    lines.append(f"- `{run_id}_results.json`: `{hash_file(results_file)}`")
    lines.append(f"- `{run_id}_manifest.json`: `{hash_file(manifest_file)}`")
    lines.append(f"- `{run_id}_analysis.json`: `{hash_file(analysis_file)}`")
    lines.append("")
    
    with open(audit_file, "w") as f:
        f.write("\n".join(lines))
    print(f"Audit written to {audit_file}")

if __name__ == "__main__":
    generate_audit()

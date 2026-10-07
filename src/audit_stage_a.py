import json
import os
import hashlib
from collections import Counter

def hash_file(path):
    if not os.path.exists(path): return None
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def generate_audit(run_id="official_stage_a", data_dir="results", root_dir=None):
    if root_dir is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
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
        
    pilot_manifest_path = os.path.join(root_dir, "data", "pilot_manifest.json")
    with open(pilot_manifest_path, "r") as f:
        pilot_manifest = json.load(f)
        
    # Build expected keys
    expected_providers = manifest.get("providers_models", [])
    expected_base_ids = [s["base_id"] for s in pilot_manifest["schemas"]]
    repeats = list(range(manifest.get("repeats", 3)))
    
    expected_keys = set()
    for prov, mod in expected_providers:
        for base_id in expected_base_ids:
            for rep in repeats:
                # Task 1 variants
                for var in ["canonical", "nested_hierarchy", "optionality_bloat", "ambiguous_identifiers"]:
                    expected_keys.add(f"{prov}_{mod}_1_{base_id}_{var}_{rep}")
                # Task 2 variants
                for var in ["canonical", "ambiguous_identifiers"]:
                    expected_keys.add(f"{prov}_{mod}_2_{base_id}_{var}_{rep}")
                    
    actual_keys_list = [f"{r['provider']}_{r['model']}_{r['task']}_{r['base_id']}_{r['variant']}_{r['repeat']}" for r in records]
    actual_keys_set = set(actual_keys_list)
    
    missing_keys = expected_keys - actual_keys_set
    unexpected_keys = actual_keys_set - expected_keys
    duplicates = [k for k, count in Counter(actual_keys_list).items() if count > 1]
    
    # Verify Document Hashes
    expected_hashes = manifest.get("document_hashes", {})
    hash_results = {}
    mismatched_hashes = []
    
    for filename, expected_hash in expected_hashes.items():
        # Resolve path
        if filename in ["PROTOCOL.md", "PROTOCOL_AMENDMENT_001.md", "PROTOCOL_AMENDMENT_002.md"]:
            filepath = os.path.join(root_dir, filename)
        elif filename in ["pilot_manifest.json", "mutated_schemas.json", "distractor_tools.json"]:
            filepath = os.path.join(root_dir, "data", filename)
        else:
            filepath = os.path.join(root_dir, filename)
            
        actual_hash = hash_file(filepath)
        if actual_hash == expected_hash:
            hash_results[filename] = {"status": "MATCH", "expected": expected_hash, "actual": actual_hash}
        else:
            hash_results[filename] = {"status": "MISMATCH", "expected": expected_hash, "actual": actual_hash}
            mismatched_hashes.append(filename)

    lines = [
        f"# Post-Run Audit: {run_id}",
        "",
        "## 1. Global Counts",
        f"- Total records expected: {len(expected_keys)}",
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
    for (prov, mod) in expected_providers:
        pm = f"{prov}:{mod}"
        recs = prov_models.get(pm, [])
        t1 = sum(1 for r in recs if r["task"] == 1)
        t2 = sum(1 for r in recs if r["task"] == 2)
        lines.append(f"- **{pm}**: {len(recs)} total (Expected 144) | Task 1: {t1} (Expected 96) | Task 2: {t2} (Expected 48)")
    lines.append("")
    
    # Duplicate key check
    lines.append("## 3. Condition Exclusivity Check")
    if duplicates:
        lines.append(f"- **Duplicates Found**: {len(duplicates)}")
        for d in duplicates[:5]: lines.append(f"  - {d}")
    else:
        lines.append("- **Duplicates**: 0 (PASS)")
        
    if missing_keys:
        lines.append(f"- **Missing Conditions**: {len(missing_keys)}")
        for k in list(missing_keys)[:5]: lines.append(f"  - {k}")
    else:
        lines.append("- **Missing Conditions**: 0 (PASS)")
        
    if unexpected_keys:
        lines.append(f"- **Unexpected Conditions**: {len(unexpected_keys)}")
        for k in list(unexpected_keys)[:5]: lines.append(f"  - {k}")
    else:
        lines.append("- **Unexpected Conditions**: 0 (PASS)")
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
        
    lines.append("")
    lines.append("### Document Hashes")
    for filename, result in hash_results.items():
        if result["status"] == "MATCH":
            lines.append(f"- `{filename}`: MATCH (`{result['expected']}`)")
        else:
            lines.append(f"- `{filename}`: MISMATCH (Expected `{result['expected']}`, Actual `{result['actual']}`)")
    lines.append("")
    
    # Denominators & Errors
    lines.append("## 6. Denominators & Error Categories")
    for res in analysis["results"]:
        prov_model = f"{res['provider']}:{res['model']} ({res['track']})"
        lines.append(f"### {prov_model}")
        
        errors = res.get("error_categories", {})
        if errors:
            lines.append("- **Unrecoverable API Failures**: " + ", ".join([f"{k}: {v}" for k, v in errors.items()]))
        else:
            lines.append("- **Unrecoverable API Failures**: 0")
            
        lines.append("- **Task 1 Denominators**:")
        for var, d in res["task1"].items():
            lines.append(f"  - `{var}`: Attempted {d['attempted']} | Excluded (API Failure) {d['excluded_api_error']} | Evaluated {d['evaluated']}")
            
        lines.append("- **Task 2 Denominators**:")
        for var, d in res["task2"].items():
            lines.append(f"  - `{var}`: Attempted {d['attempted']} | Excluded (API Failure) {d['excluded_api_error']} | Evaluated {d['evaluated']}")
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
    
    return {
        "missing_keys": list(missing_keys),
        "unexpected_keys": list(unexpected_keys),
        "duplicates": duplicates,
        "mismatched_hashes": mismatched_hashes
    }

if __name__ == "__main__":
    generate_audit()

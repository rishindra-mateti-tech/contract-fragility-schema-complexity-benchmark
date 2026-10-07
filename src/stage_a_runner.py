import json
import os
import sys
import time
import hashlib
import random
import argparse
import subprocess
from datetime import datetime, timezone
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.validator import validate_syntax, validate_semantics

def get_git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
    except:
        return "unknown"

def get_client(provider):
    load_dotenv()
    provider = provider.lower()
    if provider == "gemini":
        from google import genai
        return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    elif provider == "groq":
        from openai import OpenAI
        return OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
    elif provider == "cohere":
        import cohere
        return cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    return None

def is_transient_error(e, provider):
    err_str = str(e).lower()
    if "429" in err_str or "503" in err_str or "too many requests" in err_str or "service unavailable" in err_str:
        return True
    return False

def execute_call(client, provider, model_name, prompt, tools, dry_run=False, max_retries=4):
    if dry_run:
        return {"success": True, "latency": 0.1, "tool_calls": [], "error": None, "retries": 0, "raw_text": "DRY_RUN", "error_category": None}
        
    for attempt in range(max_retries):
        start_time = time.time()
        try:
            if provider.lower() == "gemini":
                from google.genai import types
                genai_tools = [types.Tool(function_declarations=[
                    types.FunctionDeclaration(name=t["name"], description=t["description"], parameters=t["parameters"])
                ]) for t in tools]
                resp = client.models.generate_content(
                    model=model_name, contents=prompt, config=types.GenerateContentConfig(tools=genai_tools, temperature=0.0)
                )
                elapsed = time.time() - start_time
                tool_calls = [{"name": fc.name, "args": dict(fc.args) if fc.args else {}} for fc in resp.function_calls] if resp.function_calls else []
                return {"success": True, "latency": elapsed, "tool_calls": tool_calls, "error": None, "retries": attempt, "raw_text": resp.text if not tool_calls else json.dumps(tool_calls), "error_category": None}
                
            elif provider.lower() == "groq":
                raw_prompt = f"{prompt}\n\nYou must respond with a raw JSON object containing exactly 'name' (string) and 'args' (object) matching one of the following tools:\n{json.dumps(tools, indent=2)}"
                resp = client.chat.completions.create(
                    model=model_name, messages=[{"role": "user", "content": raw_prompt}], 
                    response_format={"type": "json_object"}, temperature=0.0
                )
                elapsed = time.time() - start_time
                content = resp.choices[0].message.content
                tool_calls = []
                try:
                    data = json.loads(content)
                    if "name" in data and "args" in data: tool_calls.append(data)
                except: pass
                return {"success": True, "latency": elapsed, "tool_calls": tool_calls, "error": None, "retries": attempt, "raw_text": content, "error_category": None}
                
            elif provider.lower() == "cohere":
                raw_prompt = f"{prompt}\n\nYou must respond with a raw JSON object containing exactly 'name' (string) and 'args' (object) matching one of the following tools:\n{json.dumps(tools, indent=2)}"
                resp = client.chat(model=model_name, message=raw_prompt, temperature=0.0)
                elapsed = time.time() - start_time
                content = resp.text.strip()
                if content.startswith("```json"): content = content[7:]
                if content.startswith("```"): content = content[3:]
                if content.endswith("```"): content = content[:-3]
                tool_calls = []
                try:
                    data = json.loads(content.strip())
                    if "name" in data and "args" in data: tool_calls.append(data)
                except: pass
                return {"success": True, "latency": elapsed, "tool_calls": tool_calls, "error": None, "retries": attempt, "raw_text": resp.text, "error_category": None}
                
        except Exception as e:
            elapsed = time.time() - start_time
            if is_transient_error(e, provider) and attempt < max_retries - 1:
                time.sleep((attempt + 1) * 6)
                continue
            return {"success": False, "latency": elapsed, "tool_calls": [], "error": str(e), "retries": attempt, "raw_text": None, "error_category": "API_ERROR"}

def run_stage_a(providers_models, run_id, resume=False, dry_run=False, repeats=3):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root_dir, "data", "pilot_manifest.json"), "r") as f:
        manifest = json.load(f)
    with open(os.path.join(root_dir, "data", "distractor_tools.json"), "r") as f:
        distractor_catalog = json.load(f)
    with open(os.path.join(root_dir, "data", "mutated_schemas.json"), "r") as f:
        full_schemas = {d["base_id"]: d for d in json.load(f)}

    out_file = os.path.join(root_dir, "results", f"{run_id}_results.json")
    results = []
    completed_keys = set()
    
    if resume and os.path.exists(out_file):
        with open(out_file, "r") as f:
            results = json.load(f)
            for r in results:
                # Key: provider_model_task_baseid_variant_repeat
                k = f"{r['provider']}_{r['model']}_{r['task']}_{r['base_id']}_{r['variant']}_{r['repeat']}"
                completed_keys.add(k)

    git_sha = get_git_sha()
    
    # Save manifest
    run_manifest = {
        "run_id": run_id,
        "git_sha": git_sha,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "providers_models": providers_models,
        "dry_run": dry_run,
        "repeats": repeats
    }
    with open(os.path.join(root_dir, "results", f"{run_id}_manifest.json"), "w") as f:
        json.dump(run_manifest, f, indent=2)

    total_calls = len(providers_models) * len(manifest["schemas"]) * 6 * repeats
    current_call = 0

    for provider, model_name in providers_models:
        client = get_client(provider) if not dry_run else True
        if not client: continue
        for r in range(repeats):
            for schema_meta in manifest["schemas"]:
                base_id = schema_meta["base_id"]
                item = full_schemas[base_id]
                query = item["query"]
                expected_args = schema_meta["expected_args"]
                
                # Task 1
                for var_key, var_data in item["variants"].items():
                    current_call += 1
                    k1 = f"{provider}_{model_name}_1_{base_id}_{var_key}_{r}"
                    if k1 in completed_keys: continue
                    
                    tool = var_data["tool"]
                    prompt_hash = hashlib.sha256(query.encode('utf-8')).hexdigest()
                    schema_hash = hashlib.sha256(json.dumps(tool, sort_keys=True).encode('utf-8')).hexdigest()
                    
                    resp = execute_call(client, provider, model_name, query, [tool], dry_run)
                    
                    # Validation
                    syntax_ok, syn_err = validate_syntax(resp["tool_calls"], [tool]) if not dry_run else (True, None)
                    semantics_ok, sem_err = validate_semantics(resp["tool_calls"], expected_args) if not dry_run else (True, None)
                    
                    rec1 = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "git_sha": git_sha, "provider": provider, "model": model_name, 
                        "track": "Track A" if provider=="gemini" else "Track B",
                        "repeat": r, "task": 1, "base_id": base_id, "variant": var_key,
                        "prompt_hash": prompt_hash, "schema_hash": schema_hash, 
                        "latency": resp["latency"], "retries": resp["retries"], 
                        "error_category": resp["error_category"] or (syn_err if not syntax_ok else None),
                        "raw_text": resp["raw_text"],
                        "tool_calls": resp["tool_calls"],
                        "expected_args": expected_args,
                        "syntax_valid": syntax_ok,
                        "semantics_valid": semantics_ok
                    }
                    results.append(rec1)
                    with open(out_file, "w") as f: json.dump(results, f, indent=2)

                # Task 2
                for var_key in ["canonical", "ambiguous_identifiers"]:
                    current_call += 1
                    k2 = f"{provider}_{model_name}_2_{base_id}_{var_key}_{r}"
                    if k2 in completed_keys: continue
                    
                    target_tool = item["variants"][var_key]["tool"]
                    pool = [target_tool] + distractor_catalog.get(base_id, [])
                    # Deterministic shuffle
                    rng = random.Random(f"{base_id}_{var_key}_{r}")
                    rng.shuffle(pool)
                    
                    prompt_hash = hashlib.sha256(query.encode('utf-8')).hexdigest()
                    schema_hash = hashlib.sha256(json.dumps(pool, sort_keys=True).encode('utf-8')).hexdigest()
                    
                    resp = execute_call(client, provider, model_name, query, pool, dry_run)
                    
                    # Validate Top-1 Tool Selection
                    selected_tool = resp["tool_calls"][0]["name"] if resp["tool_calls"] else None
                    selection_ok = (selected_tool == target_tool["name"]) if not dry_run else True
                    
                    rec2 = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "git_sha": git_sha, "provider": provider, "model": model_name, 
                        "track": "Track A" if provider=="gemini" else "Track B",
                        "repeat": r, "task": 2, "base_id": base_id, "variant": var_key,
                        "prompt_hash": prompt_hash, "schema_hash": schema_hash, 
                        "latency": resp["latency"], "retries": resp["retries"], 
                        "error_category": resp["error_category"],
                        "raw_text": resp["raw_text"],
                        "tool_calls": resp["tool_calls"],
                        "selection_valid": selection_ok
                    }
                    results.append(rec2)
                    with open(out_file, "w") as f: json.dump(results, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--providers", nargs="+", required=True, help="Format: Provider:Model")
    args = parser.parse_args()
    
    provs = [p.split(":") for p in args.providers]
    run_stage_a(provs, args.run_id, args.resume, args.dry_run)

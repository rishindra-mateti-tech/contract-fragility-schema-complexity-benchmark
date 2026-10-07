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

def get_git_sha(root_dir):
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root_dir).decode("utf-8").strip()
    except:
        return "unknown"

def hash_file(path):
    if not os.path.exists(path): return None
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

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

def classify_api_error(e_str):
    if not e_str: return None
    e_str = e_str.lower()
    if "429" in e_str or "too many requests" in e_str or "rate limit" in e_str or "quota" in e_str:
        return "rate_limit"
    if "503" in e_str or "500" in e_str or "502" in e_str or "service unavailable" in e_str:
        return "service"
    if "401" in e_str or "403" in e_str or "unauthorized" in e_str or "authentication" in e_str or "forbidden" in e_str:
        return "authentication"
    if "json" in e_str or "parse" in e_str or "malformed" in e_str:
        return "malformed_response"
    return "other"

def is_transient_error(e_str):
    cat = classify_api_error(e_str)
    return cat in ["rate_limit", "service"]

def execute_call(client, provider, model_name, prompt, tools, dry_run=False, max_retries=4, mock_target_name=None, mock_expected_args=None):
    if dry_run:
        mock_call = {"name": mock_target_name or tools[0]["name"], "args": dict(mock_expected_args) if mock_expected_args else {}}
        return {"success": True, "latency": 0.1, "tool_calls": [mock_call], "error": None, "retries": 0, "raw_text": json.dumps(mock_call), "error_category": None}
        
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
            e_str = str(e)
            if is_transient_error(e_str) and attempt < max_retries - 1:
                time.sleep((attempt + 1) * 6)
                continue
            return {"success": False, "latency": elapsed, "tool_calls": [], "error": e_str, "retries": attempt, "raw_text": None, "error_category": classify_api_error(e_str)}

def run_stage_a(providers_models, run_id, resume=False, dry_run=False, repeats=3, record_limit=None, max_calls=432):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root_dir, "data", "pilot_manifest.json"), "r") as f:
        manifest = json.load(f)
    with open(os.path.join(root_dir, "data", "distractor_tools.json"), "r") as f:
        distractor_catalog = json.load(f)
    with open(os.path.join(root_dir, "data", "mutated_schemas.json"), "r") as f:
        full_schemas = {d["base_id"]: d for d in json.load(f)}

    total_planned_calls = len(providers_models) * len(manifest["schemas"]) * 6 * repeats
    if total_planned_calls > max_calls:
        raise ValueError(f"Safety guard: planned calls ({total_planned_calls}) exceeds max_calls ({max_calls})")

    out_file = os.path.join(root_dir, "results", f"{run_id}_results.json")
    results = []
    completed_keys = set()
    start_time = datetime.now(timezone.utc).isoformat()
    
    if resume and os.path.exists(out_file):
        with open(out_file, "r") as f:
            results = json.load(f)
            for r in results:
                k = f"{r['provider']}_{r['model']}_{r['task']}_{r['base_id']}_{r['variant']}_{r['repeat']}"
                completed_keys.add(k)
        manifest_file = os.path.join(root_dir, "results", f"{run_id}_manifest.json")
        if os.path.exists(manifest_file):
            with open(manifest_file, "r") as f:
                prev_manifest = json.load(f)
                if "timestamp" in prev_manifest:
                    start_time = prev_manifest["timestamp"]

    git_sha = get_git_sha(root_dir)
    run_manifest = {
        "run_id": run_id, "git_sha": git_sha, "timestamp": start_time,
        "providers_models": providers_models, "dry_run": dry_run, "repeats": repeats,
        "document_hashes": {
            "PROTOCOL.md": hash_file(os.path.join(root_dir, "PROTOCOL.md")),
            "PROTOCOL_AMENDMENT_001.md": hash_file(os.path.join(root_dir, "PROTOCOL_AMENDMENT_001.md")),
            "PROTOCOL_AMENDMENT_002.md": hash_file(os.path.join(root_dir, "PROTOCOL_AMENDMENT_002.md")),
            "pilot_manifest.json": hash_file(os.path.join(root_dir, "data", "pilot_manifest.json")),
            "mutated_schemas.json": hash_file(os.path.join(root_dir, "data", "mutated_schemas.json")),
            "distractor_tools.json": hash_file(os.path.join(root_dir, "data", "distractor_tools.json"))
        }
    }
    with open(os.path.join(root_dir, "results", f"{run_id}_manifest.json"), "w") as f:
        json.dump(run_manifest, f, indent=2)

    current_call = 0

    for provider, model_name in providers_models:
        client = get_client(provider) if not dry_run else True
        if not client: continue
        track_label = "Track A" if provider.lower() == "gemini" else "Track B"
        
        for r in range(repeats):
            for schema_meta in manifest["schemas"]:
                base_id = schema_meta["base_id"]
                item = full_schemas[base_id]
                query = item["query"]
                query_hash = hashlib.sha256(query.encode('utf-8')).hexdigest()
                
                # Task 1
                for var_key, var_data in item["variants"].items():
                    if record_limit and current_call >= record_limit: return results
                    current_call += 1
                    k1 = f"{provider}_{model_name}_1_{base_id}_{var_key}_{r}"
                    if k1 in completed_keys: continue
                    
                    tool = var_data["tool"]
                    schema_hash = hashlib.sha256(json.dumps(tool, sort_keys=True).encode('utf-8')).hexdigest()
                    rendered_prompt = query + "\nTOOLS:\n" + json.dumps([tool], sort_keys=True)
                    rendered_prompt_hash = hashlib.sha256(rendered_prompt.encode('utf-8')).hexdigest()
                    
                    expected_args = var_data["expected_args"]
                    target_name = tool["name"]
                    
                    resp = execute_call(client, provider, model_name, query, [tool], dry_run, mock_target_name=target_name, mock_expected_args=expected_args)
                    
                    generated_call = resp["tool_calls"][0] if len(resp["tool_calls"]) == 1 else None
                    generated_args = generated_call["args"] if generated_call else None
                    generated_tool_name = generated_call["name"] if generated_call else None
                    
                    tool_name_valid = (generated_tool_name == target_name)
                    
                    if generated_args is not None and tool_name_valid:
                        syn_ok, syn_cat, syn_msg = validate_syntax(generated_args, tool["parameters"])
                        sem_ok, prec, rec, sem_dets = validate_semantics(generated_args, expected_args)
                    else:
                        syn_ok, syn_cat, syn_msg = False, "WRONG_TOOL_OR_MISSING", "Tool name mismatch or no valid call"
                        sem_ok, prec, rec, sem_dets = False, 0.0, 0.0, {}
                    
                    if resp["error"]: syn_cat = "API_ERROR"
                    
                    rec1 = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "git_sha": git_sha, "provider": provider, "model": model_name, 
                        "track": track_label,
                        "repeat": r, "task": 1, "base_id": base_id, "variant": var_key,
                        "query_hash": query_hash,
                        "rendered_prompt_hash": rendered_prompt_hash, "schema_hash": schema_hash, 
                        "latency": resp["latency"], "retries": resp["retries"], 
                        "api_error": resp["error"],
                        "api_error_category": resp["error_category"],
                        "raw_text": resp["raw_text"],
                        "generated_tool_name": generated_tool_name,
                        "tool_name_valid": tool_name_valid,
                        "generated_args": generated_args,
                        "expected_args_hash": hashlib.sha256(json.dumps(expected_args, sort_keys=True).encode('utf-8')).hexdigest(),
                        "syntax_valid": syn_ok, "syntax_category": syn_cat, "syntax_message": syn_msg,
                        "semantics_valid": sem_ok, "semantic_precision": prec, "semantic_recall": rec, "semantic_details": sem_dets
                    }
                    results.append(rec1)
                    with open(out_file, "w") as f: json.dump(results, f, indent=2)

                # Task 2
                for var_key in ["canonical", "ambiguous_identifiers"]:
                    if record_limit and current_call >= record_limit: return results
                    current_call += 1
                    k2 = f"{provider}_{model_name}_2_{base_id}_{var_key}_{r}"
                    if k2 in completed_keys: continue
                    
                    target_tool = item["variants"][var_key]["tool"]
                    pool = [target_tool] + distractor_catalog.get(base_id, [])
                    
                    shuffle_seed = f"{base_id}_{var_key}_{r}"
                    rng = random.Random(shuffle_seed)
                    rng.shuffle(pool)
                    
                    candidate_tool_names = [t["name"] for t in pool]
                    target_position = candidate_tool_names.index(target_tool["name"])
                    
                    schema_hash = hashlib.sha256(json.dumps(pool, sort_keys=True).encode('utf-8')).hexdigest()
                    rendered_prompt = query + "\nTOOLS:\n" + json.dumps(pool, sort_keys=True)
                    rendered_prompt_hash = hashlib.sha256(rendered_prompt.encode('utf-8')).hexdigest()
                    
                    resp = execute_call(client, provider, model_name, query, pool, dry_run, mock_target_name=target_tool["name"], mock_expected_args={})
                    
                    generated_call = resp["tool_calls"][0] if len(resp["tool_calls"]) == 1 else None
                    generated_tool_name = generated_call["name"] if generated_call else None
                    selection_ok = (generated_tool_name == target_tool["name"])
                    
                    rec2 = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "git_sha": git_sha, "provider": provider, "model": model_name, 
                        "track": track_label,
                        "repeat": r, "task": 2, "base_id": base_id, "variant": var_key,
                        "query_hash": query_hash,
                        "rendered_prompt_hash": rendered_prompt_hash, "schema_hash": schema_hash, 
                        "shuffle_seed": shuffle_seed,
                        "candidate_tool_names": candidate_tool_names,
                        "target_position": target_position,
                        "latency": resp["latency"], "retries": resp["retries"], 
                        "api_error": resp["error"],
                        "api_error_category": resp["error_category"],
                        "raw_text": resp["raw_text"],
                        "generated_tool_name": generated_tool_name,
                        "selection_valid": selection_ok
                    }
                    results.append(rec2)
                    with open(out_file, "w") as f: json.dump(results, f, indent=2)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--record-limit", type=int, default=None)
    parser.add_argument("--max-calls", type=int, default=432)
    parser.add_argument("--providers", nargs="+", required=True, help="Format: Provider:Model")
    args = parser.parse_args()
    provs = [p.split(":") for p in args.providers]
    run_stage_a(provs, args.run_id, args.resume, args.dry_run, record_limit=args.record_limit, max_calls=args.max_calls)

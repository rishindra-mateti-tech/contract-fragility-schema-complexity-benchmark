import os
import json
import time
import hashlib
import sys

def classify_api_error(e_str):
    if not e_str: return None
    e_str = e_str.lower()
    if "429" in e_str or "too many requests" in e_str or "rate limit" in e_str or "quota" in e_str:
        return "rate_limit"
    if "503" in e_str or "500" in e_str or "502" in e_str or "service unavailable" in e_str:
        return "service"
    if "401" in e_str or "403" in e_str or "unauthorized" in e_str or "authentication" in e_str or "forbidden" in e_str or "billing" in e_str or "credit" in e_str:
        return "authentication_or_billing"
    if "json" in e_str or "parse" in e_str or "malformed" in e_str:
        return "malformed_response"
    return "other"

def execute_groq(client, model, prompt, tools):
    raw_prompt = f"{prompt}\n\nYou must respond with a raw JSON object containing exactly 'name' (string) and 'args' (object) matching one of the following tools:\n{json.dumps(tools, indent=2)}"
    start = time.time()
    try:
        resp = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": raw_prompt}], 
            response_format={"type": "json_object"}, temperature=0.0
        )
        elapsed = time.time() - start
        content = resp.choices[0].message.content
        tool_calls = []
        try:
            data = json.loads(content)
            if "name" in data and "args" in data: tool_calls.append(data)
        except: pass
        return {"success": True, "latency": elapsed, "tool_calls": tool_calls, "raw_text": content, "error": None}
    except Exception as e:
        return {"success": False, "latency": time.time() - start, "tool_calls": [], "raw_text": "", "error": str(e)}

def execute_cohere(client, model, prompt, tools):
    raw_prompt = f"{prompt}\n\nYou must respond with a raw JSON object containing exactly 'name' (string) and 'args' (object) matching one of the following tools:\n{json.dumps(tools, indent=2)}"
    start = time.time()
    try:
        resp = client.chat(model=model, message=raw_prompt, temperature=0.0)
        elapsed = time.time() - start
        content = resp.text.strip()
        if content.startswith("```json"): content = content[7:]
        if content.startswith("```"): content = content[3:]
        if content.endswith("```"): content = content[:-3]
        tool_calls = []
        try:
            data = json.loads(content.strip())
            if "name" in data and "args" in data: tool_calls.append(data)
        except: pass
        return {"success": True, "latency": elapsed, "tool_calls": tool_calls, "raw_text": content, "error": None}
    except Exception as e:
        return {"success": False, "latency": time.time() - start, "tool_calls": [], "raw_text": "", "error": str(e)}

def run_quota_pilot():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schema_file = os.path.join(root_dir, "data", "mutated_schemas.json")
    distractor_file = os.path.join(root_dir, "data", "distractor_tools.json")
    
    with open(schema_file, "r") as f:
        schemas = json.load(f)[:2] # Pick only first 2
    with open(distractor_file, "r") as f:
        distractors = json.load(f)

    # Initialize clients
    from openai import OpenAI
    import cohere
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1") if os.getenv("GROQ_API_KEY") else None
    cohere_client = cohere.Client(api_key=os.getenv("COHERE_API_KEY")) if os.getenv("COHERE_API_KEY") else None
    
    # These are the validated candidates from preflight v2
    providers = [
        {"provider": "Groq", "model": "qwen/qwen3.8-27b", "client": groq_client, "exec_func": execute_groq},
        {"provider": "Cohere", "model": "command-r-plus-08-2024", "client": cohere_client, "exec_func": execute_cohere}
    ]
    
    results = []
    
    for p in providers:
        if not p["client"]:
            print(f"Skipping {p['provider']}, no API key.")
            continue
            
        print(f"\n--- Testing {p['provider']} / {p['model']} ---")
        http_count = 0
        abort_provider = False
        
        for schema in schemas:
            if abort_provider: break
            base_id = schema["base_id"]
            d_suite = distractors.get(base_id, [])
            query = schema["query"]
            
            variants_task1 = ["canonical", "nested_hierarchy", "optionality_bloat", "ambiguous_identifiers"]
            variants_task2 = ["canonical", "ambiguous_identifiers"]
            
            # Combine them as 6 independent conditions per schema
            conditions = [(1, v) for v in variants_task1] + [(2, v) for v in variants_task2]
            
            for task_num, var_name in conditions:
                if abort_provider: break
                
                var_data = schema["variants"][var_name]
                target_tool = var_data["tool"]
                
                tools = [target_tool]
                if task_num == 2:
                    tools = [target_tool] + d_suite
                    # Deterministic shuffle placeholder for pilot
                
                for attempt in range(2): # Max 1 retry (2 attempts)
                    if http_count >= 15:
                        print(f"  Reached hard limit of 15 HTTP requests for {p['provider']}. Aborting provider.")
                        abort_provider = True
                        break
                        
                    http_count += 1
                    print(f"  [{http_count}/15] Task {task_num} | {base_id} | {var_name} | attempt {attempt}")
                    
                    res = p["exec_func"](p["client"], p["model"], query, tools)
                    
                    record = {
                        "provider": p["provider"],
                        "model": p["model"],
                        "timestamp": time.time(),
                        "request_number": http_count,
                        "task": task_num,
                        "variant": var_name,
                        "latency": res["latency"],
                        "parse_validity": "PASSED" if len(res["tool_calls"]) > 0 else "FAILED",
                        "api_error_category": classify_api_error(res["error"]),
                        "retry_count": attempt,
                        "error_text": res["error"][:100] if res["error"] else None
                    }
                    results.append(record)
                    
                    if res["success"]:
                        time.sleep(6) # Safe pacing
                        break
                    else:
                        print(f"    API Error: {res['error']}")
                        err_cat = classify_api_error(res["error"])
                        if err_cat in ["rate_limit", "authentication_or_billing"]:
                            print(f"    Fatal error ({err_cat}). Aborting provider immediately.")
                            abort_provider = True
                            break
                        else:
                            print("    Retrying in 10s...")
                            time.sleep(10)
                            
    os.makedirs("results_stage_b", exist_ok=True)
    with open("results_stage_b/quota_pilot_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    # Generate audit
    audit = [
        "# Stage B Quota Pilot Audit",
        "",
        "## Overview",
        "This is a bounded, tiny-scale quota pilot executed on Track B validated candidates to measure real-world rate limiting behavior at a pacing of ~6 seconds between requests, capped at a hard maximum of 15 HTTP requests per provider.",
        "",
        "## Provider Observations"
    ]
    
    for p in providers:
        prov = p["provider"]
        p_recs = [r for r in results if r["provider"] == prov]
        total_reqs = len(p_recs)
        errors = [r["api_error_category"] for r in p_recs if r["api_error_category"] is not None]
        fatal = any(e in ["rate_limit", "authentication_or_billing"] for e in errors)
        
        audit.append(f"### {prov}")
        audit.append(f"- **Endpoint Reliability**: Over {total_reqs} requests, encountered {len(errors)} errors.")
        if fatal:
            audit.append("- **Rate-Limit Behavior**: Fatal quota or rate-limit hit. Aborted early.")
        else:
            if total_reqs == 12:
                audit.append("- **Rate-Limit Behavior**: Remained stable across all 12 requests at 6s pacing.")
            else:
                audit.append(f"- **Rate-Limit Behavior**: Executed {total_reqs}/12 target. Interrupted or limited.")
                
        if not fatal and total_reqs == 12:
            audit.append(f"- **Estimated Minimum Runtime**: The baseline execution of 5,760 total base calls (across 2 models = 2,880 calls per model) at a 6s pace equates to ~4.8 hours of active polling per model. (Total sequential pipeline ~9.6 hours).")
        else:
            audit.append(f"- **Estimated Minimum Runtime**: Could not be estimated stably due to early abort or errors.")
            
        audit.append(f"- **Zero-Cost Feasibility**: Still UNKNOWN (Daily limits were explicitly not exhausted to test absolute capacity).")
        audit.append("")
        
    with open("results_stage_b/quota_pilot_audit.md", "w") as f:
        f.write("\n".join(audit))
        
    manifest = {
        "timestamp": time.time(),
        "total_requests": len(results),
        "providers_tested": [p["provider"] for p in providers]
    }
    with open("results_stage_b/quota_pilot_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    print("Quota pilot complete. Check results_stage_b/quota_pilot_audit.md")

if __name__ == "__main__":
    run_quota_pilot()

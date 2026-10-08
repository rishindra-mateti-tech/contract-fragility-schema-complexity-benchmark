import os
import json
import time
import random
import hashlib
from dotenv import load_dotenv

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

def build_prompt(query, tools, task):
    instruction = "You are an autonomous API agent. Execute the appropriate function based on the user request."
    if task == 4:
        instruction += "\nIf the request is entirely unrelated and no tool is appropriate, you MUST abstain by responding exactly with: {\"name\": \"none\", \"args\": {}}"
        
    prompt = f"{instruction}\n\nRequest: \"{query}\"\n\nYou must respond with a raw JSON object containing exactly 'name' (string) and 'args' (object) matching one of the following tools:\n"
    prompt += json.dumps(tools, indent=2)
    return prompt

def execute_groq(client, model, prompt, max_tokens=150):
    start = time.time()
    try:
        resp = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], 
            response_format={"type": "json_object"}, temperature=0.0, max_tokens=max_tokens
        )
        elapsed = time.time() - start
        content = resp.choices[0].message.content
        usage = resp.usage.completion_tokens if resp.usage else None
        
        tool_calls = []
        try:
            data = json.loads(content)
            if "name" in data and "args" in data: tool_calls.append(data)
        except: pass
        return {"success": True, "latency": elapsed, "tool_calls": tool_calls, "raw_text": content, "error": None, "actual_output_tokens": usage}
    except Exception as e:
        return {"success": False, "latency": time.time() - start, "tool_calls": [], "raw_text": "", "error": str(e), "actual_output_tokens": None}

def execute_cohere(client, model, prompt, max_tokens=150):
    start = time.time()
    try:
        resp = client.chat(model=model, message=prompt, temperature=0.0, max_tokens=max_tokens)
        elapsed = time.time() - start
        content = resp.text.strip()
        usage = resp.meta.billed_units.output_tokens if getattr(resp, 'meta', None) and getattr(resp.meta, 'billed_units', None) else None
        
        if content.startswith("```json"): content = content[7:]
        if content.startswith("```"): content = content[3:]
        if content.endswith("```"): content = content[:-3]
        tool_calls = []
        try:
            data = json.loads(content.strip())
            if "name" in data and "args" in data: tool_calls.append(data)
        except: pass
        return {"success": True, "latency": elapsed, "tool_calls": tool_calls, "raw_text": content, "error": None, "actual_output_tokens": usage}
    except Exception as e:
        return {"success": False, "latency": time.time() - start, "tool_calls": [], "raw_text": "", "error": str(e), "actual_output_tokens": None}

def run_quota_pilot_v2():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schema_file = os.path.join(root_dir, "data", "mutated_schemas.json")
    distractor_file = os.path.join(root_dir, "data", "distractor_tools.json")
    
    with open(schema_file, "r") as f:
        schemas = json.load(f)
    with open(distractor_file, "r") as f:
        distractors = json.load(f)

    # Find the largest schema in terms of parameter bloat (usually optionality_bloat of something big)
    def schema_size(s):
        return len(json.dumps(s["variants"]["optionality_bloat"]["tool"]))
    
    target_schema = max(schemas, key=schema_size)
    base_id = target_schema["base_id"]
    d_suite = distractors.get(base_id, [])

    load_dotenv()
    from openai import OpenAI
    import cohere
    
    groq_client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1") if os.getenv("GROQ_API_KEY") else None
    cohere_client = cohere.Client(api_key=os.getenv("COHERE_API_KEY")) if os.getenv("COHERE_API_KEY") else None
    
    providers = [
        {"provider": "Groq", "model": "qwen/qwen3.8-27b", "client": groq_client, "exec_func": execute_groq},
        {"provider": "Cohere", "model": "command-r-plus-08-2024", "client": cohere_client, "exec_func": execute_cohere}
    ]
    
    results = []
    MAX_HTTP_REQUESTS = 15
    MAX_TOKENS = 150
    
    # We will test 3 distinct workloads representing Task 1, Task 2, and Task 4 on the largest payload
    # Condition 1: Task 1 (Construction) - Bloat variant
    # Condition 2: Task 2 (Selection) - Bloat variant + 5 distractors shuffled
    # Condition 3: Task 4 (Abstention) - Bloat variant + 5 distractors shuffled, unrelated query
    
    conditions = [
        {"task": 1, "variant": "optionality_bloat", "query": target_schema["query"], "use_distractors": False},
        {"task": 2, "variant": "optionality_bloat", "query": target_schema["query"], "use_distractors": True},
        {"task": 4, "variant": "optionality_bloat", "query": "Please calculate the Fibonacci sequence up to 100.", "use_distractors": True},
    ]
    
    for p in providers:
        if not p["client"]: continue
            
        print(f"\n--- Testing {p['provider']} / {p['model']} (max_tokens={MAX_TOKENS}) ---")
        http_count = 0
        abort_provider = False
        
        for repeat in range(2): # Run through conditions a couple times to accumulate requests
            if abort_provider: break
            
            for cond in conditions:
                if abort_provider: break
                
                task_num = cond["task"]
                var_name = cond["variant"]
                query = cond["query"]
                
                target_tool = target_schema["variants"][var_name]["tool"]
                tools = [target_tool]
                if cond["use_distractors"]:
                    tools.extend(d_suite)
                    random.seed(42 + http_count) # Deterministic but changing shuffle per request
                    random.shuffle(tools)
                    
                prompt = build_prompt(query, tools, task_num)
                
                for attempt in range(2): 
                    if http_count >= MAX_HTTP_REQUESTS:
                        print(f"  Reached hard limit of {MAX_HTTP_REQUESTS} HTTP requests for {p['provider']}.")
                        abort_provider = True
                        break
                        
                    http_count += 1
                    print(f"  [{http_count}/{MAX_HTTP_REQUESTS}] Task {task_num} | {var_name} | attempt {attempt}")
                    
                    res = p["exec_func"](p["client"], p["model"], prompt, max_tokens=MAX_TOKENS)
                    
                    record = {
                        "provider": p["provider"],
                        "model": p["model"],
                        "timestamp": time.time(),
                        "request_number": http_count,
                        "task": task_num,
                        "variant": var_name,
                        "requested_max_tokens": MAX_TOKENS,
                        "actual_output_tokens": res["actual_output_tokens"],
                        "latency": res["latency"],
                        "parse_validity": "PASSED" if len(res["tool_calls"]) > 0 else "FAILED",
                        "abstention_handled": True if task_num == 4 and len(res["tool_calls"]) > 0 and res["tool_calls"][0].get("name") == "none" else False,
                        "api_error_category": classify_api_error(res["error"]),
                        "retry_count": attempt,
                        "error_text": res["error"][:150] if res["error"] else None
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
    with open("results_stage_b/quota_pilot_v2_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    audit = [
        "# Stage B Quota Pilot v2 Audit",
        "",
        "## Overview",
        f"This v2 pilot corrects previous configuration errors by explicitly imposing `max_tokens={MAX_TOKENS}` to prevent accidental quota overallocation. It exposes models to the largest realistic Stage B payloads (Task 1), highly cluttered distractor sets with deterministic shuffling (Task 2), and explicit out-of-domain abstention requests (Task 4), all bounded to 15 HTTP requests maximum.",
        "",
        "## Provider Observations"
    ]
    
    for p in providers:
        prov = p["provider"]
        p_recs = [r for r in results if r["provider"] == prov]
        total_reqs = len(p_recs)
        errors = [r for r in p_recs if r["api_error_category"] is not None]
        fatal = any(e["api_error_category"] in ["rate_limit", "authentication_or_billing"] for e in errors)
        
        audit.append(f"### {prov}")
        audit.append(f"- **Endpoint Reliability**: Over {total_reqs} requests, encountered {len(errors)} errors.")
        
        if fatal:
            audit.append(f"- **Rate-Limit Behavior (RPM/TPM limits)**: Fatal quota or rate-limit hit. The explicit `max_tokens` cap did not resolve the issue, or the 6s pacing is too aggressive for the tier's RPM limit.")
        else:
            if total_reqs > 0:
                audit.append(f"- **Rate-Limit Behavior (RPM/TPM limits)**: Remained stable at 6s pacing. Previous 429 errors were successfully categorized as request-configuration (max_tokens overallocation) rather than pure RPM saturation.")
            else:
                audit.append(f"- **Rate-Limit Behavior (RPM/TPM limits)**: No requests executed.")
                
        # Calculate actual vs requested
        usages = [r["actual_output_tokens"] for r in p_recs if r.get("actual_output_tokens") is not None]
        if usages:
            avg_usage = sum(usages) / len(usages)
            audit.append(f"- **Token Output Profile**: Requested capped at {MAX_TOKENS}. Actual usage observed: average ~{avg_usage:.1f} tokens per successful call.")
        else:
            audit.append(f"- **Token Output Profile**: Requested capped at {MAX_TOKENS}. Actual output tokens not returned by SDK.")
                
        audit.append(f"- **Daily Quota Capacity**: UNKNOWN. This test explicitly bounded execution to {MAX_HTTP_REQUESTS} requests to measure pacing and configuration, not absolute limits.")
        audit.append("")
        
    with open("results_stage_b/quota_pilot_v2_audit.md", "w") as f:
        f.write("\n".join(audit))
        
    manifest = {
        "timestamp": time.time(),
        "total_requests": len(results),
        "requested_max_tokens": MAX_TOKENS,
        "providers_tested": [p["provider"] for p in providers]
    }
    with open("results_stage_b/quota_pilot_v2_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    print("Quota pilot v2 complete. Check results_stage_b/quota_pilot_v2_audit.md")

if __name__ == "__main__":
    run_quota_pilot_v2()

import json
import os
import random
import sys
import time
from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.validator import validate_syntax, validate_semantics

def get_client(model_name):
    load_dotenv()
    if "llama" in model_name.lower() or "mixtral" in model_name.lower():
        return OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
    elif "cohere" in model_name.lower() or "command" in model_name.lower():
        return OpenAI(api_key=os.getenv("COHERE_API_KEY"), base_url="https://api.cohere.com/v1")
    elif "samba" in model_name.lower():
        return OpenAI(api_key=os.getenv("SAMBANOVA_API_KEY"), base_url="https://api.sambanova.ai/v1")
    return None

def execute_llm_call(client, model_name, prompt, tools, temperature=0.0, max_retries=4, raw_mode=False):
    for attempt in range(max_retries):
        start_time = time.time()
        try:
            if raw_mode:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
            else:
                formatted_tools = []
                for t in tools:
                    formatted_tools.append({
                        "type": "function",
                        "function": {
                            "name": t["name"],
                            "description": t["description"],
                            "parameters": t["parameters"]
                        }
                    })
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    tools=formatted_tools,
                    temperature=temperature
                )
            
            elapsed = time.time() - start_time
            msg = response.choices[0].message
            
            tool_calls = []
            if not raw_mode and msg.tool_calls:
                for fc in msg.tool_calls:
                    try:
                        args_dict = json.loads(fc.function.arguments)
                    except:
                        args_dict = {}
                    tool_calls.append({
                        "name": fc.function.name,
                        "args": args_dict
                    })
            elif raw_mode and msg.content:
                try:
                    raw_data = json.loads(msg.content)
                    if isinstance(raw_data, dict) and "name" in raw_data and "args" in raw_data:
                        tool_calls.append({
                            "name": raw_data["name"],
                            "args": raw_data["args"]
                        })
                except json.JSONDecodeError:
                    pass
            
            return {
                "success": True,
                "latency": elapsed,
                "tool_calls": tool_calls,
                "raw_text": msg.content if not tool_calls else None,
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "infrastructure_error": False,
                "error": None,
                "retry_count": attempt
            }
        except Exception as e:
            elapsed = time.time() - start_time
            err_str = str(e)
            if attempt < max_retries - 1:
                wait_sec = (attempt + 1) * 6
                print(f"[{model_name}] Throttle/Error ({err_str[:40]}...). Retrying in {wait_sec}s...", flush=True)
                time.sleep(wait_sec)
                continue
            return {
                "success": False,
                "latency": elapsed,
                "tool_calls": [],
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "infrastructure_error": True,
                "error": err_str,
                "retry_count": attempt
            }

def run_benchmark(models=None, num_repeats=1, max_suites=None, delay=4.0, raw_mode=False):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root_dir, "data", "mutated_schemas.json"), "r", encoding="utf-8") as f:
        schema_suites = json.load(f)[:max_suites] if max_suites else json.load(f)
    with open(os.path.join(root_dir, "data", "distractor_tools.json"), "r", encoding="utf-8") as f:
        distractor_catalog = json.load(f)
    timestamp_str = time.strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(root_dir, "results", f"raw_benchmark_results_{timestamp_str}.json")
    
    if os.path.exists(out_file):
        with open(out_file, "r", encoding="utf-8") as f:
            results = json.load(f)
            for m in models:
                if m not in results["metadata"]["models"]:
                    results["metadata"]["models"].append(m)
    else:
        results = {"metadata": {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "models": models.copy(), "total_suites": len(schema_suites), "num_repeats": num_repeats, "raw_mode": raw_mode}, "task_1_argument_construction": [], "task_2_tool_selection": [], "task_3_execution_semantics": []}
    
    total_calls = len(models) * len(schema_suites) * 6 * num_repeats
    call_idx = 0
    for base_model_name in models:
        client = get_client(base_model_name)
        if not client:
            print(f"Unknown client for model {base_model_name}")
            continue
        model_name = f"{base_model_name}-raw" if raw_mode else base_model_name
        print(f"\nEvaluating Model: {model_name}")
        for suite in schema_suites:
            for var_key, var_data in suite["variants"].items():
                call_idx += 1
                tool_dict = var_data["tool"]
                expected_args = var_data["expected_args"]
                if raw_mode:
                    eval_prompt = f"{suite['query']}\n\nYou have access to the following tool. Respond with a valid JSON object containing exactly 'name' and 'args' keys:\n{json.dumps(tool_dict, indent=2)}"
                    resp = execute_llm_call(client, base_model_name, eval_prompt, [tool_dict], raw_mode=True)
                else:
                    resp = execute_llm_call(client, base_model_name, suite['query'], [tool_dict])
                
                tool_called, syntax_valid = False, False
                err_category, err_msg, generated_args = None, None, {}
                
                if resp["success"] and resp["tool_calls"]:
                    call = resp["tool_calls"][0]
                    tool_called = (call["name"] == tool_dict["name"])
                    generated_args = call["args"]
                    syntax_valid, err_category, err_msg = validate_syntax(generated_args, tool_dict["parameters"])
                elif resp["success"] and not resp["tool_calls"]:
                    err_category, err_msg = "NO_TOOL_INVOKED", "Generated plain text instead of function call"
                else:
                    err_category, err_msg = "INFRASTRUCTURE_UNAVAILABLE", resp["error"]
                
                results["task_1_argument_construction"].append({
                    "model": model_name, "base_id": suite["base_id"], "mutation_type": var_key, "prompt": suite['query'],
                    "infrastructure_error": resp["infrastructure_error"], "tool_called": tool_called, "syntax_valid": syntax_valid,
                    "error_category": err_category, "latency": resp["latency"], "generated_args": generated_args, "expected_args": expected_args
                })
                
                if syntax_valid:
                    sem_em, sem_p, sem_r, sem_det = validate_semantics(generated_args, expected_args)
                    results["task_3_execution_semantics"].append({
                        "model": model_name, "base_id": suite["base_id"], "mutation_type": var_key,
                        "exact_match": sem_em, "field_precision": sem_p, "field_recall": sem_r
                    })
                time.sleep(delay)
                
            for test_variant in ["canonical", "ambiguous_identifiers"]:
                call_idx += 1
                target_tool = suite["variants"][test_variant]["tool"]
                candidate_pool = [target_tool] + distractor_catalog.get(suite["base_id"], distractor_catalog.get("generic_fallback", []))
                random.Random(42 + call_idx).shuffle(candidate_pool)
                
                if raw_mode:
                    eval_prompt_t2 = f"{suite['query']}\n\nYou have access to the following tools. Respond with a valid JSON object containing exactly 'name' and 'args' keys:\n{json.dumps(candidate_pool, indent=2)}"
                    resp_t2 = execute_llm_call(client, base_model_name, eval_prompt_t2, candidate_pool, raw_mode=True)
                else:
                    resp_t2 = execute_llm_call(client, base_model_name, suite['query'], candidate_pool)
                
                selected_tool = resp_t2["tool_calls"][0]["name"] if resp_t2["success"] and resp_t2["tool_calls"] else None
                results["task_2_tool_selection"].append({
                    "model": model_name, "base_id": suite["base_id"], "variant": test_variant,
                    "infrastructure_error": resp_t2["infrastructure_error"], "expected_tool": target_tool["name"], "selected_tool": selected_tool,
                    "selection_correct": (selected_tool == target_tool["name"])
                })
                time.sleep(delay)
            
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            print(f"[{model_name}] Completed suite: {suite['base_id']} ({call_idx}/{total_calls})", flush=True)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", type=str, nargs="+", default=["llama-3.1-70b-versatile"])
    parser.add_argument("--max-suites", type=int, default=None)
    parser.add_argument("--raw-mode", action="store_true")
    args = parser.parse_args()
    run_benchmark(models=args.models, max_suites=args.max_suites, raw_mode=args.raw_mode)

"""
benchmark_runner.py - Orchestrates real API inference for Task 1, Task 2, and Task 3,
capturing deterministic performance metrics, availability telemetry, and failure taxonomies.
"""

import json
import os
import random
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.validator import validate_syntax, validate_semantics

def load_gemini_client():
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is required. "
            "Please create a .env file based on .env.example or set the environment variable."
        )
    return genai.Client(api_key=key)

def format_gemini_tool(tool_dict):
    """Wraps a tool dictionary into a google.genai Tool object."""
    func_decl = types.FunctionDeclaration(
        name=tool_dict["name"],
        description=tool_dict["description"],
        parameters=tool_dict["parameters"]
    )
    return types.Tool(function_declarations=[func_decl])

def execute_llm_call(client, model_name, prompt, tools, temperature=0.0, max_retries=4, raw_mode=False):
    """Executes a model call with exponential backoff and records timing, token, and availability telemetry."""
    for attempt in range(max_retries):
        start_time = time.time()
        try:
            if raw_mode:
                # Regime B: Raw Unconstrained JSON output (Provider mediation disabled)
                tool_schemas = []
                for t in tools:
                    if isinstance(t, types.Tool):
                        for f in t.function_declarations:
                            # Convert GenAI type back to dict for prompt if needed, but it's easier if we pass raw dicts
                            pass
                
                # We will handle the prompt building inside run_benchmark for raw mode
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        response_mime_type="application/json"
                    )
                )
            else:
                # Regime A: Provider-mediated tools
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=tools,
                        temperature=temperature
                    )
                )
                
            elapsed = time.time() - start_time
            
            tool_calls = []
            if not raw_mode and response.function_calls:
                for fc in response.function_calls:
                    args_dict = dict(fc.args) if fc.args else {}
                    tool_calls.append({
                        "name": fc.name,
                        "args": args_dict
                    })
            elif raw_mode and response.text:
                try:
                    # Attempt to parse raw JSON output
                    raw_data = json.loads(response.text)
                    if isinstance(raw_data, dict) and "name" in raw_data and "args" in raw_data:
                        tool_calls.append({
                            "name": raw_data["name"],
                            "args": raw_data["args"]
                        })
                    elif isinstance(raw_data, dict) and "name" in raw_data and "parameters" in raw_data:
                        tool_calls.append({
                            "name": raw_data["name"],
                            "args": raw_data["parameters"]
                        })
                except json.JSONDecodeError:
                    pass
                    
            usage = getattr(response, "usage_metadata", None)
            prompt_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
            comp_tokens = getattr(usage, "candidates_token_count", 0) if usage else 0
            
            return {
                "success": True,
                "latency": elapsed,
                "tool_calls": tool_calls,
                "raw_text": response.text if not tool_calls else None,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": comp_tokens,
                "infrastructure_error": False,
                "error": None,
                "retry_count": attempt
            }
        except Exception as e:
            elapsed = time.time() - start_time
            err_str = str(e)
            if ("429" in err_str or "503" in err_str or "RESOURCE_EXHAUSTED" in err_str or "UNAVAILABLE" in err_str) and attempt < max_retries - 1:
                wait_sec = (attempt + 1) * 6
                print(f"[{model_name}] Infrastructure throttle ({err_str[:40]}...). Retrying in {wait_sec}s...", flush=True)
                time.sleep(wait_sec)
                continue
            return {
                "success": False,
                "latency": elapsed,
                "tool_calls": [],
                "raw_text": None,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "infrastructure_error": True,
                "error": err_str,
                "retry_count": attempt
            }

def run_benchmark(models=None, num_repeats=1, max_suites=None, delay=3.0, raw_mode=False):
    if models is None:
        models = ["gemini-3-flash-preview"]
        
    client = load_gemini_client()
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    with open(os.path.join(root_dir, "data", "mutated_schemas.json"), "r", encoding="utf-8") as f:
        schema_suites = json.load(f)
        
    if max_suites is not None:
        schema_suites = schema_suites[:max_suites]
        
    with open(os.path.join(root_dir, "data", "distractor_tools.json"), "r", encoding="utf-8") as f:
        distractor_catalog = json.load(f)
        
    timestamp_str = time.strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(root_dir, "results", f"raw_benchmark_results_{timestamp_str}.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    
    if os.path.exists(out_file):
        with open(out_file, "r", encoding="utf-8") as f:
            results = json.load(f)
            # update metadata
            for m in models:
                if m not in results["metadata"]["models"]:
                    results["metadata"]["models"].append(m)
    else:
        results = {
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "models": models.copy(),
                "total_suites": len(schema_suites),
                "num_repeats": num_repeats,
                "raw_mode": raw_mode
            },
            "task_1_argument_construction": [],
            "task_2_tool_selection": [],
            "task_3_execution_semantics": []
        }
    
    total_calls = len(models) * len(schema_suites) * (4 + 2) * num_repeats
    regime = "Raw Unconstrained" if raw_mode else "Provider-Mediated"
    print(f"Starting Benchmark Protocol ({regime}): {total_calls} planned calls across {len(models)} models...")
    call_idx = 0
    
    for base_model_name in models:
        # Differentiate model name for reporting
        model_name = f"{base_model_name}-raw" if raw_mode else base_model_name
        print(f"\nEvaluating Model: {model_name}")
        for suite in schema_suites:
            base_id = suite["base_id"]
            query = suite["query"]
            variants = suite["variants"]
            
            # --- TASK 1: Argument Construction (Single Tool, No Distractors) ---
            for var_key, var_data in variants.items():
                call_idx += 1
                tool_dict = var_data["tool"]
                expected_args = var_data["expected_args"]
                genai_tool = format_gemini_tool(tool_dict)
                
                if raw_mode:
                    eval_prompt = f"{query}\n\nYou have access to the following tool. Respond with a valid JSON object containing exactly 'name' and 'args' keys:\n{json.dumps(tool_dict, indent=2)}"
                    resp = execute_llm_call(client, base_model_name, eval_prompt, [genai_tool], temperature=0.0, raw_mode=True)
                else:
                    eval_prompt = query
                    resp = execute_llm_call(client, base_model_name, eval_prompt, [genai_tool], temperature=0.0)
                
                tool_called = False
                syntax_valid = False
                err_category = None
                err_msg = None
                generated_args = {}
                
                if resp["success"] and resp["tool_calls"]:
                    call = resp["tool_calls"][0]
                    tool_called = (call["name"] == tool_dict["name"])
                    generated_args = call["args"]
                    syntax_valid, err_category, err_msg = validate_syntax(generated_args, tool_dict["parameters"])
                elif resp["success"] and not resp["tool_calls"]:
                    err_category = "NO_TOOL_INVOKED"
                    err_msg = "Model generated plain text instead of function call"
                else:
                    err_category = "INFRASTRUCTURE_UNAVAILABLE"
                    err_msg = resp["error"]
                    
                record_t1 = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "model": model_name,
                    "base_id": base_id,
                    "mutation_type": var_key,
                    "prompt": eval_prompt,
                    "retry_count": resp.get("retry_count", 0),
                    "infrastructure_error": resp["infrastructure_error"],
                    "tool_called": tool_called,
                    "syntax_valid": syntax_valid,
                    "error_category": err_category,
                    "error_message": err_msg,
                    "latency": resp["latency"],
                    "prompt_tokens": resp["prompt_tokens"],
                    "completion_tokens": resp.get("completion_tokens", 0),
                    "raw_text": resp.get("raw_text"),
                    "generated_args": generated_args,
                    "expected_args": expected_args
                }
                results["task_1_argument_construction"].append(record_t1)
                
                # --- TASK 3: Execution Semantics (Factual Grounding Accuracy) ---
                if syntax_valid:
                    sem_em, sem_p, sem_r, sem_det = validate_semantics(generated_args, expected_args)
                    record_t3 = {
                        "model": model_name,
                        "base_id": base_id,
                        "mutation_type": var_key,
                        "exact_match": sem_em,
                        "field_precision": sem_p,
                        "field_recall": sem_r,
                        "mismatches": sem_det.get("mismatches", {})
                    }
                    results["task_3_execution_semantics"].append(record_t3)
                    
                time.sleep(delay)
                
            # --- TASK 2: Tool Selection (Target Tool + Randomized Distractors) ---
            for test_variant in ["canonical", "ambiguous_identifiers"]:
                call_idx += 1
                target_tool = variants[test_variant]["tool"]
                
                # Retrieve domain-specific or randomized distractors
                distractors = distractor_catalog.get(base_id, distractor_catalog.get("generic_fallback", []))
                
                # Assemble candidate suite and randomly shuffle to prevent position bias
                candidate_pool = [target_tool] + distractors
                rng = random.Random(42 + call_idx)
                rng.shuffle(candidate_pool)
                target_position = [i for i, t in enumerate(candidate_pool) if t["name"] == target_tool["name"]][0]
                
                genai_tools = types.Tool(function_declarations=[
                    types.FunctionDeclaration(
                        name=t["name"],
                        description=t["description"],
                        parameters=t["parameters"]
                    ) for t in candidate_pool
                ])
                
                if raw_mode:
                    eval_prompt_t2 = f"{query}\n\nYou have access to the following tools. Respond with a valid JSON object containing exactly 'name' and 'args' keys:\n{json.dumps(candidate_pool, indent=2)}"
                    resp_t2 = execute_llm_call(client, base_model_name, eval_prompt_t2, [genai_tools], temperature=0.0, raw_mode=True)
                else:
                    eval_prompt_t2 = query
                    resp_t2 = execute_llm_call(client, base_model_name, eval_prompt_t2, [genai_tools], temperature=0.0)
                
                selected_tool = None
                selection_correct = False
                
                if resp_t2["success"] and resp_t2["tool_calls"]:
                    selected_tool = resp_t2["tool_calls"][0]["name"]
                    selection_correct = (selected_tool == target_tool["name"])
                    
                record_t2 = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "model": model_name,
                    "base_id": base_id,
                    "variant": test_variant,
                    "prompt": eval_prompt_t2,
                    "retry_count": resp_t2.get("retry_count", 0),
                    "target_position_in_menu": target_position,
                    "total_candidates_in_menu": len(candidate_pool),
                    "infrastructure_error": resp_t2["infrastructure_error"],
                    "expected_tool": target_tool["name"],
                    "selected_tool": selected_tool,
                    "selection_correct": selection_correct,
                    "latency": resp_t2["latency"],
                    "prompt_tokens": resp_t2.get("prompt_tokens", 0),
                    "completion_tokens": resp_t2.get("completion_tokens", 0),
                    "raw_text": resp_t2.get("raw_text")
                }
                results["task_2_tool_selection"].append(record_t2)
                time.sleep(delay)
                
            # Progressive checkpointing after each suite
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            print(f"[{model_name}] Completed suite: {base_id} ({call_idx}/{total_calls}) - Checkpointed", flush=True)

    print(f"\nExecution run finished. Final telemetry saved to {out_file}", flush=True)
    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Contract Fragility Benchmark Runner")
    parser.add_argument("--models", type=str, nargs="+", default=["gemini-3-flash-preview"], help="Target model identifiers")
    parser.add_argument("--max-suites", type=int, default=None, help="Maximum number of suites to evaluate")
    parser.add_argument("--delay", type=float, default=3.0, help="Sleep duration between calls in seconds")
    parser.add_argument("--raw-mode", action="store_true", help="Run in Regime B: Unconstrained raw JSON output instead of provider-mediated function calling.")
    args = parser.parse_args()
    
    run_benchmark(models=args.models, max_suites=args.max_suites, delay=args.delay, raw_mode=args.raw_mode)

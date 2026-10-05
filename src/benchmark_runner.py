"""
benchmark_runner.py - Orchestrates real API inference for Task 1, Task 2, and Task 3,
capturing deterministic performance metrics and failure taxonomies.
"""

import json
import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google import genai
from google.genai import types

from src.validator import validate_syntax, validate_semantics

def load_gemini_client():
    env_file = r"C:\Users\rishi\OneDrive\Desktop\zuzu\ZUZU_LightRag\Backend\.env"
    key = os.environ.get("GEMINI_API_KEY")
    if not key and os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not key:
        raise ValueError("GEMINI_API_KEY not found in environment or fallback .env")
    return genai.Client(api_key=key)

def format_gemini_tool(tool_dict):
    """Wraps a tool dictionary into a google.genai Tool object."""
    func_decl = types.FunctionDeclaration(
        name=tool_dict["name"],
        description=tool_dict["description"],
        parameters=tool_dict["parameters"]
    )
    return types.Tool(function_declarations=[func_decl])

def execute_llm_call(client, model_name, prompt, tools, temperature=0.0, max_retries=3):
    """Executes a model call with exponential backoff and records timing and token telemetry."""
    for attempt in range(max_retries):
        start_time = time.time()
        try:
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
            if response.function_calls:
                for fc in response.function_calls:
                    args_dict = dict(fc.args) if fc.args else {}
                    tool_calls.append({
                        "name": fc.name,
                        "args": args_dict
                    })
                    
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
                "error": None
            }
        except Exception as e:
            elapsed = time.time() - start_time
            err_str = str(e)
            if ("429" in err_str or "503" in err_str or "RESOURCE_EXHAUSTED" in err_str) and attempt < max_retries - 1:
                wait_sec = (attempt + 1) * 3
                print(f"[{model_name}] Transient error ({err_str[:40]}...). Retrying in {wait_sec}s...")
                time.sleep(wait_sec)
                continue
            return {
                "success": False,
                "latency": elapsed,
                "tool_calls": [],
                "raw_text": None,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "error": err_str
            }

def run_benchmark(models=None, num_repeats=1):
    if models is None:
        models = ["gemini-flash-latest", "gemini-3.5-flash-lite"]
        
    client = load_gemini_client()
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    with open(os.path.join(root_dir, "data", "mutated_schemas.json"), "r", encoding="utf-8") as f:
        schema_suites = json.load(f)
        
    with open(os.path.join(root_dir, "data", "distractor_tools.json"), "r", encoding="utf-8") as f:
        distractors = json.load(f)
        
    results = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "models": models,
            "total_suites": len(schema_suites),
            "num_repeats": num_repeats
        },
        "task_1_argument_construction": [],
        "task_2_tool_selection": [],
        "task_3_execution_semantics": []
    }
    
    total_calls = len(models) * len(schema_suites) * (4 + 2) * num_repeats
    print(f"Starting Benchmark Execution: {total_calls} total model calls across {len(models)} models...")
    call_idx = 0
    
    for model_name in models:
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
                
                resp = execute_llm_call(client, model_name, query, [genai_tool], temperature=0.0)
                
                # Validation
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
                    err_category = "API_ERROR"
                    err_msg = resp["error"]
                    
                record_t1 = {
                    "model": model_name,
                    "base_id": base_id,
                    "mutation_type": var_key,
                    "tool_called": tool_called,
                    "syntax_valid": syntax_valid,
                    "error_category": err_category,
                    "error_message": err_msg,
                    "latency": resp["latency"],
                    "prompt_tokens": resp["prompt_tokens"],
                    "generated_args": generated_args,
                    "expected_args": expected_args
                }
                results["task_1_argument_construction"].append(record_t1)
                
                # --- TASK 3: Execution Semantics (Factual / Grounding Accuracy) ---
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
                    
                time.sleep(0.6)  # Rate limiting hygiene
                
            # --- TASK 2: Tool Selection (Target Tool + 4 Distractors) ---
            # Compare Canonical vs Ambiguous Identifiers in multi-tool setting
            for test_variant in ["canonical", "ambiguous_identifiers"]:
                call_idx += 1
                target_tool = variants[test_variant]["tool"]
                
                # Build tool suite with 4 distractors
                all_tools_list = [target_tool] + distractors
                genai_tools = types.Tool(function_declarations=[
                    types.FunctionDeclaration(
                        name=t["name"],
                        description=t["description"],
                        parameters=t["parameters"]
                    ) for t in all_tools_list
                ])
                
                resp_t2 = execute_llm_call(client, model_name, query, [genai_tools], temperature=0.0)
                
                selected_tool = None
                selection_correct = False
                
                if resp_t2["success"] and resp_t2["tool_calls"]:
                    selected_tool = resp_t2["tool_calls"][0]["name"]
                    selection_correct = (selected_tool == target_tool["name"])
                    
                record_t2 = {
                    "model": model_name,
                    "base_id": base_id,
                    "variant": test_variant,
                    "expected_tool": target_tool["name"],
                    "selected_tool": selected_tool,
                    "selection_correct": selection_correct,
                    "latency": resp_t2["latency"]
                }
                results["task_2_tool_selection"].append(record_t2)
                time.sleep(0.6)
                
            print(f"[{model_name}] Completed suite: {base_id} ({call_idx}/{total_calls} calls)", flush=True)

    # Save raw results
    out_file = os.path.join(root_dir, "results", "raw_benchmark_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nBenchmark completed successfully! Saved all raw logs to {out_file}")
    return results

if __name__ == "__main__":
    run_benchmark()

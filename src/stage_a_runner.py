import json
import os
import sys
import time
import hashlib
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.validator import validate_syntax, validate_semantics

def get_client(provider, model_name):
    load_dotenv()
    if provider.lower() == "gemini":
        from google import genai
        return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    elif provider.lower() in ["groq", "sambanova", "cohere"]:
        from openai import OpenAI
        base_urls = {
            "groq": "https://api.groq.com/openai/v1",
            "sambanova": "https://api.sambanova.ai/v1",
            "cohere": "https://api.cohere.com/v1"
        }
        key_envs = {"groq": "GROQ_API_KEY", "sambanova": "SAMBANOVA_API_KEY", "cohere": "COHERE_API_KEY"}
        return OpenAI(api_key=os.getenv(key_envs[provider.lower()]), base_url=base_urls[provider.lower()])
    return None

def execute_call(client, provider, model_name, prompt, tools, max_retries=4):
    for attempt in range(max_retries):
        start_time = time.time()
        try:
            if provider.lower() == "gemini":
                from google.genai import types
                genai_tools = []
                for t in tools:
                    genai_tools.append(types.Tool(function_declarations=[
                        types.FunctionDeclaration(name=t["name"], description=t["description"], parameters=t["parameters"])
                    ]))
                resp = client.models.generate_content(
                    model=model_name, contents=prompt, config=types.GenerateContentConfig(tools=genai_tools, temperature=0.0)
                )
                elapsed = time.time() - start_time
                tool_calls = [{"name": fc.name, "args": dict(fc.args) if fc.args else {}} for fc in resp.function_calls] if resp.function_calls else []
                return {"success": True, "latency": elapsed, "tool_calls": tool_calls, "error": None, "retries": attempt, "raw_text": resp.text if not tool_calls else None}
            else:
                formatted_tools = [{"type": "function", "function": t} for t in tools]
                resp = client.chat.completions.create(model=model_name, messages=[{"role": "user", "content": prompt}], tools=formatted_tools, temperature=0.0)
                elapsed = time.time() - start_time
                msg = resp.choices[0].message
                tool_calls = []
                if msg.tool_calls:
                    for fc in msg.tool_calls:
                        try: args_dict = json.loads(fc.function.arguments)
                        except: args_dict = {}
                        tool_calls.append({"name": fc.function.name, "args": args_dict})
                return {"success": True, "latency": elapsed, "tool_calls": tool_calls, "error": None, "retries": attempt, "raw_text": msg.content if not tool_calls else None}
        except Exception as e:
            elapsed = time.time() - start_time
            if attempt < max_retries - 1:
                time.sleep((attempt + 1) * 6)
                continue
            return {"success": False, "latency": elapsed, "tool_calls": [], "error": str(e), "retries": attempt, "raw_text": None}

def run_stage_a(providers_models, repeats=3):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root_dir, "data", "pilot_manifest.json"), "r") as f:
        manifest = json.load(f)
    with open(os.path.join(root_dir, "data", "distractor_tools.json"), "r") as f:
        distractor_catalog = json.load(f)
    with open(os.path.join(root_dir, "data", "mutated_schemas.json"), "r") as f:
        full_schemas = {d["base_id"]: d for d in json.load(f)}

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(root_dir, "results", f"stage_a_results_{timestamp}.json")
    results = []

    for provider, model_name in providers_models:
        client = get_client(provider, model_name)
        if not client: continue
        for r in range(repeats):
            for schema_meta in manifest["schemas"]:
                base_id = schema_meta["base_id"]
                item = full_schemas[base_id]
                query = item["query"]
                prompt_hash = hashlib.sha256(query.encode('utf-8')).hexdigest()

                # Task 1 & 3
                for var_key, var_data in item["variants"].items():
                    tool = var_data["tool"]
                    schema_hash = hashlib.sha256(json.dumps(tool, sort_keys=True).encode('utf-8')).hexdigest()
                    resp = execute_call(client, provider, model_name, query, [tool])
                    
                    record = {
                        "provider": provider, "model": model_name, "repeat": r, "task": 1, "base_id": base_id, "variant": var_key,
                        "prompt_hash": prompt_hash, "schema_hash": schema_hash, "latency": resp["latency"], "retries": resp["retries"],
                        "error": resp["error"], "tool_calls": resp["tool_calls"]
                    }
                    results.append(record)

                # Task 2
                for var_key in ["canonical", "ambiguous_identifiers"]:
                    target_tool = item["variants"][var_key]["tool"]
                    pool = [target_tool] + distractor_catalog.get(base_id, [])
                    resp = execute_call(client, provider, model_name, query, pool)
                    
                    record = {
                        "provider": provider, "model": model_name, "repeat": r, "task": 2, "base_id": base_id, "variant": var_key,
                        "latency": resp["latency"], "retries": resp["retries"], "error": resp["error"], "tool_calls": resp["tool_calls"]
                    }
                    results.append(record)
                    
                with open(out_file, "w") as f:
                    json.dump(results, f, indent=2)

    print(f"Stage A Pilot complete. Results saved to {out_file}")

if __name__ == "__main__":
    # Expects python src/stage_a_runner.py Gemini:gemini-3.1-flash-lite-preview
    import sys
    providers = []
    for arg in sys.argv[1:]:
        p, m = arg.split(":")
        providers.append((p, m))
    run_stage_a(providers)

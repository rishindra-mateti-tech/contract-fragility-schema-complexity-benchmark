import json
import os
import sys
import time
import hashlib
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def execute_call(client, provider, model_name, prompt, tools, max_retries=4):
    for attempt in range(max_retries):
        start_time = time.time()
        try:
            if provider.lower() == "gemini":
                # Track A: Provider-Mediated
                from google.genai import types
                genai_tools = [types.Tool(function_declarations=[
                    types.FunctionDeclaration(name=t["name"], description=t["description"], parameters=t["parameters"])
                ]) for t in tools]
                resp = client.models.generate_content(
                    model=model_name, contents=prompt, config=types.GenerateContentConfig(tools=genai_tools, temperature=0.0)
                )
                elapsed = time.time() - start_time
                tool_calls = [{"name": fc.name, "args": dict(fc.args) if fc.args else {}} for fc in resp.function_calls] if resp.function_calls else []
                return {"success": True, "latency": elapsed, "tool_calls": tool_calls, "error": None, "retries": attempt, "raw_text": resp.text if not tool_calls else None}
                
            elif provider.lower() == "groq":
                # Track B: Raw JSON via OpenAI compat
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
                return {"success": True, "latency": elapsed, "tool_calls": tool_calls, "error": None, "retries": attempt, "raw_text": content if not tool_calls else None}
                
            elif provider.lower() == "cohere":
                # Track B: Raw JSON via native Cohere SDK
                raw_prompt = f"{prompt}\n\nYou must respond with a raw JSON object containing exactly 'name' (string) and 'args' (object) matching one of the following tools:\n{json.dumps(tools, indent=2)}"
                resp = client.chat(model=model_name, message=raw_prompt, temperature=0.0)
                elapsed = time.time() - start_time
                content = resp.text.strip()
                # strip markdown codeblocks if they exist
                if content.startswith("```json"): content = content[7:]
                if content.startswith("```"): content = content[3:]
                if content.endswith("```"): content = content[:-3]
                tool_calls = []
                try:
                    data = json.loads(content.strip())
                    if "name" in data and "args" in data: tool_calls.append(data)
                except: pass
                return {"success": True, "latency": elapsed, "tool_calls": tool_calls, "error": None, "retries": attempt, "raw_text": resp.text if not tool_calls else None}
                
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

    total_calls = len(providers_models) * len(manifest["schemas"]) * 6 * repeats
    current_call = 0

    for provider, model_name in providers_models:
        client = get_client(provider)
        if not client: continue
        for r in range(repeats):
            for schema_meta in manifest["schemas"]:
                base_id = schema_meta["base_id"]
                item = full_schemas[base_id]
                query = item["query"]
                prompt_hash = hashlib.sha256(query.encode('utf-8')).hexdigest()

                # Task 1 (4 variants)
                for var_key, var_data in item["variants"].items():
                    current_call += 1
                    tool = var_data["tool"]
                    schema_hash = hashlib.sha256(json.dumps(tool, sort_keys=True).encode('utf-8')).hexdigest()
                    resp = execute_call(client, provider, model_name, query, [tool])
                    
                    results.append({
                        "provider": provider, "model": model_name, "track": "Track A" if provider=="gemini" else "Track B",
                        "repeat": r, "task": 1, "base_id": base_id, "variant": var_key,
                        "prompt_hash": prompt_hash, "schema_hash": schema_hash, "latency": resp["latency"], 
                        "retries": resp["retries"], "error": resp["error"], "tool_calls": resp["tool_calls"]
                    })
                    print(f"[{provider}:{model_name}] T1 {base_id} {var_key} ({current_call}/{total_calls})")
                    with open(out_file, "w") as f: json.dump(results, f, indent=2)

                # Task 2 (2 variants)
                for var_key in ["canonical", "ambiguous_identifiers"]:
                    current_call += 1
                    target_tool = item["variants"][var_key]["tool"]
                    schema_hash = hashlib.sha256(json.dumps(target_tool, sort_keys=True).encode('utf-8')).hexdigest()
                    pool = [target_tool] + distractor_catalog.get(base_id, [])
                    resp = execute_call(client, provider, model_name, query, pool)
                    
                    results.append({
                        "provider": provider, "model": model_name, "track": "Track A" if provider=="gemini" else "Track B",
                        "repeat": r, "task": 2, "base_id": base_id, "variant": var_key,
                        "prompt_hash": prompt_hash, "schema_hash": schema_hash, "latency": resp["latency"], 
                        "retries": resp["retries"], "error": resp["error"], "tool_calls": resp["tool_calls"]
                    })
                    print(f"[{provider}:{model_name}] T2 {base_id} {var_key} ({current_call}/{total_calls})")
                    with open(out_file, "w") as f: json.dump(results, f, indent=2)

if __name__ == "__main__":
    import sys
    providers = []
    for arg in sys.argv[1:]:
        p, m = arg.split(":")
        providers.append((p, m))
    run_stage_a(providers)

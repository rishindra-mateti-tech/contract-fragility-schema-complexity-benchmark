import os
import json
import time
import hashlib
from dotenv import load_dotenv

MULTI_TOOL_PROMPT = """You are a helpful assistant. Please execute the appropriate function based on the user request.
Request: "I need to ping the system to verify it's online."

You must respond with a raw JSON object containing exactly 'name' (string) and 'args' (object) matching one of the following tools:
[
  {
    "name": "ping",
    "description": "Pings the system",
    "parameters": {
      "type": "object",
      "properties": {}
    }
  },
  {
    "name": "unrelated_tool",
    "description": "Does something else",
    "parameters": {
      "type": "object",
      "properties": {"foo": {"type": "string"}}
    }
  }
]"""

EXCLUDE_TERMS = ['guard', 'safeguard', 'moderation', 'whisper', 'speech', 'audio', 'vision-only', 'embedding', 'rerank', 'tts', 'image']

def is_eligible_model(model_id, allowlist):
    mid = model_id.lower()
    for term in EXCLUDE_TERMS:
        if term in mid:
            return False
    for allow in allowlist:
        if allow in mid:
            return True
    return False

def test_groq():
    from openai import OpenAI
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return {"provider": "Groq", "status": "No API Key found"}
        
    try:
        client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
        models_resp = client.models.list()
        all_models = [m.id for m in models_resp.data]
        
        allowlist = ["llama-3", "llama3", "qwen", "gemma", "mixtral"]
        chat_models = [m for m in all_models if is_eligible_model(m, allowlist)]
        
        if not chat_models:
            return {"provider": "Groq", "status": "No eligible conversational models found in API"}
            
        selected_model = chat_models[0] # Pick the first eligible, NEVER the last index
        
        resp = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "user", "content": MULTI_TOOL_PROMPT}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        content = resp.choices[0].message.content
        parse_outcome = "FAILED"
        try:
            data = json.loads(content)
            if "name" in data and "args" in data:
                parse_outcome = "PASSED"
        except:
            pass
            
        return {
            "provider": "Groq",
            "model_id": selected_model,
            "track": "Track B",
            "native_tool_calling": False,
            "raw_json_supported": True,
            "availability": "Endpoint Reachable",
            "quota_status": "Quota Unknown; pilot required",
            "parse_outcome": parse_outcome,
            "raw_response": content,
            "timestamp": time.time(),
            "model_list_hash": hashlib.sha256(json.dumps(all_models).encode()).hexdigest(),
            "raw_models": all_models
        }
    except Exception as e:
        return {"provider": "Groq", "status": f"API Error: {str(e)[:150]}"}

def test_cohere():
    try:
        import cohere
    except ImportError:
        return {"provider": "Cohere", "status": "cohere SDK missing"}
        
    key = os.getenv("COHERE_API_KEY")
    if not key:
        return {"provider": "Cohere", "status": "No API Key found"}
        
    try:
        co = cohere.Client(api_key=key)
        # We test a known conversational model for Cohere 
        # (cohere python SDK doesn't natively expose a clean .models.list() for chat without experimental APIs)
        all_models = ["command-r-plus-08-2024", "command-r-08-2024"]
        allowlist = ["command-r"]
        chat_models = [m for m in all_models if is_eligible_model(m, allowlist)]
        
        if not chat_models:
            return {"provider": "Cohere", "status": "No eligible conversational models"}
            
        selected_model = chat_models[0]
        
        resp = co.chat(
            model=selected_model,
            message=MULTI_TOOL_PROMPT,
            temperature=0.0
        )
        
        content = resp.text.strip()
        if content.startswith("```json"): content = content[7:]
        if content.startswith("```"): content = content[3:]
        if content.endswith("```"): content = content[:-3]
        content = content.strip()
        
        parse_outcome = "FAILED"
        try:
            data = json.loads(content)
            if "name" in data and "args" in data:
                parse_outcome = "PASSED"
        except:
            pass
            
        return {
            "provider": "Cohere",
            "model_id": selected_model,
            "track": "Track B",
            "native_tool_calling": False,
            "raw_json_supported": True,
            "availability": "Endpoint Reachable",
            "quota_status": "Quota Unknown; pilot required",
            "parse_outcome": parse_outcome,
            "raw_response": content,
            "timestamp": time.time(),
            "model_list_hash": hashlib.sha256(json.dumps(all_models).encode()).hexdigest(),
            "raw_models": all_models
        }
    except Exception as e:
        return {"provider": "Cohere", "status": f"API Error: {str(e)[:150]}"}

def test_gemini():
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return {"provider": "Gemini", "status": "google.genai SDK missing"}
        
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return {"provider": "Gemini", "status": "No API Key found"}
        
    try:
        client = genai.Client(api_key=key)
        models_resp = client.models.list()
        all_models = [m.name for m in models_resp if m.name.startswith("models/")]
        
        allowlist = ["gemini-1.5", "gemini-2.0"]
        chat_models = [m.split("/")[-1] for m in all_models if is_eligible_model(m, allowlist)]
        
        if not chat_models:
            return {"provider": "Gemini", "status": "No eligible conversational models found in API"}
            
        # Select first matching model
        selected_model = chat_models[0]
        
        tools = [
            types.Tool(function_declarations=[types.FunctionDeclaration(name="ping", description="Pings the system", parameters={"type":"object","properties":{}})]),
            types.Tool(function_declarations=[types.FunctionDeclaration(name="unrelated_tool", description="Does something else", parameters={"type":"object","properties":{"foo": {"type": "string"}}})])
        ]
        
        resp = client.models.generate_content(
            model=selected_model,
            contents="I need to ping the system to verify it's online.",
            config=types.GenerateContentConfig(tools=tools, temperature=0.0)
        )
        
        parse_outcome = "FAILED"
        content = ""
        if resp.function_calls and resp.function_calls[0].name == "ping":
            parse_outcome = "PASSED"
            content = f"ToolCall({resp.function_calls[0].name})"
        else:
            content = str(resp.text)
            
        return {
            "provider": "Gemini",
            "model_id": selected_model,
            "track": "Track A",
            "native_tool_calling": True,
            "raw_json_supported": False,
            "availability": "Endpoint Reachable",
            "quota_status": "Quota Unknown; pilot required",
            "parse_outcome": parse_outcome,
            "raw_response": content,
            "timestamp": time.time(),
            "model_list_hash": hashlib.sha256(json.dumps(all_models).encode()).hexdigest(),
            "raw_models": all_models
        }
    except Exception as e:
        return {"provider": "Gemini", "status": f"API Error: {str(e)[:150]}"}

def main():
    load_dotenv()
    results = []
    
    print("Running Groq preflight v2...")
    results.append(test_groq())
    
    print("Running Cohere preflight v2...")
    results.append(test_cohere())
    
    print("Running Gemini preflight v2...")
    results.append(test_gemini())
    
    os.makedirs("results_stage_b", exist_ok=True)
    
    with open("results_stage_b/stage_b_models_snapshot_v2.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n--- STAGE B PREFLIGHT REPORT (v2) ---")
    valid_models = 0
    for r in results:
        if r.get("availability") == "Endpoint Reachable" and r.get("parse_outcome") == "PASSED":
            valid_models += 1
            print(f"[PASS] {r['provider']} | Model: {r['model_id']} | Track: {r['track']} | Hash: {r['model_list_hash'][:8]}")
            print(f"       Parse Outcome: {r['parse_outcome']} | Quota: {r['quota_status']}")
        else:
            reason = r.get("status", f"Parse Outcome: {r.get('parse_outcome')}, Raw: {r.get('raw_response', '')[:50]}")
            print(f"[FAIL] {r.get('provider', 'Unknown')} | {reason}")
            
    print(f"\nTotal Validated Conversational Models (M): {valid_models}")
    
    if valid_models < 2:
        print("WARNING: Less than 2 validated models. Do not proceed with Stage B ingestion.")
        
    # Calculate calls based on valid models
    S = 80
    V = 4
    T = 3
    R = 3
    base_calls = S * V * T * R * valid_models
    max_guard = int(base_calls * 1.1)
    
    print(f"\n--- STAGE B CALL BUDGET (v2) ---")
    print(f"Schemas (S): {S}")
    print(f"Variants (V): {V}")
    print(f"Tasks (T): {T} (Construction, Selection, Abstention)")
    print(f"Repeats (R): {R}")
    print(f"Models (M): {valid_models}")
    print(f"Total Base Calls: {base_calls}")
    print(f"Strict MAX_CALLS Guard (110%): {max_guard}")
    
    summary = {
        "valid_models_count": valid_models,
        "base_calls": base_calls,
        "max_calls_guard": max_guard
    }
    with open("results_stage_b/stage_b_preflight_report_v2.json", "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()

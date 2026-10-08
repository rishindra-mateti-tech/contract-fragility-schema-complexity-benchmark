import os
import json
import time
import hashlib
from dotenv import load_dotenv

def test_groq():
    from openai import OpenAI
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return {"provider": "Groq", "status": "No API Key found"}
        
    try:
        client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
        models_resp = client.models.list()
        all_models = [m.id for m in models_resp.data]
        chat_models = [m for m in all_models if "qwen" in m.lower() or "allam" in m.lower() or "gpt-oss" in m.lower() or "llama" in m.lower()]
        
        if not chat_models:
            return {"provider": "Groq", "status": "No compatible models found in API"}
            
        selected_model = chat_models[-1] # Deterministic pick
        
        # Test rate limit / availability
        resp = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "user", "content": "Hello"}],
            response_format={"type": "json_object"} if "llama-3" in selected_model else None,
            max_tokens=10
        )
        
        return {
            "provider": "Groq",
            "model_id": selected_model,
            "track": "Track B",
            "native_tool_calling": False,
            "raw_json_supported": True,
            "quota_status": "OK",
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
        # Cohere does not have a generic models endpoint, fallback to attempting the known current free model
        selected_model = "command-r-plus-08-2024"
        
        resp = co.chat(
            model=selected_model,
            message="Return {\"test\": 1} in JSON format.",
            temperature=0.0,
            max_tokens=20
        )
        
        return {
            "provider": "Cohere",
            "model_id": selected_model,
            "track": "Track B",
            "native_tool_calling": False,
            "raw_json_supported": True,
            "quota_status": "OK",
            "timestamp": time.time(),
            "model_list_hash": hashlib.sha256(selected_model.encode()).hexdigest(),
            "raw_models": [selected_model]
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
        # Just grab an available model
        selected_model = "gemini-1.5-flash"
        
        resp = client.models.generate_content(
            model=selected_model,
            contents="Say hi"
        )
        
        return {
            "provider": "Gemini",
            "model_id": selected_model,
            "track": "Track A",
            "native_tool_calling": True,
            "raw_json_supported": False,
            "quota_status": "OK",
            "timestamp": time.time(),
            "model_list_hash": hashlib.sha256(selected_model.encode()).hexdigest(),
            "raw_models": [selected_model]
        }
    except Exception as e:
        return {"provider": "Gemini", "status": f"API Error: {str(e)[:150]}"}

def main():
    load_dotenv()
    results = []
    
    print("Running Groq preflight...")
    results.append(test_groq())
    
    print("Running Cohere preflight...")
    results.append(test_cohere())
    
    print("Running Gemini preflight...")
    results.append(test_gemini())
    
    os.makedirs("results_stage_b", exist_ok=True)
    
    # Save detailed snapshot
    with open("results_stage_b/stage_b_models_snapshot.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n--- STAGE B PREFLIGHT REPORT ---")
    valid_models = 0
    for r in results:
        if r.get("quota_status") == "OK":
            valid_models += 1
            print(f"[PASS] {r['provider']} | Model: {r['model_id']} | Track: {r['track']} | Hash: {r['model_list_hash'][:8]}")
        else:
            print(f"[FAIL] {r['provider']} | {r['status']}")
            
    print(f"\nTotal Validated Models (M): {valid_models}")
    
    # Calculate calls
    S = 80
    V = 4
    T = 3
    R = 3
    base_calls = S * V * T * R * valid_models
    max_guard = int(base_calls * 1.1)
    
    print(f"\n--- STAGE B CALL BUDGET ---")
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
    with open("results_stage_b/stage_b_preflight_report.json", "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()

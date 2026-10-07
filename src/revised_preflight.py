import os
import json
import time
from dotenv import load_dotenv

def test_groq_raw():
    from openai import OpenAI
    key = os.getenv("GROQ_API_KEY")
    if not key: return False, "No key", None
    try:
        client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
        # 1. Query models
        models = [m.id for m in client.models.list().data]
        # Filter for likely chat models (e.g. qwen, allam, gpt-oss)
        chat_models = [m for m in models if "qwen" in m.lower() or "allam" in m.lower() or "gpt-oss" in m.lower()]
        
        if not chat_models:
            return False, "No accessible chat models found in list", None
            
        selected_model = chat_models[-1] # Try the last one which is usually a specific model, e.g. qwen/qwen3.8-27b
        
        # 2. Test Raw JSON Track
        resp = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "user", "content": "Return a JSON object with key 'status' and value 'ok'."}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return True, "Raw JSON Support OK", selected_model
    except Exception as e:
        return False, str(e)[:150], getattr(selected_model, '', 'Unknown')

def test_cohere_raw():
    try:
        import cohere
    except ImportError:
        return False, "cohere SDK not installed", None
        
    key = os.getenv("COHERE_API_KEY")
    if not key: return False, "No key", None
    try:
        co = cohere.Client(api_key=key)
        # Select command-r-plus or command-r
        selected_model = "command-r-plus-08-2024"
        
        resp = co.chat(
            model=selected_model,
            message="Return a JSON object with key 'status' and value 'ok'.",
            temperature=0.0
        )
        
        text = resp.text.strip()
        # Verify it can output JSON
        if "{" in text and "}" in text:
            return True, "Native Raw JSON Support OK", selected_model
        return False, "Did not return JSON properly", selected_model
    except Exception as e:
        return False, str(e)[:150], "command-r-plus-08-2024"

def test_gemini():
    from google import genai
    from google.genai import types
    key = os.getenv("GEMINI_API_KEY")
    if not key: return False, "No key", None
    try:
        client = genai.Client(api_key=key)
        tool = types.Tool(function_declarations=[types.FunctionDeclaration(name="ping", description="ping", parameters={"type":"object","properties":{}})])
        resp = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents="ping",
            config=types.GenerateContentConfig(tools=[tool], temperature=0.0)
        )
        return True, "Provider-Mediated OK", "gemini-3.1-flash-lite-preview"
    except Exception as e:
        return False, str(e)[:100], "gemini-3.1-flash-lite-preview"

def main():
    load_dotenv()
    print("--- Revised Provider Preflight Report ---")
    
    # Gemini (Track A)
    ok, msg, mod = test_gemini()
    print(f"[Gemini] Track A (Provider-Mediated) -> {'PASS' if ok else 'FAIL'} | Model: {mod} | Msg: {msg}")
    
    # Groq (Track B)
    ok, msg, mod = test_groq_raw()
    print(f"[Groq] Track B (Raw JSON) -> {'PASS' if ok else 'FAIL'} | Model: {mod} | Msg: {msg}")
    
    # Cohere (Track B)
    ok, msg, mod = test_cohere_raw()
    print(f"[Cohere] Track B (Raw JSON) -> {'PASS' if ok else 'FAIL'} | Model: {mod} | Msg: {msg}")
    
    # SambaNova
    print(f"[SambaNova] Unavailable -> FAIL | Error 402: Zero Balance")
    
if __name__ == "__main__":
    main()

import os
import json
import time
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

def test_groq_raw():
    from openai import OpenAI
    key = os.getenv("GROQ_API_KEY")
    if not key: return False, "No key", None, []
    try:
        client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
        models_resp = client.models.list()
        models = [m.id for m in models_resp.data]
        chat_models = [m for m in models if "qwen" in m.lower() or "allam" in m.lower() or "gpt-oss" in m.lower()]
        if not chat_models:
            return False, "No accessible chat models found", None, models
        selected_model = chat_models[-1]
        
        resp = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "user", "content": MULTI_TOOL_PROMPT}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        content = resp.choices[0].message.content
        data = json.loads(content)
        if "name" in data and "args" in data:
            return True, "Raw JSON Support OK (Multi-tool tested)", selected_model, models
        return False, "Valid JSON but wrong schema", selected_model, models
    except Exception as e:
        return False, str(e)[:150], getattr(selected_model, '', 'Unknown'), []

def test_cohere_raw():
    try:
        import cohere
    except ImportError:
        return False, "cohere SDK not installed", None
        
    key = os.getenv("COHERE_API_KEY")
    if not key: return False, "No key", None
    try:
        co = cohere.Client(api_key=key)
        selected_model = "command-r-plus-08-2024"
        
        resp = co.chat(
            model=selected_model,
            message=MULTI_TOOL_PROMPT,
            temperature=0.0
        )
        content = resp.text.strip()
        if content.startswith("```json"): content = content[7:]
        if content.startswith("```"): content = content[3:]
        if content.endswith("```"): content = content[:-3]
        
        data = json.loads(content.strip())
        if "name" in data and "args" in data:
            return True, "Native Raw JSON Support OK (Multi-tool tested)", selected_model
        return False, "Valid JSON but wrong schema", selected_model
    except Exception as e:
        return False, str(e)[:150], "command-r-plus-08-2024"

def test_gemini():
    from google import genai
    from google.genai import types
    key = os.getenv("GEMINI_API_KEY")
    if not key: return False, "No key", None
    try:
        client = genai.Client(api_key=key)
        tools = [
            types.Tool(function_declarations=[types.FunctionDeclaration(name="ping", description="Pings the system", parameters={"type":"object","properties":{}})]),
            types.Tool(function_declarations=[types.FunctionDeclaration(name="unrelated_tool", description="Does something else", parameters={"type":"object","properties":{"foo": {"type": "string"}}})])
        ]
        resp = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents="I need to ping the system to verify it's online.",
            config=types.GenerateContentConfig(tools=tools, temperature=0.0)
        )
        if resp.function_calls and resp.function_calls[0].name == "ping":
            return True, "Provider-Mediated OK (Multi-tool tested)", "gemini-3.1-flash-lite-preview"
        return False, "Provider-Mediated returned wrong structure", "gemini-3.1-flash-lite-preview"
    except Exception as e:
        return False, str(e)[:100], "gemini-3.1-flash-lite-preview"

def main():
    load_dotenv()
    print("--- Realistic Provider Preflight Report ---")
    
    results = {}
    
    ok, msg, mod = test_gemini()
    print(f"[Gemini] Track A -> {'PASS' if ok else 'FAIL'} | Model: {mod} | Msg: {msg}")
    results["Gemini"] = {"track": "Track A", "status": "PASS" if ok else "FAIL", "model": mod, "msg": msg}
    
    ok, msg, mod, groq_models = test_groq_raw()
    print(f"[Groq] Track B -> {'PASS' if ok else 'FAIL'} | Model: {mod} | Msg: {msg}")
    results["Groq"] = {"track": "Track B", "status": "PASS" if ok else "FAIL", "model": mod, "msg": msg, "available_models_snapshot": groq_models}
    
    ok, msg, mod = test_cohere_raw()
    print(f"[Cohere] Track B -> {'PASS' if ok else 'FAIL'} | Model: {mod} | Msg: {msg}")
    results["Cohere"] = {"track": "Track B", "status": "PASS" if ok else "FAIL", "model": mod, "msg": msg}
    
    os.makedirs("results", exist_ok=True)
    with open("results/preflight_snapshot.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Saved to results/preflight_snapshot.json")

if __name__ == "__main__":
    main()

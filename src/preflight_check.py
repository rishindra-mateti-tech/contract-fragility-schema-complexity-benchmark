import os
from dotenv import load_dotenv
import json

def test_gemini():
    from google import genai
    from google.genai import types
    key = os.getenv("GEMINI_API_KEY")
    if not key: return False, "No key"
    try:
        client = genai.Client(api_key=key)
        tool = types.Tool(function_declarations=[types.FunctionDeclaration(name="ping", description="ping", parameters={"type":"object","properties":{}})])
        resp = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents="ping",
            config=types.GenerateContentConfig(tools=[tool], temperature=0.0)
        )
        return True, "gemini-3.1-flash-lite-preview OK"
    except Exception as e:
        return False, str(e)[:100]

def test_openai_compat(provider, key_env, base_url, model):
    from openai import OpenAI
    key = os.getenv(key_env)
    if not key: return False, "No key"
    try:
        client = OpenAI(api_key=key, base_url=base_url)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role":"user", "content":"ping"}],
            tools=[{"type":"function", "function":{"name":"ping","description":"ping","parameters":{"type":"object","properties":{}}}}],
            temperature=0.0
        )
        return True, f"{model} OK on {provider}"
    except Exception as e:
        return False, str(e)[:100]

def main():
    load_dotenv()
    results = {}
    print("--- Provider Preflight Check ---")
    
    # Gemini
    ok, msg = test_gemini()
    results['Gemini'] = {"model": "gemini-3.1-flash-lite-preview", "status": "PASS" if ok else "FAIL", "msg": msg}
    
    # Groq
    ok, msg = test_openai_compat("Groq", "GROQ_API_KEY", "https://api.groq.com/openai/v1", "llama-3.3-70b-versatile")
    results['Groq'] = {"model": "llama-3.3-70b-versatile", "status": "PASS" if ok else "FAIL", "msg": msg}
    
    # Cohere
    ok, msg = test_openai_compat("Cohere", "COHERE_API_KEY", "https://api.cohere.com/v1", "command-r-plus-08-2024")
    results['Cohere'] = {"model": "command-r-plus-08-2024", "status": "PASS" if ok else "FAIL", "msg": msg}
    
    # SambaNova
    ok, msg = test_openai_compat("SambaNova", "SAMBANOVA_API_KEY", "https://api.sambanova.ai/v1", "Meta-Llama-3.3-70B-Instruct")
    results['SambaNova'] = {"model": "Meta-Llama-3.3-70B-Instruct", "status": "PASS" if ok else "FAIL", "msg": msg}

    valid_count = sum(1 for r in results.values() if r["status"] == "PASS")
    
    for prov, data in results.items():
        print(f"[{prov}] {data['model']} -> {data['status']} ({data['msg']})")
        
    print(f"\nTotal Valid Providers: {valid_count}/3 Required")

if __name__ == '__main__':
    main()

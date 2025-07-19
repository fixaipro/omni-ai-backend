# main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Optional
import os
from dotenv import load_dotenv
import requests
from duckduckgo_search import ddg
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()

# Required API keys
gemini_key = os.getenv("GEMINI_API_KEY")
mistral_key = os.getenv("MISTRAL_API_KEY")
if not (gemini_key and mistral_key):
    raise RuntimeError("Both GEMINI_API_KEY and MISTRAL_API_KEY must be set in environment variables.")

# Configure Gemini SDK
genai.configure(api_key=gemini_key)
app = FastAPI()

@app.post("/summary")
async def summary_endpoint(
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None)
):
    # Determine the prompt: prefer text input
    prompt = text or ""
    # audio and image are accepted but not processed in this version
    if not prompt:
        raise HTTPException(status_code=400, detail="Please provide at least text input.")

    # 1) Web search using DuckDuckGo\    
    results = ddg(prompt, max_results=1) or []
    web_snippet = results[0].get('body') if results else ""

    # 2) Query Gemini (text)
    gemini_model = genai.get_model("models/gemini-pro")
    gemini_resp = gemini_model.generate(prompt=prompt, temperature=0.7, max_output_tokens=512)
    gemini_text = gemini_resp.text.strip()

    # 3) Query Mistral
    mistral_url = "https://api.mistral.ai/v1/models/mistral-7b-instruct/generate"
    hdrs = {"Authorization": f"Bearer {mistral_key}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "max_tokens": 512, "temperature": 0.7}
    r = requests.post(mistral_url, headers=hdrs, json=payload)
    mjson = r.json()
    mistral_text = mjson.get("choices", [{}])[0].get("text", "").strip()

    # 4) Final summary via Mistral
    summary_input = (
        f"Web snippet: {web_snippet}\n"
        f"Gemini: {gemini_text}\n"
        f"Mistral: {mistral_text}\n"
    )
    spayload = {"prompt": f"Summarize the key points from these:\n{summary_input}", "max_tokens": 256, "temperature": 0.5}
    sresp = requests.post(mistral_url, headers=hdrs, json=spayload)
    sjson = sresp.json()
    summary = sjson.get("choices", [{}])[0].get("text", "").strip()

    return {"web": web_snippet, "gemini": gemini_text, "mistral": mistral_text, "summary": summary}

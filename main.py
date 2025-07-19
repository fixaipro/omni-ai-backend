```python
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
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
MISTRAL_KEY = os.getenv("MISTRAL_API_KEY")

if not GEMINI_KEY or not MISTRAL_KEY:
    raise RuntimeError("Both GEMINI_API_KEY and MISTRAL_API_KEY must be set in environment variables.")

# Configure Gemini SDK
genai.configure(api_key=GEMINI_KEY)

app = FastAPI()

@app.post("/summary")
async def summary_endpoint(
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None)
):
    # Determine the prompt: prefer text input
    prompt = text
    if audio:
        # Audio transcription not supported in this version
        prompt = prompt or ""
    if image:
        # Image analysis not implemented in this version
        prompt = prompt or ""

    if not prompt:
        raise HTTPException(status_code=400, detail="Please provide at least text, audio, or image input.")

    # 1) Web search using DuckDuckGo
    search_results = ddg(prompt, max_results=1) or []
    web_snippet = search_results[0].get('body') if search_results else None

    # 2) Query Gemini (text)
    gemini_model = genai.get_model("models/gemini-pro")
    gemini_response = gemini_model.generate(
        prompt=prompt,
        temperature=0.7,
        max_output_tokens=512
    )
    gemini_text = gemini_response.text.strip()

    # 3) Query Mistral
    mistral_url = "https://api.mistral.ai/v1/models/mistral-7b-instruct/generate"
    headers = {
        "Authorization": f"Bearer {MISTRAL_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.7
    }
    mistral_resp = requests.post(mistral_url, headers=headers, json=payload)
    mistral_json = mistral_resp.json()
    mistral_text = mistral_json.get("choices", [{}])[0].get("text", "")

    # 4) Final combined summary using Mistral
    summary_prompt = (
        f"Summarize the key points from these sources:\n"
        f"Web search snippet: {web_snippet}\n"
        f"Gemini says: {gemini_text}\n"
        f"Mistral says: {mistral_text}\n"
    )
    summary_payload = {
        "prompt": summary_prompt,
        "max_tokens": 256,
        "temperature": 0.5
    }
    summary_resp = requests.post(mistral_url, headers=headers, json=summary_payload)
    summary_json = summary_resp.json()
    summary_text = summary_json.get("choices", [{}])[0].get("text", "")

    return {
        "web": web_snippet,
        "gemini": gemini_text,
        "mistral": mistral_text,
        "summary": summary_text
    }
```

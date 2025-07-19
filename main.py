from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
import google.generativeai as genai
import anthropic

class QueryRequest(BaseModel):
    query: str

app = FastAPI()
from fastapi.responses import HTMLResponse, FileResponse

@app.get("/", response_class=HTMLResponse)
def read_root():
    return "<h2>🎉 Multi-AI Chatbot Backend is Live!</h2><p>Use POST /ask to query AI engines.</p>"

@app.get("/form", response_class=FileResponse)
def serve_form():
    return "form.html"

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@app.post("/ask")
async def ask_query(request: QueryRequest):
    q = request.query

    # GPT (OpenAI)
    gpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": q}]
    )['choices'][0]['message']['content']

    # Gemini (Google)
    gemini = genai.GenerativeModel('gemini-pro')
    gemini_response = gemini.generate_content(q).text

    # Claude (Anthropic)
    claude_response = anthropic_client.messages.create(
        model="claude-3-opus-20240229",
        messages=[{"role": "user", "content": q}],
        max_tokens=1000
    ).content[0].text

    # Final Summary
    summary_prompt = f"""Summarize this:
    GPT: {gpt_response}
    Gemini: {gemini_response}
    Claude: {claude_response}
    """
    summary = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": summary_prompt}]
    )['choices'][0]['message']['content']

    return {
        "gpt": gpt_response,
        "gemini": gemini_response,
        "claude": claude_response,
        "summary": summary
    }

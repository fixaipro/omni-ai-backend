from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow CORS for all origins (frontend on Google Sites, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment Variables (from .env file or Render Dashboard)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Helper function to call APIs
async def fetch_gpt_response(question):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": question}
        ]
    }
    async with httpx.AsyncClient() as client:
        res = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        return res.json()["choices"][0]["message"]["content"].strip()

async def fetch_claude_response(question):
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 500,
        "temperature": 0.7,
        "messages": [{"role": "user", "content": question}]
    }
    async with httpx.AsyncClient() as client:
        res = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
        return res.json()["content"][0]["text"].strip()

async def fetch_gemini_response(question):
    payload = {
        "contents": [{"parts": [{"text": question}]}]
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}",
            json=payload
        )
        return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

@app.post("/ask")
async def ask_ai(request: Request):
    body = await request.json()
    question = body.get("question", "")

    try:
        gpt, claude, gemini = await fetch_gpt_response(question), await fetch_claude_response(question), await fetch_gemini_response(question)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    # Generate a combined summary (this could be improved with logic)
    summary = f"GPT says: {gpt[:100]}... Claude says: {claude[:100]}... Gemini says: {gemini[:100]}..."

    return JSONResponse(content={
        "responses": {
            "gpt": gpt,
            "claude": claude,
            "gemini": gemini
        },
        "summary": summary
    })

@app.get("/")
def root():
    return {"message": "Multi-AI Chatbot backend running!"}

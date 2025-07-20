
import os
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

@app.get("/form", response_class=HTMLResponse)
def serve_inline_form():
    return '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Multi-AI Chatbot</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f1f3f7;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
    }
    .card {
      background: white;
      padding: 2rem;
      border-radius: 12px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.1);
      width: 100%;
      max-width: 600px;
    }
    .card h2 {
      text-align: center;
      font-size: 1.5rem;
    }
    input, button {
      width: 100%;
      padding: 0.8rem;
      margin-top: 1rem;
      border-radius: 8px;
      border: 1px solid #ccc;
      font-size: 1rem;
    }
    button {
      background-color: #007bff;
      color: white;
      border: none;
      font-weight: bold;
      cursor: pointer;
    }
    .response-block {
      margin-top: 1rem;
      padding: 1rem;
      border-left: 4px solid #007bff;
      background: #f9f9f9;
    }
    @media screen and (max-width: 600px) {
      .card {
        padding: 1rem;
      }
    }
  </style>
</head>
<body>
  <div class="card">
    <h2>🤖 <b>Multi-AI Chatbot</b></h2>
    <input id="queryInput" type="text" placeholder="Ask your question..." />
    <button onclick="ask()">Ask</button>
    <div id="output"></div>
  </div>
<script>
  async function ask() {
    const query = document.getElementById('queryInput').value;
    const output = document.getElementById('output');
    output.innerHTML = '<p>⏳ Thinking...</p>';

    try {
      const res = await fetch('https://omni-ai-backend.onrender.com/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
        mode: 'cors'
      });

      const contentType = res.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        const text = await res.text();
        output.innerHTML = '<p style="color:red;">❌ Server returned non-JSON:<br><pre>' + text + '</pre></p>';
        return;
      }

      const data = await res.json();
      output.innerHTML = `
        <div class="response-block"><b>🧠 GPT:</b><br>${data.gpt}</div>
        <div class="response-block"><b>🔮 Gemini:</b><br>${data.gemini}</div>
        <div class="response-block"><b>🤖 Claude:</b><br>${data.claude}</div>
        <div class="response-block"><b>🧾 Summary:</b><br>${data.summary}</div>
      `;
    } catch (err) {
      output.innerHTML = '<p style="color:red;">❌ Error: ' + err + '</p>';
    }
  }
</script>
</body>
</html>
'''

@app.post("/ask")
async def ask_ai(request: Request):
    body = await request.json()
    query = body.get("query", "")

    async with httpx.AsyncClient(timeout=15.0) as client:
        gpt, gemini, claude = "", "", ""

        try:
            gpt_res = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": query}]
                }
            )
            gpt = gpt_res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            gpt = f"Error: {str(e)}"

        try:
            gemini_res = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta3/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}",
                json={ "contents": [{ "parts": [{ "text": query }] }] }
            )
            gemini = gemini_res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            gemini = f"Error: {str(e)}"

        try:
            claude_res = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 500,
                    "messages": [{ "role": "user", "content": query }]
                }
            )
            claude = claude_res.json()["content"][0]["text"]
        except Exception as e:
            claude = f"Error: {str(e)}"

        try:
            summary_prompt = f"Summarize in 1 paragraph:

GPT: {gpt}

Gemini: {gemini}

Claude: {claude}"
            summary_res = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": summary_prompt}]
                }
            )
            summary = summary_res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            summary = f"Error: {str(e)}"

    return JSONResponse(content={
        "gpt": gpt,
        "gemini": gemini,
        "claude": claude,
        "summary": summary
    })

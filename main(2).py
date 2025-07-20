import os
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/form", response_class=HTMLResponse)
def serve_inline_form():
    return """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Multi-AI Chatbot</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: Arial; background: #f1f3f7; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
    .card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); width: 100%; max-width: 600px; }
    h2 { text-align: center; font-size: 1.5rem; }
    input, button { width: 100%; padding: 0.8rem; margin-top: 1rem; border-radius: 8px; border: 1px solid #ccc; font-size: 1rem; }
    button { background-color: #007bff; color: white; border: none; font-weight: bold; cursor: pointer; }
    .response-block { margin-top: 1rem; padding: 1rem; border-left: 4px solid #007bff; background: #f9f9f9; }
    @media screen and (max-width: 600px) { .card { padding: 1rem; } }
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
    const input = document.getElementById("queryInput").value;
    const outputDiv = document.getElementById("output");
    outputDiv.innerHTML = "Thinking...";

    try {
      const res = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input })
      });
      const data = await res.json();
      outputDiv.innerHTML = `
        <div class='response-block'><b>GPT:</b> ${data.gpt}</div>
        <div class='response-block'><b>Claude:</b> ${data.claude}</div>
        <div class='response-block'><b>Gemini:</b> ${data.gemini}</div>
        <div class='response-block'><b><i>Summary:</i></b> ${data.summary}</div>
      `;
    } catch (err) {
      outputDiv.innerHTML = `<span style='color:red'>❌ Error: ${err.message}</span>`;
    }
  }
</script>
</body>
</html>
"""

@app.post("/ask")
async def ask(request: Request):
    try:
        body = await request.json()
        question = body.get("question", "")

        # Dummy AI responses
        gpt_resp = f"GPT thinks: {question}"
        claude_resp = f"Claude answers: {question}"
        gemini_resp = f"Gemini says: {question}"
        summary = "Unified view: Each model agrees it's a good question."

        return JSONResponse({
            "gpt": gpt_resp,
            "claude": claude_resp,
            "gemini": gemini_resp,
            "summary": summary
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
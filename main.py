
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Allow Google Sites or any origin for embedding
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/form", response_class=HTMLResponse)
async def serve_inline_form():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Multi-AI Chatbot</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f3f4f6;
            margin: 0;
            display: flex;
            justify-content: center;
            padding: 50px;
        }
        .card {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 100%;
        }
        h2 {
            text-align: center;
        }
        input, button {
            width: 100%;
            padding: 0.75rem;
            margin-top: 1rem;
            border-radius: 8px;
            border: 1px solid #ccc;
        }
        button {
            background-color: #007bff;
            color: white;
            border: none;
        }
        .results {
            margin-top: 2rem;
        }
        .result-block {
            background-color: #f1f5f9;
            padding: 1rem;
            margin-top: 1rem;
            border-radius: 10px;
        }
        .icon {
            width: 24px;
            vertical-align: middle;
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>🤖 <strong>Multi-AI Chatbot</strong></h2>
        <input type="text" id="question" placeholder="Ask your question...">
        <button onclick="ask()">Ask</button>
        <div class="results" id="results"></div>
    </div>
    <script>
        async function ask() {
            const question = document.getElementById("question").value;
            const res = await fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question })
            });
            const data = await res.json();
            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = `
                <div class='result-block'><img class='icon' src='https://cdn-icons-png.flaticon.com/512/5968/5968778.png' width='20'/>GPT: ${data.gpt}</div>
                <div class='result-block'><img class='icon' src='https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Google_Gemini_logo.svg/2048px-Google_Gemini_logo.svg.png' width='20'/>Gemini: ${data.gemini}</div>
                <div class='result-block'><img class='icon' src='https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Anthropic_logo.svg/512px-Anthropic_logo.svg.png' width='20'/>Claude: ${data.claude}</div>
                <div class='result-block'><strong>🧠 Summary:</strong> ${data.summary}</div>
            `;
        }
    </script>
</body>
</html>"""

@app.post("/ask")
async def ask_ai(request: Request):
    body = await request.json()
    q = body.get("question", "")
    # Simulated response
    return JSONResponse(content={
        "gpt": f"GPT's answer to: {q}",
        "gemini": f"Gemini's answer to: {q}",
        "claude": f"Claude's answer to: {q}",
        "summary": f"Unified summary of responses for: {q}"
    })

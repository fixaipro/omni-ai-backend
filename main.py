
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import openai
import os
import google.generativeai as genai
import anthropic

# Load API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

app = FastAPI()

# Allow CORS for iframe loading
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask_query(request: QueryRequest):
    q = request.query

    gpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": q}]
    )['choices'][0]['message']['content']

    gemini_model = genai.GenerativeModel('gemini-pro')
    gemini_response = gemini_model.generate_content(q).text

    claude_response = anthropic_client.messages.create(
        model="claude-3-opus-20240229",
        messages=[{"role": "user", "content": q}],
        max_tokens=1000
    ).content[0].text

    summary_prompt = f"Summarize the following AI responses:\nGPT: {gpt_response}\nGemini: {gemini_response}\nClaude: {claude_response}"
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

@app.get("/", response_class=HTMLResponse)
def root():
    return "<h2>✅ Omni AI backend is live. Use <code>/form</code> or POST to <code>/ask</code>.</h2>"

@app.get("/form", response_class=HTMLResponse)
def serve_form():
    return '''
    <!DOCTYPE html>
    <html lang='en'>
    <head>
      <meta charset='UTF-8' />
      <meta name='viewport' content='width=device-width, initial-scale=1.0' />
      <title>Multi-AI Chatbot</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f2f5; }
        .container { max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h2 { text-align: center; margin-bottom: 20px; }
        input[type='text'] { width: 100%; padding: 12px; margin-bottom: 10px; border-radius: 6px; border: 1px solid #ccc; font-size: 16px; }
        button { width: 100%; padding: 12px; font-size: 16px; border: none; border-radius: 6px; background-color: #007bff; color: white; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .response-block { margin-top: 20px; background: #f9f9f9; padding: 15px; border-left: 4px solid #007bff; border-radius: 6px; }
        .ai-label { font-weight: bold; display: flex; align-items: center; }
        .ai-label span { margin-right: 8px; font-size: 20px; }
        .summary { background: #e8ffe8; border-left: 4px solid #28a745; }
      </style>
    </head>
    <body>
      <div class='container'>
        <h2>🤖 Multi-AI Chatbot</h2>
        <form id='aiForm'>
          <input type='text' id='query' placeholder='Ask your question...' required />
          <button type='submit'>Ask</button>
        </form>
        <div id='output'></div>
      </div>
      <script>
        const form = document.getElementById('aiForm');
        const output = document.getElementById('output');
        form.addEventListener('submit', async (e) => {
          e.preventDefault();
          const query = document.getElementById('query').value;
          output.innerHTML = '<p>⏳ Thinking...</p>';
          try {
            const res = await fetch('https://omni-ai-backend.onrender.com/ask', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ query }),
              mode: 'cors'
            });
            const data = await res.json();
            output.innerHTML = `
              <div class="response-block"><div class="ai-label"><span>🧠</span>GPT (OpenAI)</div><p>${data.gpt}</p></div>
              <div class="response-block"><div class="ai-label"><span>🔮</span>Gemini (Google)</div><p>${data.gemini}</p></div>
              <div class="response-block"><div class="ai-label"><span>🤖</span>Claude (Anthropic)</div><p>${data.claude}</p></div>
              <div class="response-block summary"><div class="ai-label"><span>🧾</span><strong>Summary</strong></div><p><strong>${data.summary}</strong></p></div>
            `;
          } catch (err) {
            output.innerHTML = '<p style="color:red;">❌ Error: ' + err.message + '</p>';
            console.error(err);
          }
        });
      </script>
    </body>
    </html>
    '''

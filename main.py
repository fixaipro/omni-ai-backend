from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Backend is live ✅"}

@app.post("/ask")
async def ask(request: Request):
    try:
        data = await request.json()
        question = data.get("question", "")

        if not question:
            return {"error": "Missing 'question' field."}

        api_key = os.getenv("OPENROUTER_API_KEY") or "sk-or-your-key"
        api_url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://fixaiproltd.com",
            "X-Title": "Multi-AI Omni Agent",
        }

        models = {
            "gpt-4": "GPT-4",
            "claude-3-opus": "Claude",
            "google/gemini-pro": "Gemini",
            "mistralai/mixtral-8x7b": "Grok"
        }

        responses = {}

        async with httpx.AsyncClient() as client:
            for model_id, label in models.items():
                payload = {
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": "Be concise and helpful."},
                        {"role": "user", "content": question}
                    ]
                }
                try:
                    resp = await client.post(api_url, headers=headers, json=payload)
                    resp.raise_for_status()
                    content = resp.json()["choices"][0]["message"]["content"]
                    responses[label] = content.strip()
                except Exception as e:
                    responses[label] = f"Error: {str(e)}"

        # Simple summary logic
        summary = "\n\n".join([f"{k}: {v[:200]}..." for k, v in responses.items()])

        return {
            "question": question,
            "responses": responses,
            "summary": summary
        }

    except Exception as e:
        return {"error": f"Something went wrong: {str(e)}"}

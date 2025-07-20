from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import asyncio

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
            tasks = []
            for model_id, label in models.items():
                payload = {
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": "Be concise and helpful."},
                        {"role": "user", "content": question}
                    ]
                }
                task = client.post(api_url, headers=headers, json=payload, timeout=15.0)
                tasks.append((label, task))

            results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)

            for (label, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    responses[label] = f"Error: {str(result)}"
                else:
                    try:
                        json_data = result.json()
                        if "choices" in json_data and json_data["choices"]:
                            content = json_data["choices"][0]["message"]["content"]
                            responses[label] = content.strip()
                        elif "error" in json_data:
                            responses[label] = f"API Error: {json_data['error']}"
                        else:
                            responses[label] = f"Unexpected response: {json_data}"
                    except Exception as e:
                        responses[label] = f"Error parsing: {str(e)}"

        summary = "\n\n".join([f"{k}: {v[:200]}..." for k, v in responses.items()])

        return {
            "question": question,
            "responses": responses,
            "summary": summary
        }

    except Exception as e:
        return {"error": f"Something went wrong: {str(e)}"}

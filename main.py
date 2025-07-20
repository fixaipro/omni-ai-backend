from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

# Enable CORS for all origins (safe for prototype)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# POST endpoint to handle the frontend request
@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    question = data.get("question")

    if not question:
        return {"response": "Please provide a question."}

    # Call OpenAI or any mock response for now
    try:
        headers = {
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": question}]
        }
        async with httpx.AsyncClient() as client:
            res = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            result = res.json()
            reply = result['choices'][0]['message']['content']
            return {"response": reply.strip()}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

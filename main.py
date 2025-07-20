from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    question = data.get("question", "")

    sources = [
        {"model": "GPT-4", "response": f"GPT thinks: {question}"},
        {"model": "Claude", "response": f"Claude answers: {question}"},
        {"model": "Gemini", "response": f"Gemini says: {question}"}
    ]

    summary = " | ".join([s["response"] for s in sources])

    return {
        "question": question,
        "sources": sources,
        "summary": summary
    }

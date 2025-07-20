from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI()

# CORS for frontend use (Google Sites, local, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend domain for production
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str

@app.get("/")
async def root():
    return {"status": "OK", "message": "Multi-AI Chatbot is live!"}

@app.post("/ask")
async def ask_route(query: Query):
    # Dummy response until LLM logic added
    return {
        "responses": {
            "GPT": "Placeholder answer from GPT",
            "Claude": "Placeholder answer from Claude",
            "Gemini": "Placeholder answer from Gemini"
        },
        "summary": f"Unified answer to: {query.question}"
    }

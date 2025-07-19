from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Load API keys from environment
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
SERPER_KEY = os.getenv("SERPER_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

class TextInput(BaseModel):
    text: Optional[str] = None

@app.post("/summary")
async def process_input(text: Optional[str] = Form(None),
                        audio: Optional[UploadFile] = File(None),
                        image: Optional[UploadFile] = File(None)):
    result = {
        "whisperText": "Transcribed audio text...",
        "imageAnalysis": "Description of image...",
        "gpt": "GPT says this...",
        "gemini": "Gemini says that...",
        "claude": "Claude suggests...",
        "deepseek": "DeepSeek recommends...",
        "web": "Web search result snippet...",
        "summary": "Final summary combining all sources."
    }
    return result

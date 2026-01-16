import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
import prompt

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY not found in .env")

client = Groq(api_key=api_key)

app = FastAPI(title="Health AI Assistant")

# Allow browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

EMERGENCY_KEYWORDS = [
    "chest pain",
    "shortness of breath",
    "cannot breathe",
    "unconscious",
    "seizure",
    "severe bleeding"
]

class UserInput(BaseModel):
    message: str

def is_emergency(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in EMERGENCY_KEYWORDS)

@app.post("/chat")
def chat(user_input: UserInput):
    msg = user_input.message.strip()

    if not msg:
        return {"reply": "Please describe your symptoms."}

    if is_emergency(msg):
        return {
            "reply": (
                "⚠️ These symptoms may indicate a medical emergency. "
                "Please seek immediate medical attention."
            )
        }

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": prompt.SYSTEM_PROMPT},
            {"role": "user", "content": msg}
        ],
        temperature=0.3,
        max_tokens=512
    )

    return {"reply": response.choices[0].message.content}

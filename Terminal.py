import os
from dotenv import load_dotenv
from groq import Groq
import prompt

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY not found in .env")

# Initialize Groq client
client = Groq(api_key=api_key)

# Emergency detection keywords
EMERGENCY_KEYWORDS = [
    "chest pain",
    "shortness of breath",
    "cannot breathe",
    "unconscious",
    "seizure",
    "severe bleeding"
]

def is_emergency(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in EMERGENCY_KEYWORDS)

def main():
    print("\n🩺 Baymax AI Health Assistant (Groq + LLaMA-3.1)")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["quit", "exit"]:
            print("BAYMAX: Stay healthy! Goodbye.")
            break

        if not user_input:
            continue

        if is_emergency(user_input):
            print(
                "Baymax: ⚠️ These symptoms may indicate a medical emergency. "
                "Please seek immediate medical attention."
            )
            continue

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": prompt.SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3,
                max_tokens=512
            )

            print("Baymax:", response.choices[0].message.content)

        except Exception as e:
            print("[Error]:", e)

        print()

if __name__ == "__main__":
    main()

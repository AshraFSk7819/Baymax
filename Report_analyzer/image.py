import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file
from google import genai
from google.genai import types
import Image_prompt as Image_prompt

# ===============================
# LOAD ENV
# ===============================
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

# ===============================
# INIT GEMINI
# ===============================
client = genai.Client(api_key=API_KEY)

app = Flask(__name__)

# ===============================
# MEDICAL PROMPT
# ===============================

# ===============================
# ROUTES
# ===============================

@app.route("/")
def index():
    return send_file("image_page.html")


@app.route("/analyze-report", methods=["POST"])
def analyze_report():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    image_bytes = image_file.read()

    if not image_bytes:
        return jsonify({"error": "Empty image file"}), 400

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=image_file.mimetype or "image/jpeg"
                ),
                Image_prompt.IMAGE_MEDICAL_PROMPT
            ],
            config={
                "temperature": 0.2,
                "max_output_tokens": 800
            }
        )

        return jsonify({"result": response.text})

    except Exception as e:
        return jsonify({
            "error": "Gemini failed to analyze the report",
            "details": str(e)
        }), 500


# ===============================
# ENTRY POINT
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

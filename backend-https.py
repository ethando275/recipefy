import os, io, ssl
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
from pydantic import BaseModel, Field
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Config
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_ID = "gemini-2.0-flash" 

app = Flask(__name__, static_folder='web')
CORS(app)  # Enable CORS for web frontend
client = genai.Client(api_key=GEMINI_API_KEY)

# Serve web frontend
@app.route('/')
def serve_index():
    return send_from_directory('web', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('web', filename)

# --- Schema for Structured Output ---
class Ingredient(BaseModel):
    label: str = Field(description="Singular lowercase name of the food")
    box_2d: list[int] = Field(description="Normalized [ymin, xmin, ymax, xmax] (0-1000)")

class Recipe(BaseModel):
    title: str
    description: str
    uses: list[str]

class AnalysisResponse(BaseModel):
    ingredients: list[Ingredient]
    recipes: list[Recipe]

# --- Optimized Multimodal Prompt ---
PROMPT = """
Identify all raw food ingredients in this image. 
1. Provide a bounding box [ymin, xmin, ymax, xmax] (normalized 0-1000) for each.
2. Suggest 3-5 realistic recipes using these items.
Return strictly JSON matching the schema.
"""

@app.post("/analyze_frame")
def analyze_frame():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    
    try:
        f = request.files["file"].read()
        img = Image.open(io.BytesIO(f)).convert("RGB")
        
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[PROMPT, img],
            config={
                "response_mime_type": "application/json",
                "response_json_schema": AnalysisResponse.model_json_schema(),
            }
        )
        return response.text
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Create SSL context for HTTPS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    print("🚀 Recipefy AR Server starting with HTTPS...")
    print("📱 Access from Meta Quest: https://YOUR_IP:4444")
    print("🔒 Note: You'll need to accept the SSL certificate warning")
    
    app.run(host="0.0.0.0", port=4444, ssl_context=context)

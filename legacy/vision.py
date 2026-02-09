# vision.py
import os
from google import genai
from PIL import Image
import io

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-2.0-flash"

PROMPT = """
You are a vision system for cooking preparation.
Task: Identify all raw food ingredients visible in the image.

Rules:
- Only list edible ingredients.
- Exclude utensils, plates, packaging, hands, surfaces.
- Use singular nouns.
- Output format exactly:
INGREDIENTS: item1, item2, item3
"""

def detect_ingredients(image: Image.Image) -> list[str]:
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=85)
    img_bytes = buf.getvalue()

    resp = client.models.generate_content(
        model=MODEL,
        contents=[
            PROMPT,
            {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": img_bytes,
                }
            },
        ],
    )

    text = (resp.text or "").strip().lower()

    if "ingredients:" not in text:
        return []

    items = text.split("ingredients:", 1)[-1]
    parts = [p.strip() for p in items.split(",")]
    return [p for p in parts if p]

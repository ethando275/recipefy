# backend.py
import io
import os
from typing import List

from flask import Flask, request, jsonify
from PIL import Image

import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

# ----------------------------
# Config
# ----------------------------
MODEL_ID = os.environ.get("HF_MODEL_ID", "BinhQuocNguyen/food-recognition-model")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TOPK = int(os.environ.get("TOPK", "3"))

app = Flask(__name__)

# ----------------------------
# Load HF model once at startup
# ----------------------------
processor = AutoImageProcessor.from_pretrained(MODEL_ID)
model = AutoModelForImageClassification.from_pretrained(MODEL_ID).to(DEVICE)
model.eval()

# ----------------------------
# Helpers
# ----------------------------
def normalize_label(s: str) -> str:
    # your schema wants: "Singular lowercase name of the food"
    # We'll do a lightweight normalization.
    s = (s or "").strip().lower()
    # strip some common formatting noise
    for ch in ["_", "-", "  "]:
        s = s.replace(ch, " ")
    s = " ".join(s.split())
    return s

def pick_topk_labels(logits: torch.Tensor, k: int) -> List[str]:
    probs = torch.softmax(logits, dim=-1)[0]
    k = min(k, probs.numel())
    topk = torch.topk(probs, k=k)

    id2label = getattr(model.config, "id2label", None) or {}
    labels = []
    for idx in topk.indices.tolist():
        lbl = id2label.get(idx, str(idx))
        labels.append(normalize_label(lbl))
    # de-dup while preserving order
    seen = set()
    out = []
    for l in labels:
        if l and l not in seen:
            seen.add(l)
            out.append(l)
    return out

def recipes_for(label: str):
    # Simple "good enough" recipes so your AR panel shows something realistic.
    # You can make this richer later or reintroduce Gemini for recipes only.
    if not label:
        return [
            {
                "title": "Simple pantry salad",
                "description": "Chop what you have, toss with olive oil, salt, pepper, and lemon/vinegar.",
                "uses": ["mixed ingredients"],
            }
        ]

    return [
        {
            "title": f"Quick {label} stir-fry",
            "description": f"Sauté {label} with garlic and soy sauce. Finish with sesame oil.",
            "uses": [label, "garlic", "soy sauce"],
        },
        {
            "title": f"{label} omelet",
            "description": f"Fold cooked {label} into eggs with cheese and herbs.",
            "uses": [label, "eggs", "cheese"],
        },
        {
            "title": f"Roasted {label}",
            "description": f"Roast {label} at high heat with olive oil, salt, pepper until browned.",
            "uses": [label, "olive oil", "salt", "pepper"],
        },
    ]

# ----------------------------
# Routes
# ----------------------------
@app.post("/analyze_frame")
def analyze_frame():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400

    try:
        raw = request.files["file"].read()
        img = Image.open(io.BytesIO(raw)).convert("RGB")

        inputs = processor(images=img, return_tensors="pt")
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits

        labels = pick_topk_labels(logits, TOPK)
        primary = labels[0] if labels else ""

        # Classification model => no bboxes.
        # Return a full-frame box so your overlay stays compatible.
        ingredients = []
        if primary:
            ingredients.append(
                {
                    "label": primary,
                    "box_2d": [0, 0, 1000, 1000],
                }
            )

        response = {
            "ingredients": ingredients,
            "recipes": recipes_for(primary),
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # match your existing port so the frontend keeps working
    app.run(host="0.0.0.0", port=4444)

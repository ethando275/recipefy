from flask import Flask, request, jsonify
from PIL import Image
import io

from config import get_config
from state import IngredientState
from utils import normalize_list
from vision import detect_ingredients
from gemini_client import GeminiRecipeClient

app = Flask(__name__)

cfg = get_config()

state = IngredientState(
    add_hits=cfg.ing_add_hits,
    remove_misses=cfg.ing_remove_misses,
    stable_seconds=cfg.stable_seconds,
)

gemini = GeminiRecipeClient(api_key=cfg.gemini_api_key, model=cfg.gemini_model)

@app.get("/health")
def health():
    return jsonify({"ok": True})

@app.post("/analyze_frame")
def analyze_frame():
    """
    Expects multipart/form-data:
      - file: JPEG/PNG image
    Returns:
      - confirmed ingredients (debounced)
      - recipes (4–5) when stable; otherwise empty + status
    """
    if "file" not in request.files:
        return jsonify({"error": "missing file field"}), 400

    f = request.files["file"]
    raw = f.read()

    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        return jsonify({"error": "invalid image"}), 400

    # 1) VLM -> raw ingredient strings
    observed_raw = detect_ingredients(img)

    # 2) normalize + cap
    observed = normalize_list(observed_raw, max_items=8)

    # 3) update state (debounce)
    changed = state.update(observed)

    payload = {
        "observed": observed,
        "ingredients": sorted(state.confirmed),
        "stable": state.is_stable(),
        "recipes": [],
        "status": "scanning",
    }

    # 4) if stable, call Gemini (cached)
    if state.is_stable() and len(state.confirmed) > 0:
        key = state.key()

        if key in state.cached_recipes:
            payload["recipes"] = state.cached_recipes[key]["recipes"]
            payload["status"] = "ready_cached"
            return jsonify(payload)

        # Call Gemini only if stable AND not cached.
        suggestions = gemini.suggest_recipes(
            ingredients=sorted(state.confirmed),
            min_n=cfg.recipe_count_min,
            max_n=cfg.recipe_count_max,
        )

        recipes = [r.model_dump() for r in suggestions.recipes]
        state.cached_recipes[key] = {"recipes": recipes}

        payload["recipes"] = recipes
        payload["status"] = "ready"
        return jsonify(payload)

    return jsonify(payload)

if __name__ == "__main__":
    # For local dev only. Use gunicorn in production.
    app.run(host="0.0.0.0", port=4444, debug=True)

from google import genai
from recipes_schema import RecipeSuggestions

STAPLES = ["salt", "pepper", "cooking oil", "butter", "water"]

class GeminiRecipeClient:
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def suggest_recipes(self, ingredients: list[str], min_n: int = 4, max_n: int = 5) -> RecipeSuggestions:
        # Keep prompt tight and rule-based to reduce “invented” ingredients
        prompt = f"""
You are Recipefy.ai, a helpful cooking assistant.

AVAILABLE_INGREDIENTS (use only these as primary ingredients):
{ingredients}

ALLOWED_STAPLES (you may assume these exist without listing them as missing):
{STAPLES}

Task:
Return {min_n} to {max_n} recipe suggestions that a home cook could make.
- Each suggestion must have:
  - title (short)
  - description (1–2 sentences)
  - uses (subset of AVAILABLE_INGREDIENTS actually used)
  - missing_common_items (optional): only if truly needed beyond staples
Rules:
- Do NOT include utensils or packaging.
- Do NOT invent specialty ingredients. If needed, put them in missing_common_items.
- Prefer simple, realistic dishes (15–40 minutes).
"""

        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": RecipeSuggestions.model_json_schema(),
            },
        )

        # resp.text should be a JSON string matching schema.
        return RecipeSuggestions.model_validate_json(resp.text)

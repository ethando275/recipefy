from pydantic import BaseModel, Field
from typing import List, Optional

class RecipeCard(BaseModel):
    title: str = Field(description="Short recipe name.")
    description: str = Field(description="1–2 sentence description of the dish and why it fits the ingredients.")
    uses: List[str] = Field(description="Subset of available ingredients used.")
    missing_common_items: Optional[List[str]] = Field(
        default=None,
        description="Optional: common extras needed (besides staples)."
    )

class RecipeSuggestions(BaseModel):
    recipes: List[RecipeCard] = Field(description="4–5 recipe suggestions.")

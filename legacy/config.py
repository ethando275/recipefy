import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

    vlm_fps: float = float(os.getenv("VLM_FPS", "2"))
    ing_add_hits: int = int(os.getenv("ING_ADD_HITS", "2"))
    ing_remove_misses: int = int(os.getenv("ING_REMOVE_MISSES", "3"))
    stable_seconds: float = float(os.getenv("STABLE_SECONDS", "2.0"))

    recipe_count_min: int = int(os.getenv("RECIPE_COUNT_MIN", "4"))
    recipe_count_max: int = int(os.getenv("RECIPE_COUNT_MAX", "5"))

def get_config() -> Config:
    cfg = Config()
    if not cfg.gemini_api_key:
        raise RuntimeError("Missing GEMINI_API_KEY. Put it in a .env file.")
    return cfg

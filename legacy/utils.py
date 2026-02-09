import re

SYNONYMS = {
    "scallions": "green onion",
    "spring onions": "green onion",
    "capsicum": "bell pepper",
    "bell peppers": "bell pepper",
    "tomatoes": "tomato",
    "onions": "onion",
    "garlic cloves": "garlic",
}

STOPWORDS = set(["and", "with", "a", "an", "the"])

def normalize_ingredient(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9\s\-]", "", s)
    s = re.sub(r"\s+", " ", s)

    if s in SYNONYMS:
        s = SYNONYMS[s]

    # naive singularization (MVP)
    if s.endswith("es") and len(s) > 4:
        s = s[:-2]
    elif s.endswith("s") and len(s) > 3:
        s = s[:-1]

    if s in STOPWORDS:
        return ""
    return s

def normalize_list(items: list[str], max_items: int = 8) -> list[str]:
    out = []
    seen = set()
    for it in items:
        n = normalize_ingredient(it)
        if not n or n in seen:
            continue
        seen.add(n)
        out.append(n)
        if len(out) >= max_items:
            break
    return out

import time
from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class IngredientState:
    add_hits: int
    remove_misses: int
    stable_seconds: float

    # counters
    hits: dict[str, int] = field(default_factory=dict)
    misses: dict[str, int] = field(default_factory=dict)

    confirmed: set[str] = field(default_factory=set)
    last_changed_ts: float = field(default_factory=lambda: time.time())

    # recipe cache
    last_key: Optional[str] = None

    cached_recipes: dict[str, dict] = field(default_factory=dict)

    def update(self, observed: list[str]) -> bool:
        """
        observed: normalized list from VLM
        Returns: True if confirmed set changed.
        """
        now = time.time()
        obs_set = set(observed)

        # Update hits/misses
        for ing in obs_set:
            self.hits[ing] = self.hits.get(ing, 0) + 1
            self.misses[ing] = 0

        for ing in list(self.hits.keys()):
            if ing not in obs_set:
                self.misses[ing] = self.misses.get(ing, 0) + 1
                self.hits[ing] = 0

        changed = False

        # Confirm additions
        for ing in obs_set:
            if ing not in self.confirmed and self.hits.get(ing, 0) >= self.add_hits:
                self.confirmed.add(ing)
                changed = True

        # Confirm removals
        for ing in list(self.confirmed):
            if self.misses.get(ing, 0) >= self.remove_misses:
                self.confirmed.remove(ing)
                changed = True

        if changed:
            self.last_changed_ts = now

        return changed

    def is_stable(self) -> bool:
        return (time.time() - self.last_changed_ts) >= self.stable_seconds

    def key(self, constraints: Optional[Dict] = None) -> str:
        constraints = constraints or {}
        parts = sorted(self.confirmed)
        cparts = [f"{k}={constraints[k]}" for k in sorted(constraints.keys())]
        return "|".join(parts + ["--"] + cparts)

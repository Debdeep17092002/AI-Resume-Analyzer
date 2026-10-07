import json
import re
from functools import lru_cache
from pathlib import Path

SKILLS_PATH = Path(__file__).resolve().parents[2] / "ml" / "models" / "skills.json"


@lru_cache(maxsize=1)
def _load():
    data = json.loads(SKILLS_PATH.read_text(encoding="utf-8"))
    alias_to_canonical: dict[str, str] = {}
    categories: dict[str, str] = {}

    for canonical, info in data.items():
        categories[canonical] = info.get("category", "other")
        for term in [canonical, *info.get("aliases", [])]:
            alias_to_canonical[term.lower()] = canonical

    # Longest terms first so "github actions" wins over "github"
    terms = sorted(alias_to_canonical, key=len, reverse=True)
    pattern = re.compile(
        r"(?<![A-Za-z0-9+#])("
        + "|".join(re.escape(t) for t in terms)
        + r")(?![A-Za-z0-9+#])",
        re.IGNORECASE,
    )
    return alias_to_canonical, categories, pattern


def normalize_skill(skill: str) -> str:
    """Map an alias (e.g. 'JS') to its canonical name ('javascript')."""
    alias_to_canonical, _, _ = _load()
    s = skill.strip().lower()
    return alias_to_canonical.get(s, s)


def extract_skills(text: str) -> list[str]:
    """Return a sorted list of unique canonical skills found in the text."""
    alias_to_canonical, _, pattern = _load()
    found = {alias_to_canonical[m.group(1).lower()] for m in pattern.finditer(text or "")}
    return sorted(found)


def extract_skills_by_category(text: str) -> dict[str, list[str]]:
    _, categories, _ = _load()
    grouped: dict[str, list[str]] = {}
    for skill in extract_skills(text):
        grouped.setdefault(categories.get(skill, "other"), []).append(skill)
    return grouped
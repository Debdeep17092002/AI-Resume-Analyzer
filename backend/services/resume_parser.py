import re
from functools import lru_cache

import spacy

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{8,}\d)")

# canonical section name -> heading variants
SECTION_ALIASES = {
    "summary": ["summary", "profile", "objective", "career objective",
                "professional summary", "about me"],
    "education": ["education", "academic background", "academics",
                  "educational qualification", "qualifications"],
    "experience": ["experience", "work experience", "professional experience",
                   "employment history", "internship", "internships",
                   "work history"],
    "skills": ["skills", "technical skills", "key skills", "core competencies",
               "skills and tools", "technologies"],
    "projects": ["projects", "academic projects", "personal projects"],
    "certifications": ["certifications", "certificates", "courses",
                       "licenses"],
    "achievements": ["achievements", "awards", "honors", "accomplishments"],
}

HEADING_LOOKUP = {
    alias: section
    for section, aliases in SECTION_ALIASES.items()
    for alias in aliases
}


@lru_cache(maxsize=1)
def get_nlp():
    return spacy.load("en_core_web_sm")


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[•●▪■◦]", "-", text)          # normalize bullets
    text = re.sub(r"[ \t]+", " ", text)             # collapse spaces
    text = re.sub(r"\n\s*\n+", "\n\n", text)        # collapse blank lines
    return text.strip()


def extract_email(text: str) -> str | None:
    match = EMAIL_RE.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    for match in PHONE_RE.finditer(text):
        candidate = match.group(1).strip()
        digits = re.sub(r"\D", "", candidate)
        if 10 <= len(digits) <= 13:
            return candidate
    return None


def extract_name(text: str) -> str | None:
    head = text[:300]
    doc = get_nlp()(head)
    for ent in doc.ents:
        if ent.label_ == "PERSON" and 1 < len(ent.text.split()) <= 4:
            return ent.text.strip()
    # Fallback: first short line without digits or '@'
    for line in text.splitlines():
        line = line.strip()
        if line and len(line.split()) <= 4 and not re.search(r"[\d@]", line):
            return line
    return None


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {"header": []}
    current = "header"

    for line in text.splitlines():
        key = line.strip().rstrip(":").lower()
        if key in HEADING_LOOKUP and len(line.strip()) <= 40:
            current = HEADING_LOOKUP[key]
            sections.setdefault(current, [])
            continue
        sections[current].append(line)

    return {
        name: "\n".join(lines).strip()
        for name, lines in sections.items()
        if "\n".join(lines).strip()
    }


def parse_resume(raw_text: str) -> dict:
    text = clean_text(raw_text)
    return {
        "text": text,
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "sections": split_sections(text),
    }
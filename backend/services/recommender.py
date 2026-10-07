import re
from urllib.parse import quote

from backend.services.embedding import cosine_similarity, get_embedding
from backend.services.matcher import build_result, job_to_text
from backend.services.skill_extractor import normalize_skill

RESOURCES = {
    "python": "https://docs.python.org/3/tutorial/",
    "sql": "https://www.w3schools.com/sql/",
    "git": "https://git-scm.com/book/en/v2",
    "docker": "https://docs.docker.com/get-started/",
    "kubernetes": "https://kubernetes.io/docs/tutorials/",
    "fastapi": "https://fastapi.tiangolo.com/tutorial/",
    "react": "https://react.dev/learn",
    "pandas": "https://pandas.pydata.org/docs/user_guide/10min.html",
    "numpy": "https://numpy.org/doc/stable/user/absolute_beginners.html",
    "scikit-learn": "https://scikit-learn.org/stable/tutorial/index.html",
    "pytorch": "https://pytorch.org/tutorials/",
    "tensorflow": "https://www.tensorflow.org/tutorials",
}

_job_cache: dict = {}


def _job_embedding(job: dict):
    text = job_to_text(job)
    key = (job["id"], hash(text))
    if key not in _job_cache:
        _job_cache[key] = get_embedding(text)
    return _job_cache[key]


def skill_gap_suggestions(missing_skills: list[str]) -> list[dict]:
    return [
        {
            "skill": skill,
            "resource": RESOURCES.get(
                skill, f"https://www.coursera.org/search?query={quote(skill)}"
            ),
        }
        for skill in missing_skills
    ]


def recommend_jobs(
    resume_text: str, resume_skills: list[str], jobs: list[dict], top_n: int = 5
) -> list[dict]:
    resume_vec = get_embedding(resume_text)  # embedded once for all jobs
    have = {normalize_skill(s) for s in resume_skills}

    results = []
    for job in jobs:
        required = {normalize_skill(s) for s in job["required_skills"]}
        similarity = cosine_similarity(resume_vec, _job_embedding(job))
        result = build_result(required, have, similarity)
        results.append(
            {
                "job_id": job["id"],
                "title": job["title"],
                "company": job["company"],
                **result,
            }
        )

    results.sort(key=lambda r: r["match_score"], reverse=True)
    return results[:top_n]


def resume_tips(resume: dict) -> list[str]:
    """Simple rule-based feedback on the resume itself."""
    tips = []
    text = resume.get("raw_text") or ""
    sections = resume.get("sections") or {}
    words = len(text.split())

    for name in ("education", "experience", "skills", "projects"):
        if name not in sections:
            tips.append(f"Add a clear '{name.title()}' section heading.")

    if words < 150:
        tips.append("Your resume looks very short. Add more detail about your work and projects.")
    elif words > 1000:
        tips.append("Your resume is long. Aim for 1-2 pages and keep only the most relevant points.")

    impact_text = (sections.get("experience", "") + " " + sections.get("projects", ""))
    if not re.search(r"\d+\s?%|\d{2,}", impact_text):
        tips.append("Add measurable results (e.g. 'reduced load time by 30%', 'served 500+ users').")

    lower = text.lower()
    if "github.com" not in lower:
        tips.append("Add a GitHub link to show your projects.")
    if "linkedin.com" not in lower:
        tips.append("Add your LinkedIn profile link.")

    if not resume.get("email"):
        tips.append("Add a professional email address at the top.")
    if not resume.get("phone"):
        tips.append("Add a phone number at the top.")

    return tips
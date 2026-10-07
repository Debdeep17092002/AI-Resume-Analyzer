from backend.services.embedding import cosine_similarity, get_embedding
from backend.services.skill_extractor import extract_skills, normalize_skill

# Tune these later using your hand-labelled test pairs (Step 11)
SKILL_WEIGHT = 0.6
SEMANTIC_WEIGHT = 0.4

# Raw cosine similarity between a resume and a job rarely goes below 0.15
# or above 0.65, so we stretch that range to 0-1 for a fairer score.
SIM_FLOOR = 0.15
SIM_CEIL = 0.65


def job_to_text(job: dict) -> str:
    skills = ", ".join(job.get("required_skills") or [])
    return f"{job['title']}. {job['description']}. Skills: {skills}"


def build_result(required: set[str], have: set[str], similarity: float) -> dict:
    matched = sorted(required & have)
    missing = sorted(required - have)
    overlap = len(matched) / len(required) if required else 0.0

    sim_norm = (similarity - SIM_FLOOR) / (SIM_CEIL - SIM_FLOOR)
    sim_norm = min(max(sim_norm, 0.0), 1.0)

    if required:
        score = SKILL_WEIGHT * overlap + SEMANTIC_WEIGHT * sim_norm
    else:
        score = sim_norm  # no skills listed, so use semantics only

    return {
        "match_score": round(score * 100, 1),
        "skill_overlap": round(overlap * 100, 1),
        "semantic_similarity": round(similarity, 3),
        "matched_skills": matched,
        "missing_skills": missing,
    }


def match_resume_to_job(
    resume_text: str,
    resume_skills: list[str],
    job_text: str,
    job_skills: list[str] | None = None,
) -> dict:
    required = {normalize_skill(s) for s in (job_skills or [])}
    if not required:
        required = set(extract_skills(job_text))
    have = {normalize_skill(s) for s in resume_skills}

    similarity = cosine_similarity(get_embedding(resume_text), get_embedding(job_text))
    return build_result(required, have, similarity)
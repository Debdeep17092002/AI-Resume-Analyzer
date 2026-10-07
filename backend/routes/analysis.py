import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, model_validator

from backend.models.db import get_connection
from backend.services.matcher import job_to_text, match_resume_to_job
from backend.services.recommender import recommend_jobs, resume_tips, skill_gap_suggestions
from backend.services.skill_extractor import extract_skills

router = APIRouter(prefix="/analysis", tags=["analysis"])


class MatchRequest(BaseModel):
    resume_id: int
    job_id: int | None = None
    job_description: str | None = None

    @model_validator(mode="after")
    def check_job_source(self):
        if self.job_id is None and not (self.job_description or "").strip():
            raise ValueError("Provide either job_id or job_description")
        return self


def _load_resume(resume_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,)).fetchone()
    finally:
        conn.close()
    if row is None:
        raise HTTPException(404, "Resume not found")

    resume = dict(row)
    resume["sections"] = json.loads(resume["sections"] or "{}")
    stored = json.loads(resume["extracted_skills"] or "[]")
    # Resumes uploaded before Phase 4 have no skills saved, so extract on the fly
    resume["skills"] = stored or extract_skills(resume["raw_text"] or "")
    return resume


def _job_from_row(row) -> dict:
    job = dict(row)
    job["required_skills"] = json.loads(job["required_skills"] or "[]")
    return job


@router.post("/match")
def match(req: MatchRequest):
    resume = _load_resume(req.resume_id)

    job = None
    if req.job_id is not None:
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (req.job_id,)).fetchone()
        finally:
            conn.close()
        if row is None:
            raise HTTPException(404, "Job not found")
        job = _job_from_row(row)
        job_text = job_to_text(job)
        job_skills = job["required_skills"]
    else:
        job_text = req.job_description
        job_skills = None

    result = match_resume_to_job(resume["raw_text"], resume["skills"], job_text, job_skills)

    if job is not None:
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO analyses
                   (resume_id, job_id, match_score, matched_skills, missing_skills)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    req.resume_id,
                    req.job_id,
                    result["match_score"],
                    json.dumps(result["matched_skills"]),
                    json.dumps(result["missing_skills"]),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    return {
        "resume_id": req.resume_id,
        "job_id": req.job_id,
        "job_title": job["title"] if job else None,
        **result,
        "resume_skills": resume["skills"],
        "suggestions": skill_gap_suggestions(result["missing_skills"]),
        "tips": resume_tips(resume),
    }


@router.get("/recommend/{resume_id}")
def recommend(resume_id: int, top_n: int = 5):
    resume = _load_resume(resume_id)
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM jobs").fetchall()
    finally:
        conn.close()
    jobs = [_job_from_row(r) for r in rows]
    return recommend_jobs(resume["raw_text"], resume["skills"], jobs, top_n)
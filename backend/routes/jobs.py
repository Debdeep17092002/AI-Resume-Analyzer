import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models.db import get_connection

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobCreate(BaseModel):
    title: str
    company: str | None = None
    description: str
    required_skills: list[str] = []


def row_to_job(row) -> dict:
    job = dict(row)
    job["required_skills"] = json.loads(job["required_skills"] or "[]")
    return job


@router.get("")
def list_jobs():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM jobs ORDER BY id").fetchall()
        return [row_to_job(r) for r in rows]
    finally:
        conn.close()


@router.get("/{job_id}")
def get_job(job_id: int):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return row_to_job(row)
    finally:
        conn.close()


@router.post("", status_code=201)
def create_job(job: JobCreate):
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO jobs (title, company, description, required_skills) VALUES (?, ?, ?, ?)",
            (job.title, job.company, job.description, json.dumps(job.required_skills)),
        )
        conn.commit()
        return {"id": cur.lastrowid, **job.model_dump()}
    finally:
        conn.close()
import json
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.models.db import BASE_DIR, get_connection
from backend.services.pdf_parser import (
    SUPPORTED_EXTENSIONS,
    EmptyResumeError,
    UnsupportedFileError,
    extract_text,
)
from backend.services.resume_parser import parse_resume
from backend.services.skill_extractor import extract_skills

router = APIRouter(prefix="/resume", tags=["resume"])

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def has_valid_signature(ext: str, content: bytes) -> bool:
    """Check the first bytes of the file, not just its name."""
    if ext == ".pdf":
        return content.startswith(b"%PDF")
    if ext == ".docx":
        return content.startswith(b"PK")  # DOCX files are zip archives
    return False


@router.post("/upload", status_code=201)
def upload_resume(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(400, "Only PDF and DOCX files are supported.")

    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 5 MB).")
    if not has_valid_signature(ext, content):
        raise HTTPException(400, "File content does not match its type.")

    saved_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    saved_path.write_bytes(content)

    try:
        raw_text = extract_text(saved_path)
        parsed = parse_resume(raw_text)
        skills = extract_skills(parsed["text"])
    except (EmptyResumeError, UnsupportedFileError) as e:
        raise HTTPException(422, str(e))
    except Exception:
        raise HTTPException(500, "Failed to read the file. It may be corrupted.")
    finally:
        # The text is saved in the database, so the original file isn't needed
        saved_path.unlink(missing_ok=True)

    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO resumes
               (filename, raw_text, name, email, phone, sections, extracted_skills)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                file.filename,
                parsed["text"],
                parsed["name"],
                parsed["email"],
                parsed["phone"],
                json.dumps(parsed["sections"]),
                json.dumps(skills),
            ),
        )
        conn.commit()
        resume_id = cur.lastrowid
    finally:
        conn.close()

    return {
        "id": resume_id,
        "filename": file.filename,
        "name": parsed["name"],
        "email": parsed["email"],
        "phone": parsed["phone"],
        "sections_found": list(parsed["sections"].keys()),
        "skills": skills,
        "text_preview": parsed["text"][:300],
    }


@router.get("/{resume_id}")
def get_resume(resume_id: int):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM resumes WHERE id = ?", (resume_id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(404, "Resume not found")

    resume = dict(row)
    resume["sections"] = json.loads(resume["sections"] or "{}")
    resume["extracted_skills"] = json.loads(resume["extracted_skills"] or "[]")
    return resume


@router.delete("/{resume_id}", status_code=204)
def delete_resume(resume_id: int):
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
        conn.commit()
        deleted = cur.rowcount
    finally:
        conn.close()

    if deleted == 0:
        raise HTTPException(404, "Resume not found")
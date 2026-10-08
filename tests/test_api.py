from docx import Document

DOCX_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def make_docx_bytes(tmp_path) -> bytes:
    doc = Document()
    for line in [
        "John Smith",
        "john.smith@example.com",
        "+91 98765 43210",
        "",
        "Skills",
        "Python, FastAPI, Docker, Git and REST API design",
        "",
        "Experience",
        "Built REST APIs with Python and FastAPI for a college project, "
        "improving response time by 30%.",
    ]:
        doc.add_paragraph(line)
    path = tmp_path / "resume.docx"
    doc.save(path)
    return path.read_bytes()


def upload(client, tmp_path):
    return client.post(
        "/resume/upload",
        files={"file": ("resume.docx", make_docx_bytes(tmp_path), DOCX_TYPE)},
    )


def test_health(client):
    assert client.get("/").json() == {"status": "ok"}


def test_jobs_are_seeded(client):
    jobs = client.get("/jobs").json()
    assert len(jobs) >= 8
    assert isinstance(jobs[0]["required_skills"], list)


def test_upload_resume(client, tmp_path):
    res = upload(client, tmp_path)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "john.smith@example.com"
    assert "python" in data["skills"]
    assert "skills" in data["sections_found"]


def test_upload_rejects_wrong_extension(client):
    res = client.post("/resume/upload", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert res.status_code == 400


def test_upload_rejects_fake_pdf(client):
    res = client.post(
        "/resume/upload",
        files={"file": ("fake.pdf", b"this is not a pdf", "application/pdf")},
    )
    assert res.status_code == 400


def test_match_resume_to_job(client, tmp_path):
    resume_id = upload(client, tmp_path).json()["id"]
    res = client.post("/analysis/match", json={"resume_id": resume_id, "job_id": 2})
    assert res.status_code == 200
    body = res.json()
    assert 0 <= body["match_score"] <= 100
    assert "python" in body["matched_skills"]
    assert "aws" in body["missing_skills"]
    assert isinstance(body["tips"], list)


def test_match_needs_a_job(client, tmp_path):
    resume_id = upload(client, tmp_path).json()["id"]
    res = client.post("/analysis/match", json={"resume_id": resume_id})
    assert res.status_code == 422


def test_match_unknown_resume(client):
    res = client.post("/analysis/match", json={"resume_id": 9999, "job_id": 1})
    assert res.status_code == 404


def test_recommendations_are_sorted(client, tmp_path):
    resume_id = upload(client, tmp_path).json()["id"]
    results = client.get(f"/analysis/recommend/{resume_id}?top_n=3").json()
    assert len(results) == 3
    scores = [r["match_score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_delete_resume(client, tmp_path):
    resume_id = upload(client, tmp_path).json()["id"]
    assert client.delete(f"/resume/{resume_id}").status_code == 204
    assert client.get(f"/resume/{resume_id}").status_code == 404
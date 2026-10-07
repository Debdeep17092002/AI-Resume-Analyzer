from backend.services.matcher import match_resume_to_job
from backend.services.skill_extractor import extract_skills


def test_aliases_and_no_partial_matches():
    text = "Built APIs with Python and FastAPI on AWS. Used JS, ReactJS and MySQL."
    skills = extract_skills(text)
    for s in ["python", "fastapi", "aws", "javascript", "react", "mysql"]:
        assert s in skills
    assert "java" not in skills   # 'java' must not match inside 'javascript'
    assert "sql" not in skills    # 'sql' must not match inside 'mysql'


def test_match_reports_missing_skills():
    result = match_resume_to_job(
        resume_text="Python developer who built REST APIs with FastAPI and Docker.",
        resume_skills=["python", "fastapi", "docker"],
        job_text="Backend developer needed for APIs",
        job_skills=["python", "fastapi", "docker", "aws", "kubernetes"],
    )
    assert 0 <= result["match_score"] <= 100
    assert result["matched_skills"] == ["docker", "fastapi", "python"]
    assert result["missing_skills"] == ["aws", "kubernetes"]
from backend.services.resume_parser import parse_resume

SAMPLE = (
    "John Smith\n"
    "john.smith@example.com\n"
    "+91 98765 43210\n\n"
    "Education\nB.Tech in Computer Science\n\n"
    "Skills\nPython, SQL\n\n"
    "Projects\nResume analyzer built with FastAPI\n"
)


def test_contact_details():
    parsed = parse_resume(SAMPLE)
    assert parsed["email"] == "john.smith@example.com"
    assert "9876543210" in parsed["phone"].replace(" ", "")


def test_sections_are_split():
    sections = parse_resume(SAMPLE)["sections"]
    for name in ("education", "skills", "projects"):
        assert name in sections
    assert "Python" in sections["skills"]
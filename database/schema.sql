CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    raw_text TEXT,
    name TEXT,
    email TEXT,
    phone TEXT,
    sections TEXT,            -- JSON: {"education": "...", "experience": "..."}
    extracted_skills TEXT,    -- JSON list: ["python", "sql"]
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT,
    description TEXT NOT NULL,
    required_skills TEXT,     -- JSON list
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    match_score REAL,
    matched_skills TEXT,      -- JSON list
    missing_skills TEXT,      -- JSON list
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_analyses_resume ON analyses(resume_id);
CREATE INDEX IF NOT EXISTS idx_analyses_job ON analyses(job_id);
# AI Resume Analyzer

Upload a resume, pick a job (or paste a job description), and get a match score,
matched and missing skills, learning suggestions, resume tips, and job recommendations.

## Features

- Resume parsing from PDF and DOCX (name, email, phone, sections)
- Skill extraction using a custom skills dictionary with aliases
- Match score combining skill overlap and semantic similarity (sentence embeddings)
- Skill gap suggestions and rule-based resume tips
- Job recommendations ranked by match score
- React web interface

## Tech stack

- **Backend:** Python, FastAPI, SQLite
- **ML / NLP:** sentence-transformers (all-MiniLM-L6-v2), spaCy, scikit-learn
- **Frontend:** React (Vite), React Router, Axios

## How the matching works

```
resume text ──► skill extractor ──► skills ─────────┐
resume text ──► embedding ──► vector ───────────────┼──► score (0-100)
job text    ──► embedding ──► vector ───────────────┘
```

Score = 60% skill overlap + 40% semantic similarity.
Skills are found by dictionary matching with alias normalization (e.g. "JS" → javascript).
Cosine similarity between embeddings is rescaled from its practical range (0.15–0.65) to 0–1.

## Evaluation

TODO: describe your hand-labelled test (about 20 resume/job pairs) and the results.

| Resume | Job | My label | Score |
|---|---|---|---|
| TODO | TODO | good / partial / bad | TODO |

TODO (optional): resume category classifier (TF-IDF + Logistic Regression) trained on a
small public dataset. Report accuracy and note that the dataset is small and repetitive.

## Getting started

Requirements: Python 3.10+ and Node.js 18+.

```bash
# Backend (from the project root)
python -m venv venv
venv\Scripts\Activate.ps1          # Windows PowerShell
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn backend.main:app --reload

# Frontend (in a second terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. API docs are at http://localhost:8000/docs.

## Tests

```bash
python -m pytest -q
```

## Privacy

Uploaded files are deleted right after text extraction. Only the extracted text and
parsed fields are stored. Resumes can be removed with `DELETE /resume/{id}`.

## Limitations

- Two-column or heavily designed resumes may parse poorly.
- Scanned (image-only) PDFs are not supported; there is no OCR.
- Skill detection depends on the dictionary in `ml/models/skills.json`.
- Job data is sample data; there is no live job feed.

## Future work

- OCR for scanned resumes
- Custom spaCy NER model for skill extraction
- User accounts and analysis history
- Larger job dataset


# AI Resume Analyzer

An AI-powered resume analyzer that evaluates resumes against job descriptions using NLP, calculates match scores, identifies missing skills, and generates personalized ATS-compatibility recommendations — built with Python, Streamlit, and Scikit-learn.

## Features

- **Multi-format resume parsing**: Upload PDF, DOCX, or TXT resumes
- **NLP skill extraction**: Identifies technical and soft skills from a curated skill database (100+ skills across programming, data/ML, cloud, databases, tools, and soft skills)
- **Match scoring**: Uses TF-IDF vectorization + cosine similarity to compute an overall resume-to-job-description match percentage
- **Skill gap analysis**: Highlights matched vs. missing skills side-by-side
- **Personalized recommendations**: Actionable tips based on your score, missing skills, resume structure, and phrasing
- **ATS compatibility check**: Flags common formatting issues that trip up Applicant Tracking Systems
- **Downloadable report**: Export your analysis as a text file

## Project Structure

```
resume_analyzer/
├── app.py               # Main Streamlit application (UI)
├── resume_parser.py      # PDF/DOCX/TXT text extraction
├── skill_extractor.py    # Skill database + keyword extraction
├── analyzer.py            # Match scoring, gap analysis, recommendations
├── requirements.txt
└── README.md
```

## Setup

1. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

4. Open the URL shown in your terminal (typically `http://localhost:8501`).

## How It Works

1. **Upload your resume** (PDF, DOCX, or TXT).
2. **Paste the job description** you're targeting.
3. Click **Analyze Resume**.
4. Review your:
   - Overall match score (0-100%)
   - Skill coverage chart
   - Matched vs. missing skills
   - Personalized recommendations
   - ATS formatting warnings
5. Optionally, download a text report of the full analysis.

## Extending the Skill Database

The skill list lives in `skill_extractor.py` as the `SKILL_DB` set. Add or remove skills relevant to your target industry/roles — the matching logic will automatically pick up new entries (word-boundary-aware, so multi-word phrases like "machine learning" work correctly).

## How the Match Score Works

The app vectorizes both the resume and job description using **TF-IDF** (Term Frequency–Inverse Document Frequency), which weighs words by importance rather than raw frequency, then computes **cosine similarity** between the two vectors. This gives a 0-100% score reflecting how closely the resume's language aligns with the job description's language — a common lightweight technique for ATS-style matching.

## Notes & Limitations

- Scanned/image-based PDFs won't extract text — use a text-based PDF or DOCX.
- The skill database is curated and can't catch every possible skill; extend it as needed.
- ATS formatting checks are heuristic (based on extracted text) and can't detect visual issues like multi-column layouts or embedded graphics directly — when in doubt, prefer simple, single-column resume formats.

## Potential Next Steps

- Swap the curated skill list for a spaCy/NLTK-based named entity or noun-phrase extractor for broader coverage
- Add support for multiple job descriptions to compare fit across roles
- Add a resume "rewrite suggestion" feature using bullet-point rephrasing
- Persist analysis history using a local database

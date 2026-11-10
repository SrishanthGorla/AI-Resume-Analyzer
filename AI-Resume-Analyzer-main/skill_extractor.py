"""
skill_extractor.py
Extracts skills/keywords from resume or job description text using a curated
skill database + regex/keyword matching. Designed to be easily extended.
"""

import re

# A reasonably broad curated skill database, grouped by category.
# Extend this list to widen coverage for your target roles/industries.
SKILL_DB = {
    # Programming languages
    "python", "java", "c++", "c#", "javascript", "typescript", "sql", "r",
    "go", "golang", "rust", "scala", "php", "ruby", "swift", "kotlin", "matlab",

    # Web / frameworks
    "react", "angular", "vue", "django", "flask", "streamlit", "fastapi",
    "node.js", "nodejs", "express", "spring", "asp.net", "html", "css",
    "bootstrap", "tailwind",

    # Data / ML / AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "scikit-learn", "sklearn", "tensorflow", "pytorch",
    "keras", "pandas", "numpy", "matplotlib", "seaborn", "opencv",
    "data analysis", "data visualization", "data science", "statistics",
    "regression", "classification", "clustering", "feature engineering",
    "neural networks", "llm", "large language models", "generative ai",
    "prompt engineering", "transformers", "spacy", "nltk", "hugging face",

    # Data engineering / cloud
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
    "terraform", "airflow", "spark", "hadoop", "kafka", "etl",
    "data pipeline", "snowflake", "redshift", "bigquery",

    # Databases
    "mysql", "postgresql", "mongodb", "oracle", "sqlite", "nosql",
    "database design", "data modeling",

    # Tools / practices
    "git", "github", "gitlab", "jira", "agile", "scrum", "ci/cd",
    "unit testing", "rest api", "restful api", "microservices",
    "linux", "bash", "shell scripting", "excel", "power bi", "tableau",

    # Soft / business skills
    "communication", "leadership", "teamwork", "problem solving",
    "project management", "stakeholder management", "time management",
    "critical thinking", "collaboration", "presentation skills",

    # Cybersecurity
    "cybersecurity", "penetration testing", "network security",
    "encryption", "vulnerability assessment",
}

# Sort longer phrases first so multi-word skills are matched before
# their substrings (e.g. "machine learning" before "learning").
_SORTED_SKILLS = sorted(SKILL_DB, key=len, reverse=True)


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\+\#\.\s/]", " ", text)  # keep +, #, ., / for c++, c#, node.js
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_skills(text: str) -> set:
    """
    Extract skills from text by matching against the curated skill database.
    Uses word-boundary-aware matching to avoid partial-word false positives.
    """
    normalized = _normalize(text)
    found = set()

    for skill in _SORTED_SKILLS:
        skill_normalized = _normalize(skill)
        # Build a regex pattern that respects boundaries but allows
        # special characters like + # . in skill names.
        pattern = r"(?<![a-z0-9])" + re.escape(skill_normalized).replace(r"\ ", r"\s+") + r"(?![a-z0-9])"
        if re.search(pattern, normalized):
            found.add(skill)

    return found

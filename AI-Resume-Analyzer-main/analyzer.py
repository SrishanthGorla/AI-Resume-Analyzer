"""
analyzer.py
Core analysis logic: TF-IDF/cosine similarity match scoring, skill gap analysis,
recommendation generation, and basic ATS formatting checks.
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_match_score(resume_text: str, job_description: str) -> float:
    """
    Computes an overall match score (0-100) between resume and job description
    using TF-IDF vectorization + cosine similarity.
    """
    documents = [resume_text, job_description]
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except ValueError:
        # Happens if vocabulary is empty after stop-word removal
        similarity = 0.0

    return round(similarity * 100, 1)


def get_matched_skills(resume_skills: set, jd_skills: set) -> set:
    return resume_skills & jd_skills


def get_missing_skills(resume_skills: set, jd_skills: set) -> set:
    return jd_skills - resume_skills


def generate_recommendations(match_score: float, missing_skills: set, resume_text: str) -> list:
    """
    Generates personalized, actionable recommendations to improve
    resume-job fit and ATS compatibility.
    """
    recs = []

    # Score-based recommendations
    if match_score < 40:
        recs.append(
            "Your resume has low overlap with this job description. Consider tailoring your "
            "summary and experience sections to mirror the language used in the posting."
        )
    elif match_score < 70:
        recs.append(
            "Your resume partially matches this role. Strengthen alignment by incorporating "
            "more of the job description's key terms naturally into your bullet points."
        )
    else:
        recs.append(
            "Strong overall match! Fine-tune remaining gaps below to maximize ATS scoring."
        )

    # Missing skills recommendations
    if missing_skills:
        top_missing = sorted(missing_skills)[:8]
        recs.append(
            "Add these missing skills/keywords where genuinely applicable: "
            + ", ".join(top_missing) + "."
        )
        recs.append(
            "If you have experience with these skills but didn't mention them, add specific "
            "examples (e.g., a project or achievement) rather than just listing the keyword."
        )

    # Quantification check
    if not re.search(r"\d+%|\$\d+|\d+\+|\bincreased\b|\bimproved\b|\breduced\b", resume_text.lower()):
        recs.append(
            "Quantify your achievements with numbers or percentages (e.g., 'improved processing "
            "speed by 30%') to make impact clearer to both recruiters and ATS parsers."
        )

    # Action verbs check
    weak_starts = ["responsible for", "worked on", "helped with", "duties included"]
    if any(phrase in resume_text.lower() for phrase in weak_starts):
        recs.append(
            "Replace passive phrases like 'responsible for' or 'worked on' with strong action "
            "verbs such as 'led', 'built', 'optimized', or 'delivered'."
        )

    # Length check
    word_count = len(resume_text.split())
    if word_count < 150:
        recs.append("Your resume seems short — consider adding more detail on relevant projects and achievements.")
    elif word_count > 1200:
        recs.append("Your resume is quite long — consider trimming to 1-2 pages of the most relevant content.")

    return recs


def check_ats_formatting(resume_text: str) -> list:
    """
    Flags common ATS-unfriendly patterns detectable from extracted text.
    Note: some issues (tables, images, columns, fonts) can't be detected
    from plain text alone and are noted as general best-practice tips.
    """
    issues = []

    if re.search(r"[^\x00-\x7F]", resume_text):
        issues.append(
            "Special characters or unusual symbols detected — some ATS systems may misread these. "
            "Stick to standard characters where possible."
        )

    if len(resume_text.split("\n")) < 5:
        issues.append(
            "Very little line structure was detected in your resume text. If your resume uses "
            "text boxes, columns, or graphics, ATS systems may fail to parse it correctly — "
            "use a single-column, standard format."
        )

    if not re.search(r"experience|employment|work history", resume_text.lower()):
        issues.append("No clear 'Experience' section header detected — use standard section titles like 'Experience', 'Education', and 'Skills'.")

    if not re.search(r"education", resume_text.lower()):
        issues.append("No clear 'Education' section header detected.")

    if not re.search(r"skills", resume_text.lower()):
        issues.append("No clear 'Skills' section header detected — a dedicated skills section helps ATS keyword matching.")

    email_found = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", resume_text)
    if not email_found:
        issues.append("No email address detected — ensure your contact info is in plain text, not an image.")

    return issues

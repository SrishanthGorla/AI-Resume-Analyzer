"""
AI Resume Analyzer
-------------------
Evaluates a resume against a job description using NLP + TF-IDF/cosine similarity,
extracts skills/keywords, computes a match score, highlights missing skills, and
generates personalized recommendations to improve ATS compatibility.

Run with:
    streamlit run app.py
"""

import re
import io
import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from resume_parser import extract_text_from_file
from skill_extractor import extract_skills, SKILL_DB
from analyzer import (
    compute_match_score,
    get_missing_skills,
    get_matched_skills,
    generate_recommendations,
    check_ats_formatting,
)

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .big-score {
        font-size: 3rem;
        font-weight: 700;
    }
    .score-card {
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        background-color: #f5f7fa;
        border: 1px solid #e3e6ea;
    }
    .skill-pill {
        display: inline-block;
        padding: 4px 12px;
        margin: 4px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .matched { background-color: #d4edda; color: #155724; }
    .missing { background-color: #f8d7da; color: #721c24; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📄 AI Resume Analyzer")
st.caption("Match your resume against a job description, find missing skills, and get ATS-friendly recommendations.")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("How it works")
    st.write(
        "1. Upload your resume (PDF, DOCX, or TXT)\n"
        "2. Paste the job description\n"
        "3. Click **Analyze** to get your match score, skill gaps, and tips"
    )
    st.divider()
    st.write("Built with Python, Streamlit, NLP & Scikit-learn")

# ---------- Input columns ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Resume")
    resume_file = st.file_uploader(
        "Upload your resume", type=["pdf", "docx", "txt"], label_visibility="collapsed"
    )
    resume_text = ""
    if resume_file is not None:
        try:
            resume_text = extract_text_from_file(resume_file)
            with st.expander("Preview extracted resume text"):
                st.text_area("Resume text", resume_text, height=200, label_visibility="collapsed")
        except Exception as e:
            st.error(f"Could not read file: {e}")

with col2:
    st.subheader("2. Paste Job Description")
    job_description = st.text_area(
        "Job description", height=280, label_visibility="collapsed",
        placeholder="Paste the full job description here..."
    )

st.divider()
analyze_clicked = st.button("🔍 Analyze Resume", type="primary", use_container_width=False)

# ---------- Analysis ----------
if analyze_clicked:
    if not resume_text.strip():
        st.warning("Please upload a resume first.")
    elif not job_description.strip():
        st.warning("Please paste a job description first.")
    else:
        with st.spinner("Analyzing resume against job description..."):
            match_score = compute_match_score(resume_text, job_description)
            resume_skills = extract_skills(resume_text)
            jd_skills = extract_skills(job_description)
            matched_skills = get_matched_skills(resume_skills, jd_skills)
            missing_skills = get_missing_skills(resume_skills, jd_skills)
            recommendations = generate_recommendations(
                match_score, missing_skills, resume_text
            )
            ats_issues = check_ats_formatting(resume_text)

        st.success("Analysis complete!")

        # ---- Score ----
        score_col, chart_col = st.columns([1, 2])
        with score_col:
            st.markdown('<div class="score-card">', unsafe_allow_html=True)
            st.markdown("**Overall Match Score**")
            color = "#28a745" if match_score >= 70 else "#ffc107" if match_score >= 40 else "#dc3545"
            st.markdown(
                f'<div class="big-score" style="color:{color}">{match_score:.0f}%</div>',
                unsafe_allow_html=True,
            )
            if match_score >= 70:
                st.write("🟢 Strong match")
            elif match_score >= 40:
                st.write("🟡 Moderate match")
            else:
                st.write("🔴 Weak match")
            st.markdown("</div>", unsafe_allow_html=True)

        with chart_col:
            st.markdown("**Skill Coverage**")
            total = len(jd_skills) if jd_skills else 1
            covered = len(matched_skills)
            df = pd.DataFrame(
                {"Status": ["Matched", "Missing"], "Count": [covered, len(missing_skills)]}
            )
            st.bar_chart(df.set_index("Status"))

        st.divider()

        # ---- Skills ----
        st.subheader("🧩 Skill Breakdown")
        s1, s2 = st.columns(2)
        with s1:
            st.markdown("**✅ Matched Skills**")
            if matched_skills:
                pills = "".join(f'<span class="skill-pill matched">{s}</span>' for s in sorted(matched_skills))
                st.markdown(pills, unsafe_allow_html=True)
            else:
                st.write("No overlapping skills found.")
        with s2:
            st.markdown("**❌ Missing Skills**")
            if missing_skills:
                pills = "".join(f'<span class="skill-pill missing">{s}</span>' for s in sorted(missing_skills))
                st.markdown(pills, unsafe_allow_html=True)
            else:
                st.write("Great — no missing skills detected!")

        st.divider()

        # ---- Recommendations ----
        st.subheader("💡 Personalized Recommendations")
        for rec in recommendations:
            st.write(f"- {rec}")

        # ---- ATS formatting check ----
        st.subheader("🛠️ ATS Compatibility Check")
        if ats_issues:
            for issue in ats_issues:
                st.write(f"- ⚠️ {issue}")
        else:
            st.write("✅ No obvious ATS formatting issues detected.")

        # ---- Downloadable report ----
        report_lines = [
            "AI RESUME ANALYZER REPORT",
            "=" * 30,
            f"Overall Match Score: {match_score:.0f}%",
            "",
            "Matched Skills:",
            ", ".join(sorted(matched_skills)) if matched_skills else "None",
            "",
            "Missing Skills:",
            ", ".join(sorted(missing_skills)) if missing_skills else "None",
            "",
            "Recommendations:",
        ] + [f"- {r}" for r in recommendations] + [
            "",
            "ATS Formatting Notes:",
        ] + ([f"- {i}" for i in ats_issues] if ats_issues else ["- None"])

        report_text = "\n".join(report_lines)
        st.download_button(
            "⬇️ Download Report (TXT)",
            data=report_text,
            file_name="resume_analysis_report.txt",
            mime="text/plain",
        )

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
import shutil
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from parser.resume_parser import parse_resumes
from matching.matcher import match_resumes


# ================= PAGE CONFIG =================
st.set_page_config(page_title="AI-Based ATS", layout="wide")

# ================= SESSION STATE =================
if "report_generated" not in st.session_state:
    st.session_state.report_generated = False
if "score" not in st.session_state:
    st.session_state.score = 0


# ================= THEME & HOVER FIX =================
st.markdown("""
<style>
/* -------- BACKGROUND -------- */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top right, #2b1a5c, #05030c 65%);
    color: white;
}

header, footer {visibility: hidden;}

h1, h2, h3 {
    color: white;
    font-weight: 600;
}

label {
    color: #d1d5ff !important;
}

/* ================= ALL BUTTONS BASE ================= */
button[kind="primary"],
button[kind="secondary"] {
    background: linear-gradient(135deg, #7f00ff, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 16px !important;
    transition: all 0.3s ease-in-out !important;
}

/* ================= ALL BUTTONS HOVER GLOW ================= */
button[kind="primary"]:hover,
button[kind="secondary"]:hover {
    transform: scale(1.08);

    /* PURPLE NEON GLOW */
     box-shadow:
        0 0 6px rgba(168, 85, 247, 0.45),
        0 0 14px rgba(168, 85, 247, 0.55),
        0 0 26px rgba(168, 85, 247, 0.65);

    filter: drop-shadow(0 0 5px rgba(168, 85, 247, 0.6));
}

/* ================= FEEDBACK BUTTON BASE ================= */
#feedback-section button {
    background: linear-gradient(135deg, #7f00ff, #a855f7) !important;
    color: white !important;
    border: none !important;
    font-size: 26px !important;
    padding: 18px 26px !important;
    border-radius: 22px !important;
    transition: all 0.3s ease-in-out !important;
}

/* ================= FEEDBACK BUTTON HOVER ================= */
#feedback-section button:hover {
    transform: scale(1.25);

    /* STRONGER GLOW */
     box-shadow:
        0 0 6px rgba(168, 85, 247, 0.45),
        0 0 14px rgba(168, 85, 247, 0.55),
        0 0 26px rgba(168, 85, 247, 0.65);

    filter: drop-shadow(0 0 5px rgba(168, 85, 247, 0.6));
}

</style>
""", unsafe_allow_html=True)


# ================= HEADER =================
st.markdown("""
<h1 style="text-align:center; font-size:60px;">🤖🙌</h1>
<h1 style="text-align:center;">AI-Based ATS Resume Filter System</h1>
<p style="text-align:center; color:#c7c9ff;">
Smart resume screening using NLP & AI techniques
</p>
""", unsafe_allow_html=True)


# ================= DOMAIN CONFIG =================
DOMAINS = {
    "Data Science": ["Data Scientist", "ML Engineer", "NLP Engineer", "Data Analyst", "AI Researcher"],
    "Software Development": ["Python Developer", "Backend Developer", "Fullstack Developer", "Java Developer", "Software Engineer"],
    "Cloud DevOps": ["Cloud Engineer", "DevOps Engineer", "AWS Engineer", "Site Reliability Engineer", "Infrastructure Engineer"],
    "Cybersecurity": ["Security Analyst", "Penetration Tester", "SOC Analyst", "Network Security Engineer", "Ethical Hacker"],
    "Web Development": ["Frontend Developer", "React Developer", "UI UX Designer", "Web Developer", "JavaScript Developer"]
}


# ================= ATS METRICS =================
def calculate_ats_metrics(resume_text, job_description):
    resume_text = resume_text.lower()
    job_description = job_description.lower()

    jd_words = set(re.findall(r'\b\w+\b', job_description))
    resume_words = re.findall(r'\b\w+\b', resume_text)

    keyword_pct = min(int(len(jd_words & set(resume_words)) / max(len(jd_words), 1) * 100), 100)

    tfidf = TfidfVectorizer().fit_transform([resume_text, job_description])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]

    return {
        "Keyword Match": keyword_pct,
        "Skill Relevance": keyword_pct,
        "Contextual Similarity": int(similarity * 100),
        "Term Frequency": min(sum(resume_words.count(w) for w in jd_words) * 2, 100),
        "Readability": 100 if len(resume_text.strip()) > 300 else 50
    }


# ================= DOMAIN & ROLE =================
st.subheader("🧠 Job Selection")

col_d, col_r = st.columns(2)

with col_d:
    domain = st.selectbox("Select Domain", ["-- Select Domain --"] + list(DOMAINS.keys()))

with col_r:
    role = None
    if domain != "-- Select Domain --":
        role = st.selectbox("Select Role", ["-- Select Role --"] + DOMAINS[domain])

job_description = None


# ================= JOB DESCRIPTION =================
if role and role != "-- Select Role --":
    jd_path = f"job_descriptions/{domain.replace(' ', '_')}/{role.replace(' ', '_')}.txt"

    if not os.path.exists(jd_path):
        st.error("❌ Job description not found")
        st.stop()

    job_description = open(jd_path, encoding="utf-8").read()
    st.subheader("📄 Job Description")
    st.text_area("JD", job_description, height=180, disabled=True)


# ================= UPLOAD & PROCESS =================
if job_description:
    st.subheader("📤 Upload Resumes")
    uploaded = st.file_uploader("Upload PDF/DOCX resumes", ["pdf", "docx"], accept_multiple_files=True)

    if os.path.exists("resumes"):
        shutil.rmtree("resumes")
    os.makedirs("resumes")

    if uploaded:
        for f in uploaded:
            with open(f"resumes/{f.name}", "wb") as file:
                file.write(f.getbuffer())

    if st.button("🚀 Generate ATS Report"):
        resumes = parse_resumes("resumes")
        scores = match_resumes(resumes, job_description)

        if not scores:
            st.error("❌ ATS could not evaluate resumes")
            st.stop()

        name, score = max(scores.items(), key=lambda x: x[1])
        st.session_state.report_generated = True
        st.session_state.score = score

        status = "PASS" if score >= 85 else "FAIL"
        color = "#4CAF50" if status == "PASS" else "#F44336"

        col1, col2 = st.columns([1.1, 1])

        with col1:
            donut = go.Figure(go.Pie(
                values=[score, 100-score],
                hole=0.75,
                marker_colors=[color, "#2C2F36"],
                textinfo="none"
            ))
            donut.update_layout(
                annotations=[dict(
                    text=f"<b>{score:.2f}%</b><br>{status}",
                    x=0.5, y=0.5,
                    font=dict(size=40, color="white"),
                    showarrow=False
                )],
                showlegend=False,
                height=420
            )
            st.plotly_chart(donut, use_container_width=True)

        with col2:
            st.subheader("📊 ATS Metrics")
            for k, v in calculate_ats_metrics(resumes[name], job_description).items():
                st.markdown(f"**{k}**")
                st.progress(v)

        shutil.rmtree("resumes")


# ================= AI SUGGESTION + FEEDBACK =================
if st.session_state.report_generated:
    st.markdown("---")

    center = st.columns([1, 2, 1])[1]

    with center:
        st.subheader("🧠 AI Suggestion")

        if st.session_state.score >= 85:
            st.success("✅ This resume strongly matches the job requirements.")
        else:
            st.warning("⚠️ Improve keyword relevance, skills alignment, and project descriptions.")

        st.markdown("---")
        st.subheader("💬 Feedback")

        st.markdown('<div id="feedback-section">', unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)

        with f1:
            st.button("😞 Bad", key="fb_bad")

        with f2:
            st.button("🙂 Good", key="fb_good")

        with f3:
            st.button("🤩 Excellent", key="fb_excellent")

        st.markdown('</div>', unsafe_allow_html=True)
# ================= END OF FILE =================

#run: streamlit run streamlit_app.py

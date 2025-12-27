import streamlit as st
import plotly.graph_objects as go
import os
import shutil
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from parser.resume_parser import parse_resumes
from matching.matcher import match_resumes
from ai_models.ai_job_model import generate_ai_job_description


# ================= PAGE CONFIG =================
st.set_page_config(page_title="AI-Based ATS", layout="wide")


# ================= SESSION STATE =================
if "report_generated" not in st.session_state:
    st.session_state.report_generated = False
if "score" not in st.session_state:
    st.session_state.score = 0


# ================= DOMAIN CONFIG =================
DOMAINS = {
    "Data Science": ["Data Scientist", "ML Engineer", "Data Analyst"],
    "Web Development": ["Frontend Developer", "Backend Developer", "Fullstack Developer"],
    "Cloud DevOps": ["DevOps Engineer", "Cloud Engineer"],
    "Cybersecurity": ["Security Analyst", "SOC Analyst"]
}


# ================= ATS METRICS =================
def calculate_ats_metrics(resume_text, job_description):
    resume_text = resume_text.lower()
    job_description = job_description.lower()

    jd_words = set(re.findall(r"\b\w+\b", job_description))
    resume_words = re.findall(r"\b\w+\b", resume_text)

    keyword_pct = min(
        int(len(jd_words & set(resume_words)) / max(len(jd_words), 1) * 100), 100
    )

    tfidf = TfidfVectorizer().fit_transform([resume_text, job_description])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]

    return {
        "Keyword Match": keyword_pct,
        "Skill Relevance": keyword_pct,
        "Contextual Similarity": int(similarity * 100),
        "Readability": 100 if len(resume_text) > 300 else 50,
    }


# ================= HEADER =================
st.title("🤖 AI-Based ATS Resume Filter System")
st.caption("Smart resume screening using NLP & AI")


# ================= JOB SELECTION =================
st.subheader("🧠 Job Selection")

col1, col2 = st.columns(2)
with col1:
    domain = st.selectbox("Select Domain", ["-- Select --"] + list(DOMAINS.keys()))
with col2:
    role = None
    if domain != "-- Select --":
        role = st.selectbox("Select Role", ["-- Select --"] + DOMAINS[domain])


# ================= AI JOB DESCRIPTION (CACHED) =================
@st.cache_data(show_spinner=False)
def get_ai_job(domain, role):
    return generate_ai_job_description(domain, role)


job_description = None

if role and role != "-- Select --":
    with st.spinner("🧠 Loading Job Description..."):
        ai_job = get_ai_job(domain, role)

    job_description = ai_job["job_description"]

    st.subheader("📄 Job Description")
    st.text_area("JD", job_description, height=220, disabled=True)


# ================= RESUME UPLOAD =================
if job_description:
    st.subheader("📤 Upload Resumes")
    files = st.file_uploader("Upload resumes", ["pdf", "docx"], accept_multiple_files=True)

    if files:
        if os.path.exists("resumes"):
            shutil.rmtree("resumes")
        os.makedirs("resumes")

        for f in files:
            with open(f"resumes/{f.name}", "wb") as out:
                out.write(f.getbuffer())

        if st.button("🚀 Generate ATS Report"):
            resumes = parse_resumes("resumes")
            scores = match_resumes(resumes, job_description)

            name, score = max(scores.items(), key=lambda x: x[1])
            st.session_state.report_generated = True
            st.session_state.score = score

            status = "PASS" if score >= 85 else "FAIL"
            color = "#4CAF50" if status == "PASS" else "#F44336"

            col1, col2 = st.columns(2)

            with col1:
                fig = go.Figure(go.Pie(
                    values=[score, 100 - score],
                    hole=0.7,
                    marker_colors=[color, "#2C2F36"],
                    textinfo="none"
                ))
                fig.update_layout(
                    annotations=[dict(
                        text=f"{score:.2f}%<br>{status}",
                        x=0.5, y=0.5,
                        font=dict(size=28),
                        showarrow=False
                    )],
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("📊 ATS Metrics")
                for k, v in calculate_ats_metrics(resumes[name], job_description).items():
                    st.markdown(f"**{k}**")
                    st.progress(v)

            shutil.rmtree("resumes")


# ================= AI SUGGESTION =================
if st.session_state.report_generated:
    st.subheader("🧠 AI Suggestion")
    if st.session_state.score >= 85:
        st.success("✅ Resume matches job requirements well.")
    else:
        st.warning("⚠️ Improve skills, keywords, and project descriptions.")

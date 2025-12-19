import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
import shutil

from parser.resume_parser import parse_resumes
from matching.matcher import match_resumes

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="ATS Resume Filter Report", layout="wide")

st.markdown(
    "<h1 style='text-align:center;'>ATS Resume Filter Report</h1>",
    unsafe_allow_html=True
)

# ---------------- DOMAIN & ROLE CONFIG ----------------
DOMAINS = {
    "Data Science": [
        "Data Scientist", "ML Engineer", "NLP Engineer",
        "Data Analyst", "AI Researcher"
    ],
    "Software Development": [
        "Python Developer", "Backend Developer",
        "Fullstack Developer", "Java Developer",
        "Software Engineer"
    ],
    "Cloud & DevOps": [
        "Cloud Engineer", "DevOps Engineer",
        "AWS Engineer", "Site Reliability Engineer",
        "Infrastructure Engineer"
    ],
    "Cybersecurity": [
        "Security Analyst", "Penetration Tester",
        "SOC Analyst", "Network Security Engineer",
        "Ethical Hacker"
    ],
    "Web Development": [
        "Frontend Developer", "React Developer",
        "UI UX Designer", "Web Developer",
        "JavaScript Developer"
    ]
}

# ---------------- DOMAIN SELECTION ----------------
st.subheader("🧠 Select Job Domain")
selected_domain = st.selectbox(
    "Choose Domain",
    ["-- Select Domain --"] + list(DOMAINS.keys())
)

# ---------------- ROLE SELECTION ----------------
selected_role = None
job_description = None

if selected_domain != "-- Select Domain --":
    st.subheader("🧩 Select Job Role")
    selected_role = st.selectbox(
        "Choose Role",
        ["-- Select Role --"] + DOMAINS[selected_domain]
    )

# ---------------- LOAD JOB DESCRIPTION ----------------
if selected_role and selected_role != "-- Select Role --":
    jd_path = f"job_descriptions/{selected_domain.replace(' ', '_')}/{selected_role.replace(' ', '_')}.txt"

    if not os.path.exists(jd_path):
        st.error("❌ Job description file not found.")
        st.stop()

    with open(jd_path, "r", encoding="utf-8") as f:
        job_description = f.read()

    st.subheader("📄 Job Description (Auto-loaded)")
    st.text_area(
        "Job Description",
        job_description,
        height=220,
        disabled=True
    )

# ---------------- UPLOAD RESUMES ----------------
if job_description:
    st.subheader("📤 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload PDF/DOCX resumes",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if not os.path.exists("resumes"):
        os.makedirs("resumes")

    if uploaded_files:
        for file in uploaded_files:
            with open(os.path.join("resumes", file.name), "wb") as f:
                f.write(file.getbuffer())

    # ---------------- GENERATE ATS REPORT ----------------
    if st.button("Generate ATS Report"):

        resumes = parse_resumes("resumes/")
        if not resumes:
            st.error("❌ No readable text found in uploaded resumes.")
            st.stop()

        scores = match_resumes(resumes, job_description)
        if not scores:
            st.error("❌ Unable to calculate scores.")
            st.stop()

        top_resume, score = max(scores.items(), key=lambda x: x[1])

        # ---------------- PASS / FAIL LOGIC ----------------
        PASS_THRESHOLD = 85
        status = "PASS" if score >= PASS_THRESHOLD else "FAIL"
        status_color = "#4CAF50" if score >= PASS_THRESHOLD else "#F44336"

        # ===================== LAYOUT =====================
        col1, col2 = st.columns([1, 1.3])

        # ---------------- RESUME SCORE (DONUT) ----------------
        with col1:
            st.subheader("Resume Score")

            donut = go.Figure(
                data=[
                    go.Pie(
                        values=[score, 100 - score],
                        hole=0.75,
                        marker_colors=[status_color, "#E0E0E0"],
                        textinfo="none"
                    )
                ]
            )

            donut.update_layout(
                annotations=[{
                    "text": f"<b>{score}%</b><br>{status}",
                    "font": {"size": 24, "color": status_color},
                    "showarrow": False
                }],
                showlegend=False,
                height=350
            )

            st.plotly_chart(donut, use_container_width=True)

        # ---------------- SKILLS MATCH ----------------
        with col2:
            st.subheader("Skills Match")

            skills = {
                "Python": 80,
                "Data Analysis": 75,
                "SQL": 70,
                "Machine Learning": 65,
                "Project Management": 60
            }

            for skill, val in skills.items():
                st.markdown(f"**{skill}**")
                st.progress(val)

        # ===================== SECOND ROW =====================
        col3, col4 = st.columns(2)

        # ---------------- EXPERIENCE ----------------
        with col3:
            st.subheader("Experience")

            exp_df = pd.DataFrame({
                "Level": ["Entry", "Mid", "Senior", "Lead"],
                "Score": [1, 2, 3, 4]
            })

            exp_fig = go.Figure(
                data=[go.Bar(
                    x=exp_df["Level"],
                    y=exp_df["Score"],
                    marker_color="#607D8B"
                )]
            )

            exp_fig.update_layout(
                yaxis=dict(visible=False),
                height=300
            )

            st.plotly_chart(exp_fig, use_container_width=True)
            st.markdown("<h3 style='text-align:center;'>5+ Years</h3>", unsafe_allow_html=True)

        # ---------------- PROJECTS ----------------
        with col4:
            st.subheader("Projects")

            project_fig = go.Figure(
                data=[
                    go.Pie(
                        labels=["AI Development", "Data Analysis", "Automation"],
                        values=[45, 35, 20],
                        marker_colors=["#2196F3", "#FF9800", "#FFC107"]
                    )
                ]
            )

            project_fig.update_layout(height=300)
            st.plotly_chart(project_fig, use_container_width=True)

        # ---------------- CLEANUP ----------------
        shutil.rmtree("resumes")
        os.makedirs("resumes")

#run: streamlit run streamlit_app.py
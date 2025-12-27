import json
import os
from dotenv import load_dotenv

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

load_dotenv()


def generate_ai_job_description(domain: str, role: str):
    """
    SAFE AI Job Generator:
    - Uses OpenAI if available & quota exists
    - Falls back to static JD if quota exceeded
    - NEVER crashes Streamlit
    """

    # ---------- FALLBACK JD (NO AI REQUIRED) ----------
    fallback = {
        "job_description": f"""
We are looking for a skilled {role} in the {domain} domain.
The candidate will be responsible for designing, developing,
testing, and optimizing solutions aligned with business goals.
Strong problem-solving skills, technical expertise, and teamwork
are essential for success in this role.
""",
        "core_skills": [],
        "tools_and_technologies": [],
        "ai_expectations": [],
        "soft_skills": []
    }

    if not OPENAI_AVAILABLE:
        return fallback

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback

    try:
        client = OpenAI(api_key=api_key)

        prompt = f"""
Generate a professional ATS-optimized job description.

Domain: {domain}
Role: {role}

Return STRICT JSON with:
- job_description
- core_skills
- tools_and_technologies
- ai_expectations
- soft_skills
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You generate ATS job descriptions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return json.loads(response.choices[0].message.content)

    except Exception:
        # 🔥 QUOTA / RATE LIMIT / ANY ERROR → FALLBACK
        return fallback

import nltk
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('stopwords')
from nltk.corpus import stopwords

def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = text.split()
    words = [w for w in words if w not in stopwords.words("english")]
    return " ".join(words)


def match_resumes(resumes, job_description):
    if not resumes:
        return {}

    cleaned_resumes = []
    resume_names = []

    for name, text in resumes.items():
        if text and text.strip():
            cleaned_resumes.append(clean_text(text))
            resume_names.append(name)

    if len(cleaned_resumes) == 0:
        return {}

    jd_cleaned = clean_text(job_description)

    documents = cleaned_resumes + [jd_cleaned]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity_scores = cosine_similarity(
        tfidf_matrix[:-1], tfidf_matrix[-1:]
    )

    results = {}
    for i, score in enumerate(similarity_scores):
        results[resume_names[i]] = round(score[0] * 100, 2)

    return results


def explain_score(resume_text, jd_text):
    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())
    matched = resume_words.intersection(jd_words)
    return list(matched)[:10]  # top 10 reasons


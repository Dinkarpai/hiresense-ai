import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CUSTOM_STOPWORDS = {
    "and", "or", "the", "a", "an", "to", "of", "in", "on", "for", "with",
    "is", "are", "we", "you", "will", "have", "has", "be", "as", "at",
    "by", "from", "this", "that", "it", "your", "our", "their", "than",
    "using", "used", "build", "built", "work", "worked", "experience"
}

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def calculate_similarity(resume, job_desc):
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([resume, job_desc])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])
    return round(float(similarity[0][0]) * 100, 2)

def get_missing_keywords(resume, job_desc):
    resume_words = set(resume.split())
    job_words = set(job_desc.split())

    missing = [
        word for word in job_words - resume_words
        if word not in CUSTOM_STOPWORDS and len(word) > 2 and not word.isdigit()
    ]

    return sorted(missing)[:15]
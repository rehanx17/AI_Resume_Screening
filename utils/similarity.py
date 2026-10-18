
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_tfidf(resume_text, job_description):
    """Convert resume and job description text into TF-IDF vectors."""

    documents = [
        str(resume_text or ""),
        str(job_description or ""),
    ]

    if not any(document.strip() for document in documents):
        return None

    vectorizer = TfidfVectorizer()

    try:
        return vectorizer.fit_transform(documents)
    except ValueError as error:
        message = str(error).lower()

        if (
            "empty vocabulary" in message
            or "no terms remain" in message
        ):
            return None

        raise


def calculate_similarity(resume_text, job_description):
    """Return cosine similarity as a percentage from 0 to 100."""

    resume_text = str(resume_text or "").strip()
    job_description = str(job_description or "").strip()

    if not resume_text or not job_description:
        return 0.0

    tfidf_matrix = calculate_tfidf(
        resume_text,
        job_description,
    )

    if tfidf_matrix is None:
        return 0.0

    score = float(
        cosine_similarity(tfidf_matrix)[0, 1]
    )

    return round(
        max(0.0, min(100.0, score * 100)),
        2,
    )

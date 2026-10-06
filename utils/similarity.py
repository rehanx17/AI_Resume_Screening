from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_tfidf(resume_text, job_description):
    documents = [resume_text, job_description]

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(documents)

    return tfidf_matrix


def calculate_similarity(resume_text, job_description):
    tfidf_matrix = calculate_tfidf(
        resume_text,
        job_description
    )

    similarity_matrix = cosine_similarity(tfidf_matrix)

    similarity_score = similarity_matrix[0][1]

    return round(similarity_score * 100, 2)
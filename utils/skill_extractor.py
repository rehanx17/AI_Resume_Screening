import re


SKILLS = [
    "python",
    "java",
    "sql",
    "mysql",
    "html",
    "css",
    "php",
    "machine learning",
    "data science",
    "data analytics",
    "pandas",
    "numpy",
    "excel",
    "power bi"
]


def extract_skills(text):
    found_skills = []

    for skill in SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills
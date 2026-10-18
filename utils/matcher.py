
def compare_skills(resume_skills, job_skills):
    """Compare resume skills with the skills required by a job."""

    resume_lookup = {
        str(skill).strip().casefold()
        for skill in (resume_skills or [])
        if str(skill).strip()
    }

    matched_skills = []
    missing_skills = []
    seen = set()

    for skill in (job_skills or []):
        normalized = str(skill).strip().casefold()

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)

        if normalized in resume_lookup:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    return matched_skills, missing_skills


def calculate_match_percentage(matched_skills, job_skills):
    """Calculate the percentage of required skills matched."""

    required = {
        str(skill).strip().casefold()
        for skill in (job_skills or [])
        if str(skill).strip()
    }

    if not required:
        return 0.0

    matched = {
        str(skill).strip().casefold()
        for skill in (matched_skills or [])
        if str(skill).strip()
    }

    matched_count = len(required.intersection(matched))

    return round((matched_count / len(required)) * 100, 2)

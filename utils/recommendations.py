def generate_recommendations(missing_skills):
    recommendations = []

    for skill in missing_skills:
        recommendation = (
            "Consider learning or improving " + skill +
            " because it is required by the job description."
        )

        recommendations.append(recommendation)

    return recommendations
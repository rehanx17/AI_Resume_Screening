
import os
import tempfile
import csv
import io

import streamlit as st

from utils.resume_parser import extract_text_from_pdf
from utils.skill_extractor import extract_skills
from utils.matcher import compare_skills, calculate_match_percentage
from utils.similarity import calculate_similarity
from utils.recommendations import generate_recommendations


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Resume Screening | Smart Recruiter",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM DASHBOARD STYLING
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .hero {
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(128, 128, 128, 0.3);
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        margin-bottom: 0.4rem;
    }

    div[data-testid="stMetric"] {
        padding: 1rem;
        border: 1px solid rgba(128, 128, 128, 0.3);
        border-radius: 12px;
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        min-height: 2.8rem;
    }

    div[data-testid="stDownloadButton"] button {
        border-radius: 10px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>📄 AI Resume Screening</h1>
        <p>
            Smart resume analysis and job matching powered by
            Natural Language Processing.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Upload resumes, compare them with a job description, "
    "and identify relevant skills and potential skill gaps."
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.title("⚙️ Project Information")

    st.write(
        "An NLP-based application that compares resume content "
        "with job requirements."
    )

    st.divider()

    st.subheader("Technology Stack")

    st.markdown(
        """
        - 🐍 Python
        - 🧠 Natural Language Processing
        - 📊 TF-IDF
        - 📐 Cosine Similarity
        - 🤖 Scikit-learn
        - 🌐 Streamlit
        - 📄 PyMuPDF
        """
    )

    st.divider()

    st.subheader("How It Works")

    st.markdown(
        """
        1. Upload PDF resumes.
        2. Enter a job description.
        3. Analyze skills and text.
        4. Compare candidates.
        5. Review skill gaps.
        6. Download the report.
        """
    )

    st.divider()

    st.caption("AI Resume Screening Project")


# =========================================================
# INPUT SECTION
# =========================================================

st.header("1. Enter Candidate Information")

resume_col, job_col = st.columns(2, gap="large")

with resume_col:
    st.subheader("📄 Upload Resumes")

    uploaded_resumes = st.file_uploader(
        "Choose one or more PDF resumes",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload text-based PDF resumes for comparison."
    )

    if uploaded_resumes:
        st.success(
            f"{len(uploaded_resumes)} resume(s) selected."
        )

        with st.expander("View uploaded files"):
            for resume in uploaded_resumes:
                st.write(f"📄 {resume.name}")

with job_col:
    st.subheader("💼 Job Description")

    job_description = st.text_area(
        "Paste the job requirements",
        height=220,
        placeholder=(
            "Example:\n"
            "We are looking for a Data Analyst with "
            "Python, SQL, Excel, Power BI and data "
            "visualization skills."
        )
    )

st.divider()


# =========================================================
# ANALYZE BUTTON
# =========================================================

analyze_button = st.button(
    "🔍 Analyze Resumes",
    type="primary",
    use_container_width=True
)


# =========================================================
# MULTIPLE-RESUME ANALYSIS
# =========================================================

if analyze_button:

    if not uploaded_resumes:
        st.error("Please upload at least one resume PDF.")

    elif not job_description.strip():
        st.error("Please enter a job description.")

    else:
        candidate_results = []
        failed_resumes = []

        # Extract required skills once for all candidates.
        try:
            job_skills = extract_skills(job_description)
        except Exception:
            st.error(
                "Unable to process the job description. "
                "Please review it and try again."
            )
            st.stop()

        # =============================================
        # PROCESS EACH RESUME
        # =============================================

        with st.spinner("Analyzing uploaded resumes..."):

            for uploaded_resume in uploaded_resumes:
                temporary_resume = None

                try:
                    # Create a unique temporary PDF.
                    with tempfile.NamedTemporaryFile(
                        suffix=".pdf",
                        delete=False
                    ) as temp_file:
                        temp_file.write(
                            uploaded_resume.getvalue()
                        )
                        temporary_resume = temp_file.name

                    # Extract resume text.
                    resume_text = extract_text_from_pdf(
                        temporary_resume
                    )

                    # Detect skills.
                    resume_skills = extract_skills(
                        resume_text
                    )

                    # Compare skills.
                    matched_skills, missing_skills = (
                        compare_skills(
                            resume_skills,
                            job_skills
                        )
                    )

                    # Calculate scores.
                    skill_match = calculate_match_percentage(
                        matched_skills,
                        job_skills
                    )

                    text_similarity = calculate_similarity(
                        resume_text,
                        job_description
                    )

                    # Generate recommendations.
                    recommendations = generate_recommendations(
                        missing_skills
                    )

                    # Save results for the dashboard.
                    candidate_results.append({
                        "resume_name": uploaded_resume.name,
                        "resume_text": resume_text,
                        "resume_skills": resume_skills,
                        "matched_skills": matched_skills,
                        "missing_skills": missing_skills,
                        "skill_match": float(skill_match),
                        "text_similarity": float(text_similarity),
                        "recommendations": recommendations,
                    })

                except Exception as error:
                    failed_resumes.append({
                        "name": uploaded_resume.name,
                        "error": str(error),
                    })

                finally:
                    # Always attempt to clean up temporary files.
                    if (
                        temporary_resume
                        and os.path.exists(temporary_resume)
                    ):
                        try:
                            os.remove(temporary_resume)
                        except OSError:
                            pass

        # =============================================
        # RANK CANDIDATES
        # =============================================

        candidate_results.sort(
            key=lambda candidate: candidate["skill_match"],
            reverse=True
        )

        st.divider()
        st.header("2. Candidate Screening Results")

        st.write(
            f"Successfully analyzed {len(candidate_results)} "
            f"of {len(uploaded_resumes)} resume(s)."
        )

        # =============================================
        # SUMMARY METRICS
        # =============================================

        if candidate_results:

            metric1, metric2, metric3 = st.columns(3)

            with metric1:
                st.metric(
                    "📄 Resumes Analyzed",
                    len(candidate_results)
                )

            with metric2:
                top_match = candidate_results[0]["skill_match"]

                st.metric(
                    "🏆 Highest Skill Match",
                    f"{top_match:g}%"
                )

            with metric3:
                average_match = sum(
                    candidate["skill_match"]
                    for candidate in candidate_results
                ) / len(candidate_results)

                st.metric(
                    "📈 Average Skill Match",
                    f"{average_match:.1f}%"
                )

            st.caption(
                "Candidates are ranked by detected Skill Match, "
                "from highest to lowest. Similarity scores and "
                "skill matches are comparison aids, not guarantees "
                "of job suitability or substitutes for human review."
            )

            st.divider()

            # =============================================
            # CANDIDATE RANKING TABLE
            # =============================================

            st.subheader("🏅 Candidate Ranking")

            ranking_table = []

            for rank, candidate in enumerate(
                candidate_results,
                start=1
            ):
                ranking_table.append({
                    "Rank": rank,
                    "Resume": candidate["resume_name"],
                    "Skill Match (%)": candidate["skill_match"],
                    "Text Similarity (%)": candidate["text_similarity"],
                    "Matched Skills": len(
                        candidate["matched_skills"]
                    ),
                    "Missing Skills": len(
                        candidate["missing_skills"]
                    ),
                })

            st.dataframe(
                ranking_table,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # =============================================
            # INDIVIDUAL CANDIDATE DETAILS
            # =============================================

            st.header("3. Individual Candidate Analysis")

            for rank, candidate in enumerate(
                candidate_results,
                start=1
            ):
                with st.expander(
                    f"#{rank} — {candidate['resume_name']} "
                    f"({candidate['skill_match']:g}% Skill Match)"
                ):

                    score_col1, score_col2 = st.columns(2)

                    with score_col1:
                        st.metric(
                            "🎯 Skill Match",
                            f"{candidate['skill_match']:g}%"
                        )

                        st.progress(
                            max(
                                0.0,
                                min(
                                    1.0,
                                    candidate["skill_match"] / 100
                                )
                            )
                        )

                    with score_col2:
                        st.metric(
                            "📈 Text Similarity",
                            f"{candidate['text_similarity']:g}%"
                        )

                        st.progress(
                            max(
                                0.0,
                                min(
                                    1.0,
                                    candidate["text_similarity"] / 100
                                )
                            )
                        )

                    matched_col, missing_col = st.columns(2)

                    with matched_col:
                        st.markdown("**✅ Matched Skills**")

                        if candidate["matched_skills"]:
                            for skill in candidate["matched_skills"]:
                                st.success(str(skill))
                        else:
                            st.info(
                                "No matching skills detected."
                            )

                    with missing_col:
                        st.markdown("**📌 Missing Skills**")

                        if candidate["missing_skills"]:
                            for skill in candidate["missing_skills"]:
                                st.warning(str(skill))
                        else:
                            st.success(
                                "No missing skills detected."
                            )

                    st.markdown("**💡 Recommendations**")

                    if candidate["recommendations"]:
                        for recommendation in candidate["recommendations"]:
                            st.info(str(recommendation))
                    else:
                        st.write(
                            "No specific recommendations generated."
                        )

                    with st.expander("📄 View Resume Skills"):
                        if candidate["resume_skills"]:
                            st.write(
                                ", ".join(
                                    map(
                                        str,
                                        candidate["resume_skills"]
                                    )
                                )
                            )
                        else:
                            st.write("No skills detected.")

                    with st.expander("📃 View Extracted Resume Text"):
                        st.text(candidate["resume_text"])

            st.divider()

            # =============================================
            # DOWNLOAD CSV COMPARISON REPORT
            # =============================================

            st.header("4. Download Candidate Report")

            csv_buffer = io.StringIO()

            fieldnames = [
                "Rank",
                "Resume",
                "Skill Match (%)",
                "Text Similarity (%)",
                "Matched Skills",
                "Missing Skills",
                "Recommendations",
            ]

            writer = csv.DictWriter(
                csv_buffer,
                fieldnames=fieldnames
            )

            writer.writeheader()

            for rank, candidate in enumerate(
                candidate_results,
                start=1
            ):
                writer.writerow({
                    "Rank": rank,
                    "Resume": candidate["resume_name"],
                    "Skill Match (%)": candidate["skill_match"],
                    "Text Similarity (%)": candidate["text_similarity"],
                    "Matched Skills": ", ".join(
                        map(str, candidate["matched_skills"])
                    ),
                    "Missing Skills": ", ".join(
                        map(str, candidate["missing_skills"])
                    ),
                    "Recommendations": "; ".join(
                        map(str, candidate["recommendations"])
                    ),
                })

            st.download_button(
                label="📥 Download Candidate Comparison (CSV)",
                data=csv_buffer.getvalue(),
                file_name="candidate_screening_report.csv",
                mime="text/csv",
                use_container_width=True
            )

        else:
            st.error(
                "None of the uploaded resumes could be analyzed. "
                "Please upload valid, text-based PDF resumes."
            )

        # =============================================
        # PROCESSING ERRORS
        # =============================================

        if failed_resumes:
            st.warning(
                f"{len(failed_resumes)} resume(s) could not be analyzed."
            )

            with st.expander("View processing errors"):
                for failed in failed_resumes:
                    st.write(f"**{failed['name']}**")
                    st.caption(failed["error"])


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AI Resume Screening & Job Matching System | "
    "Python • NLP • TF-IDF • Cosine Similarity • Streamlit"
)

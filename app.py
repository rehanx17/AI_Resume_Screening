
import os
import tempfile
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
    "Upload a resume, compare it with a job description, "
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

    st.subheader("How it works")

    st.markdown(
        """
        1. Upload a PDF resume.
        2. Enter a job description.
        3. Analyze skills and text.
        4. Review the results.
        5. Download the report.
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
    st.subheader("📄 Upload Resume")

    uploaded_resume = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a text-based PDF resume."
    )

    if uploaded_resume is not None:
        st.success(f"Selected: {uploaded_resume.name}")

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

analyze_button = st.button(
    "🔍 Analyze Resume",
    type="primary",
    use_container_width=True
)


# =========================================================
# ANALYSIS
# =========================================================

if analyze_button:

    if uploaded_resume is None:
        st.error("Please upload a resume PDF.")

    elif not job_description.strip():
        st.error("Please enter a job description.")

    else:
        temporary_resume = None

        try:
            with st.spinner("Analyzing the resume..."):

                with tempfile.NamedTemporaryFile(
                    suffix=".pdf",
                    delete=False
                ) as temp_file:
                    temp_file.write(uploaded_resume.getvalue())
                    temporary_resume = temp_file.name

                resume_text = extract_text_from_pdf(
                    temporary_resume
                )

                resume_skills = extract_skills(resume_text)
                job_skills = extract_skills(job_description)

                matched_skills, missing_skills = compare_skills(
                    resume_skills,
                    job_skills
                )

                skill_match_percentage = calculate_match_percentage(
                    matched_skills,
                    job_skills
                )

                similarity_percentage = calculate_similarity(
                    resume_text,
                    job_description
                )

                recommendations = generate_recommendations(
                    missing_skills
                )

        except ValueError as error:
            st.error(str(error))

        except Exception:
            st.error(
                "Unable to analyze this resume. "
                "Please check the PDF and try again."
            )

        else:
            # =============================================
            # RESULTS OVERVIEW
            # =============================================

            st.success("Resume analysis completed successfully.")

            st.header("2. Candidate Analysis Overview")

            st.caption(f"Resume analyzed: {uploaded_resume.name}")

            metric1, metric2, metric3 = st.columns(3)

            with metric1:
                st.metric(
                    "🎯 Skill Match",
                    f"{skill_match_percentage}%"
                )

            with metric2:
                st.metric(
                    "📈 Text Similarity",
                    f"{similarity_percentage}%"
                )

            with metric3:
                st.metric(
                    "✅ Skills Matched",
                    len(matched_skills)
                )

            # Keep progress values within the supported range.
            skill_progress = max(
                0.0,
                min(1.0, float(skill_match_percentage) / 100)
            )

            similarity_progress = max(
                0.0,
                min(1.0, float(similarity_percentage) / 100)
            )

            progress_col1, progress_col2 = st.columns(2)

            with progress_col1:
                st.write("Skill Match Progress")
                st.progress(skill_progress)

            with progress_col2:
                st.write("Text Similarity Progress")
                st.progress(similarity_progress)

            st.info(
                "Skill Match measures detected skill overlap. "
                "Text Similarity measures textual similarity. "
                "These scores do not guarantee job suitability "
                "and should not be used as the sole basis for hiring."
            )

            st.divider()

            # =============================================
            # SKILL GAP ANALYSIS
            # =============================================

            st.header("3. Skill Gap Analysis")

            matched_col, missing_col = st.columns(2, gap="large")

            with matched_col:
                st.subheader("✅ Matched Skills")

                if matched_skills:
                    for skill in matched_skills:
                        st.success(str(skill))
                else:
                    st.info("No matching skills were detected.")

            with missing_col:
                st.subheader("📌 Missing Skills")

                if missing_skills:
                    for skill in missing_skills:
                        st.warning(str(skill))
                else:
                    st.success(
                        "All detected job skills are matched."
                    )

            st.divider()

            # =============================================
            # RECOMMENDATIONS
            # =============================================

            st.header("4. Improvement Recommendations")

            if recommendations:
                for recommendation in recommendations:
                    st.info(str(recommendation))
            else:
                st.success(
                    "No specific recommendations were generated."
                )

            st.divider()

            # =============================================
            # DETECTED SKILLS
            # =============================================

            st.header("5. Detected Skills")

            resume_skills_col, job_skills_col = st.columns(2)

            with resume_skills_col:
                with st.expander("📄 Skills found in resume"):
                    if resume_skills:
                        st.write(", ".join(map(str, resume_skills)))
                    else:
                        st.write("No skills detected.")

            with job_skills_col:
                with st.expander("💼 Skills found in job description"):
                    if job_skills:
                        st.write(", ".join(map(str, job_skills)))
                    else:
                        st.write("No skills detected.")

            with st.expander("📃 View extracted resume text"):
                st.text(resume_text)

            st.divider()

            # =============================================
            # DOWNLOAD REPORT
            # =============================================

            st.header("6. Download Analysis Report")

            report_lines = [
                "AI RESUME SCREENING & JOB MATCHING REPORT",
                "=" * 45,
                "",
                f"Resume: {uploaded_resume.name}",
                f"Skill Match: {skill_match_percentage}%",
                f"Text Similarity: {similarity_percentage}%",
                "",
                "MATCHED SKILLS",
                "-" * 20,
                *(
                    list(map(str, matched_skills))
                    if matched_skills
                    else ["No matching skills detected."]
                ),
                "",
                "MISSING SKILLS",
                "-" * 20,
                *(
                    list(map(str, missing_skills))
                    if missing_skills
                    else ["No missing skills detected."]
                ),
                "",
                "RECOMMENDATIONS",
                "-" * 20,
                *(
                    list(map(str, recommendations))
                    if recommendations
                    else ["No specific recommendations."]
                ),
                "",
                "NOTE",
                "Scores indicate similarity and detected skill overlap.",
                "They do not guarantee job suitability.",
            ]

            report_text = "\n".join(report_lines)

            st.download_button(
                label="📥 Download Analysis Report (.txt)",
                data=report_text,
                file_name="resume_analysis_report.txt",
                mime="text/plain",
                use_container_width=True
            )

        finally:
            if (
                temporary_resume
                and os.path.exists(temporary_resume)
            ):
                try:
                    os.remove(temporary_resume)
                except OSError:
                    pass


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AI Resume Screening & Job Matching System | "
    "Python • NLP • TF-IDF • Cosine Similarity • Streamlit"
)

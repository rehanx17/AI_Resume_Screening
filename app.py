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
    page_title="AI Resume Screening & Job Matching",
    page_icon="📄",
    layout="wide"
)


# =========================================================
# HEADER
# =========================================================

st.title("📄 AI Resume Screening & Job Matching System")

st.markdown(
    """
    **NLP-based Resume Analysis System**

    Upload a resume and provide a job description to identify
    matching skills, missing skills, and textual similarity.
    """
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Project Information")

    st.write(
        """
        This system uses Natural Language Processing (NLP)
        techniques to compare a resume with a job description.
        """
    )

    st.subheader("Technologies")

    st.write("• Python")
    st.write("• NLP")
    st.write("• TF-IDF")
    st.write("• Cosine Similarity")
    st.write("• Scikit-learn")
    st.write("• Streamlit")

    st.divider()

    st.caption("AI Resume Screening Project")


# =========================================================
# INPUT SECTION
# =========================================================

st.header("📥 Input")

col1, col2 = st.columns(2)


# =========================================================
# RESUME UPLOAD
# =========================================================

with col1:

    st.subheader("📄 Resume")

    uploaded_resume = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"]
    )

    if uploaded_resume:

        st.success(
            f"Uploaded: {uploaded_resume.name}"
        )


# =========================================================
# JOB DESCRIPTION
# =========================================================

with col2:

    st.subheader("💼 Job Description")

    job_description = st.text_area(
        "Paste the job description below",
        height=220,
        placeholder=(
            "Example:\n"
            "We are looking for a Data Analyst with "
            "knowledge of Python, SQL, Excel and Power BI."
        )
    )


st.divider()


# =========================================================
# ANALYZE BUTTON
# =========================================================

analyze_button = st.button(
    "🔍 Analyze Resume",
    type="primary",
    use_container_width=True
)


# =========================================================
# ANALYSIS
# =========================================================

if analyze_button:

    # -----------------------------------------------------
    # CHECK RESUME
    # -----------------------------------------------------

    if uploaded_resume is None:

        st.error(
            "Please upload a resume PDF."
        )

        st.stop()


    # -----------------------------------------------------
    # CHECK JOB DESCRIPTION
    # -----------------------------------------------------

    if not job_description.strip():

        st.error(
            "Please enter a job description."
        )

        st.stop()


    # -----------------------------------------------------
    # START ANALYSIS
    # -----------------------------------------------------

    with st.spinner(
        "Analyzing resume and job description..."
    ):

        # -------------------------------------------------
        # Save uploaded PDF temporarily
        # -------------------------------------------------

        temporary_resume = "temp_resume.pdf"

        with open(
            temporary_resume,
            "wb"
        ) as file:

            file.write(
                uploaded_resume.getvalue()
            )


        # -------------------------------------------------
        # Extract Resume Text
        # -------------------------------------------------

        resume_text = extract_text_from_pdf(
            temporary_resume
        )


        # -------------------------------------------------
        # Extract Skills
        # -------------------------------------------------

        resume_skills = extract_skills(
            resume_text
        )

        job_skills = extract_skills(
            job_description
        )


        # -------------------------------------------------
        # Compare Skills
        # -------------------------------------------------

        matched_skills, missing_skills = compare_skills(
            resume_skills,
            job_skills
        )


        # -------------------------------------------------
        # Calculate Skill Match
        # -------------------------------------------------

        skill_match_percentage = calculate_match_percentage(
            matched_skills,
            job_skills
        )


        # -------------------------------------------------
        # Calculate Text Similarity
        # -------------------------------------------------

        similarity_percentage = calculate_similarity(
            resume_text,
            job_description
        )


        # -------------------------------------------------
        # Generate Recommendations
        # -------------------------------------------------

        recommendations = generate_recommendations(
            missing_skills
        )


    # =====================================================
    # RESULTS
    # =====================================================

    st.success(
        "Analysis completed successfully! ✅"
    )

    st.header("📊 Analysis Results")


    # =====================================================
    # SCORE CARDS
    # =====================================================

    score1, score2 = st.columns(2)


    with score1:

        st.metric(
            label="🎯 Skill Match",
            value=f"{skill_match_percentage}%"
        )


    with score2:

        st.metric(
            label="📈 Text Similarity",
            value=f"{similarity_percentage}%"
        )


    st.divider()


    # =====================================================
    # SKILL ANALYSIS
    # =====================================================

    matched_col, missing_col = st.columns(2)


    # =====================================================
    # MATCHED SKILLS
    # =====================================================

    with matched_col:

        st.subheader("✅ Matched Skills")

        if matched_skills:

            for skill in matched_skills:

                st.success(
                    skill,
                    icon="✅"
                )

        else:

            st.info(
                "No matching skills detected."
            )


    # =====================================================
    # MISSING SKILLS
    # =====================================================

    with missing_col:

        st.subheader("❌ Missing Skills")

        if missing_skills:

            for skill in missing_skills:

                st.error(
                    skill,
                    icon="❌"
                )

        else:

            st.success(
                "No missing skills detected.",
                icon="✅"
            )


    st.divider()


    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    st.subheader("💡 Recommendations")

    if recommendations:

        for recommendation in recommendations:

            st.info(
                recommendation
            )

    else:

        st.success(
            "No specific recommendations at this time."
        )


    st.divider()


    # =====================================================
    # DETECTED SKILLS
    # =====================================================

    skills_col1, skills_col2 = st.columns(2)


    # =====================================================
    # RESUME SKILLS
    # =====================================================

    with skills_col1:

        with st.expander(
            "📄 View Resume Skills"
        ):

            if resume_skills:

                for skill in resume_skills:

                    st.write(
                        f"• {skill}"
                    )

            else:

                st.write(
                    "No skills detected."
                )


    # =====================================================
    # JOB SKILLS
    # =====================================================

    with skills_col2:

        with st.expander(
            "💼 View Job Required Skills"
        ):

            if job_skills:

                for skill in job_skills:

                    st.write(
                        f"• {skill}"
                    )

            else:

                st.write(
                    "No job skills detected."
                )


    # =====================================================
    # EXTRACTED RESUME TEXT
    # =====================================================

    with st.expander(
        "📃 View Extracted Resume Text"
    ):

        st.text(
            resume_text
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AI Resume Screening & Job Matching System | "
    "Python • NLP • TF-IDF • Cosine Similarity • Streamlit"
)
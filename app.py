
import os
import tempfile
import csv
import io
from datetime import datetime
from xml.sax.saxutils import escape

import streamlit as st

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from utils.resume_parser import extract_text_from_pdf
from utils.skill_extractor import extract_skills
from utils.matcher import compare_skills, calculate_match_percentage
from utils.similarity import calculate_similarity
from utils.recommendations import generate_recommendations


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Resume Screening",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------


st.markdown(
    """
    <style>
    /* Main page */
    .stApp {
        background-color: #F8FAFC;
        color: #1E293B;
    }

    /* Main content */
    [data-testid="stAppViewContainer"] {
        background-color: #F8FAFC;
    }

    [data-testid="stHeader"] {
        background-color: #F8FAFC;
    }

    [data-testid="stMain"] {
        color: #1E293B;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    [data-testid="stSidebar"] * {
        color: #1E293B;
    }

    /* Main headings */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #172554 !important;
        margin-bottom: 0.4rem;
    }

    .subtitle {
        font-size: 1rem;
        color: #475569 !important;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }

    .section-title {
        color: #172554 !important;
        font-weight: 700;
    }

    /* General text */
    .stApp p,
    .stApp label,
    .stApp li,
    .stApp [data-testid="stMarkdownContainer"] {
        color: #1E293B;
    }

    /* Input fields */
    .stTextArea textarea,
    .stTextInput input,
    [data-baseweb="input"] input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }

    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder {
        color: #64748B !important;
        opacity: 1;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        border: 1px dashed #94A3B8;
        border-radius: 10px;
        padding: 12px;
    }

    [data-testid="stFileUploader"] section {
        background-color: #FFFFFF;
    }

    [data-testid="stFileUploader"] button {
        background-color: #EEF2FF;
        color: #3730A3;
        border: 1px solid #C7D2FE;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
    }

    [data-testid="stMetricLabel"] {
        color: #475569 !important;
    }

    [data-testid="stMetricValue"] {
        color: #172554 !important;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        background-color: #4F46E5;
        color: #FFFFFF !important;
        border: 1px solid #4F46E5;
        border-radius: 8px;
        font-weight: 600;
        min-height: 42px;
    }

    .stButton > button p,
    .stDownloadButton > button p {
        color: #FFFFFF !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: #3730A3;
        border-color: #3730A3;
        color: #FFFFFF !important;
    }

    /* Tables */
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {
        color: #172554 !important;
    }

    /* Progress bars */
    [data-testid="stProgressBar"] > div {
        background-color: #E2E8F0;
    }

    [data-testid="stProgressBar"] > div > div {
        background-color: #4F46E5;
    }

    /* Links */
    .stApp a {
        color: #4338CA !important;
    }

    /* Dividers and footer */
    hr {
        border-color: #E2E8F0 !important;
    }

    .stCaption,
    [data-testid="stCaptionContainer"] {
        color: #64748B !important;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        border-radius: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("📄 AI Resume Screening")

    st.write(
        "Screen multiple resumes against a job description "
        "and compare candidate skills."
    )

    st.divider()

    st.subheader("Features")
    st.markdown(
        """
        - Multiple PDF resume uploads
        - Automatic skill extraction
        - Job-description matching
        - Candidate ranking
        - Skill-gap recommendations
        - CSV report export
        - PDF report export
        """
    )

    st.divider()

    st.caption("AI Resume Screening System")
    st.caption("Python • Streamlit • NLP • Machine Learning")


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">AI Resume Screening Dashboard</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Upload resumes, enter a job description, and compare candidates
    using skill matching and text similarity.
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# INPUT SECTION
# --------------------------------------------------

st.subheader("1. Enter Job Details")

job_description = st.text_area(
    "Job Description",
    height=220,
    placeholder=(
        "Paste the complete job description here, including "
        "required skills, qualifications, and responsibilities..."
    ),
    help="A detailed job description generally gives more useful results.",
)

st.subheader("2. Upload Candidate Resumes")

uploaded_resumes = st.file_uploader(
    "Choose one or more PDF resumes",
    type=["pdf"],
    accept_multiple_files=True,
    help="Upload text-based PDF resumes for comparison.",
)

if uploaded_resumes:
    st.success(f"{len(uploaded_resumes)} resume(s) selected.")


# --------------------------------------------------
# SCREENING PROCESS
# --------------------------------------------------

analyze_button = st.button(
    "🔍 Analyze Resumes",
    type="primary",
    use_container_width=True,
)

if analyze_button:

    if not job_description.strip():
        st.error("Please enter a job description.")

    elif not uploaded_resumes:
        st.error("Please upload at least one PDF resume.")

    else:
        candidate_results = []
        failed_resumes = []

        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Extract job skills once.
            job_skills = extract_skills(job_description)

            if not job_skills:
                st.warning(
                    "No recognizable skills were detected in the job "
                    "description. The results may be less informative."
                )

            total_resumes = len(uploaded_resumes)

            for index, uploaded_file in enumerate(uploaded_resumes):
                status_text.write(
                    f"Analyzing resume {index + 1} of {total_resumes}: "
                    f"{uploaded_file.name}"
                )

                temp_path = None

                try:
                    # Save upload temporarily for the PDF parser.
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf",
                    ) as temp_file:
                        temp_file.write(uploaded_file.getvalue())
                        temp_path = temp_file.name

                    # Extract resume text and skills.
                    resume_text = extract_text_from_pdf(temp_path)
                    resume_skills = extract_skills(resume_text)

                    # Compare skills with the job description.
                    matched_skills, missing_skills = compare_skills(
                        job_skills,
                        resume_skills,
                    )

                    skill_match = calculate_match_percentage(
                        matched_skills,
                        job_skills,
                    )

                    # Calculate text similarity.
                    text_similarity = calculate_similarity(
                        job_description,
                        resume_text,
                    )

                    # Generate skill-gap recommendations.
                    recommendations = generate_recommendations(
                        missing_skills
                    )

                    candidate_results.append(
                        {
                            "resume_name": uploaded_file.name,
                            "resume_text": resume_text,
                            "resume_skills": resume_skills,
                            "matched_skills": matched_skills,
                            "missing_skills": missing_skills,
                            "skill_match": float(skill_match),
                            "text_similarity": float(text_similarity),
                            "recommendations": recommendations,
                        }
                    )

                except Exception as error:
                    failed_resumes.append(
                        {
                            "resume_name": uploaded_file.name,
                            "error": str(error),
                        }
                    )

                finally:
                    if temp_path and os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except OSError:
                            pass

                progress_bar.progress((index + 1) / total_resumes)

        except Exception as error:
            st.error(
                "The screening process could not be completed. "
                f"Details: {error}"
            )

        else:
            # Rank candidates by skill match.
            candidate_results.sort(
                key=lambda candidate: candidate["skill_match"],
                reverse=True,
            )

            status_text.empty()
            progress_bar.empty()

            if failed_resumes:
                st.warning(
                    f"{len(failed_resumes)} resume(s) could not be analyzed."
                )

                with st.expander("View resume processing errors"):
                    for failed in failed_resumes:
                        st.write(f"**{failed['resume_name']}**")
                        st.caption(failed["error"])

            if not candidate_results:
                st.error(
                    "No resumes could be analyzed successfully. "
                    "Check that the uploaded PDFs contain readable text."
                )

            else:
                # Store results for display in this Streamlit session.
                st.session_state["candidate_results"] = candidate_results
                st.session_state["screened_job_description"] = job_description
                st.session_state["failed_resumes"] = failed_resumes


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

candidate_results = st.session_state.get("candidate_results", [])

if candidate_results:

    st.divider()
    st.header("📊 Screening Results")

    total_candidates = len(candidate_results)

    average_match = sum(
        candidate["skill_match"] for candidate in candidate_results
    ) / total_candidates

    top_candidate = candidate_results[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Candidates Screened", total_candidates)

    with col2:
        st.metric("Average Skill Match", f"{average_match:.1f}%")

    with col3:
        st.metric(
            "Highest Skill Match",
            f"{top_candidate['skill_match']:.1f}%",
        )

    st.subheader("🏆 Candidate Ranking")

    ranking_rows = []

    for rank, candidate in enumerate(candidate_results, start=1):
        ranking_rows.append(
            {
                "Rank": rank,
                "Candidate": candidate["resume_name"],
                "Skill Match (%)": round(candidate["skill_match"], 2),
                "Text Similarity (%)": round(
                    candidate["text_similarity"], 2
                ),
                "Matched Skills": len(candidate["matched_skills"]),
                "Missing Skills": len(candidate["missing_skills"]),
            }
        )

    st.dataframe(
        ranking_rows,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Rankings are based on skill-match percentage. "
        "Similarity is shown as a separate text comparison measure."
    )

    # --------------------------------------------------
    # INDIVIDUAL CANDIDATE DETAILS
    # --------------------------------------------------

    st.subheader("👤 Candidate Details")

    for rank, candidate in enumerate(candidate_results, start=1):

        with st.expander(
            f"#{rank} — {candidate['resume_name']} "
            f"({candidate['skill_match']:.1f}% skill match)"
        ):

            metric1, metric2 = st.columns(2)

            with metric1:
                st.metric(
                    "Skill Match",
                    f"{candidate['skill_match']:.1f}%",
                )
                st.progress(
                    max(
                        0.0,
                        min(1.0, candidate["skill_match"] / 100),
                    )
                )

            with metric2:
                st.metric(
                    "Text Similarity",
                    f"{candidate['text_similarity']:.1f}%",
                )
                st.progress(
                    max(
                        0.0,
                        min(1.0, candidate["text_similarity"] / 100),
                    )
                )

            st.markdown("#### ✅ Matched Skills")

            if candidate["matched_skills"]:
                st.write(", ".join(map(str, candidate["matched_skills"])))
            else:
                st.write("No matching skills identified.")

            st.markdown("#### 📌 Missing Skills")

            if candidate["missing_skills"]:
                st.write(", ".join(map(str, candidate["missing_skills"])))
            else:
                st.write("No missing skills identified from the comparison.")

            st.markdown("#### 💡 Recommendations")

            recommendations = candidate["recommendations"]

            if recommendations:
                if isinstance(recommendations, str):
                    st.write(recommendations)
                else:
                    for recommendation in recommendations:
                        st.write(f"- {recommendation}")
            else:
                st.write("No additional recommendations.")

            st.markdown("#### 🧠 Skills Found in Resume")

            if candidate["resume_skills"]:
                st.write(", ".join(map(str, candidate["resume_skills"])))
            else:
                st.write("No recognized skills found.")

            with st.expander("View extracted resume text"):
                st.text(candidate["resume_text"])


    # --------------------------------------------------
    # CSV REPORT DOWNLOAD
    # --------------------------------------------------

    st.divider()
    st.header("📥 Download Reports")

    csv_buffer = io.StringIO()

    csv_columns = [
        "Rank",
        "Candidate",
        "Skill Match (%)",
        "Text Similarity (%)",
        "Resume Skills",
        "Matched Skills",
        "Missing Skills",
        "Recommendations",
    ]

    csv_writer = csv.DictWriter(
        csv_buffer,
        fieldnames=csv_columns,
    )

    csv_writer.writeheader()

    for rank, candidate in enumerate(candidate_results, start=1):
        csv_writer.writerow(
            {
                "Rank": rank,
                "Candidate": candidate["resume_name"],
                "Skill Match (%)": round(candidate["skill_match"], 2),
                "Text Similarity (%)": round(
                    candidate["text_similarity"], 2
                ),
                "Resume Skills": ", ".join(
                    map(str, candidate["resume_skills"])
                ),
                "Matched Skills": ", ".join(
                    map(str, candidate["matched_skills"])
                ),
                "Missing Skills": ", ".join(
                    map(str, candidate["missing_skills"])
                ),
                "Recommendations": (
                    candidate["recommendations"]
                    if isinstance(candidate["recommendations"], str)
                    else "; ".join(
                        map(str, candidate["recommendations"] or [])
                    )
                ),
            }
        )

    st.download_button(
        label="📊 Download CSV Report",
        data=csv_buffer.getvalue().encode("utf-8-sig"),
        file_name="candidate_screening_report.csv",
        mime="text/csv",
        use_container_width=True,
        key="download_csv_report",
    )


    # --------------------------------------------------
    # PDF REPORT GENERATION
    # --------------------------------------------------

    def make_pdf_report(results):
        """Create a PDF report in memory and return its bytes."""

        buffer = io.BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=40,
            bottomMargin=40,
            title="AI Resume Screening Report",
            author="AI Resume Screening System",
        )

        styles = getSampleStyleSheet()
        story = []

        story.append(
            Paragraph(
                "AI Resume Screening Report",
                styles["Title"],
            )
        )
        story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                "Generated: "
                + datetime.now().strftime("%d %B %Y, %I:%M %p"),
                styles["Normal"],
            )
        )
        story.append(
            Paragraph(
                f"Candidates successfully screened: {len(results)}",
                styles["Normal"],
            )
        )

        if st.session_state.get("screened_job_description"):
            story.append(Spacer(1, 8))
            story.append(
                Paragraph("Job Description", styles["Heading2"])
            )

            job_text = escape(
                st.session_state["screened_job_description"]
            ).replace("\n", "<br/>")

            story.append(Paragraph(job_text, styles["BodyText"]))

        story.append(Spacer(1, 16))
        story.append(
            Paragraph("Candidate Rankings", styles["Heading2"])
        )

        table_data = [
            [
                "Rank",
                "Candidate",
                "Skill Match",
                "Similarity",
            ]
        ]

        for rank, candidate in enumerate(results, start=1):
            table_data.append(
                [
                    str(rank),
                    Paragraph(
                        escape(str(candidate["resume_name"])),
                        styles["BodyText"],
                    ),
                    f"{candidate['skill_match']:.1f}%",
                    f"{candidate['text_similarity']:.1f}%",
                ]
            )

        ranking_table = Table(
            table_data,
            colWidths=[38, 265, 85, 85],
            repeatRows=1,
        )

        ranking_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#17365D"),
                    ),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.lightgrey,
                    ),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor("#F0F4F8"),
                        ],
                    ),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )

        story.append(ranking_table)
        story.append(Spacer(1, 18))

        story.append(
            Paragraph("Candidate Skill Analysis", styles["Heading2"])
        )

        def display_items(items):
            if not items:
                return "None identified"

            if isinstance(items, str):
                return escape(items)

            return escape(", ".join(map(str, items)))

        for rank, candidate in enumerate(results, start=1):
            story.append(
                Paragraph(
                    f"{rank}. {escape(str(candidate['resume_name']))}",
                    styles["Heading3"],
                )
            )

            story.append(
                Paragraph(
                    f"Skill Match: {candidate['skill_match']:.1f}%",
                    styles["BodyText"],
                )
            )

            story.append(
                Paragraph(
                    "Text Similarity: "
                    f"{candidate['text_similarity']:.1f}%",
                    styles["BodyText"],
                )
            )
            story.append(Spacer(1, 5))

            story.append(
                Paragraph(
                    "<b>Resume Skills:</b> "
                    + display_items(candidate["resume_skills"]),
                    styles["BodyText"],
                )
            )
            story.append(Spacer(1, 5))

            story.append(
                Paragraph(
                    "<b>Matched Skills:</b> "
                    + display_items(candidate["matched_skills"]),
                    styles["BodyText"],
                )
            )
            story.append(Spacer(1, 5))

            story.append(
                Paragraph(
                    "<b>Missing Skills:</b> "
                    + display_items(candidate["missing_skills"]),
                    styles["BodyText"],
                )
            )
            story.append(Spacer(1, 5))

            recommendations = candidate["recommendations"]

            if isinstance(recommendations, str):
                recommendation_text = escape(recommendations)
            else:
                recommendation_text = display_items(recommendations)

            story.append(
                Paragraph(
                    "<b>Recommendations:</b> " + recommendation_text,
                    styles["BodyText"],
                )
            )

            story.append(Spacer(1, 14))

        document.build(story)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes


    try:
        pdf_report = make_pdf_report(candidate_results)

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_report,
            file_name="candidate_screening_report.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="download_pdf_report",
        )

    except Exception as error:
        st.error(
            "Could not generate the PDF report. "
            f"Details: {error}"
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI Resume Screening System | Built with Python, Streamlit, "
    "PDF text extraction, skill matching, and text similarity."
)

st.caption(
    "Screening scores are decision-support indicators, not a substitute "
    "for human review. Review candidates fairly and verify information "
    "before making recruitment decisions."
)

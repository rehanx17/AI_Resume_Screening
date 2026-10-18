
import io
import csv
import os
import tempfile
from datetime import datetime
from xml.sax.saxutils import escape

import pandas as pd
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


# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="AI Resume Screening",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# 2. CUSTOM CSS
# ==========================================================

st.markdown(
    """
    <style>
    .stApp,
    [data-testid="stAppViewContainer"] {
        background-color: #F8FAFC;
        color: #1E293B;
    }

    [data-testid="stHeader"] {
        background-color: #F8FAFC;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    [data-testid="stSidebar"] * {
        color: #1E293B;
    }

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

    .stApp p,
    .stApp label,
    .stApp li,
    .stApp [data-testid="stMarkdownContainer"] {
        color: #1E293B;
    }

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
    }

    [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
    }

    [data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {
        color: #172554 !important;
    }

    .resume-text-box {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 18px;
        font-family: Arial, sans-serif;
        font-size: 14px;
        line-height: 1.7;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        max-height: 500px;
        overflow-y: auto;
    }

    .resume-text-box,
    .resume-text-box * {
        color: #1E293B !important;
    }

    .stApp a {
        color: #4338CA !important;
    }

    hr {
        border-color: #E2E8F0 !important;
    }

    [data-testid="stCaptionContainer"] {
        color: #64748B !important;
    }

    [data-testid="stAlert"] {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# 3. HELPER FUNCTIONS
# ==========================================================

def format_items(items):
    """Convert a list or string into readable text."""
    if not items:
        return "None identified"

    if isinstance(items, str):
        return items

    return ", ".join(str(item) for item in items)


def recommendations_to_text(recommendations):
    """Convert recommendations into readable text."""
    if not recommendations:
        return "No additional recommendations."

    if isinstance(recommendations, str):
        return recommendations

    return "; ".join(str(item) for item in recommendations)


def make_pdf_report(results, job_description):
    """Create a PDF screening report in memory."""

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

    if job_description:
        story.append(Spacer(1, 12))
        story.append(
            Paragraph("Job Description", styles["Heading2"])
        )

        safe_description = escape(str(job_description)).replace(
            "\n", "<br/>"
        )

        story.append(
            Paragraph(safe_description, styles["BodyText"])
        )

    story.append(Spacer(1, 18))
    story.append(
        Paragraph("Candidate Rankings", styles["Heading2"])
    )

    table_data = [
        ["Rank", "Candidate", "Skill Match", "Similarity"]
    ]

    for rank, candidate in enumerate(results, start=1):
        table_data.append(
            [
                str(rank),
                Paragraph(
                    escape(str(candidate["resume_name"])),
                    styles["BodyText"],
                ),
                f'{candidate["skill_match"]:.1f}%',
                f'{candidate["text_similarity"]:.1f}%',
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

    for rank, candidate in enumerate(results, start=1):
        story.append(
            Paragraph(
                f'{rank}. {escape(str(candidate["resume_name"]))}',
                styles["Heading3"],
            )
        )

        story.append(
            Paragraph(
                f'Skill Match: {candidate["skill_match"]:.1f}%',
                styles["BodyText"],
            )
        )

        story.append(
            Paragraph(
                f'Text Similarity: '
                f'{candidate["text_similarity"]:.1f}%',
                styles["BodyText"],
            )
        )

        for label, key in [
            ("Resume Skills", "resume_skills"),
            ("Matched Skills", "matched_skills"),
            ("Missing Skills", "missing_skills"),
        ]:
            safe_items = escape(format_items(candidate.get(key, [])))

            story.append(
                Paragraph(
                    f"<b>{label}:</b> {safe_items}",
                    styles["BodyText"],
                )
            )

        safe_recommendations = escape(
            recommendations_to_text(
                candidate.get("recommendations", [])
            )
        )

        story.append(
            Paragraph(
                f"<b>Recommendations:</b> {safe_recommendations}",
                styles["BodyText"],
            )
        )

        story.append(Spacer(1, 14))

    document.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


def analyze_resume(uploaded_file, job_description, job_skills):
    """Process one resume and return its screening results."""

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name

        resume_text = extract_text_from_pdf(temp_path)

        if not resume_text or not resume_text.strip():
            raise ValueError(
                "No readable text was found in this PDF. "
                "Scanned PDFs may require OCR."
            )

        resume_skills = extract_skills(resume_text)

        if job_skills:
            matched_skills, missing_skills = compare_skills(
                resume_skills,
                job_skills,
            )

            skill_match = calculate_match_percentage(
                matched_skills,
                job_skills,
            )
        else:
            matched_skills = []
            missing_skills = []
            skill_match = 0.0

        # Calculate similarity for every successfully parsed resume.
        text_similarity = calculate_similarity(
            resume_text,
            job_description,
        )

        recommendations = generate_recommendations(
            missing_skills
        )

        return {
            "resume_name": uploaded_file.name,
            "resume_text": resume_text,
            "resume_skills": resume_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "skill_match": float(skill_match),
            "text_similarity": float(text_similarity),
            "recommendations": recommendations,
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


# ==========================================================
# 4. SIDEBAR
# ==========================================================

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
        - Candidate comparison chart
        - Skill-gap recommendations
        - CSV report export
        - PDF report export
        """
    )

    st.divider()
    st.caption("AI Resume Screening System")
    st.caption("Python • Streamlit • NLP • Text Similarity")


# ==========================================================
# 5. PAGE HEADER
# ==========================================================

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


# ==========================================================
# 6. INPUT SECTION
# ==========================================================

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
    st.success(
        f"{len(uploaded_resumes)} resume(s) selected."
    )


# ==========================================================
# 7. ANALYZE RESUMES
# ==========================================================

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
        # Clear previous results before starting a new screening.
        st.session_state.pop("candidate_results", None)
        st.session_state.pop("screened_job_description", None)
        st.session_state.pop("failed_resumes", None)

        candidate_results = []
        failed_resumes = []

        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            job_skills = extract_skills(job_description)

            if not job_skills:
                st.warning(
                    "No recognizable skills were detected in the job "
                    "description. Skill-match results will be zero."
                )

            total_resumes = len(uploaded_resumes)

            for index, uploaded_file in enumerate(uploaded_resumes):
                status_text.write(
                    f"Analyzing resume {index + 1} of {total_resumes}: "
                    f"{uploaded_file.name}"
                )

                try:
                    result = analyze_resume(
                        uploaded_file,
                        job_description,
                        job_skills,
                    )
                    candidate_results.append(result)

                except Exception as error:
                    failed_resumes.append(
                        {
                            "resume_name": uploaded_file.name,
                            "error": str(error),
                        }
                    )

                progress_bar.progress(
                    (index + 1) / total_resumes
                )

            # Rank candidates by skill-match percentage.
            candidate_results.sort(
                key=lambda candidate: candidate["skill_match"],
                reverse=True,
            )

            if candidate_results:
                st.session_state["candidate_results"] = (
                    candidate_results
                )
                st.session_state["screened_job_description"] = (
                    job_description
                )

            st.session_state["failed_resumes"] = failed_resumes

        except Exception as error:
            st.error(
                "The screening process could not be completed. "
                f"Details: {error}"
            )

        finally:
            status_text.empty()
            progress_bar.empty()

        if failed_resumes:
            st.warning(
                f"{len(failed_resumes)} resume(s) could not be analyzed."
            )

            with st.expander("View resume processing errors"):
                for failed in failed_resumes:
                    st.write(f'**{failed["resume_name"]}**')
                    st.caption(failed["error"])

        if not candidate_results:
            st.error(
                "No resumes could be analyzed successfully. "
                "Check that the uploaded PDFs contain readable text."
            )


# ==========================================================
# 8. DISPLAY SCREENING RESULTS
# ==========================================================

candidate_results = st.session_state.get(
    "candidate_results", []
)

if candidate_results:
    st.divider()
    st.header("📊 Screening Results")

    total_candidates = len(candidate_results)

    average_match = (
        sum(
            candidate["skill_match"]
            for candidate in candidate_results
        )
        / total_candidates
    )

    top_candidate = candidate_results[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Candidates Screened",
            total_candidates,
        )

    with col2:
        st.metric(
            "Average Skill Match",
            f"{average_match:.1f}%",
        )

    with col3:
        st.metric(
            "Highest Skill Match",
            f'{top_candidate["skill_match"]:.1f}%',
        )

    # ------------------------------------------------------
    # CANDIDATE RANKING
    # ------------------------------------------------------

    st.subheader("🏆 Candidate Ranking")

    ranking_rows = []

    for rank, candidate in enumerate(
        candidate_results, start=1
    ):
        ranking_rows.append(
            {
                "Rank": rank,
                "Candidate": candidate["resume_name"],
                "Skill Match (%)": round(
                    candidate["skill_match"], 2
                ),
                "Text Similarity (%)": round(
                    candidate["text_similarity"], 2
                ),
                "Matched Skills": len(
                    candidate["matched_skills"]
                ),
                "Missing Skills": len(
                    candidate["missing_skills"]
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(ranking_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Rankings are based on skill-match percentage. "
        "Text similarity is displayed as a separate measure."
    )

    # ------------------------------------------------------
    # CANDIDATE COMPARISON CHART
    # ------------------------------------------------------

    st.divider()
    st.subheader("📈 Candidate Comparison")

    chart_data = [
        {
            "Candidate": candidate["resume_name"],
            "Skill Match (%)": round(
                candidate["skill_match"], 2
            ),
            "Text Similarity (%)": round(
                candidate["text_similarity"], 2
            ),
        }
        for candidate in candidate_results
    ]

    chart_df = pd.DataFrame(chart_data).set_index("Candidate")

    st.bar_chart(chart_df)

    st.caption(
        "Higher scores indicate greater measured skill overlap or "
        "text similarity, not a guaranteed hiring outcome."
    )

    # ------------------------------------------------------
    # INDIVIDUAL CANDIDATE DETAILS
    # ------------------------------------------------------

    st.subheader("👤 Candidate Details")

    for rank, candidate in enumerate(
        candidate_results, start=1
    ):
        with st.expander(
            f'#{rank} — {candidate["resume_name"]} '
            f'({candidate["skill_match"]:.1f}% skill match)'
        ):
            metric1, metric2 = st.columns(2)

            with metric1:
                st.metric(
                    "Skill Match",
                    f'{candidate["skill_match"]:.1f}%',
                )
                st.progress(
                    max(
                        0.0,
                        min(
                            1.0,
                            candidate["skill_match"] / 100,
                        ),
                    )
                )

            with metric2:
                st.metric(
                    "Text Similarity",
                    f'{candidate["text_similarity"]:.1f}%',
                )
                st.progress(
                    max(
                        0.0,
                        min(
                            1.0,
                            candidate["text_similarity"] / 100,
                        ),
                    )
                )

            st.markdown("#### ✅ Matched Skills")

            if candidate["matched_skills"]:
                st.write(
                    format_items(candidate["matched_skills"])
                )
            else:
                st.write("No matching skills identified.")

            st.markdown("#### 📌 Missing Skills")

            if candidate["missing_skills"]:
                st.write(
                    format_items(candidate["missing_skills"])
                )
            else:
                st.write(
                    "No missing skills identified from the comparison."
                )

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
                st.write(
                    format_items(candidate["resume_skills"])
                )
            else:
                st.write("No recognized skills found.")

            with st.expander("📄 View extracted resume text"):
                safe_resume_text = escape(
                    candidate.get("resume_text", "") or ""
                )

                st.markdown(
                    f'<div class="resume-text-box">'
                    f"{safe_resume_text}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # ======================================================
    # 9. DOWNLOAD CSV REPORT
    # ======================================================

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

    for rank, candidate in enumerate(
        candidate_results, start=1
    ):
        csv_writer.writerow(
            {
                "Rank": rank,
                "Candidate": candidate["resume_name"],
                "Skill Match (%)": round(
                    candidate["skill_match"], 2
                ),
                "Text Similarity (%)": round(
                    candidate["text_similarity"], 2
                ),
                "Resume Skills": format_items(
                    candidate["resume_skills"]
                ),
                "Matched Skills": format_items(
                    candidate["matched_skills"]
                ),
                "Missing Skills": format_items(
                    candidate["missing_skills"]
                ),
                "Recommendations": recommendations_to_text(
                    candidate["recommendations"]
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

    # ======================================================
    # 10. DOWNLOAD PDF REPORT
    # ======================================================

    try:
        pdf_report = make_pdf_report(
            candidate_results,
            st.session_state.get(
                "screened_job_description", ""
            ),
        )

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


# ==========================================================
# 11. FOOTER
# ==========================================================

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

# AI Resume Screening System

An AI-assisted resume screening web application that analyzes multiple PDF resumes against a job description, compares skills, ranks candidates, and generates screening reports.

## Live Demo

**Live Application:** https://airesumescreening-nnvkwbanjwbmfesrvmthcq.streamlit.app/

**Source Code:** https://github.com/rehanx17/AI_Resume_Screening

## Project Overview

Recruiters may need to review many resumes for a single job opening. Manually comparing every resume can be time-consuming.

The AI Resume Screening System helps simplify this process by extracting text from PDF resumes, identifying skills, comparing them with job requirements, and presenting candidate results in an organized dashboard.

The system assists recruitment decisions; final candidate selection should remain a human decision.

## Features

* Upload and analyze multiple PDF resumes.
* Extract text from PDF documents.
* Identify skills in resumes and job descriptions.
* Compare candidate skills with job requirements.
* Calculate skill-match percentages.
* Calculate text similarity scores.
* Rank candidates according to skill-match percentage.
* Display matched and missing skills.
* Generate skill-gap recommendations.
* Compare candidates using a chart.
* Download screening results as CSV.
* Generate downloadable PDF screening reports.
* Handle invalid or unreadable PDF files.
* Access the application through a web browser.

## Technologies Used

* **Python:** Core programming language.
* **Streamlit:** Interactive web application and dashboard.
* **PyMuPDF:** PDF text extraction.
* **Pandas:** Tabular data handling and chart preparation.
* **Scikit-learn:** Text vectorization and similarity calculations.
* **TF-IDF and Cosine Similarity:** Text similarity analysis.
* **ReportLab:** PDF report generation.
* **GitHub:** Source code management.
* **Streamlit Community Cloud:** Application hosting.

## How the System Works

1. The user enters a job description.
2. The user uploads one or more PDF resumes.
3. The system extracts readable text from each resume.
4. The system identifies skills in the resumes and job description.
5. It compares resume skills with the required skills.
6. It calculates skill-match and text-similarity scores.
7. It ranks candidates according to skill-match percentage.
8. It displays matched skills, missing skills, and recommendations.
9. The user downloads the results as CSV or PDF reports.

## System Architecture

```text
        User
         |
         v
   Streamlit Dashboard
         |
         v
 Job Description + PDF Resumes
         |
         v
   PDF Text Extraction
         |
         v
    Skill Extraction
         |
         v
 Skill Matching and Text Similarity
         |
         v
   Candidate Ranking
         |
         v
 Results, Charts and Recommendations
         |
         v
      CSV / PDF Reports
```

## Installation and Setup

### Prerequisites

* Python 3.10 or a compatible Python version.
* Git.
* A code editor such as VS Code.
* The project source code.

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/rehanx17/AI_Resume_Screening.git
   ```

2. Open the project directory:

   ```bash
   cd AI_Resume_Screening
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   streamlit run app.py
   ```

5. Open the local URL displayed in your terminal.

## Project Structure

```text
AI_Resume_Screening/
├── app.py
├── requirements.txt
├── utils/
│   ├── resume_parser.py
│   ├── skill_extractor.py
│   ├── matcher.py
│   ├── similarity.py
│   └── recommendations.py
└── README.md
```

## Scoring and Ranking

**Skill Match:** Measures the overlap between the skills identified in a resume and the skills extracted from the job description.

**Text Similarity:** Estimates how similar the resume text is to the job description using text vectorization and cosine similarity.

Candidates are ranked by skill-match percentage. Text similarity is displayed as a separate measure.

These scores are indicators to support human review. They do not guarantee job suitability or predict job performance.

## Testing

The application should be tested for:

* Successful PDF uploads and text extraction.
* Multiple-resume screening.
* Skill matching and candidate ranking.
* Matched and missing skill display.
* Candidate comparison chart.
* CSV and PDF report generation.
* Empty input and unreadable PDF handling.

## Limitations

* Scanned PDFs without an accessible text layer may not be processed correctly.
* Skill detection depends on the project's skill extraction logic.
* Similarity scores do not establish a candidate's actual competence.
* Resume formatting and terminology can affect extraction and matching.
* The system does not replace recruiter judgment.

## Future Enhancements

* Add a database for screening history.
* Support DOCX resumes.
* Improve skill extraction using advanced NLP models.
* Add candidate search and filtering.
* Introduce authentication and user roles.
* Improve reporting and analytics.

## Conclusion

The AI Resume Screening System demonstrates how Python, text processing, skill matching, and an interactive dashboard can assist in organizing and comparing job applications. It provides a practical foundation for further development in recruitment automation and natural language processing.

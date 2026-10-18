
import pymupdf


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF resume safely."""

    if not pdf_path:
        raise ValueError("No PDF file was provided.")

    try:
        text_parts = []

        with pymupdf.open(pdf_path) as document:
            if document.is_encrypted:
                raise ValueError(
                    "This PDF is password-protected. "
                    "Please upload an unlocked PDF."
                )

            if len(document) == 0:
                raise ValueError("The uploaded PDF has no pages.")

            for page in document:
                page_text = page.get_text("text")
                if page_text:
                    text_parts.append(page_text)

        extracted_text = "\n".join(text_parts).strip()

        if not extracted_text:
            raise ValueError(
                "No readable text was found in this PDF. "
                "Please upload a text-based resume PDF."
            )

        return extracted_text

    except ValueError:
        raise

    except Exception as error:
        raise ValueError(
            "Unable to read this PDF. Please upload a valid PDF file."
        ) from error

"""
resume_parser.py
Extracts raw text from uploaded resume files (PDF, DOCX, TXT).
"""

import io
from PyPDF2 import PdfReader
import docx


def extract_text_from_pdf(file_obj) -> str:
    reader = PdfReader(file_obj)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_obj) -> str:
    document = docx.Document(file_obj)
    paragraphs = [p.text for p in document.paragraphs]
    # Also grab text inside tables (common in resumes)
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                paragraphs.append(cell.text)
    return "\n".join(paragraphs)


def extract_text_from_txt(file_obj) -> str:
    raw = file_obj.read()
    if isinstance(raw, bytes):
        return raw.decode("utf-8", errors="ignore")
    return raw


def extract_text_from_file(uploaded_file) -> str:
    """
    Dispatches to the correct extractor based on file extension.
    `uploaded_file` is a Streamlit UploadedFile object (file-like).
    """
    name = uploaded_file.name.lower()
    # Ensure pointer at start
    uploaded_file.seek(0)

    if name.endswith(".pdf"):
        text = extract_text_from_pdf(uploaded_file)
    elif name.endswith(".docx"):
        text = extract_text_from_docx(uploaded_file)
    elif name.endswith(".txt"):
        text = extract_text_from_txt(uploaded_file)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")

    text = text.strip()
    if not text:
        raise ValueError("No readable text found in the uploaded file (it may be a scanned/image-based PDF).")
    return text

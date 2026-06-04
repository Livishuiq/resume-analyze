"""
PDF parsing utilities for resume text extraction.
Uses pdfplumber (primary) with PyPDF2 fallback.
"""

import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_pdfplumber(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using pdfplumber."""
    import pdfplumber

    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_pypdf2(file_bytes: bytes) -> str:
    """Fallback: extract text using pypdf (formerly PyPDF2)."""
    try:
        from pypdf import PdfReader
    except ImportError:
        import PyPDF2  # type: ignore
        PdfReader = PyPDF2.PdfReader  # type: ignore

    text_parts = []
    reader = PdfReader(io.BytesIO(file_bytes))
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file given as bytes.
    Tries pdfplumber first, falls back to PyPDF2.
    Raises ValueError if no text could be extracted.
    """
    if not file_bytes:
        raise ValueError("Empty file provided.")

    text = ""

    # Primary: pdfplumber
    try:
        text = extract_text_pdfplumber(file_bytes)
    except Exception as e:
        logger.warning("pdfplumber failed: %s. Trying PyPDF2.", e)

    # Fallback: PyPDF2
    if not text.strip():
        try:
            text = extract_text_pypdf2(file_bytes)
        except Exception as e:
            logger.error("PyPDF2 also failed: %s", e)

    if not text.strip():
        raise ValueError(
            "Could not extract text from the PDF. "
            "The file may be image-based (scanned). "
            "Please use a text-based PDF."
        )

    return _post_process(text)


def _post_process(text: str) -> str:
    """Clean up extracted PDF text."""
    import re

    # Fix common PDF extraction artifacts
    text = re.sub(r"\n{3,}", "\n\n", text)          # collapse excessive newlines
    text = re.sub(r"[ \t]{2,}", " ", text)           # collapse spaces/tabs
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)     # rejoin hyphenated words
    return text.strip()


def get_page_count(file_bytes: bytes) -> int:
    """Return number of pages in the PDF."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return len(pdf.pages)
    except Exception:
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            return len(reader.pages)
        except Exception:
            return 0

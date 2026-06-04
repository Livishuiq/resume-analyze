"""Unit tests for pdf_parser module."""

import io
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.pdf_parser import _post_process, extract_text, get_page_count


class TestPostProcess:
    def test_collapses_multiple_newlines(self):
        text = "Hello\n\n\n\nWorld"
        result = _post_process(text)
        assert "\n\n\n" not in result

    def test_collapses_multiple_spaces(self):
        text = "Hello    World"
        result = _post_process(text)
        assert "    " not in result

    def test_rejoins_hyphenated_words(self):
        text = "pro-\ngramming"
        result = _post_process(text)
        assert "programming" in result

    def test_strips_whitespace(self):
        text = "  Hello World  "
        result = _post_process(text)
        assert result == "Hello World"


class TestExtractText:
    def test_raises_on_empty_bytes(self):
        with pytest.raises(ValueError, match="Empty file"):
            extract_text(b"")

    def test_raises_on_unextractable_pdf(self):
        """Should raise ValueError if both parsers fail to get text."""
        with patch("utils.pdf_parser.extract_text_pdfplumber", return_value=""), \
             patch("utils.pdf_parser.extract_text_pypdf2", return_value=""):
            with pytest.raises(ValueError):
                extract_text(b"%PDF-1.4 fake content")

    def test_falls_back_to_pypdf2_when_pdfplumber_fails(self):
        expected = "Extracted via PyPDF2"
        with patch("utils.pdf_parser.extract_text_pdfplumber", side_effect=Exception("fail")), \
             patch("utils.pdf_parser.extract_text_pypdf2", return_value=expected):
            result = extract_text(b"%PDF-1.4 fake")
        assert result == expected

    def test_returns_pdfplumber_text_when_available(self):
        expected = "Extracted via pdfplumber"
        with patch("utils.pdf_parser.extract_text_pdfplumber", return_value=expected):
            result = extract_text(b"%PDF-1.4 fake")
        assert result == expected


class TestGetPageCount:
    def test_returns_zero_on_failure(self):
        result = get_page_count(b"not a pdf")
        assert result == 0

"""Unit tests for report_generator module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.report_generator import _chunk_list, _grade_color, _score_color, _strip_markdown, generate_report


class TestHelpers:
    def test_strip_markdown_bold(self):
        result = _strip_markdown("**Hello** World")
        assert "**" not in result
        assert "Hello" in result

    def test_strip_markdown_empty(self):
        result = _strip_markdown("")
        assert result == ""

    def test_chunk_list_even(self):
        result = _chunk_list([1, 2, 3, 4], 2)
        assert result == [[1, 2], [3, 4]]

    def test_chunk_list_uneven(self):
        result = _chunk_list([1, 2, 3], 2)
        assert result == [[1, 2], [3]]

    def test_chunk_list_empty(self):
        assert _chunk_list([], 4) == []

    def test_score_color_high(self):
        from reportlab.lib import colors
        color = _score_color(85)
        assert color == colors.HexColor("#10B981")

    def test_score_color_medium(self):
        color = _score_color(65)
        assert color is not None

    def test_score_color_low(self):
        color = _score_color(30)
        assert color is not None

    def test_grade_color_a(self):
        color = _grade_color("A")
        assert color is not None

    def test_grade_color_f(self):
        color = _grade_color("F")
        assert color is not None


class TestGenerateReport:
    def _make_report(self, **kwargs):
        defaults = dict(
            ats_score=72.5,
            grade="B",
            matching_skills={"python", "docker", "aws", "react"},
            missing_skills={"kubernetes", "terraform"},
            extra_skills={"perl", "cobol"},
            recommendations=["Add missing skills.", "Improve formatting."],
            score_breakdown={
                "Skill Match (40%)": 80.0,
                "Keyword Similarity (30%)": 60.0,
                "Keyword Density (15%)": 70.0,
                "Format Quality (15%)": 75.0,
            },
            job_title="Senior Engineer",
        )
        defaults.update(kwargs)
        return generate_report(**defaults)

    def test_returns_bytes(self):
        result = self._make_report()
        assert isinstance(result, bytes)

    def test_returns_valid_pdf(self):
        result = self._make_report()
        assert result[:4] == b"%PDF"

    def test_nonempty_output(self):
        result = self._make_report()
        assert len(result) > 1000

    def test_no_matching_skills(self):
        result = self._make_report(matching_skills=set())
        assert isinstance(result, bytes)

    def test_no_missing_skills(self):
        result = self._make_report(missing_skills=set())
        assert isinstance(result, bytes)

    def test_no_extra_skills(self):
        result = self._make_report(extra_skills=set())
        assert isinstance(result, bytes)

    def test_perfect_score(self):
        result = self._make_report(ats_score=100.0, grade="A")
        assert isinstance(result, bytes)

    def test_zero_score(self):
        result = self._make_report(
            ats_score=0.0, grade="F",
            matching_skills=set(), missing_skills={"python", "java"},
        )
        assert isinstance(result, bytes)

    def test_many_skills(self):
        many = {f"skill_{i}" for i in range(30)}
        result = self._make_report(matching_skills=many, missing_skills=many)
        assert isinstance(result, bytes)

    def test_empty_recommendations(self):
        result = self._make_report(recommendations=[])
        assert isinstance(result, bytes)

    def test_default_job_title(self):
        result = self._make_report(job_title="")
        assert isinstance(result, bytes)

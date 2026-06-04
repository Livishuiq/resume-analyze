"""Unit tests for ats_calculator module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.ats_calculator import (
    ATSResult,
    _compute_format_score,
    _compute_keyword_density,
    _compute_skill_match_score,
    _compute_tfidf_similarity,
    _score_to_grade,
    calculate_ats_score,
)

RESUME = """
John Doe | john@example.com | 555-0100

SUMMARY
Experienced Python developer with 5 years building scalable web services.

SKILLS
Python, JavaScript, React, PostgreSQL, Docker, AWS, Git, REST APIs

EXPERIENCE
Backend Engineer — Tech Corp (2020–Present)
- Developed REST APIs using Python/FastAPI serving 100k+ daily users
- Reduced infrastructure costs by 40% via Docker + AWS optimizations
- Led team of 4 engineers in Agile environment

EDUCATION
B.S. Computer Science, State University, 2019
"""

JD = """
We need a Python developer experienced with:
- Python (3+ years)
- JavaScript and React
- PostgreSQL or MySQL databases
- Docker and Kubernetes
- AWS cloud services
- REST API development
- Agile/Scrum methodologies
Strong communication skills required.
"""

UNRELATED_JD = """
Seeking an experienced pastry chef for a fine dining restaurant.
Must know sourdough bread, cake decoration, sugar work, and chocolate tempering.
French culinary training preferred.
"""


class TestScoreToGrade:
    def test_90_is_A(self): assert _score_to_grade(90) == "A"
    def test_85_is_A(self): assert _score_to_grade(85) == "A"
    def test_75_is_B(self): assert _score_to_grade(75) == "B"
    def test_60_is_C(self): assert _score_to_grade(60) == "C"
    def test_45_is_D(self): assert _score_to_grade(45) == "D"
    def test_30_is_F(self): assert _score_to_grade(30) == "F"


class TestSkillMatchScore:
    def test_perfect_match(self):
        skills = {"python", "react"}
        score = _compute_skill_match_score(skills, set(), skills)
        assert score == 100.0

    def test_zero_match(self):
        jd_skills = {"python", "react"}
        score = _compute_skill_match_score(set(), jd_skills, jd_skills)
        assert score == 0.0

    def test_partial_match(self):
        jd_skills = {"python", "react", "docker", "aws"}
        matching = {"python", "react"}
        score = _compute_skill_match_score(matching, jd_skills - matching, jd_skills)
        assert score == 50.0

    def test_no_jd_skills_returns_neutral(self):
        score = _compute_skill_match_score(set(), set(), set())
        assert score == 50.0


class TestTfidfSimilarity:
    def test_same_text_is_100(self):
        score = _compute_tfidf_similarity(RESUME, RESUME)
        assert score > 95

    def test_similar_texts_high_score(self):
        score = _compute_tfidf_similarity(RESUME, JD)
        assert score > 10  # They share significant vocabulary

    def test_unrelated_texts_low_score(self):
        score = _compute_tfidf_similarity(RESUME, UNRELATED_JD)
        assert score < 20

    def test_returns_0_to_100(self):
        score = _compute_tfidf_similarity(RESUME, JD)
        assert 0 <= score <= 100


class TestKeywordDensity:
    def test_identical_texts(self):
        score = _compute_keyword_density(RESUME, RESUME)
        assert score > 80

    def test_empty_jd_returns_neutral(self):
        score = _compute_keyword_density(RESUME, "")
        assert score == 50.0

    def test_returns_0_to_100(self):
        score = _compute_keyword_density(RESUME, JD)
        assert 0 <= score <= 100


class TestFormatScore:
    def test_well_formatted_resume(self):
        score = _compute_format_score(RESUME)
        assert score >= 60

    def test_minimal_resume_lower_score(self):
        score = _compute_format_score("John Doe. Python developer.")
        assert score < 60

    def test_returns_0_to_100(self):
        score = _compute_format_score(RESUME)
        assert 0 <= score <= 100


class TestCalculateATSScore:
    def setup_method(self):
        self.result = calculate_ats_score(RESUME, JD)

    def test_returns_ats_result(self):
        assert isinstance(self.result, ATSResult)

    def test_score_in_range(self):
        assert 0 <= self.result.total_score <= 100

    def test_has_grade(self):
        assert self.result.grade in {"A", "B", "C", "D", "F"}

    def test_has_recommendations(self):
        assert len(self.result.recommendations) > 0

    def test_has_score_breakdown(self):
        assert len(self.result.score_breakdown) == 4

    def test_matching_skills_not_empty(self):
        assert len(self.result.matching_skills) > 0

    def test_python_in_matching(self):
        assert "python" in self.result.matching_skills

    def test_unrelated_jd_lower_score(self):
        unrelated_result = calculate_ats_score(RESUME, UNRELATED_JD)
        assert unrelated_result.total_score < self.result.total_score

    def test_score_breakdown_keys(self):
        keys = set(self.result.score_breakdown.keys())
        assert "Skill Match (40%)" in keys
        assert "Keyword Similarity (30%)" in keys

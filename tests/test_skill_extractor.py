"""Unit tests for skill_extractor module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.skill_extractor import (
    categorize_skill,
    compare_skills,
    extract_skills,
    get_all_skills,
)

SAMPLE_RESUME = """
John Doe | john@example.com | (555) 123-4567

SKILLS
Python, JavaScript, TypeScript, React, Node.js, PostgreSQL, Docker, AWS, Git

EXPERIENCE
Senior Software Engineer — Acme Corp (2021–Present)
- Built scalable REST APIs using FastAPI and Python
- Deployed microservices on Kubernetes and AWS ECS
- Used TensorFlow for recommendation system (30% accuracy improvement)
- Collaborated in Agile/Scrum sprints

EDUCATION
B.S. Computer Science, State University, 2019
"""

SAMPLE_JD = """
We are looking for a Senior Software Engineer with experience in:
- Python, JavaScript, TypeScript
- React or Vue.js
- PostgreSQL or MySQL
- Docker and Kubernetes
- AWS or Azure cloud platforms
- CI/CD pipelines (GitHub Actions, Jenkins)
- Strong communication and problem-solving skills
"""


class TestExtractSkills:
    def test_returns_dict(self):
        result = extract_skills(SAMPLE_RESUME)
        assert isinstance(result, dict)

    def test_detects_programming_languages(self):
        result = extract_skills(SAMPLE_RESUME)
        langs = result.get("Programming Languages", [])
        assert "python" in [l.lower() for l in langs]

    def test_detects_frameworks(self):
        result = extract_skills(SAMPLE_RESUME)
        frameworks = result.get("Web Frameworks", [])
        assert any("react" in f.lower() for f in frameworks)

    def test_detects_cloud_devops(self):
        result = extract_skills(SAMPLE_RESUME)
        cloud = result.get("Cloud & DevOps", [])
        assert any("docker" in c.lower() or "aws" in c.lower() for c in cloud)

    def test_empty_text_returns_empty(self):
        result = extract_skills("")
        assert result == {}

    def test_no_false_positives_on_garbage(self):
        result = extract_skills("asdfghjkl qwerty 12345")
        # Should find nothing
        assert all(len(v) == 0 for v in result.values())


class TestGetAllSkills:
    def test_returns_set(self):
        result = get_all_skills(SAMPLE_RESUME)
        assert isinstance(result, set)

    def test_all_lowercase(self):
        result = get_all_skills(SAMPLE_RESUME)
        assert all(s == s.lower() for s in result)

    def test_finds_python(self):
        result = get_all_skills(SAMPLE_RESUME)
        assert "python" in result


class TestCompareSkills:
    def test_returns_three_sets(self):
        matching, missing, extra = compare_skills(SAMPLE_RESUME, SAMPLE_JD)
        assert isinstance(matching, set)
        assert isinstance(missing, set)
        assert isinstance(extra, set)

    def test_matching_subset_of_both(self):
        matching, missing, extra = compare_skills(SAMPLE_RESUME, SAMPLE_JD)
        resume_skills = get_all_skills(SAMPLE_RESUME)
        jd_skills = get_all_skills(SAMPLE_JD)
        assert matching.issubset(resume_skills)
        assert matching.issubset(jd_skills)

    def test_missing_not_in_resume(self):
        matching, missing, extra = compare_skills(SAMPLE_RESUME, SAMPLE_JD)
        resume_skills = get_all_skills(SAMPLE_RESUME)
        assert not missing.intersection(resume_skills)

    def test_python_is_matching(self):
        matching, _, _ = compare_skills(SAMPLE_RESUME, SAMPLE_JD)
        assert "python" in matching


class TestCategorizeSkill:
    def test_python_is_programming_language(self):
        assert categorize_skill("python") == "Programming Languages"

    def test_react_is_web_framework(self):
        assert categorize_skill("react") == "Web Frameworks"

    def test_unknown_skill_returns_other(self):
        assert categorize_skill("xyzunknown") == "Other"

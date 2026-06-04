"""
ATS (Applicant Tracking System) score calculator.
Computes a 0–100 score based on multiple weighted signals.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.skill_extractor import compare_skills, get_all_skills
from utils.text_preprocessor import preprocess


# ---------------------------------------------------------------------------
# Score weights (must sum to 1.0)
# ---------------------------------------------------------------------------
WEIGHTS = {
    "skill_match": 0.40,
    "keyword_similarity": 0.30,
    "keyword_density": 0.15,
    "format_quality": 0.15,
}

# Resume section keywords used for format scoring
SECTION_KEYWORDS = [
    "education", "experience", "skills", "projects", "summary",
    "objective", "certifications", "awards", "publications",
    "work history", "employment", "volunteer",
]


@dataclass
class ATSResult:
    total_score: float
    skill_match_score: float
    keyword_similarity_score: float
    keyword_density_score: float
    format_quality_score: float
    matching_skills: Set[str]
    missing_skills: Set[str]
    extra_skills: Set[str]
    jd_skills: Set[str]
    resume_skills: Set[str]
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    grade: str = ""

    def __post_init__(self):
        self.score_breakdown = {
            "Skill Match (40%)": round(self.skill_match_score, 1),
            "Keyword Similarity (30%)": round(self.keyword_similarity_score, 1),
            "Keyword Density (15%)": round(self.keyword_density_score, 1),
            "Format Quality (15%)": round(self.format_quality_score, 1),
        }
        self.grade = _score_to_grade(self.total_score)
        self.recommendations = _generate_recommendations(self)


def _score_to_grade(score: float) -> str:
    if score >= 85:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 55:
        return "C"
    elif score >= 40:
        return "D"
    return "F"


def _compute_skill_match_score(
    matching: Set[str], missing: Set[str], jd_skills: Set[str]
) -> float:
    """Ratio of JD skills found in the resume (0–100)."""
    if not jd_skills:
        return 50.0  # No skills in JD → neutral
    return min(100.0, (len(matching) / len(jd_skills)) * 100)


def _compute_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """Cosine similarity between TF-IDF vectors (0–100)."""
    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            stop_words="english",
        )
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(np.clip(similarity * 100, 0, 100))
    except Exception:
        return 0.0


def _compute_keyword_density(resume_text: str, jd_text: str) -> float:
    """
    Fraction of JD tokens (preprocessed) present in resume (0–100).
    Rewards breadth of keyword coverage, not just skill matches.
    """
    jd_tokens = set(preprocess(jd_text))
    resume_tokens = set(preprocess(resume_text))
    if not jd_tokens:
        return 50.0
    overlap = jd_tokens & resume_tokens
    return min(100.0, (len(overlap) / len(jd_tokens)) * 100)


def _compute_format_score(resume_text: str) -> float:
    """
    Heuristic format quality score (0–100).
    Checks for section headers, length, contact info, quantified achievements.
    """
    text_lower = resume_text.lower()
    score = 0.0

    # 1. Section headers present (up to 40 pts)
    found_sections = sum(1 for s in SECTION_KEYWORDS if s in text_lower)
    score += min(40, found_sections * 8)

    # 2. Document length (up to 20 pts)
    word_count = len(resume_text.split())
    if 300 <= word_count <= 1200:
        score += 20
    elif word_count > 200:
        score += 10

    # 3. Contact info present (up to 20 pts)
    has_email = bool(re.search(r"[\w._%+-]+@[\w.-]+\.\w+", resume_text))
    has_phone = bool(re.search(r"\+?\d[\d\s\-\(\)]{6,}\d", resume_text))
    score += 10 if has_email else 0
    score += 10 if has_phone else 0

    # 4. Quantified achievements (up to 20 pts)
    numbers_with_context = len(
        re.findall(r"\b\d+[\+%xX]?\s*(years?|months?|%|percent|users?|customers?|projects?|million|k\b)", text_lower)
    )
    score += min(20, numbers_with_context * 4)

    return min(100.0, score)


def calculate_ats_score(resume_text: str, jd_text: str) -> ATSResult:
    """
    Compute a comprehensive ATS score.

    Args:
        resume_text: Extracted resume text.
        jd_text: Job description text.

    Returns:
        ATSResult dataclass with scores, skills, and recommendations.
    """
    matching, missing, extra = compare_skills(resume_text, jd_text)
    jd_skills = get_all_skills(jd_text)
    resume_skills = get_all_skills(resume_text)

    skill_score = _compute_skill_match_score(matching, missing, jd_skills)
    tfidf_score = _compute_tfidf_similarity(resume_text, jd_text)
    density_score = _compute_keyword_density(resume_text, jd_text)
    format_score = _compute_format_score(resume_text)

    total = (
        WEIGHTS["skill_match"] * skill_score
        + WEIGHTS["keyword_similarity"] * tfidf_score
        + WEIGHTS["keyword_density"] * density_score
        + WEIGHTS["format_quality"] * format_score
    )
    total = round(float(np.clip(total, 0, 100)), 1)

    return ATSResult(
        total_score=total,
        skill_match_score=skill_score,
        keyword_similarity_score=tfidf_score,
        keyword_density_score=density_score,
        format_quality_score=format_score,
        matching_skills=matching,
        missing_skills=missing,
        extra_skills=extra,
        jd_skills=jd_skills,
        resume_skills=resume_skills,
    )


def _generate_recommendations(result: ATSResult) -> List[str]:
    """Generate actionable, prioritized recommendations."""
    recs: List[str] = []
    score = result.total_score

    # Skill gap recommendations
    if result.missing_skills:
        top_missing = sorted(result.missing_skills)[:5]
        recs.append(
            f"🎯 **Add missing skills** to your resume: "
            f"{', '.join(top_missing)}. These appear in the job description but not your resume."
        )

    # Keyword similarity
    if result.keyword_similarity_score < 50:
        recs.append(
            "📝 **Mirror the job description language.** Use the same terminology, "
            "acronyms, and phrasing the employer uses. ATS systems reward exact matches."
        )

    # Format quality
    if result.format_quality_score < 60:
        recs.append(
            "📄 **Improve resume structure.** Ensure you have clearly labeled sections: "
            "Summary, Experience, Skills, Education. Add contact information (email & phone)."
        )
    
    if result.format_quality_score < 80:
        recs.append(
            "📊 **Quantify your achievements.** Replace vague statements with metrics: "
            "'Improved performance by 40%', 'Managed a team of 8', 'Reduced costs by $50K'."
        )

    # Keyword density
    if result.keyword_density_score < 40:
        recs.append(
            "🔑 **Increase relevant keyword coverage.** Expand your experience descriptions "
            "to naturally incorporate more keywords from the job description."
        )

    # Skill count
    if len(result.resume_skills) < 5:
        recs.append(
            "🛠️ **Expand your skills section.** List all relevant technical skills, tools, "
            "and technologies. Even foundational skills matter for ATS parsing."
        )

    # High-scoring positive feedback
    if score >= 80:
        recs.append(
            "✅ **Strong match!** Your resume is well-aligned with this role. "
            "Focus on tailoring your summary and cover letter to stand out further."
        )
    elif score >= 60:
        recs.append(
            "💡 **Good foundation.** A few targeted improvements can significantly "
            "boost your chances. Focus on the skill gaps and keyword alignment above."
        )

    # Generic ATS best practices
    recs.append(
        "🤖 **ATS best practices:** Use a clean, single-column layout. Avoid tables, "
        "headers/footers, and images. Save as PDF (text-based, not scanned)."
    )

    return recs

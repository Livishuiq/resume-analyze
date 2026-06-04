"""
Skill extraction engine.
Detects technical skills, tools, languages, and frameworks from text.
"""

from __future__ import annotations

import re
from typing import Dict, List, Set, Tuple

# ---------------------------------------------------------------------------
# Master skill taxonomy
# ---------------------------------------------------------------------------

SKILL_TAXONOMY: Dict[str, List[str]] = {
    "Programming Languages": [
        "python", "java", "javascript", "typescript", "c", "c++", "c#", "go",
        "golang", "rust", "ruby", "php", "swift", "kotlin", "scala", "r",
        "matlab", "perl", "shell", "bash", "powershell", "lua", "dart",
        "groovy", "haskell", "elixir", "erlang", "clojure", "fortran",
        "cobol", "vba", "objective-c", "assembly",
    ],
    "Web Frameworks": [
        "react", "reactjs", "react.js", "angular", "angularjs", "vue", "vuejs",
        "vue.js", "next.js", "nextjs", "nuxt.js", "nuxtjs", "svelte",
        "django", "flask", "fastapi", "express", "expressjs", "spring",
        "spring boot", "springboot", "laravel", "rails", "ruby on rails",
        "asp.net", "asp net", ".net", "dotnet", "nestjs", "nest.js",
        "gatsby", "remix", "astro",
    ],
    "Machine Learning & AI": [
        "machine learning", "deep learning", "neural network", "natural language processing",
        "nlp", "computer vision", "reinforcement learning", "transfer learning",
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "xgboost",
        "lightgbm", "catboost", "hugging face", "transformers", "bert", "gpt",
        "llm", "large language model", "opencv", "pandas", "numpy", "scipy",
        "matplotlib", "seaborn", "plotly", "mlflow", "kubeflow", "ray",
        "langchain", "llamaindex", "stable diffusion", "generative ai",
        "feature engineering", "model deployment",
    ],
    "Data & Analytics": [
        "sql", "nosql", "mysql", "postgresql", "postgres", "sqlite",
        "mongodb", "redis", "cassandra", "elasticsearch", "neo4j",
        "snowflake", "bigquery", "redshift", "databricks", "spark",
        "hadoop", "kafka", "airflow", "dbt", "tableau", "power bi",
        "looker", "qlik", "excel", "data analysis", "data visualization",
        "etl", "data pipeline", "data warehouse", "data lake",
        "business intelligence", "bi", "statistics", "data science",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "k8s", "terraform", "ansible", "jenkins", "ci/cd", "github actions",
        "gitlab ci", "circleci", "travis ci", "linux", "unix",
        "nginx", "apache", "serverless", "lambda", "microservices",
        "devops", "sre", "site reliability", "prometheus", "grafana",
        "elk stack", "helm", "istio", "argocd", "pulumi",
    ],
    "Version Control & Collaboration": [
        "git", "github", "gitlab", "bitbucket", "svn", "jira", "confluence",
        "trello", "asana", "notion", "slack", "agile", "scrum", "kanban",
        "sprint", "product management",
    ],
    "Mobile Development": [
        "android", "ios", "react native", "flutter", "xamarin",
        "mobile development", "swift", "kotlin", "xcode",
    ],
    "Security": [
        "cybersecurity", "penetration testing", "ethical hacking", "owasp",
        "soc", "siem", "firewall", "encryption", "ssl", "tls",
        "oauth", "jwt", "zero trust", "sast", "dast", "devsecops",
    ],
    "Soft Skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "critical thinking", "time management", "project management",
        "stakeholder management", "presentation", "mentoring", "coaching",
        "collaboration", "adaptability", "creativity", "analytical",
    ],
    "Other Technical": [
        "rest", "restful", "graphql", "grpc", "api", "microservices",
        "object oriented", "oop", "functional programming", "design patterns",
        "system design", "architecture", "tdd", "bdd", "unit testing",
        "integration testing", "selenium", "playwright", "cypress",
        "webpack", "vite", "babel", "eslint", "linux", "blockchain",
        "web3", "solidity", "iot", "embedded systems", "fpga",
    ],
}

# Flatten to a lookup set for fast membership checks
_ALL_SKILLS_FLAT: Set[str] = {
    skill.lower()
    for skills in SKILL_TAXONOMY.values()
    for skill in skills
}

# Multi-word skills (sorted longest first for greedy matching)
_MULTI_WORD_SKILLS: List[str] = sorted(
    [s for s in _ALL_SKILLS_FLAT if " " in s],
    key=lambda x: -len(x),
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_skills(text: str) -> Dict[str, List[str]]:
    """
    Extract skills from text, grouped by category.
    Returns a dict: {category: [matched_skills]}.
    """
    normalized = _normalize(text)
    found: Set[str] = set()

    # Step 1: Match multi-word skills first (greedy, order by length)
    for skill in _MULTI_WORD_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, normalized):
            found.add(skill)

    # Step 2: Match single-word skills using word boundaries
    single_word = [s for s in _ALL_SKILLS_FLAT if " " not in s]
    for skill in single_word:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, normalized):
            found.add(skill)

    # Group by category
    result: Dict[str, List[str]] = {}
    for category, skills in SKILL_TAXONOMY.items():
        matched = [s for s in skills if s.lower() in found]
        if matched:
            # Deduplicate while preserving order
            seen: Set[str] = set()
            unique = []
            for s in matched:
                key = s.lower()
                if key not in seen:
                    seen.add(key)
                    unique.append(s)
            result[category] = unique

    return result


def get_all_skills(text: str) -> Set[str]:
    """Return a flat set of all detected skills (lowercase)."""
    grouped = extract_skills(text)
    return {s.lower() for skills in grouped.values() for s in skills}


def compare_skills(
    resume_text: str, jd_text: str
) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Compare skills between resume and job description.

    Returns:
        matching: skills in both resume and JD
        missing:  skills in JD but not in resume
        extra:    skills in resume but not in JD
    """
    resume_skills = get_all_skills(resume_text)
    jd_skills = get_all_skills(jd_text)

    matching = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    extra = resume_skills - jd_skills

    return matching, missing, extra


def categorize_skill(skill: str) -> str:
    """Return the category of a given skill."""
    skill_lower = skill.lower()
    for category, skills in SKILL_TAXONOMY.items():
        if skill_lower in {s.lower() for s in skills}:
            return category
    return "Other"

# 🎯 AI Resume Analyzer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4%2B-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-22D3EE?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-76%20passing-10B981?style=for-the-badge)

**Upload your resume. Paste a job description. Get your ATS score in seconds.**

[🚀 Live Demo](#deployment) · [📖 Docs](#installation) · [🐛 Issues](https://github.com/your-username/resume-analyzer/issues)

![App Screenshot](screenshots/dashboard.png)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **PDF Parsing** | Multi-page resume extraction with pdfplumber + pypdf fallback |
| 🎯 **ATS Scoring** | 0–100 score based on 4 weighted signals |
| 🛠️ **Skill Detection** | 500+ skills across 10 categories (languages, frameworks, cloud, ML, etc.) |
| 📊 **Gap Analysis** | Matching, missing, and extra skills vs job description |
| 💡 **Recommendations** | Actionable, prioritized improvement suggestions |
| 📥 **PDF Report** | Professional downloadable report via ReportLab |
| ⚡ **Fast** | Full analysis in under 3 seconds |

---

## 🏗️ Project Architecture

```
resume-analyzer/
│
├── app.py                    # Streamlit application entry point
├── requirements.txt          # Python dependencies
├── README.md
├── .gitignore
├── LICENSE                   # MIT
│
├── .streamlit/
│   └── config.toml           # Streamlit theme & server config
│
├── utils/                    # Core analysis engine
│   ├── __init__.py
│   ├── pdf_parser.py         # PDF text extraction (pdfplumber + pypdf)
│   ├── text_preprocessor.py  # NLTK-based tokenization, lemmatization
│   ├── skill_extractor.py    # Skill taxonomy + pattern matching (500+ skills)
│   ├── ats_calculator.py     # ATS score engine (TF-IDF + skill matching)
│   └── report_generator.py   # ReportLab PDF report generator
│
├── tests/                    # Pytest unit tests (76 tests)
│   ├── test_pdf_parser.py
│   ├── test_skill_extractor.py
│   ├── test_ats_calculator.py
│   └── test_text_preprocessor.py
│
├── assets/                   # Static assets
├── screenshots/              # App screenshots
├── reports/                  # Generated reports (gitignored)
├── sample_data/              # Sample resumes & JDs
│
└── .github/
    └── workflows/
        └── python-tests.yml  # CI: test on Python 3.10, 3.11, 3.12
```

---

## 📐 ATS Scoring Algorithm

The ATS score (0–100) is a weighted composite of four signals:

```
ATS Score = (Skill Match × 0.40)
          + (TF-IDF Cosine Similarity × 0.30)
          + (Keyword Density × 0.15)
          + (Format Quality × 0.15)
```

| Component | Weight | Description |
|-----------|--------|-------------|
| **Skill Match** | 40% | % of JD skills found in resume |
| **Keyword Similarity** | 30% | TF-IDF cosine similarity (bigrams, 5k features) |
| **Keyword Density** | 15% | % of JD tokens covered in resume |
| **Format Quality** | 15% | Section headers, length, contact info, quantified achievements |

**Grades:** A (≥85) · B (≥70) · C (≥55) · D (≥40) · F (<40)

---

## 🛠️ Skill Categories

The analyzer detects 500+ skills across 10 categories:

- **Programming Languages** — Python, Java, JavaScript, TypeScript, Go, Rust, C++, Kotlin, Swift, R, and 25+ more
- **Web Frameworks** — React, Angular, Vue, Next.js, Django, FastAPI, Spring Boot, Rails, and 20+ more
- **Machine Learning & AI** — TensorFlow, PyTorch, scikit-learn, Hugging Face, LLMs, NLP, Computer Vision
- **Data & Analytics** — SQL, PostgreSQL, MongoDB, Snowflake, Spark, Airflow, Tableau, Power BI
- **Cloud & DevOps** — AWS, Azure, GCP, Docker, Kubernetes, Terraform, GitHub Actions, Prometheus
- **Version Control** — Git, GitHub, GitLab, Jira, Agile, Scrum
- **Mobile** — Android, iOS, React Native, Flutter
- **Security** — Cybersecurity, OWASP, OAuth, Zero Trust, DevSecOps
- **Soft Skills** — Leadership, Communication, Project Management, Mentoring
- **Other Technical** — REST APIs, GraphQL, System Design, TDD, Microservices

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/resume-analyzer.git
cd resume-analyzer

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate          # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 🧪 Running Tests

```bash
# Run all 76 tests
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=utils --cov-report=term-missing

# Run a specific test file
pytest tests/test_skill_extractor.py -v
```

---

## ☁️ Deployment on Streamlit Community Cloud

1. **Fork this repository** to your GitHub account.

2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.

3. Click **"New app"** and configure:
   - **Repository:** `your-username/resume-analyzer`
   - **Branch:** `main`
   - **Main file path:** `app.py`

4. Click **"Deploy"** — Streamlit handles the rest.

> **Note:** The app runs on Python 3.11 on Streamlit Cloud. NLTK data is downloaded automatically on first run via `utils/text_preprocessor.py`.

---

## 📸 Screenshots

<details>
<summary>View Screenshots</summary>

### Main Dashboard
![Dashboard](screenshots/dashboard.png)

### ATS Score & Breakdown
![Score](screenshots/score.png)

### Skill Analysis
![Skills](screenshots/skills.png)

### PDF Report
![Report](screenshots/report.png)

</details>

---

## 🔮 Future Enhancements

- [ ] **AI-Powered Suggestions** — LLM integration for natural language improvement suggestions
- [ ] **Multi-Resume Comparison** — Compare multiple resumes against the same JD
- [ ] **Cover Letter Generator** — Auto-generate tailored cover letters
- [ ] **Job Board Integration** — Fetch JDs directly from LinkedIn, Indeed, Glassdoor
- [ ] **Resume Templates** — ATS-optimized resume templates
- [ ] **Role-Specific Scoring** — Specialized scoring for data science, frontend, backend roles
- [ ] **Persistent History** — Save and compare analysis history
- [ ] **OCR Support** — Analyze scanned/image-based resumes via Tesseract
- [ ] **API Endpoint** — REST API for programmatic access

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please ensure all tests pass and add tests for new functionality.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io) — rapid web app framework
- [pdfplumber](https://github.com/jsvine/pdfplumber) — reliable PDF extraction
- [NLTK](https://www.nltk.org) — natural language processing
- [scikit-learn](https://scikit-learn.org) — TF-IDF vectorization
- [ReportLab](https://www.reportlab.com) — PDF generation

---

<div align="center">
  Made with ❤️ and Python
  <br><br>
  <a href="https://github.com/your-username/resume-analyzer">⭐ Star this repo if it helped you!</a>
</div>

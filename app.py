"""
AI Resume Analyzer — Streamlit Application
==========================================
Upload a PDF resume, paste a job description, and get a comprehensive
ATS score, skill gap analysis, and actionable recommendations.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Path setup (ensures utils/ is importable when running from repo root)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.ats_calculator import calculate_ats_score
from utils.pdf_parser import extract_text, get_page_count
from utils.report_generator import generate_report
from utils.skill_extractor import extract_skills

# ---------------------------------------------------------------------------
# Page config — MUST be first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-username/resume-analyzer",
        "Report a bug": "https://github.com/your-username/resume-analyzer/issues",
        "About": "AI Resume Analyzer — Match your resume to any job description.",
    },
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
  /* Import fonts */
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* Hide Streamlit branding */
  #MainMenu, footer, header { visibility: hidden; }

  /* Main background */
  .stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border-right: 1px solid rgba(99, 102, 241, 0.3);
  }

  /* Metric cards */
  [data-testid="metric-container"] {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 12px;
    padding: 16px;
    backdrop-filter: blur(10px);
  }

  /* Score display */
  .score-card {
    background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(34,211,238,0.1));
    border: 2px solid rgba(99, 102, 241, 0.5);
    border-radius: 20px;
    padding: 32px;
    text-align: center;
    backdrop-filter: blur(20px);
  }

  .score-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 72px;
    font-weight: 700;
    line-height: 1;
    margin: 0;
  }

  .score-grade {
    font-size: 28px;
    font-weight: 600;
    margin-top: 8px;
  }

  /* Skill pills */
  .skill-pill-match {
    display: inline-block;
    background: rgba(16, 185, 129, 0.2);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.4);
    border-radius: 20px;
    padding: 4px 12px;
    margin: 3px;
    font-size: 12px;
    font-weight: 500;
  }

  .skill-pill-missing {
    display: inline-block;
    background: rgba(239, 68, 68, 0.2);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.4);
    border-radius: 20px;
    padding: 4px 12px;
    margin: 3px;
    font-size: 12px;
    font-weight: 500;
  }

  .skill-pill-extra {
    display: inline-block;
    background: rgba(99, 102, 241, 0.2);
    color: #a5b4fc;
    border: 1px solid rgba(99, 102, 241, 0.4);
    border-radius: 20px;
    padding: 4px 12px;
    margin: 3px;
    font-size: 12px;
    font-weight: 500;
  }

  /* Section headers */
  .section-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(99, 102, 241, 0.4);
  }

  /* Progress bar custom */
  .stProgress > div > div > div > div {
    background: linear-gradient(90deg, #6366f1, #22d3ee) !important;
    border-radius: 4px;
  }

  /* Recommendation cards */
  .rec-card {
    background: rgba(30, 41, 59, 0.6);
    border-left: 3px solid #6366f1;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #cbd5e1;
    font-size: 14px;
    line-height: 1.6;
  }

  /* Info boxes */
  .info-box {
    background: rgba(34, 211, 238, 0.1);
    border: 1px solid rgba(34, 211, 238, 0.3);
    border-radius: 10px;
    padding: 12px 16px;
    color: #67e8f9;
    font-size: 13px;
    margin: 8px 0;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background: rgba(15, 23, 42, 0.6);
    border-radius: 10px;
    padding: 4px;
  }

  .stTabs [data-baseweb="tab"] {
    color: #94a3b8;
    font-weight: 500;
  }

  .stTabs [aria-selected="true"] {
    background: rgba(99, 102, 241, 0.3) !important;
    color: #a5b4fc !important;
    border-radius: 8px;
  }

  /* File uploader */
  [data-testid="stFileUploader"] {
    background: rgba(30, 41, 59, 0.5);
    border: 2px dashed rgba(99, 102, 241, 0.4);
    border-radius: 12px;
  }

  /* Text areas */
  textarea {
    background: rgba(15, 23, 42, 0.8) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(99, 102, 241, 0.4) !important;
    border-radius: 8px !important;
  }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 32px;
    font-weight: 600;
    font-size: 16px;
    width: 100%;
    transition: all 0.2s ease;
    font-family: 'DM Sans', sans-serif;
  }

  .stButton > button:hover {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
  }

  /* Download button */
  .stDownloadButton > button {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-weight: 600;
    width: 100%;
  }

  /* Expander */
  .streamlit-expanderHeader {
    background: rgba(30, 41, 59, 0.6) !important;
    color: #e2e8f0 !important;
    border-radius: 8px;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.4); }
  ::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.5); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
def _init_state():
    defaults = {
        "ats_result": None,
        "resume_text": None,
        "jd_text": None,
        "resume_skills": None,
        "pdf_bytes": None,
        "analysis_done": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _score_color(score: float) -> str:
    if score >= 80:
        return "#10b981"
    elif score >= 60:
        return "#f59e0b"
    elif score >= 40:
        return "#f97316"
    return "#ef4444"


def _grade_label(grade: str) -> str:
    labels = {"A": "Excellent", "B": "Good", "C": "Average", "D": "Below Average", "F": "Poor"}
    return labels.get(grade, "")


def _skill_pills(skills: set, pill_class: str) -> str:
    if not skills:
        return "<em style='color:#64748b'>None detected</em>"
    return "".join(f'<span class="{pill_class}">{s}</span>' for s in sorted(skills))


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px;'>
      <div style='font-size:40px'>🎯</div>
      <div style='font-family:"Space Grotesk",sans-serif; font-size:20px;
                  font-weight:700; color:#e2e8f0; margin-top:8px'>
        Resume Analyzer
      </div>
      <div style='font-size:12px; color:#64748b; margin-top:4px'>
        AI-Powered ATS Scoring
      </div>
    </div>
    <hr style='border-color:rgba(99,102,241,0.3); margin:16px 0'/>
    """, unsafe_allow_html=True)

    st.markdown("### 📂 Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload your resume as a text-based PDF (not scanned).",
        label_visibility="collapsed",
    )

    if uploaded_file:
        file_bytes = uploaded_file.read()
        file_size_kb = len(file_bytes) / 1024
        page_count = get_page_count(file_bytes)
        st.success(f"✅ {uploaded_file.name}")
        col1, col2 = st.columns(2)
        col1.metric("Pages", page_count)
        col2.metric("Size", f"{file_size_kb:.0f} KB")
        st.session_state["pdf_bytes"] = file_bytes

    st.markdown("---")
    st.markdown("### ℹ️ How It Works")
    st.markdown("""
    <div style='color:#94a3b8; font-size:13px; line-height:1.8'>
    1. 📤 Upload your resume PDF<br>
    2. 📋 Paste the job description<br>
    3. 🤖 Click Analyze<br>
    4. 📊 Review your ATS score<br>
    5. 📥 Download PDF report
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='color:#475569; font-size:11px; text-align:center'>
    Built with ❤️ using Python & Streamlit<br>
    <a href='https://github.com/your-username/resume-analyzer'
       style='color:#6366f1'>GitHub →</a>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
# Hero header
st.markdown("""
<div style='text-align:center; padding:40px 0 24px'>
  <h1 style='font-family:"Space Grotesk",sans-serif; font-size:48px; font-weight:700;
             background:linear-gradient(135deg,#6366f1,#22d3ee);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent;
             margin:0; line-height:1.2'>
    AI Resume Analyzer
  </h1>
  <p style='color:#94a3b8; font-size:18px; margin-top:12px; max-width:600px;
            margin-left:auto; margin-right:auto'>
    Match your resume to any job description. Get your ATS score,
    identify skill gaps, and download a professional report.
  </p>
</div>
""", unsafe_allow_html=True)

# Stats row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Skills Tracked", "500+")
c2.metric("Score Components", "4")
c3.metric("Analysis Time", "< 3s")
c4.metric("Report Format", "PDF")

st.markdown("---")

# ---------------------------------------------------------------------------
# Input section
# ---------------------------------------------------------------------------
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="section-header">📄 Resume Preview</div>', unsafe_allow_html=True)
    if st.session_state.get("pdf_bytes"):
        try:
            resume_text = extract_text(st.session_state["pdf_bytes"])
            st.session_state["resume_text"] = resume_text
            with st.expander("📖 Extracted Text Preview", expanded=False):
                st.text_area(
                    "Resume text",
                    value=resume_text[:3000] + ("..." if len(resume_text) > 3000 else ""),
                    height=200,
                    disabled=True,
                    label_visibility="collapsed",
                )
            word_count = len(resume_text.split())
            st.caption(f"📝 {word_count:,} words extracted from resume")
        except ValueError as e:
            st.error(f"❌ {e}")
    else:
        st.markdown("""
        <div style='background:rgba(30,41,59,0.4); border:2px dashed rgba(99,102,241,0.3);
                    border-radius:12px; padding:40px; text-align:center; color:#475569'>
          <div style='font-size:36px; margin-bottom:12px'>📤</div>
          <div style='font-size:15px'>Upload your resume PDF from the sidebar</div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="section-header">💼 Job Description</div>', unsafe_allow_html=True)
    jd_text = st.text_area(
        "Paste the job description here",
        placeholder="Paste the full job description here...\n\nInclude requirements, responsibilities, and preferred qualifications for the best analysis.",
        height=320,
        label_visibility="collapsed",
    )
    if jd_text:
        jd_word_count = len(jd_text.split())
        st.caption(f"📝 {jd_word_count:,} words in job description")
        st.session_state["jd_text"] = jd_text

# Job title (optional)
job_title = st.text_input(
    "Job Title (optional — used in report)",
    placeholder="e.g. Senior Machine Learning Engineer",
    help="This appears in the PDF report header.",
)

# ---------------------------------------------------------------------------
# Analyze button
# ---------------------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

analyze_col, _ = st.columns([1, 2])
with analyze_col:
    analyze_btn = st.button("🚀 Analyze My Resume", use_container_width=True)

if analyze_btn:
    resume_text = st.session_state.get("resume_text")
    jd_input = st.session_state.get("jd_text") or jd_text

    # Validation
    if not resume_text:
        st.error("⚠️ Please upload a resume PDF first.")
        st.stop()
    if not jd_input or len(jd_input.strip()) < 50:
        st.error("⚠️ Please paste a job description (at least 50 characters).")
        st.stop()

    with st.spinner("🤖 Analyzing your resume..."):
        progress = st.progress(0, text="Extracting skills…")
        time.sleep(0.3)
        resume_skills_grouped = extract_skills(resume_text)
        progress.progress(30, text="Comparing to job description…")
        time.sleep(0.2)
        ats_result = calculate_ats_score(resume_text, jd_input)
        progress.progress(70, text="Generating recommendations…")
        time.sleep(0.2)
        st.session_state["ats_result"] = ats_result
        st.session_state["resume_skills"] = resume_skills_grouped
        st.session_state["analysis_done"] = True
        progress.progress(100, text="Done!")
        time.sleep(0.3)
        progress.empty()

    st.success("✅ Analysis complete! Scroll down to see your results.")

# ---------------------------------------------------------------------------
# Results section
# ---------------------------------------------------------------------------
if st.session_state.get("analysis_done") and st.session_state.get("ats_result"):
    result = st.session_state["ats_result"]
    resume_skills_grouped = st.session_state.get("resume_skills", {})
    jd_input = st.session_state.get("jd_text", "")

    st.markdown("---")
    st.markdown("""
    <div style='font-family:"Space Grotesk",sans-serif; font-size:28px; font-weight:700;
                color:#e2e8f0; margin-bottom:24px'>
      📊 Analysis Results
    </div>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Top row: ATS Score + breakdown
    # -----------------------------------------------------------------------
    score_col, breakdown_col = st.columns([1, 2], gap="large")

    score_color = _score_color(result.total_score)
    grade_labels = {"A": "Excellent Match", "B": "Good Match", "C": "Fair Match",
                    "D": "Weak Match", "F": "Poor Match"}

    with score_col:
        st.markdown(f"""
        <div class="score-card">
          <div style='color:#94a3b8; font-size:13px; font-weight:500; text-transform:uppercase;
                      letter-spacing:2px; margin-bottom:8px'>ATS Score</div>
          <div class="score-number" style='color:{score_color}'>{result.total_score:.1f}</div>
          <div style='color:#64748b; font-size:14px; margin-top:4px'>out of 100</div>
          <div class="score-grade" style='color:{score_color}; margin-top:16px'>
            Grade: {result.grade}
          </div>
          <div style='color:#94a3b8; font-size:14px; margin-top:4px'>
            {grade_labels.get(result.grade, '')}
          </div>
        </div>
        """, unsafe_allow_html=True)

    with breakdown_col:
        st.markdown('<div class="section-header" style="font-size:16px">Score Breakdown</div>',
                    unsafe_allow_html=True)
        for label, val in result.score_breakdown.items():
            col_label, col_bar = st.columns([2, 3])
            with col_label:
                st.markdown(f"<div style='color:#cbd5e1; font-size:13px; padding-top:6px'>"
                            f"{label}</div>", unsafe_allow_html=True)
            with col_bar:
                pct = val / 100
                bar_color = _score_color(val)
                st.markdown(
                    f"<div style='background:rgba(30,41,59,0.6); border-radius:6px; "
                    f"padding:6px 10px; margin-top:2px'>"
                    f"<div style='background:linear-gradient(90deg,{bar_color},{bar_color}88);"
                    f"width:{val}%; height:8px; border-radius:4px; margin-bottom:3px'></div>"
                    f"<span style='color:#94a3b8; font-size:12px'>{val:.1f}/100</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Tabs: Skills | Recommendations | Resume Skills | Raw Text
    # -----------------------------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Skill Analysis", "💡 Recommendations", "🛠️ Resume Skills", "📄 Raw Text"
    ])

    with tab1:
        col_match, col_miss = st.columns(2, gap="large")

        with col_match:
            st.markdown(
                f'<div class="section-header" style="font-size:16px">'
                f'✅ Matching Skills <span style="color:#10b981">({len(result.matching_skills)})</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                _skill_pills(result.matching_skills, "skill-pill-match"),
                unsafe_allow_html=True,
            )

        with col_miss:
            st.markdown(
                f'<div class="section-header" style="font-size:16px">'
                f'❌ Missing Skills <span style="color:#ef4444">({len(result.missing_skills)})</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                _skill_pills(result.missing_skills, "skill-pill-missing"),
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-header" style="font-size:16px">'
            f'➕ Additional Resume Skills <span style="color:#a5b4fc">({len(result.extra_skills)})</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            _skill_pills(result.extra_skills, "skill-pill-extra"),
            unsafe_allow_html=True,
        )
        if result.extra_skills:
            st.caption("These skills appear on your resume but not in the job description.")

    with tab2:
        st.markdown('<div class="section-header" style="font-size:16px">💡 Improvement Recommendations</div>',
                    unsafe_allow_html=True)
        for rec in result.recommendations:
            st.markdown(f'<div class="rec-card">{rec}</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-header" style="font-size:16px">🛠️ Skills Detected on Resume</div>',
                    unsafe_allow_html=True)
        if resume_skills_grouped:
            for category, skills in resume_skills_grouped.items():
                with st.expander(f"📂 {category} ({len(skills)} skills)", expanded=False):
                    st.markdown(
                        "".join(f'<span class="skill-pill-extra">{s}</span>' for s in skills),
                        unsafe_allow_html=True,
                    )
        else:
            st.info("No structured skills detected on the resume.")

    with tab4:
        r_col, j_col = st.columns(2)
        with r_col:
            st.markdown("**📄 Resume Text**")
            resume_text_display = st.session_state.get("resume_text", "")
            st.text_area("Resume", value=resume_text_display, height=300,
                         disabled=True, label_visibility="collapsed")
        with j_col:
            st.markdown("**💼 Job Description**")
            st.text_area("JD", value=jd_input, height=300,
                         disabled=True, label_visibility="collapsed")

    # -----------------------------------------------------------------------
    # Download report
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.markdown('<div class="section-header">📥 Download Report</div>', unsafe_allow_html=True)

    dl_col, info_col = st.columns([1, 2])
    with dl_col:
        try:
            pdf_report = generate_report(
                ats_score=result.total_score,
                grade=result.grade,
                matching_skills=result.matching_skills,
                missing_skills=result.missing_skills,
                extra_skills=result.extra_skills,
                recommendations=result.recommendations,
                score_breakdown=result.score_breakdown,
                job_title=job_title or "Target Role",
            )
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_report,
                file_name="resume_ats_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Report generation failed: {e}")

    with info_col:
        st.markdown("""
        <div class="info-box">
          📋 Your report includes: ATS score, score breakdown, matching skills,
          skill gaps, all recommendations, and a summary. Perfect for sharing
          with your career coach or keeping track of applications.
        </div>
        """, unsafe_allow_html=True)

"""
PDF report generator using ReportLab.
Produces a professional, downloadable analysis report.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import List, Set

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Brand colors
# ---------------------------------------------------------------------------
BRAND_DARK = colors.HexColor("#0F172A")       # slate-900
BRAND_PRIMARY = colors.HexColor("#6366F1")    # indigo-500
BRAND_ACCENT = colors.HexColor("#22D3EE")     # cyan-400
BRAND_SUCCESS = colors.HexColor("#10B981")    # emerald-500
BRAND_WARNING = colors.HexColor("#F59E0B")    # amber-500
BRAND_DANGER = colors.HexColor("#EF4444")     # red-500
BRAND_MUTED = colors.HexColor("#64748B")      # slate-500
BRAND_LIGHT = colors.HexColor("#F1F5F9")      # slate-100
TEXT_DARK = colors.HexColor("#1E293B")        # slate-800
TEXT_BODY = colors.HexColor("#334155")        # slate-700


def _grade_color(grade: str) -> colors.HexColor:
    return {
        "A": BRAND_SUCCESS,
        "B": colors.HexColor("#84CC16"),
        "C": BRAND_WARNING,
        "D": colors.HexColor("#F97316"),
        "F": BRAND_DANGER,
    }.get(grade, BRAND_MUTED)


def _score_color(score: float) -> colors.HexColor:
    if score >= 80:
        return BRAND_SUCCESS
    elif score >= 60:
        return BRAND_WARNING
    return BRAND_DANGER


def _strip_markdown(text: str) -> str:
    """Remove markdown bold/emoji for ReportLab compatibility."""
    import re
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    # Remove emoji (basic Unicode range)
    text = re.sub(r"[^\x00-\x7F\u00C0-\u024F\u1E00-\u1EFF]+", "", text)
    return text.strip()


def generate_report(
    ats_score: float,
    grade: str,
    matching_skills: Set[str],
    missing_skills: Set[str],
    extra_skills: Set[str],
    recommendations: List[str],
    score_breakdown: dict,
    job_title: str = "Target Role",
) -> bytes:
    """
    Generate a PDF analysis report and return it as bytes.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Resume ATS Analysis Report",
        author="AI Resume Analyzer",
    )

    styles = getSampleStyleSheet()
    story = []

    # -----------------------------------------------------------------------
    # Helper styles
    # -----------------------------------------------------------------------
    def h1(text):
        return Paragraph(text, ParagraphStyle(
            "H1", fontSize=22, textColor=BRAND_PRIMARY, spaceAfter=4,
            fontName="Helvetica-Bold", alignment=TA_LEFT,
        ))

    def h2(text):
        return Paragraph(text, ParagraphStyle(
            "H2", fontSize=13, textColor=TEXT_DARK, spaceAfter=3,
            fontName="Helvetica-Bold", spaceBefore=10,
        ))

    def body(text, color=TEXT_BODY):
        return Paragraph(_strip_markdown(text), ParagraphStyle(
            "Body", fontSize=9.5, textColor=color, spaceAfter=3,
            fontName="Helvetica", leading=14,
        ))

    def small(text, color=BRAND_MUTED):
        return Paragraph(text, ParagraphStyle(
            "Small", fontSize=8, textColor=color, spaceAfter=2,
            fontName="Helvetica",
        ))

    def hr(color=BRAND_PRIMARY, thickness=0.5):
        return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=8, spaceBefore=4)

    # -----------------------------------------------------------------------
    # Header
    # -----------------------------------------------------------------------
    story.append(Paragraph(
        "AI Resume Analyzer",
        ParagraphStyle("Brand", fontSize=10, textColor=BRAND_MUTED, fontName="Helvetica",
                       alignment=TA_RIGHT),
    ))

    story.append(Paragraph(
        "Resume ATS Analysis Report",
        ParagraphStyle("Title", fontSize=26, textColor=BRAND_DARK, fontName="Helvetica-Bold",
                       spaceAfter=2),
    ))

    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}  |  Role: {job_title}",
        ParagraphStyle("Sub", fontSize=9, textColor=BRAND_MUTED, fontName="Helvetica",
                       spaceAfter=6),
    ))
    story.append(hr(BRAND_PRIMARY, 1.5))
    story.append(Spacer(1, 4))

    # -----------------------------------------------------------------------
    # ATS Score card
    # -----------------------------------------------------------------------
    grade_col = _grade_color(grade)
    score_col = _score_color(ats_score)

    score_table = Table(
        [[
            Paragraph(f"{ats_score:.1f}", ParagraphStyle(
                "ScoreNum", fontSize=48, textColor=score_col,
                fontName="Helvetica-Bold", alignment=TA_CENTER,
            )),
            Paragraph("/ 100", ParagraphStyle(
                "ScoreOf", fontSize=16, textColor=BRAND_MUTED,
                fontName="Helvetica", alignment=TA_LEFT,
            )),
            Paragraph(f"Grade: {grade}", ParagraphStyle(
                "Grade", fontSize=22, textColor=grade_col,
                fontName="Helvetica-Bold", alignment=TA_CENTER,
            )),
        ]],
        colWidths=[5 * cm, 3 * cm, 8 * cm],
    )
    score_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_LIGHT),
        ("ROUNDEDCORNERS", [6]),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 10))

    # Score breakdown table
    story.append(h2("Score Breakdown"))
    breakdown_data = [["Component", "Score", "Visual"]]
    for label, val in score_breakdown.items():
        bar_filled = int(val / 10)
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        breakdown_data.append([label, f"{val:.1f} / 100", bar])

    breakdown_table = Table(breakdown_data, colWidths=[8 * cm, 3.5 * cm, 5 * cm])
    breakdown_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (2, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(breakdown_table)
    story.append(Spacer(1, 12))

    # -----------------------------------------------------------------------
    # Skills sections
    # -----------------------------------------------------------------------
    story.append(hr())

    # Matching skills
    story.append(h2(f"Matching Skills  ({len(matching_skills)} found)"))
    if matching_skills:
        chunks = _chunk_list(sorted(matching_skills), 4)
        skill_data = [[Paragraph(s, ParagraphStyle(
            "SkillCell", fontSize=8.5, textColor=BRAND_SUCCESS,
            fontName="Helvetica-Bold", alignment=TA_CENTER,
        )) for s in row] for row in chunks]
        # Pad last row
        if skill_data and len(skill_data[-1]) < 4:
            skill_data[-1] += [""] * (4 - len(skill_data[-1]))
        if skill_data:
            st = Table(skill_data, colWidths=[4.1 * cm] * 4)
            st.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#D1FAE5")),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#A7F3D0")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))
            story.append(st)
    else:
        story.append(body("No matching skills detected.", BRAND_MUTED))

    story.append(Spacer(1, 10))

    # Missing skills
    story.append(h2(f"Missing Skills  ({len(missing_skills)} gaps)"))
    if missing_skills:
        chunks = _chunk_list(sorted(missing_skills), 4)
        skill_data = [[Paragraph(s, ParagraphStyle(
            "SkillCellM", fontSize=8.5, textColor=BRAND_DANGER,
            fontName="Helvetica-Bold", alignment=TA_CENTER,
        )) for s in row] for row in chunks]
        if skill_data and len(skill_data[-1]) < 4:
            skill_data[-1] += [""] * (4 - len(skill_data[-1]))
        if skill_data:
            st = Table(skill_data, colWidths=[4.1 * cm] * 4)
            st.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEE2E2")),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#FECACA")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))
            story.append(st)
    else:
        story.append(body("No skill gaps detected — great match!", BRAND_SUCCESS))

    story.append(Spacer(1, 10))

    # Additional resume skills
    if extra_skills:
        story.append(h2(f"Additional Skills on Resume  ({len(extra_skills)})"))
        story.append(body(
            "These skills are on your resume but not explicitly mentioned in the job description. "
            "They may be valuable for other roles or future discussions.",
            BRAND_MUTED,
        ))
        story.append(body(", ".join(sorted(extra_skills))))
        story.append(Spacer(1, 10))

    # -----------------------------------------------------------------------
    # Recommendations
    # -----------------------------------------------------------------------
    story.append(hr())
    story.append(h2("Improvement Recommendations"))
    for i, rec in enumerate(recommendations, 1):
        story.append(body(f"{i}. {rec}"))
        story.append(Spacer(1, 3))

    # -----------------------------------------------------------------------
    # Footer
    # -----------------------------------------------------------------------
    story.append(Spacer(1, 16))
    story.append(hr(BRAND_MUTED, 0.5))
    story.append(Paragraph(
        "Generated by AI Resume Analyzer  |  For personal use only  |  "
        f"{datetime.now().year}",
        ParagraphStyle("Footer", fontSize=7.5, textColor=BRAND_MUTED,
                       alignment=TA_CENTER, fontName="Helvetica"),
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def _chunk_list(lst: list, n: int) -> list:
    """Split list into rows of n items."""
    return [lst[i:i + n] for i in range(0, len(lst), n)]

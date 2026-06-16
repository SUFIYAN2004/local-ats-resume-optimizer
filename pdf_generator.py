import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from pypdf import PdfReader


PRIMARY_COLOR   = colors.HexColor("#1A365D")
SECONDARY_COLOR = colors.HexColor("#4A5568")
TEXT_COLOR      = colors.HexColor("#2D3748")
LINE_COLOR      = colors.HexColor("#CBD5E0")
BLUE_COLOR      = colors.HexColor("#2779F5")
NAVY_COLOR      = colors.HexColor("#1337AD")


def S(name, **kw):
    return ParagraphStyle(name, **kw)


NAME    = S("NAME",  fontSize=14.5, leading=17, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=PRIMARY_COLOR, spaceAfter=1)
ROLE    = S("ROLE",  fontSize=9,    leading=11, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=SECONDARY_COLOR, spaceAfter=1)
CONTACT = S("CON",   fontSize=8,    leading=10, fontName="Helvetica",      alignment=TA_CENTER, textColor=TEXT_COLOR, spaceAfter=1)
CITY    = S("CITY",  fontSize=8,    leading=10, fontName="Helvetica",      alignment=TA_CENTER, textColor=SECONDARY_COLOR, spaceAfter=2)
SEC_HDR = S("SEC",   fontSize=8,    leading=10, fontName="Helvetica-Bold", textColor=NAVY_COLOR, letterSpacing=2.5)
BODY    = S("BODY",  fontSize=8,    leading=11, fontName="Helvetica",      textColor=TEXT_COLOR, spaceAfter=0.5)
BULLET  = S("BUL",   fontSize=8,    leading=11, fontName="Helvetica",      textColor=TEXT_COLOR, leftIndent=10, firstLineIndent=-8, spaceAfter=0.5)
PROJ_HDR= S("PHDR",  fontSize=8,    leading=10, fontName="Helvetica-Bold", textColor=TEXT_COLOR, spaceBefore=2, spaceAfter=0.5)
LINK    = S("LINK",  fontSize=7.8,  leading=9,  fontName="Helvetica",      textColor=BLUE_COLOR, spaceAfter=0.5)


def spaced(text):
    return "  ".join(text.upper())


def hr():
    return HRFlowable(width="100%", thickness=0.7, color=LINE_COLOR, spaceAfter=2, spaceBefore=0.5)


def sec(title):
    return [Paragraph(spaced(title), SEC_HDR), hr()]


def b(text):
    return Paragraph(f"- {text}", BULLET)


def generate_resume_pdf(resume_data: dict, output_path: str) -> str:
    """
    resume_data keys:
    - name, role, phone, email, linkedin, github, city
    - summary
    - skills: {languages, frameworks, ml_dl, tools}
    - experience: list of {title, company, period, bullets, link}
    - projects: list of {title, tech, bullets, link}
    - achievements: list of strings
    - education: {degree, college, period, certifications}
    """

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.3 * inch,
        bottomMargin=0.3 * inch,
    )

    story = []

    # ── HEADER ──────────────────────────────────────────
    story.append(Paragraph(resume_data.get("name", ""), NAME))
    story.append(Paragraph(resume_data.get("role", ""), ROLE))

    contact = " | ".join(filter(None, [
        resume_data.get("phone", ""),
        resume_data.get("email", ""),
        resume_data.get("linkedin", ""),
        resume_data.get("github", ""),
    ]))
    story.append(Paragraph(contact, CONTACT))
    story.append(Paragraph(resume_data.get("city", ""), CITY))
    story.append(Spacer(1, 0.2 * inch))

    # ── SUMMARY ─────────────────────────────────────────
    if resume_data.get("summary"):
        story += sec("Professional Summary")
        story.append(Paragraph(resume_data["summary"], BODY))
        story.append(Spacer(1, 0.2 * inch))

    # ── SKILLS ──────────────────────────────────────────
    skills = resume_data.get("skills", {})
    if skills:
        story += sec("Technical Skills")
        if skills.get("languages"):
            story.append(Paragraph(f"<b>Languages & DB:</b>  {skills['languages']}", BODY))
        if skills.get("frameworks"):
            story.append(Paragraph(f"<b>Frameworks & Libraries:</b>  {skills['frameworks']}", BODY))
        if skills.get("ml_dl"):
            story.append(Paragraph(f"<b>ML / DL:</b>  {skills['ml_dl']}", BODY))
        if skills.get("tools"):
            story.append(Paragraph(f"<b>Tools:</b>  {skills['tools']}", BODY))
        story.append(Spacer(1, 0.2 * inch))

    # ── EXPERIENCE ──────────────────────────────────────
    experience = resume_data.get("experience", [])
    if experience:
        story += sec("Experience")
        for exp in experience:
            header = f"<b>{exp.get('title', '')}  |  {exp.get('company', '')}  |  {exp.get('period', '')}</b>"
            story.append(Paragraph(header, PROJ_HDR))
            for bullet in exp.get("bullets", []):
                story.append(b(bullet))
            if exp.get("link"):
                story.append(Paragraph(f"Link: {exp['link']}", LINK))
        story.append(Spacer(1, 0.2 * inch))

    # ── PROJECTS ────────────────────────────────────────
    projects = resume_data.get("projects", [])
    if projects:
        story += sec("Projects")
        for proj in projects:
            header = f"<b>{proj.get('title', '')}  |  Tech: {proj.get('tech', '')}</b>"
            story.append(Paragraph(header, PROJ_HDR))
            for bullet in proj.get("bullets", []):
                story.append(b(bullet))
            if proj.get("link"):
                story.append(Paragraph(f"Link: {proj['link']}", LINK))
            story.append(Spacer(1, 0.1 * inch))
        story.append(Spacer(1, 0.1 * inch))

    # ── ACHIEVEMENTS ────────────────────────────────────
    achievements = resume_data.get("achievements", [])
    if achievements:
        story += sec("Achievements & Activities")
        for ach in achievements:
            story.append(b(ach))
        story.append(Spacer(1, 0.2 * inch))

    # ── EDUCATION ───────────────────────────────────────
    edu = resume_data.get("education", {})
    if edu:
        story += sec("Education & Certifications")
        story.append(Paragraph(f"<b>{edu.get('degree', '')}</b>", PROJ_HDR))
        story.append(Paragraph(edu.get("college", ""), BODY))
        story.append(Paragraph(edu.get("period", ""), BODY))
        if edu.get("certifications"):
            story.append(Paragraph(edu["certifications"], BODY))

    doc.build(story)
    return output_path


def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()
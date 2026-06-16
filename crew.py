import os
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

from crewai import Crew, Process
from agents import get_parser_agent, get_ats_analyzer, get_resume_writer, get_pdf_agent
from tasks import get_parse_task, get_ats_task, get_writer_task, get_pdf_task
from pdf_generator import extract_text_from_pdf, generate_resume_pdf
import json
import re


def clean_json(raw: str) -> dict:
    raw = str(raw).strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'^```\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    raw = raw.strip()
    try:
        return json.loads(raw)
    except:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
    return {}


def clean_field(value):
    if isinstance(value, list):
        return ", ".join(str(x) for x in value)
    if isinstance(value, dict):
        return ", ".join(str(v) for v in value.values())
    return str(value) if value else ""


def clean_bullets(bullets):
    result = []
    for b in bullets:
        if isinstance(b, dict):
            text = (b.get("description") or b.get("text") or
                    b.get("bullet") or b.get("content") or
                    b.get("Title") or b.get("title") or str(b))
            result.append(text)
        elif isinstance(b, str) and b.strip():
            result.append(b.strip())
    return result


def clean_resume_data(data: dict) -> dict:
    if not data:
        return data

    # Fix skills
    skills = data.get("skills", {})
    if isinstance(skills, dict):
        for key in skills:
            skills[key] = clean_field(skills[key])
    elif isinstance(skills, list):
        data["skills"] = {
            "languages": clean_field(skills),
            "frameworks": "",
            "ml_dl": "",
            "tools": ""
        }

    # Fix achievements
    achievements = data.get("achievements", [])
    if isinstance(achievements, list):
        data["achievements"] = clean_bullets(achievements)
    elif isinstance(achievements, str):
        data["achievements"] = [achievements]

    # Fix experience
    experience = data.get("experience", [])
    if isinstance(experience, list):
        for exp in experience:
            if isinstance(exp, dict):
                exp["bullets"] = clean_bullets(exp.get("bullets", []))
                exp["title"]   = clean_field(exp.get("title", ""))
                exp["company"] = clean_field(exp.get("company", ""))
                exp["period"]  = clean_field(exp.get("period", ""))
                exp["link"]    = clean_field(exp.get("link", ""))

    # Fix projects
    projects = data.get("projects", [])
    if isinstance(projects, list):
        for proj in projects:
            if isinstance(proj, dict):
                proj["bullets"] = clean_bullets(proj.get("bullets", []))
                proj["title"]   = clean_field(proj.get("title", ""))
                proj["tech"]    = clean_field(proj.get("tech", ""))
                proj["link"]    = clean_field(proj.get("link", ""))

    # Fix education
    edu = data.get("education", {})
    if isinstance(edu, dict):
        for key in ["degree", "college", "period", "certifications"]:
            edu[key] = clean_field(edu.get(key, ""))

    # Ensure empty lists not None
    if not data.get("experience"):
        data["experience"] = []
    if not data.get("projects"):
        data["projects"] = []
    if not data.get("achievements"):
        data["achievements"] = []

    return data


def run_resume_crew(pdf_path: str, output_dir: str, log_queue=None) -> str:

    def log(msg):
        print(msg)
        if log_queue:
            log_queue.put(msg)

    log("📄 Extracting text from uploaded resume...")
    resume_text = extract_text_from_pdf(pdf_path)

    if not resume_text:
        raise ValueError("Could not extract text from PDF!")

    log(f"✅ Extracted {len(resume_text)} characters from resume")
    log("🔍 Agent 1: Parsing resume structure...")

    parser  = get_parser_agent()
    ats     = get_ats_analyzer()
    writer  = get_resume_writer()
    pdf_agt = get_pdf_agent()

    parse_task  = get_parse_task(parser, resume_text)
    ats_task    = get_ats_task(ats, [parse_task])
    writer_task = get_writer_task(writer, [parse_task, ats_task])
    pdf_task    = get_pdf_task(pdf_agt, [writer_task])

    crew = Crew(
        agents=[parser, ats, writer, pdf_agt],
        tasks=[parse_task, ats_task, writer_task, pdf_task],
        process=Process.sequential,
        verbose=False,
    )

    log("🚀 Crew is working — this takes 3-5 mins on CPU...")
    result = crew.kickoff()

    log("📊 Agent 2: ATS analysis complete...")
    log("✍️ Agent 3: Rewriting resume content...")
    log("✅ Agent 4: Validating final output...")

    resume_data = clean_resume_data(clean_json(result.raw))

    if not resume_data or not resume_data.get("name"):
        log("⚠️ Final output parse failed — trying writer task...")
        try:
            writer_output = str(writer_task.output)
            resume_data = clean_resume_data(clean_json(writer_output))
        except:
            pass

    if not resume_data or not resume_data.get("name"):
        log("⚠️ Writer failed — using parser output...")
        try:
            parse_output = str(parse_task.output)
            resume_data = clean_resume_data(clean_json(parse_output))
        except:
            pass

    if not resume_data or not resume_data.get("name"):
        raise ValueError("All agents failed to produce valid resume JSON!")

    log(f"💾 Generating PDF for: {resume_data.get('name', 'Unknown')}")

    output_path = os.path.join(output_dir, "optimized_resume.pdf")
    os.makedirs(output_dir, exist_ok=True)
    generate_resume_pdf(resume_data, output_path)

    log(f"✅ PDF saved: {output_path}")
    return output_path
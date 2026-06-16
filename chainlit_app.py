import os
import sys

os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chainlit as cl
import asyncio
import tempfile
import json


def fix_settings():
    settings_path = os.path.expanduser("~/.config/crewai/settings.json")
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump({"tracing": False}, f)

fix_settings()


@cl.on_chat_start
async def start():
    await cl.Message(
        content="""👋 Welcome to **Resume ATS Optimizer**!

Upload your resume PDF and my 4 AI agents will:
- 🔍 Parse your entire resume structure
- 📊 Score your ATS compatibility
- ✍️ Rewrite bullets with metrics and keywords
- 💾 Generate a professional optimized PDF

**Upload your PDF using the attachment button below!**""",
        author="Resume AI"
    ).send()


@cl.on_message
async def main(message: cl.Message):

    # Check for PDF
    pdf_file = None
    for element in message.elements:
        if hasattr(element, 'name') and element.name.lower().endswith(".pdf"):
            pdf_file = element
            break

    if not pdf_file:
        await cl.Message(
            content="Please upload your resume as a **PDF file** using the 📎 attachment button!",
            author="Resume AI"
        ).send()
        return

    await cl.Message(
        content=f"📄 Got **{pdf_file.name}** — starting optimization now...",
        author="Resume AI"
    ).send()

    output_dir = tempfile.mkdtemp()
    loop = asyncio.get_event_loop()

    try:
        # ── Step 1: Extract text ──────────────────────
        async with cl.Step(name="📄 Extracting Resume Text") as step:
            step.output = "Reading your PDF..."
            await step.update()

            from pdf_generator import extract_text_from_pdf

            resume_text = await loop.run_in_executor(
                None, extract_text_from_pdf, pdf_file.path
            )

            if not resume_text or len(resume_text) < 50:
                raise ValueError("Could not extract text from PDF. Is it a scanned image?")

            step.output = f"✅ Extracted {len(resume_text)} characters"
            await step.update()

        # ── Step 2: Run Crew ──────────────────────────
        async with cl.Step(name="🤖 AI Agents Working") as step:
            step.output = "Parser → ATS Analyzer → Writer → Validator running..."
            await step.update()

            from agents import (
                get_parser_agent, get_ats_analyzer,
                get_resume_writer, get_pdf_agent
            )
            from tasks import (
                get_parse_task, get_ats_task,
                get_writer_task, get_pdf_task
            )
            from crewai import Crew, Process

            error_holder = {"error": None, "result": None,
                           "parse_task": None, "writer_task": None}

            def run_crew_sync():
                try:
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
                        verbose=True,
                    )

                    result = crew.kickoff()
                    error_holder["result"]      = result
                    error_holder["parse_task"]  = parse_task
                    error_holder["writer_task"] = writer_task

                except Exception as e:
                    error_holder["error"] = str(e)
                    print(f"CREW ERROR: {e}")
                    import traceback
                    traceback.print_exc()

            await loop.run_in_executor(None, run_crew_sync)

            if error_holder["error"]:
                raise ValueError(f"Crew failed: {error_holder['error']}")

            result      = error_holder["result"]
            parse_task  = error_holder["parse_task"]
            writer_task = error_holder["writer_task"]

            step.output = "✅ All agents completed!"
            await step.update()

        # ── Step 3: Parse JSON ────────────────────────
        async with cl.Step(name="🔍 Processing Results") as step:
            step.output = "Parsing agent output..."
            await step.update()

            from crew import clean_json, clean_resume_data

            resume_data = None

            # Try result first
            if result and result.raw:
                resume_data = clean_resume_data(clean_json(result.raw))
                print(f"Result parse: {bool(resume_data and resume_data.get('name'))}")

            # Try writer task
            if not resume_data or not resume_data.get("name"):
                print("Trying writer task output...")
                try:
                    writer_out = str(writer_task.output) if writer_task else ""
                    if writer_out:
                        resume_data = clean_resume_data(clean_json(writer_out))
                        print(f"Writer parse: {bool(resume_data and resume_data.get('name'))}")
                except Exception as e:
                    print(f"Writer parse error: {e}")

            # Try parse task
            if not resume_data or not resume_data.get("name"):
                print("Trying parse task output...")
                try:
                    parse_out = str(parse_task.output) if parse_task else ""
                    if parse_out:
                        resume_data = clean_resume_data(clean_json(parse_out))
                        print(f"Parse task result: {bool(resume_data and resume_data.get('name'))}")
                except Exception as e:
                    print(f"Parse task error: {e}")

            if not resume_data or not resume_data.get("name"):
                # Show what we got for debugging
                print(f"RAW RESULT: {str(result.raw)[:500] if result else 'None'}")
                raise ValueError("Could not extract resume data — check terminal for raw output!")

            step.output = f"✅ Resume data ready for: **{resume_data.get('name')}**"
            await step.update()

        # ── Step 4: Generate PDF ──────────────────────
        async with cl.Step(name="💾 Generating PDF") as step:
            step.output = "Creating professional PDF with your styling..."
            await step.update()

            from pdf_generator import generate_resume_pdf

            output_path = os.path.join(output_dir, "ATS_Optimized_Resume.pdf")

            await loop.run_in_executor(
                None, generate_resume_pdf, resume_data, output_path
            )

            step.output = "✅ PDF created successfully!"
            await step.update()

        # ── Send result ───────────────────────────────
        elements = [
            cl.File(
                name="ATS_Optimized_Resume.pdf",
                path=output_path,
                display="inline",
            )
        ]

        await cl.Message(
            content="""✅ **Your ATS-optimized resume is ready!**

What the AI improved:
- 💪 Stronger action verbs in all bullet points
- 🎯 ATS keywords added throughout
- 📝 Professional summary rewritten
- 📈 Project descriptions show clear impact

👇 **Download your new resume below:**""",
            elements=elements,
            author="Resume AI"
        ).send()

    except Exception as e:
        print(f"MAIN ERROR: {e}")
        import traceback
        traceback.print_exc()
        await cl.Message(
            content=f"❌ **Error:** {str(e)}\n\nPlease try uploading your resume again.",
            author="Resume AI"
        ).send()
from crewai import Task


def get_parse_task(agent, resume_text: str):
    return Task(
        description=f"""Extract ALL information from this resume text and output as JSON.

Resume text:
{resume_text}

Output ONLY this JSON structure, nothing else:
{{
  "name": "full name",
  "role": "job title/role",
  "phone": "phone number",
  "email": "email address",
  "linkedin": "linkedin url",
  "github": "github url",
  "city": "city, state/country",
  "summary": "professional summary paragraph",
  "skills": {{
    "languages": "comma separated languages and databases",
    "frameworks": "comma separated frameworks and libraries",
    "ml_dl": "comma separated ML/DL concepts",
    "tools": "comma separated tools and platforms"
  }},
  "experience": [
    {{
      "title": "job title",
      "company": "company name",
      "period": "date range",
      "bullets": ["bullet 1", "bullet 2"],
      "link": "url if any"
    }}
  ],
  "projects": [
    {{
      "title": "project name",
      "tech": "technologies used",
      "bullets": ["bullet 1", "bullet 2"],
      "link": "github url"
    }}
  ],
  "achievements": ["achievement 1", "achievement 2"],
  "education": {{
    "degree": "degree name",
    "college": "college name and location",
    "period": "date range",
    "certifications": "certifications as one string"
  }}
}}""",
        expected_output="Valid JSON object with all resume fields extracted. No extra text.",
        agent=agent,
    )


def get_ats_task(agent, context_tasks):
    return Task(
        description="""Analyze the extracted resume data for ATS compatibility.

Check for:
1. Missing high-value keywords for AI/ML roles
2. Weak bullet points that lack metrics or action verbs
3. Summary quality — is it ATS optimized?
4. Skills section completeness
5. Project descriptions — do they show impact?

Output a clear analysis with:
- ATS Score: X/100
- Missing keywords: list them
- Weak sections: list them  
- Specific improvements needed: list them
- Keywords to add: list the exact keywords""",
        expected_output="""ATS analysis with score, missing keywords, weak sections, 
        and specific improvement recommendations.""",
        agent=agent,
        context=context_tasks,
    )


def get_writer_task(agent, context_tasks):
    return Task(
        description="""Using the original resume data AND the ATS analysis, 
rewrite the complete resume with improvements.

Rules:
- Strengthen ALL bullet points with action verbs + metrics
- Add missing ATS keywords naturally
- Improve professional summary  
- Keep all factual information accurate — don't invent facts
- Make project bullets show clear impact and results

Output ONLY valid JSON in EXACTLY the same structure as the parsed resume:
{{
  "name": "...",
  "role": "...",
  "phone": "...",
  "email": "...",
  "linkedin": "...",
  "github": "...",
  "city": "...",
  "summary": "improved summary...",
  "skills": {{ ... }},
  "experience": [ ... ],
  "projects": [ ... ],
  "achievements": [ ... ],
  "education": {{ ... }}
}}

Output ONLY the JSON. No explanation.""",
        expected_output="Complete improved resume as valid JSON. No extra text.",
        agent=agent,
        context=context_tasks,
    )


def get_pdf_task(agent, context_tasks):
    return Task(
        description="""Review the optimized resume JSON and ensure it is 
complete and clean for PDF generation.

Check:
- All required fields present
- No empty critical fields
- Content is professional
- JSON is valid

Output the final clean JSON ready for PDF generation.
Output ONLY the JSON. Nothing else.""",
        expected_output="Final validated resume JSON ready for PDF generation.",
        agent=agent,
        context=context_tasks,
    )
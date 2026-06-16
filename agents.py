from crewai import Agent
from llm_setup import get_llm


def get_parser_agent():
    return Agent(
        role="Resume Parser",
        goal="Extract all information from a resume texxt accurately",
        backstory="""You are an expert at reading resumes and extracting structured data. You extract every detail - name, contact info, skills, experience, projects, achievements, education - into a clean structured format. You output ONLY valid JSON. Nothing else.""",
        llm=get_llm(),
        verbose=False,
        allow_delegation=False,
    )

def get_ats_analyzer():
    return Agent(
        role="ATS Expert",
        goal="Analyze resume for ATS compatibility and identify improvements",
        backstory="""You are an Applicant Tracking System expert with 10 years 
        of experience in HR tech. You know exactly what keywords, formats, and 
        structures make resumes pass ATS filters. You identify weak bullet points,
        missing keywords, and formatting issues. You give specific actionable 
        feedback on what to fix and what keywords to add.""",
        llm=get_llm(),
        verbose=False,
        allow_delegation=False,
    
    )   

def get_resume_writer():
    return Agent(
        role="Professional Resume Writer",
        goal="Rewrite and optimize resume content for maximum ATS score",
        backstory="""You are a professional resume writer who has helped 500+ 
        candidates land jobs at top tech companies. You:
        - Rewrite bullet points with strong action verbs and quantified metrics
        - Add relevant ATS keywords naturally into the content  
        - Strengthen the professional summary
        - Improve project descriptions to highlight impact
        You output the complete improved resume as valid JSON only.""",
        llm=get_llm(),
        verbose=False,
        allow_delegation=False,
    )


def get_pdf_agent():
    return Agent(
        role="PDF Formatter",
        goal="Convert optimized resume JSON into a clean formatted output",
        backstory="""You are responsible for taking the final optimized resume 
        data and ensuring it is clean, complete, and properly structured JSON
        ready for PDF generation. You validate all fields are present and 
        the content is professional.""",
        llm=get_llm(),
        verbose=False,
        allow_delegation=False,
    )
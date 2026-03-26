# app/agents/agent_1_parser.py
# Agent 1: Resume Parsing Agent — Extracts structured JSON from raw resume text

from app.agents.graph_state import GraphState
from app.agents.gemini_client import call_llm_json


PARSER_PROMPT = """You are an expert resume parser for Indian engineering students.

Extract ALL information from the resume text below into a strict JSON structure.

RULES:
1. Extract EXACTLY what is written. NEVER invent or guess information.
2. If a field is missing (e.g., GPA not mentioned), set it to null.
3. Normalize skill names to lowercase (e.g., "ReactJS" → "react", "NodeJS" → "node.js").
4. Dates should be in "Month Year" format if available, otherwise null.
5. Return ONLY the JSON object, nothing else.

RESUME TEXT:
\"\"\"
{raw_text}
\"\"\"

Return this EXACT JSON structure:
{{
    "name": "<full name or null>",
    "email": "<email or null>",
    "phone": "<phone number or null>",
    "linkedin": "<linkedin URL or null>",
    "github": "<github URL or null>",
    "portfolio": "<portfolio URL or null>",
    "summary": "<professional summary if present, or null>",
    "education": [
        {{
            "degree": "<e.g., B.Tech in Computer Science>",
            "institution": "<college/university name>",
            "year": "<graduation year or null>",
            "gpa": "<GPA/CGPA/percentage or null>",
            "location": "<city or null>"
        }}
    ],
    "skills": {{
        "programming_languages": ["<lowercase list>"],
        "frameworks": ["<lowercase list>"],
        "databases": ["<lowercase list>"],
        "tools": ["<lowercase list>"],
        "cs_fundamentals": ["<e.g., dsa, oops, dbms, os, cn>"],
        "other": ["<anything else>"]
    }},
    "projects": [
        {{
            "title": "<project name>",
            "description": "<1-2 sentence description>",
            "tech_stack": ["<lowercase list>"],
            "date": "<date range or null>",
            "link": "<project URL or null>"
        }}
    ],
    "experience": [
        {{
            "role": "<job title/internship role>",
            "company": "<company name>",
            "duration": "<date range or null>",
            "description": ["<bullet points>"],
            "location": "<city or null>"
        }}
    ],
    "certifications": ["<list of certifications>"],
    "achievements": ["<list of achievements, awards, positions of responsibility>"],
    "all_skills_flat": ["<flat lowercase list of ALL technical skills found anywhere in resume>"]
}}
"""


def run_parser(state: GraphState) -> dict:
    """Agent 1: Parse raw resume text into structured JSON."""
    raw_text = state["raw_text"]

    if not raw_text or not raw_text.strip():
        return {
            "parsed_json": None,
            "errors": state.get("errors", []) + ["Agent 1: No raw text provided"],
        }

    try:
        prompt = PARSER_PROMPT.format(raw_text=raw_text[:8000])
        result = call_llm_json(prompt, temperature=0.1)

        # Ensure all_skills_flat exists
        if "all_skills_flat" not in result:
            all_skills = []
            skills = result.get("skills", {})
            for category in skills.values():
                if isinstance(category, list):
                    all_skills.extend(category)
            result["all_skills_flat"] = sorted(set(s.lower().strip() for s in all_skills))

        print(f"✅ Agent 1 (Parser): Extracted {len(result.get('all_skills_flat', []))} skills, "
              f"{len(result.get('projects', []))} projects")

        return {"parsed_json": result}

    except Exception as e:
        print(f"❌ Agent 1 (Parser) failed: {e}")
        return {
            "parsed_json": None,
            "errors": state.get("errors", []) + [f"Agent 1: {str(e)}"],
        }

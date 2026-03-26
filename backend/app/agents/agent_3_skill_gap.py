# app/agents/agent_3_skill_gap.py
# Agent 3: Skill Gap Agent — Compares skills against Indian campus placement demands

from app.agents.graph_state import GraphState
from app.agents.gemini_client import call_llm_json


# Standard skills expected for Indian campus placements by role
PLACEMENT_DEMANDS = {
    "common_core": [
        "dsa", "oops", "dbms", "operating systems", "computer networks",
        "sql", "git", "problem solving"
    ],
    "software_engineer": [
        "java", "python", "c++", "system design", "rest api",
        "html", "css", "javascript", "react", "node.js",
        "postgresql", "mongodb", "docker", "linux"
    ],
    "data_analyst": [
        "python", "sql", "excel", "power bi", "tableau",
        "pandas", "numpy", "data visualization", "statistics"
    ],
    "data_scientist": [
        "python", "machine learning", "deep learning", "tensorflow",
        "pytorch", "pandas", "numpy", "sql", "statistics", "nlp"
    ],
    "frontend_developer": [
        "html", "css", "javascript", "react", "typescript",
        "tailwind", "redux", "next.js", "responsive design"
    ],
    "backend_developer": [
        "python", "java", "node.js", "fastapi", "django", "spring boot",
        "postgresql", "mongodb", "redis", "docker", "rest api", "microservices"
    ],
}


SKILL_GAP_PROMPT = """You are a strict and HIGHLY ACCURATE Indian campus placement advisor.

A student is targeting the role: "{target_role}"

Here is the student's FULL PARSED RESUME:
\"\"\"
{parsed_resume}
\"\"\"

Here is the RAW RESUME TEXT (use this as the ultimate source of truth):
\"\"\"
{raw_text}
\"\"\"

STANDARD REQUIREMENTS FOR THIS ROLE IN INDIAN PLACEMENTS:
Core CS Fundamentals: {core_skills}
Role-Specific Skills: {role_skills}

CRITICAL ACCURACY INSTRUCTION: 
Analyze the gap between what the student has and what Indian recruiters expect.
YOU MUST check the ENTIRE parsed resume (projects, experience, summary) AND the raw text. 
If a skill (like "DSA", "Java", "Python") is mentioned ANYWHERE in the resume, you MUST consider it as a skill the student possesses. 
NEVER flag a skill as missing if it appears anywhere in the candidate's document.

Return this EXACT JSON structure:
{{
    "student_has": ["<skills the student already possesses that are relevant>"],
    "missing_critical": ["<MUST-HAVE skills they are missing — high priority>"],
    "missing_recommended": ["<GOOD-TO-HAVE skills — medium priority>"],
    "missing_nice_to_have": ["<BONUS skills — low priority>"],
    "extra_skills": ["<skills they have that aren't typically required but add value>"],
    "priority_actions": [
        {{
            "skill": "<skill name>",
            "priority": "<high | medium | low>",
            "reason": "<why this matters for Indian placements>",
            "resource_hint": "<brief suggestion: e.g., 'Practice on LeetCode', 'Take NPTEL course'>"
        }}
    ],
    "overall_readiness": "<one of: Not Ready | Needs Work | Almost Ready | Placement Ready>",
    "summary": "<2-3 sentence realistic assessment>"
}}

RULES:
1. Be SPECIFIC to Indian campus placements.
2. DSA and OOP are NON-NEGOTIABLE for any software role. If missing, they must be "high" priority.
3. Be realistic — a student doesn't need 20 skills. Focus on the most impactful gaps.
4. ABSOLUTE ACCURACY: Do not hallucinate skills they don't have, and do NOT say they are missing a skill they actually have. Check the project descriptions carefully!
"""


def _get_role_skills(target_role: str) -> list[str]:
    """Match target role to known skill demands."""
    role_lower = target_role.lower()
    for key, skills in PLACEMENT_DEMANDS.items():
        if key.replace("_", " ") in role_lower or role_lower in key.replace("_", " "):
            return skills
    # Default to software engineer
    return PLACEMENT_DEMANDS["software_engineer"]


def run_skill_gap(state: GraphState) -> dict:
    """Agent 3: Identify skill gaps for Indian campus placements."""
    parsed_json = state.get("parsed_json")

    if not parsed_json:
        return {
            "skill_gaps": None,
            "errors": state.get("errors", []) + ["Agent 3: No parsed_json available"],
        }

    try:
        import json

        student_skills = parsed_json.get("all_skills_flat", [])
        target_role = state.get("target_role", "Software Engineer")
        role_skills = _get_role_skills(target_role)

        prompt = SKILL_GAP_PROMPT.format(
            target_role=target_role,
            parsed_resume=json.dumps(parsed_json, indent=2)[:6000],
            raw_text=state.get("raw_text", "")[:4000],
            core_skills=json.dumps(PLACEMENT_DEMANDS["common_core"]),
            role_skills=json.dumps(role_skills),
        )

        result = call_llm_json(prompt, temperature=0.2)

        missing_count = len(result.get("missing_critical", []))
        readiness = result.get("overall_readiness", "Unknown")
        print(f"✅ Agent 3 (Skill Gap): {missing_count} critical gaps, Readiness: {readiness}")

        return {"skill_gaps": result}

    except Exception as e:
        print(f"❌ Agent 3 (Skill Gap) failed: {e}")
        return {
            "skill_gaps": None,
            "errors": state.get("errors", []) + [f"Agent 3: {str(e)}"],
        }

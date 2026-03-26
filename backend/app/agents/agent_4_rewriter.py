# app/agents/agent_4_rewriter.py
# Agent 4: Resume Rewrite Agent — Improves bullet points with action verbs, zero hallucination

from app.agents.graph_state import GraphState
from app.agents.gemini_client import call_llm_json


REWRITER_PROMPT = """You are an expert resume rewriter for Indian engineering students preparing for campus placements.

Rewrite the resume to be more impactful for ATS systems and recruiters.

ORIGINAL PARSED RESUME:
\"\"\"
{parsed_json}
\"\"\"

TARGET ROLE: {target_role}

ATS FEEDBACK:
\"\"\"
{ats_feedback}
\"\"\"

{supervisor_feedback}

REWRITING RULES — FOLLOW THESE STRICTLY:
1. Use STRONG action verbs: "Engineered", "Spearheaded", "Architected", "Optimized", "Implemented", "Developed", "Designed", "Deployed"
2. ADD METRICS where possible: "Reduced load time by 40%", "Serving 500+ users", "Processed 10K+ records"
3. NEVER hallucinate new technologies. Only use technologies that appear in the original resume.
4. NEVER invent fake internships, companies, or experiences.
5. NEVER add skills that aren't in the original. You may only REPHRASE existing content.
6. LENGTH CONSTRAINT: Keep project descriptions concise — MAX 2-3 bullet points each. Bullet points must be short (under 120 characters each). This resume MUST fit on ONE printed page.
7. LENGTH CONSTRAINT: Limit experience strictly to the top 3-4 most impactful achievements using the STAR format. Eliminate fluff.

Return this EXACT JSON structure:
{{
    "name": "<same as original>",
    "email": "<same as original>",
    "phone": "<same as original>",
    "summary": "<rewritten professional summary — 2-3 impactful sentences>",
    "education": <same as original — do NOT change education details>,
    "skills": <same as original — do NOT add new skills>,
    "projects": [
        {{
            "title": "<same project title>",
            "description": "<rewritten: 1 impactful sentence>",
            "bullets": ["<rewritten bullet 1 with action verb + metric>", "<bullet 2>", "<bullet 3>"],
            "tech_stack": ["<same tech stack — do NOT add new tech>"]
        }}
    ],
    "experience": [
        {{
            "role": "<same role>",
            "company": "<same company>",
            "duration": "<same duration>",
            "bullets": ["<rewritten with STAR format + action verbs>"]
        }}
    ],
    "certifications": <same as original>,
    "achievements": <same as original>,
    "changes_made": [
        "<list each specific change you made, e.g., 'Added metric to Project 1 bullet', 'Changed verb in Experience 1'>"
    ]
}}
"""


def run_rewriter(state: GraphState) -> dict:
    """Agent 4: Rewrite resume with action verbs and metrics, no hallucination."""
    parsed_json = state.get("parsed_json")
    ats_score = state.get("ats_score")

    if not parsed_json:
        return {
            "improved_resume": None,
            "errors": state.get("errors", []) + ["Agent 4: No parsed_json available"],
        }

    try:
        import json

        # Include supervisor feedback if this is a retry
        supervisor_feedback = ""
        if state.get("supervisor_feedback"):
            supervisor_feedback = (
                f"⚠️ SUPERVISOR FEEDBACK (FIX THESE ISSUES):\n"
                f"{state['supervisor_feedback']}\n"
                f"You MUST address ALL the issues listed above."
            )

        ats_feedback = ""
        if ats_score:
            ats_feedback = json.dumps(ats_score.get("breakdown", {}), indent=2)[:2000]

        prompt = REWRITER_PROMPT.format(
            parsed_json=json.dumps(parsed_json, indent=2)[:5000],
            target_role=state.get("target_role", "Software Engineer"),
            ats_feedback=ats_feedback or "No ATS feedback available",
            supervisor_feedback=supervisor_feedback,
        )

        result = call_llm_json(prompt, temperature=0.3)

        changes = result.get("changes_made", [])
        print(f"✅ Agent 4 (Rewriter): Made {len(changes)} changes")

        return {"improved_resume": result}

    except Exception as e:
        print(f"❌ Agent 4 (Rewriter) failed: {e}")
        return {
            "improved_resume": None,
            "errors": state.get("errors", []) + [f"Agent 4: {str(e)}"],
        }

# app/agents/agent_2_ats.py
# Agent 2: ATS Scoring Agent — Scores resume like a strict Indian IT recruiter
# Includes whitespace/formatting and page count analysis

from app.agents.graph_state import GraphState
from app.agents.gemini_client import call_llm_json


ATS_PROMPT = """You are a ruthless ATS (Applicant Tracking System) used by top Indian IT recruiters at companies like TCS, Infosys, Wipro, and product companies like Google, Microsoft, Flipkart.

Analyze the following parsed resume JSON and score it out of 100 based on these EXACT categories:

PARSED RESUME:
\"\"\"
{parsed_json}
\"\"\"

TARGET ROLE: {target_role}

RESUME METADATA:
- Page count: {page_count} page(s)
- Character count: {char_count}

Score the resume on these 7 categories. Be STRICT and REALISTIC — most fresh graduates score 40-65.

Return this EXACT JSON structure:
{{
    "total_score": <0-100 integer>,
    "breakdown": {{
        "formatting": {{
            "score": <0-15>,
            "max": 15,
            "feedback": "<Check: Is it 1 page? Are sections clearly separated? Is whitespace even and minimal? Are margins consistent? Penalize heavily if >1 page for freshers.>"
        }},
        "whitespace_and_layout": {{
            "score": <0-10>,
            "max": 10,
            "feedback": "<Check: Is whitespace evenly distributed? Are there excessive blank areas? Is content density optimal? A good resume uses space efficiently with no large gaps or cramped sections.>"
        }},
        "keywords": {{
            "score": <0-20>,
            "max": 20,
            "feedback": "<are relevant keywords present for the target role?>"
        }},
        "action_verbs": {{
            "score": <0-15>,
            "max": 15,
            "feedback": "<does the resume use strong action verbs like Developed, Engineered, Spearheaded?>"
        }},
        "quantified_metrics": {{
            "score": <0-15>,
            "max": 15,
            "feedback": "<are achievements quantified with numbers? e.g., Improved latency by 30%>"
        }},
        "section_completeness": {{
            "score": <0-15>,
            "max": 15,
            "feedback": "<are all key sections present: Education, Skills, Projects, Experience?>"
        }},
        "overall_coherence": {{
            "score": <0-10>,
            "max": 10,
            "feedback": "<is the resume well-organized and easy to scan?>"
        }}
    }},
    "page_check": {{
        "pages": {page_count},
        "passed": <true if 1 page, false otherwise>,
        "message": "<If >1 page: 'Resume should be exactly 1 page for freshers/early career. Currently {page_count} pages — cut less relevant content.' If 1 page: 'Good — resume fits on 1 page.'>"
    }},
    "whitespace_analysis": {{
        "even_distribution": <true/false>,
        "excessive_gaps": <true/false>,
        "feedback": "<2 sentences about whitespace usage: Are margins consistent? Is content density optimal? Any large blank areas?>"
    }},
    "strengths": ["<top 3 resume strengths>"],
    "weaknesses": ["<top 3 resume weaknesses>"],
    "reasoning": "<2-3 sentence overall assessment as an Indian recruiter>"
}}

RULES:
1. Be REALISTIC. A fresher with only college projects should score 35-55.
2. A strong candidate with internships, good projects, and quantified results scores 60-80.
3. Only exceptional candidates score 80+.
4. PENALIZE HEAVILY if resume is more than 1 page for freshers.
5. PENALIZE if whitespace is uneven — good resumes have consistent spacing between sections.
6. Indian recruiters especially value: DSA skills, project diversity, and relevant tech stacks.
"""


def run_ats_scorer(state: GraphState) -> dict:
    """Agent 2: Score the parsed resume like an ATS system."""
    parsed_json = state.get("parsed_json")

    if not parsed_json:
        return {
            "ats_score": None,
            "errors": state.get("errors", []) + ["Agent 2: No parsed_json available"],
        }

    try:
        import json
        prompt = ATS_PROMPT.format(
            parsed_json=json.dumps(parsed_json, indent=2)[:6000],
            target_role=state.get("target_role", "Software Engineer"),
            page_count=state.get("page_count", 1),
            char_count=len(state.get("raw_text", "")),
        )
        result = call_llm_json(prompt, temperature=0.2)

        total = result.get("total_score", 0)
        print(f"✅ Agent 2 (ATS Scorer): Score = {total}/100")

        return {"ats_score": result}

    except Exception as e:
        print(f"❌ Agent 2 (ATS Scorer) failed: {e}")
        return {
            "ats_score": None,
            "errors": state.get("errors", []) + [f"Agent 2: {str(e)}"],
        }

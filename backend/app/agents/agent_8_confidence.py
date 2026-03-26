# app/agents/agent_8_confidence.py
# Agent 8: Confidence Score Agent — Calculates overall placement readiness

from app.agents.graph_state import GraphState
from app.agents.gemini_client import call_llm_json


CONFIDENCE_PROMPT = """You are a campus placement readiness evaluator for Indian engineering colleges.

Based on the candidate's complete analysis below, calculate their OVERALL placement readiness.

ATS SCORE:
\"\"\"
{ats_score}
\"\"\"

SKILL GAP ANALYSIS:
\"\"\"
{skill_gaps}
\"\"\"

INTERVIEW READINESS (based on generated Q&A):
\"\"\"
{interview_summary}
\"\"\"

TARGET ROLE: {target_role}

Calculate the placement confidence score and provide a realistic assessment.

Return this EXACT JSON:
{{
    "confidence_percentage": <0-100 integer>,
    "tier_readiness": {{
        "service_based": {{
            "ready": <true/false>,
            "companies": ["<e.g., TCS, Infosys, Wipro, Cognizant>"],
            "notes": "<why ready/not ready>"
        }},
        "mid_tier_product": {{
            "ready": <true/false>,
            "companies": ["<e.g., Zoho, Mindtree, LTI, Mphasis>"],
            "notes": "<why ready/not ready>"
        }},
        "top_product": {{
            "ready": <true/false>,
            "companies": ["<e.g., Google, Microsoft, Amazon, Flipkart>"],
            "notes": "<why ready/not ready>"
        }}
    }},
    "summary": "<2-3 sentence realistic placement prediction — e.g., 'Ready for Service-Based companies. Needs to improve DSA skills for Product-Based roles. Strong project work gives an edge in technical rounds.'>",
    "action_items": [
        "<top 3 most impactful things to do before placement season>"
    ],
    "estimated_package_range": "<realistic Indian campus placement range — e.g., '4-7 LPA for Service-Based, 12-18 LPA if cracks Product-Based'>"
}}

RULES:
1. Be BRUTALLY honest but constructive
2. ATS score below 40 = not ready for top companies
3. Missing DSA = instant disqualification from product-based companies
4. Good projects can compensate for lower GPA in many companies
5. Use realistic Indian salary ranges (LPA = Lakh Per Annum)
"""


def run_confidence(state: GraphState) -> dict:
    """Agent 8: Calculate overall placement readiness and confidence score."""
    ats_score = state.get("ats_score")
    skill_gaps = state.get("skill_gaps")
    interview_qna = state.get("interview_qna")

    try:
        import json

        # Summarize interview readiness
        interview_summary = "Not available"
        if interview_qna:
            q_count = len(interview_qna.get("questions", []))
            difficulty = interview_qna.get("estimated_difficulty", "unknown")
            interview_summary = f"{q_count} questions generated, estimated difficulty: {difficulty}"

        prompt = CONFIDENCE_PROMPT.format(
            ats_score=json.dumps(ats_score, indent=2)[:3000] if ats_score else "Not available",
            skill_gaps=json.dumps(skill_gaps, indent=2)[:3000] if skill_gaps else "Not available",
            interview_summary=interview_summary,
            target_role=state.get("target_role", "Software Engineer"),
        )

        result = call_llm_json(prompt, temperature=0.2)

        confidence = result.get("confidence_percentage", 0)
        summary = result.get("summary", "")
        print(f"✅ Agent 8 (Confidence): {confidence}% — {summary[:100]}")

        return {"confidence_score": result}

    except Exception as e:
        print(f"❌ Agent 8 (Confidence) failed: {e}")
        return {
            "confidence_score": None,
            "errors": state.get("errors", []) + [f"Agent 8: {str(e)}"],
        }

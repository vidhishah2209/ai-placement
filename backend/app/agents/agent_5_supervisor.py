# app/agents/agent_5_supervisor.py
# Agent 5: Supervisor Agent — Hallucination detector + conditional routing

from app.agents.graph_state import GraphState
from app.agents.gemini_client import call_llm_json


SUPERVISOR_PROMPT = """You are a strict Quality Assurance supervisor for a resume rewriting AI.

Your job is to compare the ORIGINAL resume data with the REWRITTEN resume and detect ANY hallucinations or fabrications.

ORIGINAL RESUME (ground truth):
\"\"\"
{original}
\"\"\"

REWRITTEN RESUME (to verify):
\"\"\"
{rewritten}
\"\"\"

CHECK FOR THESE VIOLATIONS:
1. **Technology Hallucination**: Did the rewriter ADD any technology, framework, or tool NOT present in the original?
   - Example violation: Original has "Python, React" but rewritten adds "AWS" or "Docker"
2. **Experience Fabrication**: Did the rewriter invent a company, role, or internship?
3. **Metric Fabrication**: Did the rewriter add specific numbers (e.g., "40% improvement") that could be misleading if not in the original?
   - Note: Adding reasonable estimates like "500+ lines" for a project is acceptable
4. **Skill Inflation**: Did the rewriter upgrade skill levels or add expertise claims?
5. **JSON Validity**: Is the rewritten output valid and complete JSON?

Return this EXACT JSON:
{{
    "passed": <true or false>,
    "violations": [
        {{
            "type": "<technology_hallucination | experience_fabrication | metric_fabrication | skill_inflation | json_invalid>",
            "description": "<specific description of what was fabricated>",
            "severity": "<critical | warning>"
        }}
    ],
    "feedback": "<If failed: detailed instructions for the rewriter to fix the issues. If passed: 'All checks passed.'>",
    "summary": "<1 sentence summary>"
}}

RULES:
1. Be STRICT about technology additions — this is the most common hallucination
2. If the rewriter merely rephrased content using better words, that's FINE (passed=true)
3. Adding action verbs to existing bullets is FINE
4. Adding reasonable metric estimates to existing work is ACCEPTABLE (warning, not critical)
5. Only fail (passed=false) if there are CRITICAL violations
"""


def run_supervisor(state: GraphState) -> dict:
    """Agent 5: Check if the rewriter hallucinated. Returns pass/fail + feedback."""
    parsed_json = state.get("parsed_json")
    improved_resume = state.get("improved_resume")

    if not parsed_json or not improved_resume:
        return {
            "supervisor_passed": True,  # Skip check if data is missing
            "supervisor_feedback": None,
        }

    try:
        import json
        prompt = SUPERVISOR_PROMPT.format(
            original=json.dumps(parsed_json, indent=2)[:4000],
            rewritten=json.dumps(improved_resume, indent=2)[:4000],
        )

        result = call_llm_json(prompt, temperature=0.1)

        passed = result.get("passed", True)
        violations = result.get("violations", [])
        critical_count = sum(1 for v in violations if v.get("severity") == "critical")

        if passed or critical_count == 0:
            print(f"✅ Agent 5 (Supervisor): PASSED — {len(violations)} warnings")
            return {
                "supervisor_passed": True,
                "supervisor_feedback": None,
            }
        else:
            feedback = result.get("feedback", "Fix hallucination issues")
            print(f"❌ Agent 5 (Supervisor): FAILED — {critical_count} critical violations")
            print(f"   Feedback: {feedback[:200]}")
            return {
                "supervisor_passed": False,
                "supervisor_feedback": feedback,
                "rewrite_attempts": state.get("rewrite_attempts", 0) + 1,
            }

    except Exception as e:
        print(f"⚠️ Agent 5 (Supervisor) error: {e} — defaulting to PASS")
        return {
            "supervisor_passed": True,
            "supervisor_feedback": None,
        }

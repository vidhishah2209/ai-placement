# app/agents/agent_7_interview.py
# Agent 7: Interview Agent — Generates both HR and Technical questions for Indian campus placements

from app.agents.graph_state import GraphState
from app.agents.gemini_client import call_llm_json


INTERVIEW_PROMPT = """You are a panel of experienced interviewers conducting campus placement interviews at a top Indian engineering college.

The panel includes:
- A Senior Technical Interviewer (tests coding, DSA, system design, projects)
- An HR Manager (tests communication, teamwork, cultural fit, situational judgment)

Based on the candidate's IMPROVED RESUME below, generate HIGHLY SPECIFIC interview questions that would be asked during a real Indian campus placement drive.

CANDIDATE'S RESUME:
\"\"\"
{resume}
\"\"\"

TARGET ROLE: {target_role}

Generate questions in these 5 categories:

1. **Technical - Project Deep Dive** (4 questions): Ask detailed questions about their specific projects.
   - Ask about architecture decisions, challenges faced, and what they would do differently.
   - Example: "In your e-commerce project, how did you handle concurrent cart updates when multiple users modify inventory?"

2. **Technical - DSA & CS Fundamentals** (4 questions): Ask DSA, OOP, DBMS, OS questions relevant to Indian placements.
   - Include questions similar to those asked at TCS, Infosys, Wipro, Cognizant, and product company placement drives.
   - Example: "Explain the difference between HashMap and TreeMap. When would you use each in your Task Management project?"

3. **HR - Behavioral & Personality** (4 questions): Standard HR questions asked at Indian campus placements.
   - Cover: Tell me about yourself, strengths/weaknesses, teamwork, leadership, failure handling, why this company.
   - Make questions reference the candidate's ACTUAL achievements, clubs, or roles from their resume.
   - Example: "As Technical Lead of the Coding Club, how did you motivate members who were struggling with competitive programming?"

4. **HR - Situational Judgment** (2 questions): Hypothetical workplace scenarios common in Indian IT companies.
   - Example: "Your team lead assigns you a technology you've never worked with, and the deadline is in 2 weeks. How do you approach this?"

5. **Technical - System Design / Scenario** (2 questions): Practical problem-solving for the target role.
   - Example: "If you had to design the backend for a food delivery app like Zomato, what database schema would you use?"

Return this EXACT JSON:
{{
    "questions": [
        {{
            "id": <1-16>,
            "category": "<technical_project | technical_fundamentals | hr_behavioral | hr_situational | technical_design>",
            "difficulty": "<easy | medium | hard>",
            "question": "<the interview question>",
            "context": "<why this question is relevant — reference a specific resume detail>",
            "model_answer": {{
                "intro": "<opening 1 sentence using STAR format if applicable>",
                "core": "<main answer — 4-5 sentences, specific and detailed>",
                "example": "<concrete example from their resume or a general best practice>",
                "conclusion": "<closing impact statement>"
            }},
            "follow_up": "<a likely follow-up question the interviewer would ask>"
        }}
    ],
    "interview_tips": [
        "<5 specific tips for this candidate — cover both technical and HR preparation>"
    ],
    "estimated_difficulty": "<easy | moderate | challenging>"
}}

IMPORTANT RULES:
1. Questions MUST reference the candidate's ACTUAL projects, skills, and experience from the resume
2. HR questions should be the kind asked in TCS, Infosys, Wipro, Cognizant, HCL campus drives
3. Include the classic "Tell me about yourself" as the first HR question — model answer should be a 60-second elevator pitch
4. Include "Why should we hire you?" as one of the HR questions
5. Technical questions should match Indian campus placement difficulty — not FAANG L5 level
6. Model answers should use STAR format (Situation, Task, Action, Result) for HR questions
7. Tips should cover: dress code, body language, common mistakes, and preparation strategy
"""


def run_interview(state: GraphState) -> dict:
    """Agent 7: Generate interview questions based on the candidate's resume."""
    improved_resume = state.get("improved_resume")
    # Fall back to parsed_json if no improved resume
    resume = improved_resume or state.get("parsed_json")

    if not resume:
        return {
            "interview_qna": None,
            "errors": state.get("errors", []) + ["Agent 7: No resume data available"],
        }

    try:
        import json
        prompt = INTERVIEW_PROMPT.format(
            resume=json.dumps(resume, indent=2)[:5000],
            target_role=state.get("target_role", "Software Engineer"),
        )

        result = call_llm_json(prompt, temperature=0.4)

        q_count = len(result.get("questions", []))
        print(f"✅ Agent 7 (Interview): Generated {q_count} questions")

        return {"interview_qna": result}

    except Exception as e:
        print(f"❌ Agent 7 (Interview) failed: {e}")
        return {
            "interview_qna": None,
            "errors": state.get("errors", []) + [f"Agent 7: {str(e)}"],
        }

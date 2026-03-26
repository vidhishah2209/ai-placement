# app/agents/graph_state.py
# Master state shared by all agents in the LangGraph pipeline

from typing import TypedDict


class GraphState(TypedDict):
    """
    The single source of truth flowing through the LangGraph pipeline.
    Every agent reads from and writes to this dictionary.
    """

    # ── Input ──
    raw_text: str                    # Raw text extracted from the PDF
    target_role: str                 # e.g. "Software Engineer", "Data Analyst"
    page_count: int                  # Number of pages in the uploaded PDF

    # ── Agent 1: Parser output ──
    parsed_json: dict | None         # Structured resume data (name, skills, projects, etc.)

    # ── Agent 2: ATS Scorer output ──
    ats_score: dict | None           # { score: int, breakdown: {...}, reasoning: str }

    # ── Agent 3: Skill Gap output ──
    skill_gaps: dict | None          # { missing: [...], priorities: {...} }

    # ── Agent 4: Resume Rewriter output ──
    improved_resume: dict | None     # Rewritten resume sections

    # ── Agent 5: Supervisor output ──
    supervisor_feedback: str | None  # Feedback if hallucination detected
    supervisor_passed: bool          # True if rewrite is valid
    rewrite_attempts: int            # Counter for rewrite loops (max 2)

    # ── Agent 7: Interview output ──
    interview_qna: dict | None       # { questions: [...] }

    # ── Agent 8: Confidence Score output ──
    confidence_score: dict | None    # { score: int, summary: str }

    # ── Agent 6: DB Saver output ──
    db_saved: bool                   # True after successful DB save

    # ── Metadata ──
    user_id: str | None
    resume_id: str | None
    errors: list[str]                # Accumulated error messages

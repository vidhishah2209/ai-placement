# app/agents/pipeline.py
# LangGraph StateGraph — wires all 8 agents with conditional routing

from langgraph.graph import StateGraph, END

from app.agents.graph_state import GraphState
from app.agents.agent_1_parser import run_parser
from app.agents.agent_2_ats import run_ats_scorer
from app.agents.agent_3_skill_gap import run_skill_gap
from app.agents.agent_4_rewriter import run_rewriter
from app.agents.agent_5_supervisor import run_supervisor
from app.agents.agent_6_db_saver import run_db_saver
from app.agents.agent_7_interview import run_interview
from app.agents.agent_8_confidence import run_confidence


# ═══════════════════════════════════════════════════
# CONDITIONAL EDGE: Supervisor routing
# ═══════════════════════════════════════════════════

MAX_REWRITE_ATTEMPTS = 2


def supervisor_router(state: GraphState) -> str:
    """
    After Agent 5 (Supervisor), decide next step:
    - If passed → continue to db_saver
    - If failed and retries remain → loop back to rewriter
    - If failed and max retries hit → continue anyway (save what we have)
    """
    if state.get("supervisor_passed", True):
        return "db_saver"

    attempts = state.get("rewrite_attempts", 0)
    if attempts < MAX_REWRITE_ATTEMPTS:
        print(f"🔄 Supervisor: Looping back to rewriter (attempt {attempts + 1}/{MAX_REWRITE_ATTEMPTS})")
        return "rewriter"
    else:
        print(f"⚠️ Supervisor: Max retries reached, proceeding with current version")
        return "db_saver"


# ═══════════════════════════════════════════════════
# BUILD THE GRAPH
# ═══════════════════════════════════════════════════

def build_pipeline() -> StateGraph:
    """
    Build the LangGraph pipeline:

    START → parser → ats_scorer → skill_gap → rewriter
      → supervisor → [conditional]
          if passed → db_saver → interview → confidence → END
          if failed (retry) → rewriter → supervisor → ...
          if max retries → db_saver → interview → confidence → END
    """
    graph = StateGraph(GraphState)

    # Add all agent nodes
    graph.add_node("parser", run_parser)
    graph.add_node("ats_scorer", run_ats_scorer)
    graph.add_node("skill_gap", run_skill_gap)
    graph.add_node("rewriter", run_rewriter)
    graph.add_node("supervisor", run_supervisor)
    graph.add_node("db_saver", run_db_saver)
    graph.add_node("interview", run_interview)
    graph.add_node("confidence", run_confidence)

    # Wire the edges (sequential flow)
    graph.set_entry_point("parser")
    graph.add_edge("parser", "ats_scorer")
    graph.add_edge("ats_scorer", "skill_gap")
    graph.add_edge("skill_gap", "rewriter")
    graph.add_edge("rewriter", "supervisor")

    # Conditional edge: Supervisor decides next step
    graph.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "db_saver": "db_saver",
            "rewriter": "rewriter",
        },
    )

    # After DB save → interview → confidence → END
    graph.add_edge("db_saver", "interview")
    graph.add_edge("interview", "confidence")
    graph.add_edge("confidence", END)

    return graph


# ═══════════════════════════════════════════════════
# RUN THE PIPELINE
# ═══════════════════════════════════════════════════

# Compile once at module level
_compiled_pipeline = build_pipeline().compile()


def run_pipeline(raw_text: str, target_role: str = "Software Engineer", user_id: str = None, page_count: int = 1) -> dict:
    """
    Execute the full 8-agent pipeline.

    Args:
        raw_text: Raw text extracted from PDF resume
        target_role: Target job role (e.g., "Software Engineer")
        user_id: UUID of the user (for DB saving)
        page_count: Number of pages in the uploaded PDF

    Returns:
        Final GraphState dict with all agent outputs
    """
    print("\n" + "=" * 60)
    print("🚀 STARTING AI PLACEMENT CELL PIPELINE")
    print(f"   Target Role: {target_role}")
    print(f"   Text Length: {len(raw_text)} chars")
    print(f"   Page Count: {page_count}")
    print("=" * 60 + "\n")

    initial_state: GraphState = {
        "raw_text": raw_text,
        "target_role": target_role,
        "page_count": page_count,
        "parsed_json": None,
        "ats_score": None,
        "skill_gaps": None,
        "improved_resume": None,
        "supervisor_feedback": None,
        "supervisor_passed": False,
        "rewrite_attempts": 0,
        "interview_qna": None,
        "confidence_score": None,
        "db_saved": False,
        "user_id": user_id,
        "resume_id": None,
        "errors": [],
    }

    # Run the compiled graph
    result = _compiled_pipeline.invoke(initial_state)

    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETE")
    ats = result.get('ats_score') or {}
    conf = result.get('confidence_score') or {}
    print(f"   ATS Score: {ats.get('total_score', 'N/A')}")
    print(f"   Supervisor: {'PASSED' if result.get('supervisor_passed') else 'FAILED'}")
    print(f"   DB Saved: {result.get('db_saved')}")
    print(f"   Confidence: {conf.get('confidence_percentage', 'N/A')}%")
    print(f"   Errors: {len(result.get('errors', []))}")
    print("=" * 60 + "\n")

    return dict(result)

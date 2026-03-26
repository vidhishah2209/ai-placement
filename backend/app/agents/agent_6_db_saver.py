# app/agents/agent_6_db_saver.py
# Agent 6: Database Saver Agent — Pure Python, saves all results to Neon PostgreSQL

import uuid
import json
import asyncio
from app.agents.graph_state import GraphState
from app.database import AsyncSessionLocal
from app.models import Resume, ResumeAnalytics, InterviewPrep


async def _save_to_db(state: GraphState) -> dict:
    """Async helper: save all pipeline results to the Neon database."""
    user_id = state.get("user_id")
    if not user_id:
        return {"db_saved": False, "errors": state.get("errors", []) + ["Agent 6: No user_id"]}

    resume_id = str(uuid.uuid4())

    try:
        async with AsyncSessionLocal() as session:
            # 1. Save Resume (original + improved)
            resume = Resume(
                id=resume_id,
                user_id=user_id,
                raw_text=state.get("raw_text", "")[:50000],  # Cap at 50K chars
                original_parsed_data=state.get("parsed_json"),
                improved_resume_data=state.get("improved_resume"),
            )
            session.add(resume)

            # 2. Save Analytics (ATS score + skill gaps)
            if state.get("ats_score") or state.get("skill_gaps"):
                ats_data = state.get("ats_score", {})
                analytics = ResumeAnalytics(
                    id=str(uuid.uuid4()),
                    resume_id=resume_id,
                    ats_score=ats_data.get("total_score", 0) if ats_data else 0,
                    ats_breakdown=ats_data,
                    skill_gaps=state.get("skill_gaps"),
                )
                session.add(analytics)

            # 3. Save Interview Prep
            if state.get("interview_qna"):
                interview = InterviewPrep(
                    id=str(uuid.uuid4()),
                    resume_id=resume_id,
                    questions_data=state.get("interview_qna"),
                )
                session.add(interview)

            await session.commit()
            print(f"✅ Agent 6 (DB Saver): Saved to Neon — resume_id={resume_id}")

            return {
                "db_saved": True,
                "resume_id": resume_id,
            }

    except Exception as e:
        print(f"❌ Agent 6 (DB Saver) failed: {e}")
        return {
            "db_saved": False,
            "resume_id": resume_id,
            "errors": state.get("errors", []) + [f"Agent 6: {str(e)}"],
        }


def run_db_saver(state: GraphState) -> dict:
    """Agent 6: Save pipeline results to Neon DB. Runs async internally."""
    try:
        # Run async save in the current event loop or create one
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're inside an async context (FastAPI) — use a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = pool.submit(asyncio.run, _save_to_db(state)).result()
            return result
        else:
            return asyncio.run(_save_to_db(state))
    except RuntimeError:
        # No event loop — create one
        return asyncio.run(_save_to_db(state))

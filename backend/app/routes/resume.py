from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Resume
from app.scoring.engine import calculate_final_score
from app.agents.pipeline import run_pipeline
import shutil
import os
import uuid
import json
import PyPDF2

router = APIRouter()


def extract_text_from_pdf(file_path):
    text = ""
    page_count = 0
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        page_count = len(reader.pages)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text, page_count


@router.post("/upload-resume/")
async def upload_resume(
    user_id: str = Form(...),
    job_description: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Save file to uploads folder
    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text from PDF
    extracted_text, _ = extract_text_from_pdf(file_path)

    if not extracted_text.strip():
        return {"error": "Could not extract text from PDF. Is it a scanned image?"}

    # Run scoring engine (Gemini primary, fallback if unavailable)
    scoring_result = calculate_final_score(extracted_text, job_description)

    # Save to DB (with error handling so scoring still returns even if DB fails)
    resume_id = str(uuid.uuid4())
    try:
        clean_scoring = json.loads(json.dumps(scoring_result))
        new_resume = Resume(
            id=resume_id,
            user_id=user_id,
            raw_text=extracted_text,
            original_parsed_data=clean_scoring,
        )
        db.add(new_resume)
        await db.commit()
        await db.refresh(new_resume)
    except Exception as e:
        print(f"⚠️ DB save failed (scoring still returned): {e}")
        await db.rollback()

    return {
        "message": "Resume analyzed successfully",
        "resume_id": resume_id,
        "filename": file.filename,
        "text_preview": extracted_text[:500],
        "scoring": scoring_result,
    }


# ═══════════════════════════════════════════════════════════
# NEW: Full LangGraph Pipeline Endpoint
# ═══════════════════════════════════════════════════════════

@router.post("/analyze-resume/")
async def analyze_resume(
    user_id: str = Form(...),
    target_role: str = Form(default="Software Engineer"),
    file: UploadFile = File(...),
):
    """
    Run the full 8-agent LangGraph pipeline on an uploaded resume PDF.

    Returns: parsed resume, ATS score, skill gaps, improved resume,
    interview Q&A, and placement confidence score.
    """
    # Save file
    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text and page count
    extracted_text, page_count = extract_text_from_pdf(file_path)

    if not extracted_text.strip():
        return {"error": "Could not extract text from PDF. Is it a scanned image?"}

    # Run the full LangGraph pipeline (Agents 1-8)
    result = run_pipeline(
        raw_text=extracted_text,
        target_role=target_role,
        user_id=user_id,
        page_count=page_count,
    )

    # Build response (exclude raw_text to keep response lean)
    return {
        "message": "Full pipeline analysis complete",
        "resume_id": result.get("resume_id"),
        "filename": file.filename,
        "text_preview": extracted_text[:500],
        "parsed_resume": result.get("parsed_json"),
        "ats_score": result.get("ats_score"),
        "skill_gaps": result.get("skill_gaps"),
        "improved_resume": result.get("improved_resume"),
        "supervisor_passed": result.get("supervisor_passed"),
        "interview_qna": result.get("interview_qna"),
        "confidence_score": result.get("confidence_score"),
        "db_saved": result.get("db_saved"),
        "errors": result.get("errors", []),
    }

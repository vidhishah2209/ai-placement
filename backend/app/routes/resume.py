from fastapi import APIRouter, UploadFile, File, Form, Depends, BackgroundTasks
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

# In-memory store for background jobs (Use Redis in a real distributed production env)
job_store = {}

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
# Full LangGraph Pipeline (Background Polling Architecture)
# ═══════════════════════════════════════════════════════════

def run_pipeline_background(job_id: str, raw_text: str, target_role: str, user_id: str, page_count: int, filename: str):
    try:
        result = run_pipeline(
            raw_text=raw_text,
            target_role=target_role,
            user_id=user_id,
            page_count=page_count,
        )
        
        job_store[job_id] = {
            "status": "completed",
            "data": {
                "message": "Full pipeline analysis complete",
                "resume_id": result.get("resume_id"),
                "filename": filename,
                "text_preview": raw_text[:500],
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
        }
    except Exception as e:
        job_store[job_id] = {
            "status": "error",
            "message": str(e)
        }

@router.post("/analyze-resume/")
async def analyze_resume(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    target_role: str = Form(default="Software Engineer"),
    file: UploadFile = File(...),
):
    """
    Kicks off the full 8-agent LangGraph pipeline in the background.
    Returns a job_id instantly to prevent Render 60s proxy timeouts.
    """
    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text, page_count = extract_text_from_pdf(file_path)

    if not extracted_text.strip():
        return {"error": "Could not extract text from PDF. Is it a scanned image?"}

    job_id = str(uuid.uuid4())
    job_store[job_id] = {"status": "processing"}

    background_tasks.add_task(
        run_pipeline_background,
        job_id=job_id,
        raw_text=extracted_text,
        target_role=target_role,
        user_id=user_id,
        page_count=page_count,
        filename=file.filename
    )

    return {"job_id": job_id, "status": "processing"}

@router.get("/analyze-status/{job_id}")
async def get_analyze_status(job_id: str):
    """
    Check the status of a background job.
    Returns the final dataset if status=="completed".
    """
    job = job_store.get(job_id)
    if not job:
        return {"status": "error", "message": "Unknown Job ID"}
    return job

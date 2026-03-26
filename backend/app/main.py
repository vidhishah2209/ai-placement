from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.routes.user import router as user_router
from app.routes.resume import router as resume_router
from app.routes.chat import router as chat_router

app = FastAPI()

# CORS — Allow React frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://ai-placement-cell.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(user_router)
app.include_router(resume_router)
app.include_router(chat_router)

@app.get("/")
async def root():
    return {"message": "Backend running successfully"}

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created successfully!")
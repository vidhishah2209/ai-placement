# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Toggle this to False when you want to connect to Neon again
USE_LOCAL_DB = False

if USE_LOCAL_DB:
    DATABASE_URL = "sqlite+aiosqlite:///./local_dev.db"
else:
    DATABASE_URL = os.getenv("DATABASE_URL")

# Groq API (primary LLM provider)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()

# Gemini API keys (fallback, rotate to avoid rate limits)
GEMINI_API_KEYS = [
    k.strip().lstrip("-") for k in [
        os.getenv("GEMINI_API_KEY", ""),
        os.getenv("GEMINI_API_KEY_1", ""),
        os.getenv("GEMINI_API_KEY_2", ""),
        os.getenv("GEMINI_API_KEY_3", ""),
        os.getenv("GEMINI_API_KEY_4", ""),
    ] if k and k.strip()
]

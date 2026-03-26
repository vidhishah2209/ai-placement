# app/agents/gemini_client.py
# Unified LLM client: Groq (primary) + Gemini (fallback)
# Groq uses openai/gpt-oss-120b — 128K context, strong reasoning

import json
from groq import Groq
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import GROQ_API_KEY, GROQ_MODEL, GEMINI_API_KEYS

# ── Model names ──
GEMINI_MODEL = "gemini-2.0-flash"

# ── Gemini key rotation ──
_gemini_key_index = 0


def _rotate_gemini_key() -> str:
    global _gemini_key_index
    if not GEMINI_API_KEYS:
        raise RuntimeError("No Gemini API keys configured")
    key = GEMINI_API_KEYS[_gemini_key_index % len(GEMINI_API_KEYS)]
    _gemini_key_index += 1
    return key


# ═══════════════════════════════════════════════════
# GROQ CALLS (Primary — openai/gpt-oss-120b)
# ═══════════════════════════════════════════════════

def _call_groq_json(prompt: str, temperature: float = 0.1) -> dict:
    """Call Groq with JSON response mode. Returns parsed dict."""
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        response_format={"type": "json_object"},
        max_tokens=4096,
    )
    return json.loads(response.choices[0].message.content)


def _call_groq_text(prompt: str, temperature: float = 0.3) -> str:
    """Call Groq with plain text response. Returns raw string."""
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=4096,
    )
    return response.choices[0].message.content


# ═══════════════════════════════════════════════════
# GEMINI CALLS (Fallback)
# ═══════════════════════════════════════════════════

def _call_gemini_json(prompt: str, temperature: float = 0.1) -> dict:
    """Call Gemini with JSON response mode. Returns parsed dict."""
    key = _rotate_gemini_key()
    genai.configure(api_key=key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=temperature,
        ),
    )
    return json.loads(response.text)


def _call_gemini_text(prompt: str, temperature: float = 0.3) -> str:
    """Call Gemini with plain text response. Returns raw string."""
    key = _rotate_gemini_key()
    genai.configure(api_key=key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(temperature=temperature),
    )
    return response.text


# ═══════════════════════════════════════════════════
# PUBLIC API: Groq (primary) → Gemini (fallback)
# ═══════════════════════════════════════════════════

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=15),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def call_llm_json(prompt: str, temperature: float = 0.1) -> dict:
    """
    Call LLM with JSON response mode.
    Uses Groq/gpt-oss-120b (primary) → Gemini (fallback).
    """
    if GROQ_API_KEY:
        try:
            result = _call_groq_json(prompt, temperature)
            return result
        except Exception as e:
            print(f"⚠️ Groq failed: {e}, falling back to Gemini...")

    if GEMINI_API_KEYS:
        return _call_gemini_json(prompt, temperature)

    raise RuntimeError("No LLM provider available. Set GROQ_API_KEY or GEMINI_API_KEY in .env")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=15),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def call_llm_text(prompt: str, temperature: float = 0.3) -> str:
    """
    Call LLM with plain text response.
    Uses Groq/gpt-oss-120b (primary) → Gemini (fallback).
    """
    if GROQ_API_KEY:
        try:
            result = _call_groq_text(prompt, temperature)
            return result
        except Exception as e:
            print(f"⚠️ Groq failed: {e}, falling back to Gemini...")

    if GEMINI_API_KEYS:
        return _call_gemini_text(prompt, temperature)

    raise RuntimeError("No LLM provider available. Set GROQ_API_KEY or GEMINI_API_KEY in .env")


# ── Backwards-compatible aliases ──
call_gemini_json = call_llm_json
call_gemini_text = call_llm_text

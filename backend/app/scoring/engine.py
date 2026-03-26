# app/scoring/engine.py
# Production-ready scoring engine: Groq/Gemini LLM primary + TF-IDF fallback

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.scoring.skills import (
    extract_skills,
    score_resume_against_jd,
    _fallback_extract,
)


# ═══════════════════════════════════════════════════
# EDUCATION HIERARCHY
# ═══════════════════════════════════════════════════

EDUCATION_SCORES = {
    "phd": 10, "ph.d": 10, "doctorate": 10,
    "m.tech": 8, "mtech": 8, "master": 8, "mba": 8, "m.s.": 8, "m.e.": 8, "mca": 8,
    "b.tech": 7, "btech": 7, "b.e.": 7, "bachelor": 7, "b.sc": 7, "bca": 7,
    "diploma": 4, "polytechnic": 4,
    "12th": 2, "hsc": 2, "intermediate": 2,
    "none": 2,
}


# ═══════════════════════════════════════════════════
# TF-IDF RELEVANCE (fallback component)
# ═══════════════════════════════════════════════════

def _tfidf_relevance(resume_text: str, job_description: str) -> float:
    """TF-IDF cosine similarity between full resume and JD (0-15 scale)."""
    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2),
        )
        vectors = vectorizer.fit_transform([resume_text, job_description])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return round(min(similarity * 15, 15.0), 2)
    except ValueError:
        return 0.0


# ═══════════════════════════════════════════════════
# MAIN SCORING FUNCTION
# ═══════════════════════════════════════════════════

def calculate_final_score(resume_text: str, job_description: str) -> dict:
    """
    Master scoring function.
    Uses Gemini for accurate skill extraction and matching.
    Falls back to TF-IDF if Gemini is unavailable.
    """

    # ── Step 1: Ask Gemini for comprehensive analysis ──
    gemini_result = score_resume_against_jd(resume_text, job_description)

    if gemini_result:
        # ── Gemini succeeded: build scores from its analysis ──

        matched = gemini_result.get("matched_skills", [])
        missing = gemini_result.get("missing_skills", [])
        resume_only = gemini_result.get("resume_only_skills", [])
        skill_pct = gemini_result.get("skill_match_percentage", 0)

        # Component 1: Skill Match (40%) — from Gemini's analysis
        skill_score = round((skill_pct / 100) * 40, 2)

        # Component 2: Skill Depth (15%) — count matched skill mentions
        resume_lower = resume_text.lower()
        total_mentions = sum(resume_lower.count(s.lower()) for s in matched)
        expected = max(len(matched) * 2, 1)
        frequency_score = round(min((total_mentions / expected) * 15, 15.0), 2)

        # Component 3: Experience (20%) — from Gemini + regex
        exp_data = gemini_result.get("experience_assessment", {})
        resume_yrs = exp_data.get("resume_years", 0)
        jd_yrs = exp_data.get("jd_required_years", 0)

        if jd_yrs == 0:
            experience_score = 10.0 if resume_yrs > 0 else 5.0
        elif resume_yrs >= jd_yrs:
            experience_score = 20.0
        else:
            experience_score = round((resume_yrs / jd_yrs) * 20, 2)

        # Component 4: Education (10%) — from Gemini
        edu_found = gemini_result.get("education_found", "none").lower()
        education_score = 2.0  # default
        for keyword, score in EDUCATION_SCORES.items():
            if keyword in edu_found:
                education_score = float(score)
                break

        # Component 5: Relevance (15%) — TF-IDF (complements Gemini)
        relevance_score = _tfidf_relevance(resume_text, job_description)

        # Aggregate
        final_score = round(
            skill_score + frequency_score + experience_score +
            education_score + relevance_score,
            2
        )

        return {
            "final_score": min(final_score, 100.0),
            "breakdown": {
                "skill_match": {"score": skill_score, "max": 40, "weight": "40%"},
                "skill_depth": {"score": frequency_score, "max": 15, "weight": "15%"},
                "experience": {"score": experience_score, "max": 20, "weight": "20%"},
                "education": {"score": education_score, "max": 10, "weight": "10%"},
                "relevance": {"score": relevance_score, "max": 15, "weight": "15%"},
            },
            "matched_skills": [s.lower() for s in matched],
            "missing_skills": [s.lower() for s in missing],
            "resume_only_skills": [s.lower() for s in resume_only],
            "overall_fit": gemini_result.get("overall_fit", "Unknown"),
            "reasoning": gemini_result.get("reasoning", ""),
            "powered_by": "gemini",
        }

    else:
        # ── Gemini failed: fallback to keyword + TF-IDF ──
        print("⚠️ Using fallback scoring (Gemini unavailable)")

        jd_skills = _fallback_extract(job_description)
        resume_skills = _fallback_extract(resume_text)

        jd_set = set(jd_skills)
        resume_set = set(resume_skills)
        matched = sorted(jd_set & resume_set)
        missing = sorted(jd_set - resume_set)

        overlap_ratio = len(matched) / len(jd_set) if jd_set else 0
        skill_score = round(overlap_ratio * 40, 2)

        resume_lower = resume_text.lower()
        total_mentions = sum(resume_lower.count(s) for s in matched)
        expected = max(len(matched) * 2, 1)
        frequency_score = round(min((total_mentions / expected) * 15, 15.0), 2)

        experience_score = 5.0
        education_score = 2.0

        relevance_score = _tfidf_relevance(resume_text, job_description)

        final_score = round(
            skill_score + frequency_score + experience_score +
            education_score + relevance_score,
            2
        )

        return {
            "final_score": min(final_score, 100.0),
            "breakdown": {
                "skill_match": {"score": skill_score, "max": 40, "weight": "40%"},
                "skill_depth": {"score": frequency_score, "max": 15, "weight": "15%"},
                "experience": {"score": experience_score, "max": 20, "weight": "20%"},
                "education": {"score": education_score, "max": 10, "weight": "10%"},
                "relevance": {"score": relevance_score, "max": 15, "weight": "15%"},
            },
            "matched_skills": matched,
            "missing_skills": missing,
            "resume_only_skills": sorted(resume_set - jd_set),
            "overall_fit": "Unknown (fallback mode)",
            "reasoning": "Gemini was unavailable. Used keyword matching.",
            "powered_by": "fallback",
        }

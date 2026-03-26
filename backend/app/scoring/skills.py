# app/scoring/skills.py
# Groq-powered skill extraction with Gemini fallback

import json
import re
from app.agents.gemini_client import call_llm_json


def extract_skills(text: str, context: str = "resume") -> list[str]:
    """
    Use LLM (Groq primary, Gemini fallback) to intelligently extract ALL
    technical skills, tools, frameworks, languages, and CS concepts.
    Returns a clean, deduplicated, lowercase list.
    """
    prompt = f"""You are an expert technical recruiter for Indian campus placements.

Analyze the following {context} text and extract ALL technical skills, programming languages, 
frameworks, libraries, databases, tools, cloud services, and CS concepts mentioned.

RULES:
1. Extract EVERY skill, no matter how it's written (abbreviations, full names, etc.)
2. Normalize all skills to lowercase
3. Map common abbreviations: "DSA" → "dsa", "OOPS/OOP" → "oops", "DBMS" → "dbms", "OS" → "operating systems", "CN" → "computer networks"
4. If someone mentions "Data Structures and Algorithms", also include "dsa"
5. If someone mentions "React.js" or "ReactJS", normalize to "react"
6. If someone mentions "Node.js" or "NodeJS", normalize to "node.js"
7. Include soft concepts like "system design", "agile", "scrum" if mentioned
8. Return ONLY a JSON object with a "skills" key containing an array of strings
9. Do NOT hallucinate skills that are not mentioned in the text

TEXT:
\"\"\"
{text[:5000]}
\"\"\"

Return ONLY a valid JSON object like: {{"skills": ["python", "react", "dsa", "sql"]}}
"""

    try:
        result = call_llm_json(prompt, temperature=0.1)
        raw_skills = result.get("skills", [])
        skills = list(set(s.strip().lower() for s in raw_skills if isinstance(s, str)))
        return sorted(skills)
    except Exception as e:
        print(f"⚠️ LLM extraction failed: {e}")
        return _fallback_extract(text)


def score_resume_against_jd(resume_text: str, job_description: str) -> dict:
    """
    Use LLM (Groq primary, Gemini fallback) for comprehensive resume-JD analysis.
    Returns structured scoring with matched/missing skills and detailed reasoning.
    """
    prompt = f"""You are a strict ATS (Applicant Tracking System) scoring engine used by top Indian IT recruiters.

Analyze the RESUME against the JOB DESCRIPTION and return a detailed JSON scoring.

RESUME:
\"\"\"
{resume_text[:4000]}
\"\"\"

JOB DESCRIPTION:
\"\"\"
{job_description}
\"\"\"

Return ONLY a valid JSON object with this EXACT structure:
{{
    "matched_skills": ["list of skills found in BOTH resume and JD"],
    "missing_skills": ["list of skills required by JD but NOT in resume"],
    "resume_only_skills": ["list of extra skills in resume not asked in JD"],
    "skill_match_percentage": <0-100 number>,
    "experience_assessment": {{
        "resume_years": <number or 0 for freshers>,
        "jd_required_years": <number or 0 if not specified>,
        "match": <true/false>
    }},
    "education_found": "<highest degree found, e.g. B.Tech, M.Tech, PhD, or none>",
    "overall_fit": "<one of: Strong Match, Good Match, Partial Match, Weak Match>",
    "reasoning": "<2-3 sentence explanation of the scoring>"
}}

RULES:
1. Be ACCURATE — only list a skill as "matched" if it genuinely appears in BOTH texts
2. Understand abbreviations: DSA = Data Structures & Algorithms, OOP/OOPS = Object Oriented Programming, etc.
3. Be case-insensitive: "Python" and "python" are the same skill
4. Understand context: "built a REST API with FastAPI" means the candidate knows both "rest api" and "fastapi"
5. Do NOT hallucinate — only report what's actually in the text
"""

    try:
        return call_llm_json(prompt, temperature=0.1)
    except Exception as e:
        print(f"⚠️ LLM scoring failed: {e}")
        return None


# ── Fallback keyword extractor (if LLM fails) ──

MASTER_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c", "c#",
    "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "r",
    "react", "angular", "vue", "next.js", "html", "css", "sass",
    "tailwind", "bootstrap", "redux", "svelte",
    "node.js", "express", "fastapi", "django", "flask", "spring",
    "spring boot", "asp.net", "laravel",
    "rest api", "graphql", "sql", "postgresql", "mysql", "mongodb",
    "redis", "sqlite", "firebase", "supabase",
    "aws", "azure", "gcp", "docker", "kubernetes",
    "terraform", "jenkins", "ci/cd", "nginx", "linux",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "pandas", "numpy",
    "scikit-learn", "opencv", "data analysis", "data science",
    "power bi", "tableau", "spark", "hadoop",
    "langchain", "langgraph", "hugging face",
    "data structures", "algorithms", "dsa", "oops",
    "operating systems", "dbms", "computer networks",
    "system design", "design patterns",
    "git", "github", "jira", "postman", "agile", "scrum",
    "microservices", "api", "websocket", "kafka",
    "android", "ios", "flutter", "react native",
}

SKILL_ALIASES = {
    "js": "javascript", "ts": "typescript", "reactjs": "react",
    "react.js": "react", "nodejs": "node.js", "node": "node.js",
    "nextjs": "next.js", "postgres": "postgresql", "mongo": "mongodb",
    "k8s": "kubernetes", "ml": "machine learning", "dl": "deep learning",
    "oop": "oops", "ds": "data structures", "algo": "algorithms",
    "cpp": "c++", "golang": "go", "sklearn": "scikit-learn",
}


def _fallback_extract(text: str) -> list[str]:
    """Enhanced keyword extraction with word-boundary matching."""
    text_lower = text.lower()
    found = set()

    # Multi-word skills: exact substring match (order matters)
    multi_word = sorted(
        [s for s in MASTER_SKILLS if " " in s or "." in s or "/" in s],
        key=len, reverse=True,
    )
    for skill in multi_word:
        if skill in text_lower:
            found.add(skill)

    # Single-word skills: word boundary aware
    for skill in MASTER_SKILLS:
        if " " not in skill and "." not in skill and "/" not in skill:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill)

    # Alias resolution
    for alias, canonical in SKILL_ALIASES.items():
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, text_lower):
            found.add(canonical)

    return sorted(found)


# ── Backwards-compatible aliases ──
extract_skills_gemini = extract_skills
score_resume_against_jd_gemini = score_resume_against_jd

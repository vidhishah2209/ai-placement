# test_pipeline.py
# Standalone test script for the LangGraph pipeline
# Run from backend/ with venv activated:
#   python test_pipeline.py

import sys
import os
import json

# Ensure the backend app is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.pipeline import run_pipeline


# ═══════════════════════════════════════════════════
# SAMPLE RESUME TEXT (typical Indian engineering student)
# ═══════════════════════════════════════════════════

SAMPLE_RESUME = """
RAHUL SHARMA
Email: rahul.sharma@gmail.com | Phone: +91 98765 43210
LinkedIn: linkedin.com/in/rahulsharma | GitHub: github.com/rahulsharma

EDUCATION
B.Tech in Computer Science and Engineering
Indian Institute of Technology, Delhi | 2021 - 2025
CGPA: 8.2/10

12th (CBSE) - 92.4% | DPS, New Delhi | 2021
10th (CBSE) - 95.1% | DPS, New Delhi | 2019

TECHNICAL SKILLS
Languages: Python, Java, C++, JavaScript
Frameworks: React.js, Node.js, Express.js, FastAPI
Databases: PostgreSQL, MongoDB, Redis
Tools: Git, Docker, Linux, Postman, VS Code
Core CS: Data Structures & Algorithms, Object-Oriented Programming, DBMS, Operating Systems

PROJECTS
1. E-Commerce Platform | React, Node.js, MongoDB, Stripe API
   - Built a full-stack e-commerce website with user authentication, product catalog, and payment gateway
   - Implemented shopping cart with real-time inventory management
   - Deployed on AWS EC2 with Nginx reverse proxy

2. Task Management API | FastAPI, PostgreSQL, SQLAlchemy, Docker
   - Developed RESTful API with CRUD operations for task management
   - Added JWT authentication and role-based access control
   - Used Docker for containerization and GitHub Actions for CI/CD

3. Chat Application | React, Socket.io, Node.js, Redis
   - Real-time messaging app with group chat and typing indicators
   - Used Redis for message caching and Socket.io for WebSocket communication
   - Features: file sharing, message deletion, online status

EXPERIENCE
Software Engineering Intern | Tech Corp Pvt Ltd | May 2024 - July 2024
- Worked on backend microservices using Python and FastAPI
- Optimized database queries reducing response time by 30%
- Collaborated with team of 5 to deliver features on sprint deadlines

CERTIFICATIONS
- AWS Cloud Practitioner
- Data Structures and Algorithms (NPTEL - IIT Kharagpur)

ACHIEVEMENTS
- Solved 500+ problems on LeetCode (Rating: 1800+)
- Won Smart India Hackathon 2023 - Software Edition
- Technical Lead of Coding Club, IIT Delhi
"""


def main():
    print("🧪 Testing LangGraph Pipeline with sample resume...\n")

    result = run_pipeline(
        raw_text=SAMPLE_RESUME,
        target_role="Software Engineer",
        user_id=None,  # Skip DB save in test mode
    )

    # Save full result
    output_dir = os.path.join(os.path.dirname(__file__), "..", "executed_outputs")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "pipeline_test_result.json")

    # Filter out non-serializable fields
    serializable = {k: v for k, v in result.items() if k != "raw_text"}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n📁 Full result saved to: {output_path}")

    # Validation summary
    print("\n" + "=" * 50)
    print("📋 VALIDATION SUMMARY")
    print("=" * 50)

    checks = [
        ("parsed_json", result.get("parsed_json") is not None),
        ("ats_score", result.get("ats_score") is not None),
        ("skill_gaps", result.get("skill_gaps") is not None),
        ("improved_resume", result.get("improved_resume") is not None),
        ("supervisor_passed", result.get("supervisor_passed", False)),
        ("interview_qna", result.get("interview_qna") is not None),
        ("confidence_score", result.get("confidence_score") is not None),
    ]

    for name, passed in checks:
        icon = "✅" if passed else "❌"
        print(f"  {icon} {name}")

    errors = result.get("errors", [])
    if errors:
        print(f"\n⚠️ Errors ({len(errors)}):")
        for err in errors:
            print(f"  - {err}")

    all_passed = all(p for _, p in checks) and not errors
    print(f"\n{'🎉 ALL CHECKS PASSED!' if all_passed else '⚠️ SOME CHECKS FAILED'}")


if __name__ == "__main__":
    main()

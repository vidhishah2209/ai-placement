import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

keys = [
    os.getenv("GEMINI_API_KEY").strip(),
    os.getenv("GEMINI_API_KEY_1").strip(),
    os.getenv("GEMINI_API_KEY_2").strip(),
]

results = []
for i, key in enumerate(keys):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        r = model.generate_content("Say hi in one word")
        results.append(f"KEY {i}: OK -> {r.text.strip()}")
    except Exception as e:
        results.append(f"KEY {i}: FAIL -> {type(e).__name__}: {str(e)[:200]}")

with open("test_result.txt", "w") as f:
    f.write("\n".join(results))
print("Done")

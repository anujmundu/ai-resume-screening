import os
import json
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
)

def sanitize_to_json(text: str) -> str:
    if not text:
        return ""
    cleaned = text.strip()
    if cleaned.startswith("```") and cleaned.endswith("```"):
        cleaned = cleaned[3:-3].strip()
    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:].strip()
    return cleaned

def extract_data(resume_text: str) -> dict | None:
    prompt = f"""
Extract structured JSON from the following resume text.

Resume:
{resume_text}

Schema:
{{
  "skills": [],
  "experience_years": 0,
  "education": ""
}}

Rules:
- Return ONLY valid JSON matching the schema.
- Do NOT include markdown, code fences, or explanations.
- If unsure, leave fields empty or set to 0.
"""

    try:
        completion = client.chat.completions.create(
            model="google/gemma-3-4b-it:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        raw = completion.choices[0].message.content or ""
        print("DEBUG raw content:", raw)

        cleaned = sanitize_to_json(raw)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            print("WARN: Model returned non-JSON. Using fallback.")
            data = {
                "skills": [],
                "experience_years": 0,
                "education": "",
                "raw_output": raw,
            }

        return data

    except Exception as e:
        print("AI extraction error:", e)
        return None

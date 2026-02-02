import os
import re
import json
import requests

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

def get_api_key():
    return os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

def sanitize_to_json(text: str) -> str:
    if not text:
        return ""
    cleaned = text.strip()
    if "```" in cleaned:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
        if match:
            cleaned = match.group(1).strip()
    if not (cleaned.startswith("{") and cleaned.endswith("}")):
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            cleaned = match.group(0).strip()
    return cleaned

def generate_heuristic_interview_questions(skills: list, missing_skills: list, experience_years: float, role_title: str) -> list[dict]:
    questions = []
    if skills:
        primary_skill = skills[0]
        questions.append({
            "question": f"Can you walk me through a challenging production issue you encountered while building with {primary_skill}, and how you debugged and resolved it?",
            "focus_area": f"Depth in {primary_skill} & Problem Solving",
            "suggested_answer": f"Look for concrete architecture trade-offs, profiling/debugging tools used, and measurable results achieved with {primary_skill}."
        })
    else:
        questions.append({
            "question": "Describe the most complex software architecture you have designed and deployed to date.",
            "focus_area": "System Architecture & Engineering Depth",
            "suggested_answer": "Look for modular design, clean separation of concerns, and scalability considerations."
        })

    if missing_skills:
        missing_target = missing_skills[0]
        questions.append({
            "question": f"This role requires hands-on experience with {missing_target}. How would your existing skill set enable you to ramp up quickly on {missing_target}?",
            "focus_area": f"Adaptability & {missing_target} Knowledge",
            "suggested_answer": f"Candidate should draw parallels between tools they already master and {missing_target} paradigms."
        })
    elif len(skills) > 1:
        second_skill = skills[1]
        questions.append({
            "question": f"How do you ensure reliability, automated testing, and performance optimization when deploying {second_skill} in a production environment?",
            "focus_area": f"Reliability & Production Readiness in {second_skill}",
            "suggested_answer": "Look for unit/integration testing methodologies, CI/CD automation, and monitoring."
        })
    else:
        questions.append({
            "question": "How do you approach automated testing and continuous integration across your repositories?",
            "focus_area": "Testing & CI/CD Discipline",
            "suggested_answer": "Candidate should mention unit test frameworks, coverage gates, and GitHub Actions or similar."
        })

    if experience_years >= 3:
        questions.append({
            "question": "How do you profile and eliminate latency bottlenecks or throughput limitations in high-load services?",
            "focus_area": "Performance Profiling & Optimization",
            "suggested_answer": "Look for experience with caching (e.g. Redis), distributed tracing (OpenTelemetry), and query optimization."
        })
    else:
        questions.append({
            "question": "Tell me about a technical project where you had to learn a completely new framework under tight deadlines.",
            "focus_area": "Learning Agility & Execution",
            "suggested_answer": "Look for structured learning ability, reading documentation, and rapid prototyping."
        })

    return questions

def heuristic_fallback_extract(resume_text: str, job_description: str = "") -> dict:
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", resume_text)
    email = email_match.group(0) if email_match else ""

    phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", resume_text)
    phone = phone_match.group(0) if phone_match else ""

    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    candidate_name = "Candidate"
    for line in lines[:5]:
        if len(line) < 40 and not re.search(r"[@\d:]|resume|curriculum|profile|phone|email", line, re.IGNORECASE):
            candidate_name = line.title()
            break

    exp_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+of)?\s+experience", resume_text, re.IGNORECASE)
    experience_years = float(exp_matches[0]) if exp_matches else 0.0

    tech_vocab = [
        # Languages & Core Backend
        "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "php", "go", "golang", "rust", "scala",
        "sql", "mysql", "postgresql", "mongodb", "redis", "docker", "kubernetes", "aws", "azure", "gcp",
        "node.js", "express", "django", "flask", "fastapi", "spring boot", "git", "ci/cd", "linux", "rest api", "graphql",
        # Data Engineering & Cloud Data
        "spark", "apache spark", "pyspark", "airflow", "apache airflow", "dbt", "snowflake", "bigquery", "kafka", "apache kafka",
        "iceberg", "databricks", "hadoop", "redshift", "data modeling", "etl", "elt",
        # DevOps & SRE
        "terraform", "ansible", "prometheus", "grafana", "istio", "helm", "opentelemetry", "datadog", "argocd", "gitops", "celery",
        # Security & SOC
        "siem", "splunk", "elastic security", "vulnerability assessment", "penetration testing", "threat hunting",
        "zero trust", "iso 27001", "soc 2", "wireshark", "mitre att&ck", "edr",
        # Frontend & Mobile
        "react", "angular", "vue", "next.js", "tailwind", "tailwindcss", "html5", "css3", "redux", "jest", "playwright",
        "storybook", "flutter", "dart", "swift", "kotlin", "react native",
        # AI / ML
        "machine learning", "deep learning", "nlp", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
        "rag", "llm", "onnx", "quantization", "opencv", "yolo", "tensorrt",
        # Product & Management
        "product roadmap", "prd", "a/b testing", "agile", "scrum", "jira", "user research", "stakeholder management",
        # Creative & Design
        "figma", "photoshop", "illustrator", "indesign", "typography", "brand identity", "copywriting"
    ]
    text_lower = resume_text.lower()
    found_skills = [skill.title() for skill in tech_vocab if re.search(rf"\b{re.escape(skill)}\b", text_lower)]

    edu_match = re.search(r"\b(MCA|BCA|B\.?Tech|M\.?Tech|B\.?Sc|M\.?Sc|B\.?E|MBA|Ph\.?D|Bachelor|Master)\b", resume_text, re.IGNORECASE)
    education = edu_match.group(0).upper() if edu_match else "Bachelor's Degree"

    matched_skills = []
    missing_skills = []
    if job_description:
        jd_lower = job_description.lower()
        jd_skills = [skill.title() for skill in tech_vocab if re.search(rf"\b{re.escape(skill)}\b", jd_lower)]
        matched_skills = [s for s in found_skills if s in jd_skills]
        missing_skills = [s for s in jd_skills if s not in found_skills]

    top_skills_str = ", ".join(found_skills[:4]) if found_skills else "general software engineering"
    if matched_skills:
        memo = f"Strong candidate showing verified alignment with target requirements in {', '.join(matched_skills[:3])}. Profile demonstrates {experience_years:g}+ years of experience and solid fundamentals. Recommended for technical screening."
    elif found_skills:
        memo = f"Candidate possesses valuable skills in {top_skills_str}. Alignment with role specifics is moderate; suggest probing hands-on depth during initial conversation."
    else:
        memo = "Candidate profile is general. Additional technical portfolio review is recommended before advancing."

    interview_questions = generate_heuristic_interview_questions(
        found_skills, missing_skills, experience_years, job_description[:50]
    )

    return {
        "candidate_name": candidate_name,
        "email": email,
        "phone": phone,
        "skills": found_skills,
        "experience_years": experience_years,
        "education": education,
        "summary": "Extracted via intelligent heuristic talent parser.",
        "strengths": found_skills[:5],
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recruiter_memo": memo,
        "interview_questions": interview_questions
    }

def extract_data(resume_text: str, job_description: str = "") -> dict:
    api_key = get_api_key()
    if not api_key:
        return heuristic_fallback_extract(resume_text, job_description)

    jd_context = ""
    if job_description.strip():
        jd_context = f"""
Target Job Description / Role:
\"\"\"{job_description.strip()}\"\"\"
"""

    prompt = f"""
You are an executive AI talent intelligence director. Analyze the following candidate resume against the target role requirements.
{jd_context}
Resume Text:
\"\"\"{resume_text}\"\"\"

Return ONLY a valid JSON object matching this exact schema:
{{
  "candidate_name": "Full Name",
  "email": "email@example.com",
  "phone": "Phone Number",
  "skills": ["Skill 1", "Skill 2"],
  "experience_years": 0.0,
  "education": "Highest Degree (e.g. MCA, B.Tech, MS)",
  "summary": "2-sentence professional summary",
  "strengths": ["Key Strength 1", "Key Strength 2", "Key Strength 3"],
  "matched_skills": ["Skills from resume that match the JD"],
  "missing_skills": ["Key JD requirements not found in resume"],
  "recruiter_memo": "3-sentence executive hiring memo: why shortlist or reject, key strengths, and potential caution/risk areas.",
  "interview_questions": [
    {{
      "question": "Specific technical interview question tailored to candidate's projects or gaps",
      "focus_area": "Topic",
      "suggested_answer": "What the interviewer should listen for in a strong response"
    }},
    {{
      "question": "Second tailored interview question",
      "focus_area": "Topic",
      "suggested_answer": "Expected key technical concepts"
    }},
    {{
      "question": "Third tailored interview question",
      "focus_area": "Topic",
      "suggested_answer": "Expected key technical concepts"
    }}
  ]
}}

Rules:
1. Return ONLY pure JSON. No markdown fences.
2. In 'recruiter_memo', be concise, objective, and executive.
3. In 'interview_questions', ask specific questions about the candidate's actual projects and technologies.
"""

    models_to_try = [
        os.getenv("AI_MODEL", "google/gemma-3-4b-it:free"),
        "meta-llama/llama-3.2-3b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
    ]

    for model in models_to_try:
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=25
            )
            if resp.status_code == 200:
                raw = resp.json()["choices"][0]["message"]["content"] or ""
            else:
                continue

            cleaned = sanitize_to_json(raw)
            data = json.loads(cleaned)

            defaults = {
                "candidate_name": "Candidate",
                "email": "",
                "phone": "",
                "skills": [],
                "experience_years": 0.0,
                "education": "",
                "summary": "",
                "strengths": [],
                "matched_skills": [],
                "missing_skills": [],
                "recruiter_memo": "",
                "interview_questions": []
            }
            for k, v in defaults.items():
                if k not in data or data[k] is None:
                    data[k] = v

            try:
                data["experience_years"] = float(data.get("experience_years", 0))
            except (ValueError, TypeError):
                data["experience_years"] = 0.0

            if not data.get("recruiter_memo"):
                data["recruiter_memo"] = f"Candidate demonstrates skills in {', '.join(data.get('skills', [])[:3])}. Profile shows {data.get('experience_years', 0):g} years of experience."
            if not data.get("interview_questions"):
                data["interview_questions"] = generate_heuristic_interview_questions(
                    data.get("skills", []), data.get("missing_skills", []), data.get("experience_years", 0), job_description
                )

            return data
        except Exception as err:
            print(f"[AI Extractor] Failed with model {model}: {err}")
            continue

    print("[AI Extractor] Using heuristic fallback for extraction, memo, and interview questions.")
    return heuristic_fallback_extract(resume_text, job_description)

# ---------------- Option 1: Recruiter Copilot (Chat with Resume) ----------------
def chat_with_resume(candidate_data: dict, question: str) -> str:
    """
    Answers a recruiter's natural-language question grounded strictly in candidate resume data.
    """
    q_clean = question.strip()
    if not q_clean:
        return "Please ask a specific question about the candidate's experience or skills."

    api_key = get_api_key()
    name = candidate_data.get("candidate_name", "Candidate")
    skills = candidate_data.get("skills", [])
    exp = candidate_data.get("experience_years", 0)
    edu = candidate_data.get("education", "")
    summary = candidate_data.get("summary", "")
    strengths = candidate_data.get("strengths", [])
    memo = candidate_data.get("recruiter_memo", "")

    context = f"""
Candidate Name: {name}
Education: {edu}
Years of Experience: {exp}
Skills: {', '.join(skills)}
Summary: {summary}
Strengths: {', '.join(strengths)}
Recruiter Notes: {memo}
"""

    if api_key:
        prompt = f"""You are an objective AI Recruiter Copilot. Answer the recruiter's question using ONLY the candidate's resume information below.
Be concise (2-4 sentences), factual, and professional. If the information is not present, clearly state that it is not mentioned in the resume.

{context}

Recruiter Question: {q_clean}
"""
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": os.getenv("AI_MODEL", "google/gemma-3-4b-it:free"),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                answer = resp.json()["choices"][0]["message"]["content"]
                return answer.strip()
        except Exception as e:
            print(f"[Copilot Error]: {e}")

    # Heuristic Answer Fallback
    q_lower = q_clean.lower()
    if any(w in q_lower for w in ["skill", "stack", "technology", "technologies", "tool"]):
        return f"{name} has verified skills in: {', '.join(skills) if skills else 'general software engineering'}."
    elif any(w in q_lower for w in ["experience", "years", "tenure", "how long"]):
        return f"{name} has approximately {exp:g} years of professional experience with a focus in {skills[0] if skills else 'software engineering'}."
    elif any(w in q_lower for w in ["education", "degree", "college", "university"]):
        return f"{name} holds a credential in {edu}."
    elif any(w in q_lower for w in ["cloud", "aws", "docker", "kubernetes", "infra"]):
        cloud_skills = [s for s in skills if s.lower() in ["aws", "docker", "kubernetes", "gcp", "azure", "linux", "ci/cd", "terraform"]]
        if cloud_skills:
            return f"Yes, {name} demonstrates cloud & infrastructure proficiency in: {', '.join(cloud_skills)}."
        return f"Cloud or DevOps infrastructure skills are not prominently highlighted in {name}'s parsed profile."
    else:
        return f"Based on the resume, {name} has {exp:g} years of experience specializing in {', '.join(skills[:3]) if skills else 'software development'}. Summary: {summary}"

# ---------------- Option 5: Personalized Outreach & Feedback Email ----------------
def generate_candidate_email(candidate_record: dict, email_type: str = "outreach") -> dict:
    """
    Generates tailored email subject and body for candidate outreach or constructive feedback.
    """
    data = candidate_record.get("data", {})
    name = data.get("candidate_name", "Candidate")
    email = data.get("email", "")
    score = candidate_record.get("score", 0)
    decision = candidate_record.get("decision", "review")
    skills = data.get("skills", [])
    matched_skills = data.get("matched_skills", [])
    missing_skills = data.get("missing_skills", [])

    if email_type == "outreach" or decision == "shortlist":
        subject = f"Interview Invitation: Exciting Technical Opportunity at Our Team"
        highlight = f"your impressive background in {', '.join(matched_skills[:2]) if matched_skills else ', '.join(skills[:2])}"
        body = f"""Hi {name},

I hope this email finds you well.

I came across your profile and was very impressed by {highlight}. Given your strong background and proven track record, we believe your experience aligns exceptionally well with what we're building on our team.

We would love to invite you for an initial 30-minute introductory conversation to learn more about your technical journey, share our engineering vision, and discuss where you could make an immediate impact.

Are you available for a brief call later this week? Please let me know times that work best for you, or feel free to book directly on my calendar.

Looking forward to speaking with you!

Best regards,
Technical Recruiting Team
"""
    else:
        subject = f"Update on your application with our Technical Team"
        growth_areas = f"hands-on experience with {', '.join(missing_skills[:2])}" if missing_skills else "advanced production specialization"
        body = f"""Dear {name},

Thank you for taking the time to share your resume with us and for your interest in our team.

We carefully reviewed your qualifications and appreciate your strong foundation in {', '.join(skills[:2]) if skills else 'software engineering'}. At this stage, our requirements prioritize candidates with deeper {growth_areas}. 

While we are not advancing with your application for this specific opening, we were impressed by your background and will keep your profile in our talent network for future openings that match your skills.

We wish you the very best in your career pursuits!

Warm regards,
Talent Acquisition Team
"""

    return {
        "subject": subject,
        "body": body,
        "recipient": email,
        "name": name
    }

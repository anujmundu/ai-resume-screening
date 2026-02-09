import math
import re
from collections import Counter

def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z0-9_+#.-]+\b", text.lower())

def _get_ngrams(tokens: list[str], n: int = 2) -> list[str]:
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

def compute_semantic_similarity(resume_text: str, job_description: str) -> float:
    """
    Computes semantic similarity percentage (0.0 to 100.0) between resume text and JD.
    Uses scikit-learn TF-IDF if installed, or an intelligent built-in n-gram vectorizer
    with zero external dependencies.
    """
    if not resume_text.strip() or not job_description.strip():
        return 0.0

    # 1. Try scikit-learn TF-IDF first if available
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=5000)
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        raw_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        return round(min(max(raw_sim * 175.0, 0.0), 100.0), 1)
    except Exception:
        pass

    # 2. Pure Python N-gram Cosine Similarity (Zero Dependencies)
    stop_words = {
        "the", "and", "a", "an", "in", "on", "for", "with", "to", "at", "of",
        "from", "as", "by", "is", "are", "be", "this", "that", "it", "or", "we", "you", "our"
    }
    tokens_r = [w for w in _tokenize(resume_text) if w not in stop_words and len(w) > 1]
    tokens_j = [w for w in _tokenize(job_description) if w not in stop_words and len(w) > 1]

    if not tokens_j or not tokens_r:
        return 0.0

    terms_r = tokens_r + _get_ngrams(tokens_r, 2)
    terms_j = tokens_j + _get_ngrams(tokens_j, 2)

    vec_r = Counter(terms_r)
    vec_j = Counter(terms_j)

    intersection = set(vec_r.keys()).intersection(set(vec_j.keys()))
    if not intersection:
        return 0.0

    dot_product = sum(vec_r[t] * vec_j[t] for t in intersection)
    mag_r = math.sqrt(sum(v**2 for v in vec_r.values()))
    mag_j = math.sqrt(sum(v**2 for v in vec_j.values()))

    if mag_r == 0 or mag_j == 0:
        return 0.0

    raw_sim = dot_product / (mag_r * mag_j)
    scaled_sim = min(max(raw_sim * 220.0, 0.0), 100.0)
    return round(scaled_sim, 1)

def evaluate_resume(data: dict, job_description: str = "", resume_text: str = "") -> dict:
    """
    Computes a transparent, recruiter-friendly score (0–100), decision, and breakdown.
    Supports dynamic JD matching, semantic alignment, and general profile evaluation across ANY role.
    """
    skills = data.get("skills", [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    skills = [str(s).strip() for s in skills if s]

    exp_years = 0.0
    try:
        exp_years = float(data.get("experience_years", 0) or 0)
    except (ValueError, TypeError):
        exp_years = 0.0

    education = str(data.get("education", "") or "").lower()

    # Calculate semantic alignment if JD and resume text are present
    semantic_fit = 0.0
    if job_description.strip() and resume_text.strip():
        semantic_fit = compute_semantic_similarity(resume_text, job_description)

    # 1. Skills Scoring (Max 35 with JD, 40 without JD)
    matched_skills = data.get("matched_skills", [])
    missing_skills = data.get("missing_skills", [])

    if job_description.strip() and (matched_skills or missing_skills):
        total_req_skills = len(matched_skills) + len(missing_skills)
        if total_req_skills > 0:
            skills_score = int((len(matched_skills) / total_req_skills) * 35)
        else:
            skills_score = min(len(skills) * 5, 35)
    else:
        skills_score = min(len(skills) * 5, 40)

    # 2. Experience Scoring (Max 25 with JD, 30 without JD)
    if job_description.strip():
        base_exp = min(max(exp_years, 0) * 5, 25)
        total_req_skills = len(matched_skills) + len(missing_skills)
        if total_req_skills > 0:
            match_ratio = len(matched_skills) / total_req_skills
            # Severe role mismatch: scale experience to prevent unqualified cross-field advancement
            if match_ratio < 0.2 and semantic_fit < 25.0:
                relevance_factor = max(match_ratio, semantic_fit / 100.0, 0.15)
                experience_score = int(base_exp * relevance_factor)
            else:
                experience_score = int(base_exp)
        else:
            experience_score = int(base_exp)
    else:
        experience_score = int(min(max(exp_years, 0) * 6, 30))

    # 3. Education & Credentials Scoring (Max 15 points)
    education_score = 0
    if any(deg in education for deg in ["phd", "doctorate", "m.tech", "mtech", "ms", "msc", "mca", "mba"]):
        education_score = 15
    elif any(deg in education for deg in ["b.tech", "btech", "b.e", "be", "bca", "bsc", "bachelor"]):
        education_score = 12
    elif education.strip():
        education_score = 8

    # 4. Semantic Alignment Score (Max 15 points if JD provided)
    semantic_score = 0
    if job_description.strip():
        semantic_score = int((semantic_fit / 100.0) * 15)

    # 5. Profile Quality & Completeness (Max 10 with JD, 15 without JD)
    profile_score = 0
    if data.get("candidate_name") and data.get("candidate_name") != "Candidate":
        profile_score += 3
    if data.get("email") or data.get("phone"):
        profile_score += 3
    if data.get("summary"):
        profile_score += 2
    if data.get("strengths"):
        profile_score += 2 if job_description.strip() else 7

    total_score = min(skills_score + experience_score + education_score + semantic_score + profile_score, 100)

    total_req_skills = len(matched_skills) + len(missing_skills)
    if total_score >= 65:
        decision = "shortlist"
    elif total_score >= 45:
        # Severe mismatch protection: if semantic fit < 20% or 0 matching skills on requirements >= 3
        if job_description.strip() and (semantic_fit < 20.0 or (total_req_skills >= 3 and len(matched_skills) == 0)):
            decision = "reject"
        else:
            decision = "review"
    else:
        decision = "reject"

    return {
        "score": total_score,
        "decision": decision,
        "semantic_fit": semantic_fit,
        "score_breakdown": {
            "skills": skills_score,
            "experience": experience_score,
            "education": education_score,
            "semantic": semantic_score,
            "profile": profile_score,
        }
    }

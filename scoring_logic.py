def score_resume(data: dict) -> tuple[int, str]:
    """
    Compute a recruiter-like score and decision.
    Weights:
    - Core skills: Python (30), SQL (20)
    - Bonus: +5 per additional skill
    - Experience: 10 per year, capped at 30
    - Education: MCA/BTech/MSc = +20
    Decision: shortlist if score >= 60
    """
    score = 0

    skills = [s.strip().lower() for s in data.get("skills", []) if isinstance(s, str)]
    exp = data.get("experience_years", 0)
    edu = str(data.get("education", "")).strip().lower()

    # Skills weights
    if "python" in skills:
        score += 30
    if "sql" in skills:
        score += 20

    # Bonus for breadth
    score += max(0, len(skills) - len(set(["python", "sql"]))) * 5

    # Experience (cap at 30)
    try:
        exp_int = int(exp)
    except (ValueError, TypeError):
        exp_int = 0
    score += min(exp_int * 10, 30)

    # Education
    if edu in {"mca", "btech", "msc"}:
        score += 20

    decision = "shortlist" if score >= 60 else "reject"
    return score, decision

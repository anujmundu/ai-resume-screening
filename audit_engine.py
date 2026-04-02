import re
from datetime import datetime

def audit_resume(resume_text: str, data: dict) -> dict:
    """
    Analyzes resume text and extracted candidate data for:
    1. Buzzword stuffing (skills listed without practical context in experience/projects)
    2. Employment gaps & date chronology anomalies
    3. Job tenure stability
    Returns an Integrity & Consistency report with a 0-100% rating.
    """
    flags = []
    deductions = 0

    skills = [str(s).strip() for s in data.get("skills", []) if s]
    exp_years = float(data.get("experience_years", 0) or 0)
    text_lower = resume_text.lower()

    # 1. Buzzword Stuffing Audit
    # Check which skills appear ONLY once (likely just in a bulleted skill list) vs in contextual text
    unverified_skills = []
    for skill in skills:
        pattern = rf"\b{re.escape(skill.lower())}\b"
        occurrences = len(re.findall(pattern, text_lower))
        # If it only occurs once in the entire resume, it's likely just in the "Skills:" list
        if occurrences <= 1 and len(skills) > 6:
            unverified_skills.append(skill)

    stuffing_ratio = len(unverified_skills) / len(skills) if skills else 0.0
    if stuffing_ratio > 0.45 and len(skills) > 8:
        deductions += 15
        flags.append({
            "type": "warning",
            "category": "Buzzword Stuffing",
            "message": f"{len(unverified_skills)} of {len(skills)} listed skills ({stuffing_ratio:.0%}) lack practical evidence in project descriptions or work history."
        })
    elif stuffing_ratio > 0.3 and len(skills) > 8:
        deductions += 5
        flags.append({
            "type": "info",
            "category": "Skill Context",
            "message": f"Minor gap: {len(unverified_skills)} skills appear only in the summary list without explicit project context."
        })

    # 2. Date Chronology & Inversion Check
    year_ranges = re.findall(r"\b(20\d{2})\s*(?:-|–|to)\s*(20\d{2}|present|current)\b", text_lower)
    for start_year_str, end_year_str in year_ranges:
        try:
            start_yr = int(start_year_str)
            end_yr = datetime.now().year if end_year_str in ["present", "current"] else int(end_year_str)
            if start_yr > end_yr:
                deductions += 20
                flags.append({
                    "type": "danger",
                    "category": "Chronology Anomaly",
                    "message": f"Inverted date range detected: {start_year_str} - {end_year_str}."
                })
        except Exception:
            pass

    # 3. Employment Gap Detection
    years_found = sorted(list(set(int(y) for y in re.findall(r"\b(20\d{2})\b", text_lower))))
    if len(years_found) >= 2:
        max_gap = 0
        gap_period = ""
        for i in range(len(years_found) - 1):
            gap = years_found[i+1] - years_found[i]
            if gap > 2:  # More than 2 years gap between milestones
                if gap > max_gap:
                    max_gap = gap
                    gap_period = f"{years_found[i]} to {years_found[i+1]}"

        if max_gap > 2:
            deductions += 10
            flags.append({
                "type": "warning",
                "category": "Career Gap",
                "message": f"Potential gap of ~{max_gap} years detected between milestones ({gap_period})."
            })

    # 4. Job Tenure & Stability Metrics
    role_indicators = len(re.findall(r"\b(engineer|developer|lead|analyst|manager|specialist|intern)\b", text_lower))
    estimated_roles = max(min(role_indicators // 2, 6), 1)
    avg_tenure = (exp_years / estimated_roles) if estimated_roles > 0 else exp_years

    if exp_years >= 3 and avg_tenure < 1.0:
        deductions += 10
        flags.append({
            "type": "warning",
            "category": "Tenure Stability",
            "message": f"High role mobility: Average estimated tenure is under 1 year per role ({avg_tenure:.1f} yrs)."
        })
    elif exp_years >= 2 and avg_tenure >= 1.8:
        flags.append({
            "type": "success",
            "category": "Tenure Stability",
            "message": f"Strong tenure stability: Average stay of {avg_tenure:.1f} years per engagement."
        })

    integrity_score = max(min(100 - deductions, 100), 40)

    # Positive reinforcement if clean
    if not flags or all(f["type"] in ["success", "info"] for f in flags):
        flags.insert(0, {
            "type": "success",
            "category": "Profile Integrity",
            "message": "High consistency: Verified skill references and sound chronological progression."
        })

    return {
        "integrity_score": integrity_score,
        "flags": flags,
        "unverified_skills": unverified_skills[:8],
        "tenure_summary": f"Estimated average tenure: {avg_tenure:.1f} yrs across ~{estimated_roles} roles"
    }

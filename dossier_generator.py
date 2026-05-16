import io
import fitz

def generate_pdf_dossier(candidate_record: dict) -> bytes:
    """
    Generates a high-impact, 1-page executive PDF dossier report for a candidate
    using PyMuPDF (fitz).
    """
    data = candidate_record.get("data", {})
    name = data.get("candidate_name", "Candidate")
    email = data.get("email", "N/A")
    phone = data.get("phone", "N/A")
    exp = data.get("experience_years", 0)
    edu = data.get("education", "N/A")
    summary = data.get("summary", "")
    score = candidate_record.get("score", 0)
    decision = candidate_record.get("decision", "review").upper()
    semantic_fit = candidate_record.get("semantic_fit", 0.0)
    breakdown = candidate_record.get("score_breakdown", {})
    skills = data.get("skills", [])
    matched_skills = data.get("matched_skills", [])
    missing_skills = data.get("missing_skills", [])
    memo = data.get("recruiter_memo", candidate_record.get("recruiter_memo", ""))
    questions = data.get("interview_questions", candidate_record.get("interview_questions", []))

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4

    # Top Header Banner
    page.draw_rect(fitz.Rect(0, 0, 595, 80), color=(0.06, 0.09, 0.16), fill=(0.06, 0.09, 0.16))
    page.insert_text((40, 35), "TALENTAI EXECUTIVE CANDIDATE DOSSIER", fontsize=11, fontname="helv", color=(0.4, 0.6, 1.0))
    page.insert_text((40, 58), name.upper(), fontsize=18, fontname="helv", color=(1.0, 1.0, 1.0))

    # Decision Badge on Header Right
    badge_bg = (0.06, 0.45, 0.3) if decision == "SHORTLIST" else ((0.6, 0.4, 0.1) if decision == "REVIEW" else (0.6, 0.1, 0.1))
    page.draw_rect(fitz.Rect(430, 25, 555, 60), color=badge_bg, fill=badge_bg)
    page.insert_text((445, 42), f"{decision} ({score}/100)", fontsize=11, fontname="helv", color=(1.0, 1.0, 1.0))
    if semantic_fit > 0:
        page.insert_text((445, 54), f"Semantic Fit: {semantic_fit}%", fontsize=8, fontname="helv", color=(1.0, 1.0, 1.0))

    y = 105
    # Contact & Profile Bar
    contact_text = f"Email: {email}   |   Phone: {phone}   |   Experience: {exp:g} yrs   |   Education: {edu}"
    page.insert_text((40, y), contact_text, fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))
    page.draw_line((40, y + 8), (555, y + 8), color=(0.85, 0.85, 0.85), width=1)

    # Score Breakdown Section
    y += 28
    page.insert_text((40, y), "SCORING BREAKDOWN", fontsize=10, fontname="helv", color=(0.1, 0.1, 0.1))
    page.draw_rect(fitz.Rect(40, y + 6, 555, y + 42), color=(0.95, 0.96, 0.98), fill=(0.95, 0.96, 0.98))

    pts_skills = breakdown.get("skills", 0)
    pts_exp = breakdown.get("experience", 0)
    pts_edu = breakdown.get("education", 0)
    pts_sem = breakdown.get("semantic", 0)
    pts_prof = breakdown.get("profile", 0)

    breakdown_str = f"Technical Skills: {pts_skills}/35    |    Experience: {pts_exp}/25    |    Education: {pts_edu}/15    |    Semantic Fit: {pts_sem}/15    |    Profile: {pts_prof}/10"
    page.insert_text((55, y + 27), breakdown_str, fontsize=8.5, fontname="helv", color=(0.15, 0.2, 0.3))

    # Executive Recruiter Memo
    y += 65
    page.insert_text((40, y), "EXECUTIVE RECRUITER BRIEFING", fontsize=10, fontname="helv", color=(0.1, 0.1, 0.1))
    page.draw_rect(fitz.Rect(40, y + 6, 555, y + 55), color=(0.92, 0.94, 0.99), fill=(0.92, 0.94, 0.99))
    memo_lines = [memo[i:i+95] for i in range(0, len(memo), 95)] if memo else ["Candidate profile shows relevant skills for this position."]
    line_y = y + 22
    for line in memo_lines[:3]:
        page.insert_text((52, line_y), line, fontsize=8.5, fontname="helv", color=(0.1, 0.15, 0.3))
        line_y += 12

    # Technical Skills Matrix
    y += 75
    page.insert_text((40, y), "SKILLS & COMPETENCY PROFILE", fontsize=10, fontname="helv", color=(0.1, 0.1, 0.1))
    page.draw_line((40, y + 4), (555, y + 4), color=(0.85, 0.85, 0.85), width=0.5)

    y += 18
    all_skills_str = ", ".join(skills[:15]) if skills else "General Software Engineering"
    page.insert_text((40, y), f"Detected Skills: {all_skills_str}", fontsize=8.5, fontname="helv", color=(0.2, 0.2, 0.2))

    if matched_skills:
        y += 14
        page.insert_text((40, y), f"JD Matched Competencies: {', '.join(matched_skills)}", fontsize=8.5, fontname="helv", color=(0.05, 0.5, 0.2))

    if missing_skills:
        y += 14
        page.insert_text((40, y), f"Gaps / Missing Competencies: {', '.join(missing_skills)}", fontsize=8.5, fontname="helv", color=(0.7, 0.15, 0.15))

    # Tailored Technical Interview Questions
    y += 30
    page.insert_text((40, y), "TAILORED TECHNICAL INTERVIEW QUESTIONS", fontsize=10, fontname="helv", color=(0.1, 0.1, 0.1))
    page.draw_line((40, y + 4), (555, y + 4), color=(0.85, 0.85, 0.85), width=0.5)

    y += 16
    for idx, q in enumerate(questions[:3]):
        q_text = f"Q{idx+1}: {q.get('question', '')}"
        focus_text = f"Focus: {q.get('focus_area', '')}"
        listen_text = f"Listen For: {q.get('suggested_answer', '')}"

        page.draw_rect(fitz.Rect(40, y, 555, y + 46), color=(0.97, 0.98, 0.99), fill=(0.97, 0.98, 0.99))
        page.insert_text((48, y + 13), q_text[:95], fontsize=8.5, fontname="helv", color=(0.08, 0.08, 0.15))
        page.insert_text((48, y + 26), focus_text[:95], fontsize=8, fontname="helv", color=(0.3, 0.3, 0.7))
        page.insert_text((48, y + 38), listen_text[:95], fontsize=7.5, fontname="helv", color=(0.4, 0.4, 0.4))
        y += 52

    # Footer
    page.draw_line((40, 810), (555, 810), color=(0.85, 0.85, 0.85), width=0.5)
    page.insert_text((40, 824), "Generated by TalentAI Screening Platform  |  Confidential Recruiter Dossier", fontsize=8, fontname="helv", color=(0.5, 0.5, 0.5))

    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes

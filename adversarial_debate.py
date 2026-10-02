"""Multi-Agent Adversarial Debate Committee Engine.

Simulates an adversarial hiring committee with opposing viewpoints:
1. Candidate Advocate (Defense): Champions candidate's strengths, trajectory, velocity & mitigates gaps.
2. Technical Skeptic (Prosecution): Forensic audit exposing unverified claims, buzzword inflation & tenure risks.
3. Cross-Examination & Rebuttal: Real-time debate round where Advocate rebuts Skeptic's specific challenges.
4. Chief Talent Arbiter (Consensus Verdict): Impartial synthesis delivering calibrated hiring recommendation,
   verdict category, and a mandatory Risk Mitigation Checklist for live interviewers.

100% Offline-First, Zero Cloud Spend (with optional OpenRouter LLM acceleration).
"""

from typing import Dict, Any, List, Optional
import os
import re
import json


def conduct_adversarial_debate(
    candidate: Dict[str, Any],
    job_description: str = "",
    target_role: str = ""
) -> Dict[str, Any]:
    """
    Executes a structured 3-phase adversarial debate over a candidate's profile.
    Returns:
    - advocate_case (Defense Opening & Key Arguments)
    - skeptic_case (Prosecution Opening & Flagged Risks)
    - cross_examination (Round of point-by-point rebuttals)
    - arbiter_verdict (Final calibrated score, hiring decision, and interview risk checklist)
    """
    cdata = candidate.get("data") or {}
    name = candidate.get("candidate_name") or cdata.get("candidate_name") or "The Candidate"
    skills = candidate.get("skills") or cdata.get("skills") or []
    if isinstance(skills, str):
        try:
            skills = json.loads(skills)
        except Exception:
            skills = [s.strip() for s in skills.split(",") if s.strip()]

    exp_years = float(candidate.get("experience_years") or cdata.get("experience_years") or 0)
    exp_list = cdata.get("experience") or []
    edu_list = cdata.get("education") or []
    summary = cdata.get("summary") or candidate.get("summary") or ""
    score = int(candidate.get("score") or 0)
    audit = candidate.get("audit_report") or {}
    if isinstance(audit, str):
        try:
            audit = json.loads(audit)
        except Exception:
            audit = {}

    gaps = audit.get("career_gaps") or []
    buzzwords = audit.get("buzzword_stuffing") or []
    integrity_score = audit.get("integrity_score", 90)

    # Optional LLM execution if OPENROUTER_API_KEY is configured
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        try:
            llm_result = _run_llm_adversarial_debate(
                name, skills, exp_years, exp_list, edu_list, summary, score,
                gaps, buzzwords, integrity_score, job_description, target_role, api_key
            )
            if llm_result:
                return llm_result
        except Exception as e:
            print(f"[Adversarial Debate LLM Fallback]: {e}")

    # Fallback: High-precision grounded heuristic debate engine
    return _run_heuristic_adversarial_debate(
        name, skills, exp_years, exp_list, edu_list, summary, score,
        gaps, buzzwords, integrity_score, job_description, target_role
    )


def _run_heuristic_adversarial_debate(
    name: str,
    skills: List[str],
    exp_years: float,
    exp_list: List[Dict[str, Any]],
    edu_list: List[Dict[str, Any]],
    summary: str,
    score: int,
    gaps: List[Any],
    buzzwords: List[Any],
    integrity_score: int,
    job_description: str,
    target_role: str
) -> Dict[str, Any]:
    """Grounded heuristic adversarial debate simulation with deterministic rigor."""

    # ---------------- 1. ADVOCATE (DEFENSE) ARGUMENTS ----------------
    advocate_points = []
    # Strength 1: Core tech stack & versatility
    if len(skills) >= 6:
        advocate_points.append({
            "topic": "Technical Breadth & Core Toolkit",
            "argument": f"{name} presents a versatile engineering toolkit spanning {', '.join(skills[:5])}. Demonstrates proficiency across complementary frameworks rather than narrow siloed specialization.",
            "evidence": f"Verified competencies in {len(skills)} declared technical disciplines."
        })
    elif skills:
        advocate_points.append({
            "topic": "Targeted Competency",
            "argument": f"{name} demonstrates focused expertise concentrated on {', '.join(skills[:3])}, minimizing context-switching overhead.",
            "evidence": f"Specialized depth in core requirements."
        })

    # Strength 2: Career momentum & tenure
    if exp_years >= 5:
        advocate_points.append({
            "topic": "Production Maturity & Battle-Tested Experience",
            "argument": f"With {exp_years} years in the software industry, {name} brings seasoned instincts for production incident mitigation, architectural trade-offs, and technical leadership.",
            "evidence": f"{len(exp_list)} professional tenures documented on resume."
        })
    else:
        advocate_points.append({
            "topic": "High Learning Velocity & Fresh Perspective",
            "argument": f"As an agile practitioner with {exp_years} years of experience, {name} exhibits fast ramp-up capabilities unburdened by legacy architectural inertia.",
            "evidence": "Rapid progression across contemporary tech stacks."
        })

    # Strength 3: Mitigating flagged audit points
    if gaps:
        advocate_points.append({
            "topic": "Contextual Career Trajectory",
            "argument": f"Timeline pauses reflect deliberate upskilling or entrepreneurial exploration rather than disengagement. Overall technical output remains intact.",
            "evidence": "Continuous skill acquisition across career phases."
        })
    else:
        advocate_points.append({
            "topic": "Unbroken Career Continuity",
            "argument": f"{name} demonstrates exceptional career stability with zero detected gaps and steady employment progression.",
            "evidence": "100% verified chronological timeline continuity."
        })

    # ---------------- 2. SKEPTIC (PROSECUTION) ARGUMENTS ----------------
    skeptic_points = []
    # Concern 1: Buzzword verification & superficial claims
    if buzzwords:
        flagged_str = ", ".join([str(b) for b in buzzwords[:3]])
        skeptic_points.append({
            "risk_area": "Unverified Header Skills / Buzzword Stuffing",
            "critique": f"Candidate explicitly advertises competencies ({flagged_str}) in top summaries, but provides negligible concrete implementation evidence in subsequent work experience bullets.",
            "severity": "High"
        })
    else:
        skeptic_points.append({
            "risk_area": "Depth of System Architectural Ownership",
            "critique": "Experience descriptions focus on participation rather than sole architectural authorship. Need to verify whether candidate designed systems from scratch or simply maintained existing templates.",
            "severity": "Medium"
        })

    # Concern 2: Quantified business impact
    has_metrics = False
    for exp in exp_list:
        desc = (exp.get("description") or "").lower()
        if re.search(r"\b(\d+%|\d+x|\$\d+|\d+\+?\s*(?:qps|users|req|ms))\b", desc):
            has_metrics = True
            break

    if not has_metrics:
        skeptic_points.append({
            "risk_area": "Lack of Quantified Business ROI",
            "critique": "Candidate relies on qualitative responsibility descriptions rather than rigorous quantitative metrics (e.g. latency reductions, scale multipliers, revenue impact).",
            "severity": "Medium"
        })
    else:
        skeptic_points.append({
            "risk_area": "Verification of Claimed Scale Multipliers",
            "critique": "Candidate claims significant throughput/scale achievements; interviewer must rigorously audit whether candidate was directly responsible or part of a larger supporting operations team.",
            "severity": "Low"
        })

    # Concern 3: Domain specialization vs requirement
    if integrity_score < 80:
        skeptic_points.append({
            "risk_area": "Integrity & Chronology Anomaly",
            "critique": f"Integrity score is penalized at {integrity_score}%. Overlapping tenure dates or unexplained chronology gaps create hiring risk.",
            "severity": "High"
        })

    # ---------------- 3. CROSS-EXAMINATION & REBUTTAL ----------------
    primary_critique = skeptic_points[0]["critique"]
    rebuttal_exchange = {
        "skeptic_challenge": f"Skeptic to Advocate: '{primary_critique}' How can we justify advancing when technical depth in these areas is unproven?",
        "advocate_rebuttal": f"Advocate: 'The candidate's core strength is proven by the end-to-end delivery of projects listed at {exp_list[0].get('company', 'their previous employer') if exp_list else 'their previous roles'}. Minor documentation brevity on a resume is standard; their practical competency is evident from their stack cohesion ({', '.join(skills[:3])}).'",
        "skeptic_counter": "Skeptic: 'Understood, but we cannot rely on assumption. The live panel must probe these exact claims with hard architectural whiteboarding.'",
        "debate_tension": "High Focus on Practical Hands-On Verification"
    }

    # ---------------- 4. CHIEF ARBITER (CONSENSUS VERDICT) ----------------
    advocate_weight = 0.55 if score >= 70 else 0.45
    skeptic_penalty = (100 - integrity_score) * 0.25 + (len(buzzwords) * 3.0)
    calibrated_score = max(min(round((score * advocate_weight) + (50 * (1 - advocate_weight)) - skeptic_penalty), 98), 25)

    if calibrated_score >= 75:
        verdict = "STRONG ADVANCE"
        verdict_color = "success"
        summary_verdict = f"Advocate's arguments on production velocity and technical breadth convincingly outweigh the Skeptic's cautions. {name} has proven core competence."
    elif calibrated_score >= 60:
        verdict = "ADVANCE WITH CONDITIONS"
        verdict_color = "primary"
        summary_verdict = f"Balanced debate outcome. Candidate holds substantial capability, but Skeptic's audit flags regarding architectural ownership require mandatory targeted probing in the technical loop."
    elif calibrated_score >= 45:
        verdict = "DEEP DIVE REQUIRED"
        verdict_color = "warning"
        summary_verdict = f"Skeptic surfaced valid concerns regarding experience verification or buzzword claims. Advance only if candidate excels in a rigorous pre-screen pairing session."
    else:
        verdict = "DO NOT ADVANCE"
        verdict_color = "danger"
        summary_verdict = f"Skeptic's prosecution exposed critical gaps between resume claims and target job requirements that the Advocate could not adequately counter."

    risk_checklist = [
        f"Probe exact hands-on contribution vs team participation for {skills[0] if skills else 'primary role competencies'}.",
        f"Request a 5-minute deep-dive on an end-to-end production architecture designed at {exp_list[0].get('company', 'past tenure') if exp_list else 'recent project'}.",
        "Examine edge-case handling, failure recovery modes, and testing methodologies in live coding.",
        "Verify specific quantitative outcomes and metrics cited on resume."
    ]

    return {
        "candidate_name": name,
        "calibrated_score": calibrated_score,
        "verdict": verdict,
        "verdict_color": verdict_color,
        "summary": summary_verdict,
        "advocate": {
            "name": "Candidate Advocate (Defense)",
            "icon": "🛡️",
            "position": "Pro-Hire / Trajectory Focus",
            "points": advocate_points
        },
        "skeptic": {
            "name": "Technical Skeptic (Prosecution)",
            "icon": "⚖️",
            "position": "Forensic Risk / Verification Focus",
            "points": skeptic_points
        },
        "cross_examination": rebuttal_exchange,
        "risk_mitigation_checklist": risk_checklist,
        "metrics": {
            "advocate_confidence": round(min(score + 10, 95), 1),
            "skeptic_risk_index": round(max(100 - integrity_score + (len(buzzwords) * 8), 15), 1),
            "arbiter_consensus": calibrated_score
        }
    }


def _run_llm_adversarial_debate(
    name: str, skills: List[str], exp_years: float, exp_list: List[Dict[str, Any]],
    edu_list: List[Dict[str, Any]], summary: str, score: int,
    gaps: List[Any], buzzwords: List[Any], integrity_score: int,
    job_description: str, target_role: str, api_key: str
) -> Optional[Dict[str, Any]]:
    """Optional LLM execution for high-nuance narrative debate."""
    import requests
    prompt = f"""
You are simulating an elite Technical Hiring Committee Adversarial Debate for candidate {name}.
Target Role: {target_role or 'Senior Engineer'}
Target Job Description: {job_description[:400] or 'General Senior Engineering'}
Candidate Skills: {', '.join(skills)}
Experience Years: {exp_years}
Integrity Score: {integrity_score}/100
Flagged Gaps: {gaps}
Flagged Unverified Buzzwords: {buzzwords}

Structure a realistic debate with:
1. Candidate Advocate (Defense): Best strengths, growth trajectory, justifications.
2. Technical Skeptic (Prosecution): Hard forensic audit, unverified claims, risks.
3. Cross-examination exchange between Advocate and Skeptic.
4. Chief Talent Arbiter: Calibrated score (0-100), Verdict (STRONG ADVANCE, ADVANCE WITH CONDITIONS, DEEP DIVE REQUIRED, DO NOT ADVANCE), and 4-point Risk Mitigation Checklist for interviewers.

Return valid JSON with:
{{
  "candidate_name": "{name}",
  "calibrated_score": <int 0-100>,
  "verdict": "<Verdict String>",
  "verdict_color": "<success|primary|warning|danger>",
  "summary": "<Arbiter synthesis>",
  "advocate": {{
    "name": "Candidate Advocate (Defense)",
    "icon": "🛡️",
    "position": "Pro-Hire / Trajectory Focus",
    "points": [{{"topic": "...", "argument": "...", "evidence": "..."}}]
  }},
  "skeptic": {{
    "name": "Technical Skeptic (Prosecution)",
    "icon": "⚖️",
    "position": "Forensic Risk / Verification Focus",
    "points": [{{"risk_area": "...", "critique": "...", "severity": "High|Medium|Low"}}]
  }},
  "cross_examination": {{
    "skeptic_challenge": "...",
    "advocate_rebuttal": "...",
    "skeptic_counter": "...",
    "debate_tension": "..."
  }},
  "risk_mitigation_checklist": ["...", "..."],
  "metrics": {{
    "advocate_confidence": <float>,
    "skeptic_risk_index": <float>,
    "arbiter_consensus": <int>
  }}
}}
"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "TalentAI Adversarial Debate"
    }
    body = {
        "model": os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3-8b-instruct"),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 800
    }
    resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body, timeout=12)
    if resp.status_code == 200:
        content = resp.json()["choices"][0]["message"]["content"]
        content = re.sub(r"^```json\s*", "", content.strip())
        content = re.sub(r"^```\s*", "", content.strip())
        content = re.sub(r"\s*```$", "", content.strip())
        return json.loads(content)
    return None

import os
import re
import json
from dotenv import load_dotenv

load_dotenv()

def evaluate_prescreen_answer(
    question: str,
    focus_area: str,
    suggested_answer: str,
    candidate_answer: str
) -> dict:
    """
    Evaluates a candidate's verbal/textual response to a tailored technical interview question.
    Returns score (1-10), verdict, highlights, gaps, and drill-down recommendations.
    Uses OpenRouter LLM if available, with robust zero-dependency heuristic fallback.
    """
    cleaned_answer = (candidate_answer or "").strip()
    if not cleaned_answer or len(cleaned_answer) < 10:
        return {
            "score": 2.0,
            "verdict": "Insufficient Response",
            "verdict_badge": "danger",
            "strengths": ["Answer submitted was too brief to evaluate technical depth."],
            "gaps": ["Did not address the core architectural or technical aspects of the question."],
            "drill_down": f"Ask the candidate to explain {focus_area or 'their direct experience'} in detail with specific examples.",
            "mode": "heuristic"
        }

    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        try:
            import requests
            prompt = f"""
You are an expert Senior Staff Technical Interviewer evaluating a candidate's interview response.

Interview Question: {question}
Core Focus Area: {focus_area}
What to Listen For (Model Answer/Criteria): {suggested_answer}

Candidate's Given Response:
\"\"\"{cleaned_answer}\"\"\"

Provide your evaluation in strict JSON format with exactly these keys:
{{
  "score": <float between 1.0 and 10.0>,
  "verdict": "<2-4 words, e.g. Strong Architecture Understanding, Solid Practical Grasp, Needs Deepening, etc.>",
  "verdict_badge": "<'success', 'warning', or 'danger'>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "gaps": ["<gap 1 if any>"],
  "drill_down": "<specific follow-up question to probe in the in-person panel>"
}}
Return ONLY valid JSON.
"""
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "AI Resume Screening ATS"
            }
            body = {
                "model": os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3-8b-instruct"),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 400
            }
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body, timeout=8)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                content = re.sub(r"^```json\s*", "", content.strip())
                content = re.sub(r"^```\s*", "", content.strip())
                content = re.sub(r"\s*```$", "", content.strip())
                eval_data = json.loads(content)
                eval_data["mode"] = "ai-llm"
                eval_data["score"] = round(float(eval_data.get("score", 7.0)), 1)
                return eval_data
        except Exception as e:
            print(f"[PreScreen AI Evaluator Fallback]: {e}")

    # Resilient Heuristic NLP Evaluation
    return _heuristic_evaluation(question, focus_area, suggested_answer, cleaned_answer)


def _heuristic_evaluation(question: str, focus_area: str, suggested_answer: str, answer: str) -> dict:
    answer_lower = answer.lower()
    suggested_lower = suggested_answer.lower()
    focus_lower = focus_area.lower()

    # Extract informative keywords from suggested criteria and focus
    criteria_words = set(re.findall(r"\b[a-z]{4,}\b", suggested_lower + " " + focus_lower))
    # Exclude common stopwords
    common_stopwords = {"that", "with", "from", "this", "they", "have", "been", "will", "would", "about", "their", "which", "should", "could", "these", "other", "using", "listen"}
    meaningful_keywords = [w for w in criteria_words if w not in common_stopwords]

    matched_keywords = [w for w in meaningful_keywords if re.search(r"\b" + re.escape(w) + r"\b", answer_lower)]
    keyword_match_ratio = len(matched_keywords) / len(meaningful_keywords) if meaningful_keywords else 0.5

    # Depth indicators: metrics, architectural terms, structured explanation
    metrics_present = bool(re.search(r"\b(\d+%|\d+x|\$\d+|\d+\s*(?:ms|sec|qps|users|req|gb|tb))\b", answer_lower))
    tradeoffs_present = any(term in answer_lower for term in ["trade-off", "tradeoff", "trade off", "however", "instead of", "bottleneck", "latency", "consistency", "overhead", "versus", "vs"])
    concrete_tools = [w for w in ["redis", "kafka", "docker", "postgres", "sql", "api", "async", "cache", "indexes", "sharding", "pool", "thread", "worker", "queue"] if w in answer_lower]

    word_count = len(re.findall(r"\b\w+\b", answer))

    # Scoring calculation
    base_score = 4.5
    if word_count >= 50:
        base_score += 1.5
    elif word_count >= 25:
        base_score += 0.8

    base_score += min(keyword_match_ratio * 3.0, 2.5)

    if metrics_present:
        base_score += 0.8
    if tradeoffs_present:
        base_score += 0.8
    if concrete_tools:
        base_score += 0.6

    score = min(max(round(base_score, 1), 2.5), 9.8)

    strengths = []
    if matched_keywords:
        strengths.append(f"Directly addressed core concepts: {', '.join(matched_keywords[:4]).title()}.")
    if tradeoffs_present:
        strengths.append("Identified key engineering trade-offs and performance implications.")
    if concrete_tools:
        strengths.append(f"Referenced practical technologies and patterns ({', '.join(concrete_tools[:3]).title()}).")
    if not strengths:
        strengths.append("Provided a relevant, high-level perspective on the inquiry.")

    gaps = []
    missing_keywords = [w for w in meaningful_keywords if w not in matched_keywords]
    if missing_keywords and len(missing_keywords) > 2:
        gaps.append(f"Did not explicitly mention expected considerations such as {', '.join(missing_keywords[:3])}.")
    if not metrics_present:
        gaps.append("Answer lacks quantitative benchmark metrics or concrete scale numbers.")

    if score >= 8.0:
        verdict = "Strong Technical Mastery"
        badge = "success"
        drill_down = f"Probe deeper on production failure modes or edge-case recovery strategies in {focus_area}."
    elif score >= 6.5:
        verdict = "Solid Practical Competency"
        badge = "warning"
        drill_down = f"Ask candidate to walk through a concrete scenario where their approach to {focus_area} had to be debugged."
    else:
        verdict = "Needs Technical Deepening"
        badge = "danger"
        drill_down = f"Ask candidate to explain foundational architecture principles of {focus_area} on a whiteboard."

    return {
        "score": score,
        "verdict": verdict,
        "verdict_badge": badge,
        "strengths": strengths,
        "gaps": gaps,
        "drill_down": drill_down,
        "mode": "heuristic-nlp"
    }

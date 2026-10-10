"""Dynamic Adaptive Technical Interview Engine.

Provides:
1. Real-time answer evaluation across technical depth, precision, and architectural trade-offs.
2. Dynamic follow-up generation: detects vague or unverified technical assertions and
   generates adaptive drill-down questions targeting candidate weak spots.
3. Interviewer Rubric & What to Listen For on the follow-up question.

100% Offline-First with optional OpenRouter LLM acceleration.
"""

from typing import Dict, Any, List, Optional
import os
import re
import json


def evaluate_and_generate_adaptive_followup(
    question: str,
    focus_area: str,
    candidate_answer: str,
    candidate_skills: Optional[List[str]] = None,
    candidate_tenure: float = 0.0
) -> Dict[str, Any]:
    """
    Evaluates a candidate's answer to an interview question and generates a dynamic
    adaptive follow-up question probing deeper into edge cases, architecture, or vagueness.
    """
    cleaned_answer = (candidate_answer or "").strip()
    if not cleaned_answer or len(cleaned_answer) < 15:
        return {
            "depth_score": 2.5,
            "verdict": "Vague / Insufficient Depth",
            "verdict_badge": "danger",
            "feedback": "The response was brief and lacked concrete technical specifics or implementation details.",
            "detected_strengths": [],
            "flagged_ambiguities": ["Answer did not address underlying system mechanics or operational challenges."],
            "adaptive_followup": f"Could you walk me through the step-by-step implementation of how you worked with {focus_area or 'this technology'} in production, specifically highlighting a concrete outage or failure case you resolved?",
            "interviewer_rubric": "Listen for specific architecture diagrams, failure modes, logging, and measurable trade-offs rather than generic textbook definitions."
        }

    # Optional LLM execution
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        try:
            llm_result = _run_llm_adaptive_followup(
                question, focus_area, cleaned_answer, candidate_skills or [], candidate_tenure, api_key
            )
            if llm_result:
                return llm_result
        except Exception as e:
            print(f"[Adaptive Interview LLM Fallback]: {e}")

    # Heuristic dynamic evaluation & follow-up generator
    return _run_heuristic_adaptive_followup(
        question, focus_area, cleaned_answer, candidate_skills or [], candidate_tenure
    )


def _run_heuristic_adaptive_followup(
    question: str,
    focus_area: str,
    answer: str,
    skills: List[str],
    tenure: float
) -> Dict[str, Any]:
    """Deterministic, high-rigor technical analysis of interview responses."""
    ans_lower = answer.lower()

    # 1. Depth & metric signals
    has_metrics = bool(re.search(r"\b(\d+%\.?\d*|\d+x|\$\d+|\d+\+?\s*(?:ms|sec|qps|users|req|gb|tb|mb|k))\b", ans_lower))
    has_tradeoffs = any(t in ans_lower for t in ["trade-off", "tradeoff", "downside", "bottleneck", "latency", "overhead", "concurrency", "instead of", "race condition", "memory leak"])
    has_edge_cases = any(t in ans_lower for t in ["retry", "circuit breaker", "failover", "timeout", "idempotent", "fallback", "dead letter", "rate limit"])
    has_architecture = any(t in ans_lower for t in ["scale", "cluster", "distributed", "microservice", "partition", "sharding", "replica", "async", "event-driven"])

    # Base scoring
    score = 3.5
    strengths = []
    ambiguities = []

    if has_metrics:
        score += 1.8
        strengths.append("Incorporates quantified performance metrics and measurable impact.")
    else:
        ambiguities.append("Relies on qualitative claims without measurable scale or latency impact numbers.")

    if has_tradeoffs:
        score += 1.8
        strengths.append("Demonstrates senior engineering maturity by articulating architectural trade-offs.")
    else:
        ambiguities.append("Presents a one-sided solution without discussing alternative designs or limitations.")

    if has_edge_cases:
        score += 1.4
        strengths.append("Explicitly accounts for failure recovery, resilience, and system edge cases.")
    else:
        ambiguities.append("Does not mention failure modes, recovery strategies, or error states.")

    if has_architecture:
        score += 1.4
        strengths.append("Grounded in distributed systems patterns and scalability.")

    depth_score = round(min(max(score, 2.5), 9.8), 1)

    if depth_score >= 8.0:
        verdict = "Staff-Level Architectural Mastery"
        verdict_badge = "success"
        adaptive_followup = f"You clearly understand the standard implementation for {focus_area or 'this architecture'}. Under extreme multi-region disaster scenarios or partition network splits, how would you prevent data inconsistency and ensure deterministic recovery?"
        rubric = "Listen for quorum calculations, split-brain mitigation (Raft/Paxos), idempotency keys, and eventual consistency reconcilers."
    elif depth_score >= 6.0:
        verdict = "Solid Practical Engineering Grasp"
        verdict_badge = "primary"
        adaptive_followup = f"You outlined a viable workflow for {focus_area or 'the problem'}. If traffic scaled by 10x tomorrow, what specific bottleneck would break first, and how would you redesign the bottlenecks without increasing infrastructure costs 10x?"
        rubric = "Look for caching strategies (write-through/read-through), database indexing/read replicas, queue buffering, or asynchronous task offloading."
    else:
        verdict = "Needs Architectural Deepening"
        verdict_badge = "warning"
        adaptive_followup = f"In your answer regarding {focus_area or 'this design'}, how did you personally test and benchmark this system before pushing to production? What automated observability or alerting did you configure?"
        rubric = "Look for concrete test framework experience (pytest, k6, Locust), profiling tools, and APM metrics (Prometheus, Datadog)."

    return {
        "depth_score": depth_score,
        "verdict": verdict,
        "verdict_badge": verdict_badge,
        "feedback": f"Evaluated candidate response for {focus_area or 'technical inquiry'}. Score: {depth_score}/10.",
        "detected_strengths": strengths if strengths else ["Basic familiarity with the discussed tooling."],
        "flagged_ambiguities": ambiguities if ambiguities else ["Minor ambiguity regarding extreme edge-case recovery."],
        "adaptive_followup": adaptive_followup,
        "interviewer_rubric": rubric
    }


def _run_llm_adaptive_followup(
    question: str,
    focus_area: str,
    answer: str,
    skills: List[str],
    tenure: float,
    api_key: str
) -> Optional[Dict[str, Any]]:
    """Optional LLM execution for highly adaptive, nuanced technical probing."""
    import requests
    prompt = f"""
You are a Principal Software Architect conducting an adaptive technical interview.
Original Question: {question}
Focus Area: {focus_area}
Candidate's Given Answer:
\"\"\"{answer}\"\"\"

Analyze the answer for technical depth, missing edge cases, and hand-waving assertions.
Generate an adaptive follow-up drill-down question that aggressively probes whatever the candidate left vague or untested.

Return valid JSON with:
{{
  "depth_score": <float 1.0 - 10.0>,
  "verdict": "<e.g. Staff-Level Depth, Practical Competency, Needs Deepening>",
  "verdict_badge": "<success|primary|warning|danger>",
  "feedback": "<concise evaluation summary>",
  "detected_strengths": ["...", "..."],
  "flagged_ambiguities": ["...", "..."],
  "adaptive_followup": "<direct, piercing follow-up question>",
  "interviewer_rubric": "<what to listen for in candidate's reply>"
}}
"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "TalentAI Adaptive Interview"
    }
    body = {
        "model": os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3-8b-instruct"),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 500
    }
    resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body, timeout=10)
    if resp.status_code == 200:
        content = resp.json()["choices"][0]["message"]["content"]
        content = re.sub(r"^```json\s*", "", content.strip())
        content = re.sub(r"^```\s*", "", content.strip())
        content = re.sub(r"\s*```$", "", content.strip())
        data = json.loads(content)
        data["depth_score"] = round(float(data.get("depth_score", 7.0)), 1)
        return data
    return None

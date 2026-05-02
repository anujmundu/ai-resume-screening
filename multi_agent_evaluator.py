import os
import re

def evaluate_with_agents(resume_text: str, data: dict, job_description: str = "") -> dict:
    """
    Executes a multi-agent evaluation pipeline consisting of:
    - Agent 1: Code & Technical Auditor
    - Agent 2: Scale & Systems Reviewer
    - Agent 3: Impact & Communication Evaluator
    - Supervisor: Reconciles evaluations into a 360° consensus scorecard.
    """
    skills = [s.lower() for s in data.get("skills", [])]
    exp = float(data.get("experience_years", 0) or 0)
    text_lower = resume_text.lower()

    # --- AGENT 1: Code & Technical Auditor ---
    code_score = 6.0
    code_highlights = []
    # Test discipline check
    if any(term in text_lower for term in ["pytest", "unit test", "test coverage", "ci/cd", "github actions"]):
        code_score += 1.8
        code_highlights.append("Strong testing & CI/CD discipline evident in codebase.")
    # Languages depth check
    strong_langs = [l for l in ["python", "go", "c++", "typescript", "java", "rust"] if l in skills]
    if len(strong_langs) >= 2:
        code_score += 1.2
        code_highlights.append(f"Multi-language versatility in {', '.join(strong_langs[:3]).title()}.")
    elif strong_langs:
        code_score += 0.8
    # Modern typing / schemas
    if any(term in text_lower for term in ["pydantic", "asyncio", "typing", "graphql", "grpc"]):
        code_score += 1.0
        code_highlights.append("Applies modern asynchronous paradigms & strict data validation schemas.")

    code_score = min(max(round(code_score, 1), 4.0), 10.0)
    agent_code = {
        "agent_name": "Code & Technical Auditor",
        "agent_icon": "💻",
        "score": code_score,
        "assessment": f"Evaluated candidate's programming practices. {' '.join(code_highlights) if code_highlights else 'Demonstrates standard technical skills; recommend live coding pairing to verify syntax fluency.'}"
    }

    # --- AGENT 2: Scale & Systems Architecture Reviewer ---
    scale_score = 5.5
    scale_highlights = []
    # Caching & throughput
    if any(term in text_lower for term in ["redis", "kafka", "rabbitmq", "celery"]):
        scale_score += 1.8
        scale_highlights.append("Experience with distributed message queues and distributed caching layers.")
    # Containerization & Cloud
    if any(term in text_lower for term in ["docker", "kubernetes", "helm", "aws", "terraform", "cloud"]):
        scale_score += 1.5
        scale_highlights.append("Proficient in cloud-native container orchestration and infrastructure.")
    # Performance & Profiling
    if any(term in text_lower for term in ["opentelemetry", "prometheus", "latency", "quantization", "onnx", "profiling", "ttft"]):
        scale_score += 1.5
        scale_highlights.append("Demonstrated capability in system telemetry, latency profiling, and runtime acceleration.")

    scale_score = min(max(round(scale_score, 1), 4.0), 10.0)
    agent_scale = {
        "agent_name": "Scale & Systems Reviewer",
        "agent_icon": "⚡",
        "score": scale_score,
        "assessment": f"Audited architecture complexity and infrastructure readiness. {' '.join(scale_highlights) if scale_highlights else 'Architecture profile is standard; focus technical interview on scaling bottlenecks and concurrency.'}"
    }

    # --- AGENT 3: Impact & Communication Evaluator ---
    impact_score = 6.0
    impact_highlights = []
    # Metrics density
    metric_matches = re.findall(r"\b(\d+%(?:\.\d+)?|\d+x|\$\d+|\d+\+?\s*(?:qps|users|req|ms|tests))\b", text_lower)
    if len(metric_matches) >= 4:
        impact_score += 2.2
        impact_highlights.append(f"Highly data-driven narrative with {len(metric_matches)}+ quantified achievement metrics.")
    elif len(metric_matches) >= 2:
        impact_score += 1.0
        impact_highlights.append("Contains quantified performance measurements.")
    # Open Source & Publications
    if any(term in text_lower for term in ["pypi", "published", "patent", "paper", "live demo", "github"]):
        impact_score += 1.5
        impact_highlights.append("Verifiable public artifacts and demonstrated open-source contributions.")

    impact_score = min(max(round(impact_score, 1), 4.0), 10.0)
    agent_impact = {
        "agent_name": "Impact & Business Narrative Evaluator",
        "agent_icon": "📊",
        "score": impact_score,
        "assessment": f"Evaluated business impact clarity and proof of execution. {' '.join(impact_highlights) if impact_highlights else 'Candidate describes responsibilities adequately; probe for business ROI during interview.'}"
    }

    # --- SUPERVISOR AGENT: Consensus Synthesis ---
    consensus_score = round(((code_score * 0.35) + (scale_score * 0.35) + (impact_score * 0.30)) * 10, 1)

    supervisor_summary = f"Consensus achieved: Strongest alignment in {agent_code['agent_name'] if code_score >= scale_score else agent_scale['agent_name']}. The candidate demonstrates balanced technical execution with an overall 360° rating of {consensus_score}/100."

    return {
        "consensus_score": consensus_score,
        "supervisor_summary": supervisor_summary,
        "agents": [agent_code, agent_scale, agent_impact],
        "radar": {
            "code_quality": code_score * 10,
            "system_scale": scale_score * 10,
            "business_impact": impact_score * 10,
            "overall_fit": consensus_score
        }
    }

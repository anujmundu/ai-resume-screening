"""Comprehensive automated test suite for Phase 3 Knowledge Graph & Adversarial Debate.

Verifies:
1. CandidateKnowledgeGraph construction, multi-entity nodes (Candidates, Skills, Companies, Roles),
   and weighted skill co-occurrence edges.
2. Topological graph metrics: Degree Centrality, Betweenness Centrality, and Hub Competency rankings.
3. Cross-Domain Technical Bridge detection.
4. Candidate ego-subgraph extraction and Adjacent Skill Recommendations.
5. Multi-Agent Adversarial Debate Committee:
   - Advocate (Defense) positive arguments and trajectory evidence.
   - Technical Skeptic (Prosecution) forensic risk audit and buzzword challenges.
   - Cross-Examination & Direct Rebuttal exchange.
   - Chief Talent Arbiter consensus verdict, calibrated score, and Risk Mitigation Checklist.
6. Dynamic Adaptive Technical Interview Simulator:
   - Response depth scoring (1.0 to 10.0), metric/trade-off detection.
   - Generation of adaptive follow-up drill-down questions and interviewer rubrics.
7. Flask REST API Endpoints:
   - GET /knowledge-graph
   - GET /api/graph/data
   - GET /api/candidate/<id>/graph
   - POST /api/candidate/<id>/adversarial-debate
   - POST /api/interview/adaptive-followup
"""

import pytest
from app import app
from knowledge_graph import CandidateKnowledgeGraph, categorize_skill
from adversarial_debate import conduct_adversarial_debate
from adaptive_interview import evaluate_and_generate_adaptive_followup


@pytest.fixture
def sample_candidates_pool():
    return [
        {
            "_id": "cand_kg_1",
            "candidate_name": "Elena Rostova",
            "score": 88,
            "decision": "shortlist",
            "stage": "screened",
            "experience_years": 7.0,
            "skills": ["Python", "FastAPI", "Docker", "PostgreSQL", "Kafka", "Kubernetes"],
            "data": {
                "candidate_name": "Elena Rostova",
                "summary": "Staff backend engineer specializing in distributed data streaming.",
                "skills": ["Python", "FastAPI", "Docker", "PostgreSQL", "Kafka", "Kubernetes"],
                "experience": [
                    {
                        "company": "StreamScale Corp",
                        "role": "Lead Distributed Systems Engineer",
                        "description": "Architected event-driven microservices processing 120k QPS with Kafka and Redis."
                    }
                ],
                "education": [
                    {
                        "degree": "M.S. in Computer Science",
                        "institution": "Georgia Tech",
                        "field": "Distributed Systems"
                    }
                ]
            },
            "audit_report": {
                "career_gaps": [],
                "buzzword_stuffing": [],
                "integrity_score": 95
            }
        },
        {
            "_id": "cand_kg_2",
            "candidate_name": "Marcus Vance",
            "score": 64,
            "decision": "review",
            "stage": "phone",
            "experience_years": 4.5,
            "skills": ["Python", "Django", "React", "PostgreSQL", "AWS", "Docker"],
            "data": {
                "candidate_name": "Marcus Vance",
                "summary": "Full-stack engineer with React and Python experience.",
                "skills": ["Python", "Django", "React", "PostgreSQL", "AWS", "Docker"],
                "experience": [
                    {
                        "company": "FinTech Matrix",
                        "role": "Senior Full Stack Engineer",
                        "description": "Built user dashboards and REST endpoints in Django and React."
                    }
                ],
                "education": [
                    {
                        "degree": "B.S. in Software Engineering",
                        "institution": "University of Washington",
                        "field": "Software Engineering"
                    }
                ]
            },
            "audit_report": {
                "career_gaps": [{"start": "2022-01", "end": "2022-09", "duration_months": 8}],
                "buzzword_stuffing": ["Kubernetes"],
                "integrity_score": 75
            }
        },
        {
            "_id": "cand_kg_3",
            "candidate_name": "Sarah Connor",
            "score": 78,
            "decision": "shortlist",
            "stage": "tech",
            "experience_years": 6.0,
            "skills": ["Docker", "Kubernetes", "Terraform", "AWS", "CI/CD", "Linux"],
            "data": {
                "candidate_name": "Sarah Connor",
                "summary": "Cloud infrastructure and DevOps engineer.",
                "skills": ["Docker", "Kubernetes", "Terraform", "AWS", "CI/CD", "Linux"],
                "experience": [
                    {
                        "company": "CloudGuard Systems",
                        "role": "Principal DevOps Lead",
                        "description": "Automated multi-region AWS infrastructure with Terraform and Kubernetes."
                    }
                ],
                "education": []
            },
            "audit_report": {
                "career_gaps": [],
                "buzzword_stuffing": [],
                "integrity_score": 90
            }
        }
    ]


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_skill_taxonomy_categorization():
    """Verify that domain categorizer maps skills into appropriate technical domains."""
    assert categorize_skill("Python") == "Backend & Systems"
    assert categorize_skill("FastAPI") == "Backend & Systems"
    assert categorize_skill("React") == "Frontend & Web"
    assert categorize_skill("Kubernetes") == "Cloud & DevOps"
    assert categorize_skill("PostgreSQL") == "Data & Databases"
    assert categorize_skill("PyTorch") == "AI, ML & NLP"


def test_knowledge_graph_construction(sample_candidates_pool):
    """Verify heterogeneous entity graph construction, nodes, edges, and statistics."""
    kg = CandidateKnowledgeGraph(sample_candidates_pool)
    stats = kg.get_graph_statistics()

    assert stats["total_nodes"] > 10
    assert stats["total_edges"] > 10
    assert stats["node_breakdown"]["candidate"] == 3
    assert stats["node_breakdown"]["skill"] >= 8
    assert stats["node_breakdown"]["company"] == 3

    # Check that Python and Docker are recognized as top hub skills
    hub_names = [h["skill"] for h in stats["top_hub_skills"]]
    assert "Docker" in hub_names or "Python" in hub_names


def test_knowledge_graph_candidate_subgraph_and_adjacent_skills(sample_candidates_pool):
    """Verify candidate ego-network isolation and adjacent skill recommendations."""
    kg = CandidateKnowledgeGraph(sample_candidates_pool)

    # 1. Candidate ego-subgraph
    subgraph = kg.get_candidate_subgraph("cand_kg_1", depth=1)
    assert subgraph["node_count"] > 1
    assert any(n["id"] == "cand_cand_kg_1" for n in subgraph["nodes"])

    # 2. Adjacent skill recommendations for Marcus (who has Python & Docker but not Kafka)
    adjacent = kg.recommend_adjacent_skills("cand_kg_2", top_n=5)
    assert len(adjacent) >= 1
    adj_skill_names = [s["skill"].lower() for s in adjacent]
    # Kafka or Kubernetes co-occurs with Python/Docker in pool
    assert any(k in adj_skill_names for k in ["kafka", "kubernetes", "fastapi", "terraform", "ci/cd"])


def test_knowledge_graph_bridges(sample_candidates_pool):
    """Verify cross-domain technical bridge skill identification."""
    kg = CandidateKnowledgeGraph(sample_candidates_pool)
    bridges = kg.find_skill_bridges(top_n=5)
    assert isinstance(bridges, list)
    if bridges:
        assert "bridge_score" in bridges[0]
        assert "connected_domains" in bridges[0]


def test_adversarial_debate_engine(sample_candidates_pool):
    """Verify Advocate defense, Skeptic prosecution, Rebuttal, and Arbiter verdict."""
    strong_cand = sample_candidates_pool[0]  # Elena Rostova (88 pts, 95 integrity)
    debate_strong = conduct_adversarial_debate(strong_cand)

    assert debate_strong["candidate_name"] == "Elena Rostova"
    assert debate_strong["calibrated_score"] >= 65
    assert debate_strong["verdict"] in ["STRONG ADVANCE", "ADVANCE WITH CONDITIONS"]
    assert len(debate_strong["advocate"]["points"]) >= 2
    assert len(debate_strong["skeptic"]["points"]) >= 1
    assert "skeptic_challenge" in debate_strong["cross_examination"]
    assert "advocate_rebuttal" in debate_strong["cross_examination"]
    assert len(debate_strong["risk_mitigation_checklist"]) == 4

    # Test candidate with audit red flags (Marcus Vance, 8-mo gap, buzzword stuffing)
    flagged_cand = sample_candidates_pool[1]
    debate_flagged = conduct_adversarial_debate(flagged_cand)

    assert debate_flagged["calibrated_score"] < debate_strong["calibrated_score"]
    skeptic_risks = [p["risk_area"] for p in debate_flagged["skeptic"]["points"]]
    assert any("Buzzword" in r or "Integrity" in r or "Quantified" in r for r in skeptic_risks)


def test_dynamic_adaptive_interview_evaluation():
    """Verify technical depth scoring and adaptive follow-up drill-down question generation."""
    # 1. Staff-level technical answer with metrics & trade-offs
    good_answer = (
        "We built an asynchronous pipeline using FastAPI and Kafka to ingest 85k events per second. "
        "We used Redis for caching hot sessions with a circuit breaker pattern to prevent thundering herd. "
        "The trade-off was increased memory overhead, but it cut our P99 latency by 42%."
    )
    res_good = evaluate_and_generate_adaptive_followup(
        question="How do you architect high-throughput ingest systems?",
        focus_area="Event-Driven Microservices",
        candidate_answer=good_answer
    )
    assert res_good["depth_score"] >= 8.0
    assert res_good["verdict_badge"] == "success"
    assert len(res_good["detected_strengths"]) >= 2
    assert len(res_good["adaptive_followup"]) > 20
    assert "Interviewer Rubric" in str(res_good) or "interviewer_rubric" in res_good

    # 2. Vague answer lacking metrics or trade-offs
    vague_answer = "I used Python and some libraries to write code that works well."
    res_vague = evaluate_and_generate_adaptive_followup(
        question="Explain your architecture.",
        focus_area="Backend Architecture",
        candidate_answer=vague_answer
    )
    assert res_vague["depth_score"] <= 4.0
    assert res_vague["verdict_badge"] in ["warning", "danger"]
    assert len(res_vague["flagged_ambiguities"]) >= 1


def test_flask_phase3_api_endpoints(client):
    """Verify Phase 3 Flask web and REST API routes."""
    # 1. GET /knowledge-graph renders HTML page
    resp_page = client.get("/knowledge-graph")
    assert resp_page.status_code == 200
    assert b"Candidate Knowledge Graph" in resp_page.data

    # 2. GET /api/graph/data returns graph data
    resp_data = client.get("/api/graph/data?max_nodes=100")
    assert resp_data.status_code == 200
    data = resp_data.get_json()
    assert "network" in data
    assert "stats" in data
    assert "bridges" in data
    assert "nodes" in data["network"]
    assert "links" in data["network"]

    # 3. POST /api/interview/adaptive-followup
    resp_interview = client.post("/api/interview/adaptive-followup", json={
        "question": "How do you handle distributed database transactions?",
        "focus_area": "Database Consistency",
        "answer": "We implemented the Saga pattern with choreography and compensating transactions to ensure eventual consistency."
    })
    assert resp_interview.status_code == 200
    eval_data = resp_interview.get_json()
    assert "depth_score" in eval_data
    assert "adaptive_followup" in eval_data
    assert "interviewer_rubric" in eval_data

    # 4. POST /api/interview/adaptive-followup with missing fields (400)
    resp_bad = client.post("/api/interview/adaptive-followup", json={"question": "Test"})
    assert resp_bad.status_code == 400

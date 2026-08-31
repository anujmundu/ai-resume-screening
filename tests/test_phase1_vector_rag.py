"""Comprehensive automated test suite for Phase 1 Vector Search, RAG, and XAI.

Verifies:
1. CandidateVectorIndex building, semantic cosine queries, and peer similarity.
2. CandidateRAGRetriever semantic chunking, grounded retrieval, and source citations.
3. SemanticAlignmentEngine multi-dimensional vector alignment (Skills, Exp, Edu).
4. XAIFactorAttribution SHAP-style positive/negative score decomposition.
5. Flask REST endpoints for vector search, RAG inquiry, and alignment.
"""

import pytest
from app import app
from vector_search import CandidateVectorIndex
from rag_engine import chunk_candidate_profile, CandidateRAGRetriever
from semantic_alignment import compute_semantic_alignment
from xai_engine import explain_candidate_score


@pytest.fixture
def sample_candidates():
    return [
        {
            "_id": "cand_01",
            "score": 85,
            "decision": "shortlist",
            "stage": "shortlisted",
            "job_description": "Senior Backend Engineer with Python, FastAPI, Docker, and PostgreSQL.",
            "data": {
                "candidate_name": "Carlos Mendoza",
                "email": "carlos@example.com",
                "summary": "Senior backend specialist with 6 years experience building scalable microservices in Python, FastAPI, and Docker.",
                "skills": ["Python", "FastAPI", "Docker", "PostgreSQL", "Redis", "CI/CD"],
                "experience": [
                    {
                        "role": "Lead Backend Engineer",
                        "company": "CloudScale Inc",
                        "duration": "2021 - Present",
                        "description": "Architected low-latency microservices with FastAPI and Docker. Optimized PostgreSQL queries reducing latency by 40%."
                    }
                ],
                "education": [
                    {
                        "degree": "B.Tech in Computer Science",
                        "field": "Computer Science",
                        "institution": "National Institute of Technology",
                        "graduation_year": "2018"
                    }
                ]
            },
            "audit_report": {
                "career_gaps": [],
                "buzzword_stuffing": [],
                "integrity_score": 95
            },
            "score_breakdown": {
                "skills": 36,
                "experience": 26,
                "education": 14,
                "completeness": 14
            }
        },
        {
            "_id": "cand_02",
            "score": 45,
            "decision": "reject",
            "stage": "rejected",
            "job_description": "Senior Backend Engineer with Python, FastAPI, Docker, and PostgreSQL.",
            "data": {
                "candidate_name": "Chloe Bennett",
                "email": "chloe@example.com",
                "summary": "Creative UI designer with expertise in Figma, Photoshop, Illustrator, and typography.",
                "skills": ["Figma", "Photoshop", "Illustrator", "UI/UX", "Wireframing"],
                "experience": [
                    {
                        "role": "Senior Graphic Designer",
                        "company": "DesignStudio",
                        "duration": "2020 - Present",
                        "description": "Designed mobile UI wireframes and brand guidelines in Figma."
                    }
                ],
                "education": [
                    {
                        "degree": "Bachelor of Fine Arts",
                        "field": "Design",
                        "institution": "Art Academy",
                        "graduation_year": "2019"
                    }
                ]
            },
            "audit_report": {
                "career_gaps": [{"duration_months": 8}],
                "buzzword_stuffing": ["Python"],
                "integrity_score": 75
            },
            "score_breakdown": {
                "skills": 12,
                "experience": 12,
                "education": 8,
                "completeness": 13
            }
        }
    ]


# ---------------- 1. Vector Search Tests ----------------

def test_vector_index_building_and_search(sample_candidates):
    idx = CandidateVectorIndex()
    indexed_count = idx.build_index(sample_candidates)
    assert indexed_count == 2
    assert idx.is_fitted is True

    # Search for backend Python skills
    results = idx.search("FastAPI and Python backend microservices", top_k=2)
    assert len(results) >= 1
    assert results[0]["name"] == "Carlos Mendoza"
    assert results[0]["similarity_score"] > 10.0

    # Search for design skills
    results_design = idx.search("Figma wireframing and graphic design", top_k=2)
    assert len(results_design) >= 1
    assert results_design[0]["name"] == "Chloe Bennett"


def test_vector_similar_candidates(sample_candidates):
    idx = CandidateVectorIndex()
    idx.build_index(sample_candidates)
    
    similar = idx.find_similar_candidates("cand_01", top_k=2)
    assert isinstance(similar, list)
    # Target candidate Carlos shouldn't return himself
    for c in similar:
        assert c["id"] != "cand_01"


# ---------------- 2. Evidence-Grounded RAG Tests ----------------

def test_rag_chunking(sample_candidates):
    c1 = sample_candidates[0]
    chunks = chunk_candidate_profile(c1)
    assert len(chunks) >= 3
    
    sections = [c.section for c in chunks]
    assert "Executive Summary" in sections
    assert "Skills Inventory" in sections
    assert "Professional Experience" in sections


def test_rag_query_with_grounding(sample_candidates):
    c1 = sample_candidates[0]
    retriever = CandidateRAGRetriever(c1)
    assert retriever.is_ready is True

    # Query specific technical experience
    resp = retriever.query_with_grounding("What evidence supports FastAPI and PostgreSQL experience?")
    assert resp["status"] == "GROUNDED"
    assert resp["grounding_score"] >= 40.0
    assert len(resp["citations"]) >= 1
    assert "Carlos Mendoza" in resp["answer"]
    assert "FastAPI" in resp["answer"] or "PostgreSQL" in resp["answer"]


# ---------------- 3. Semantic Alignment Tests ----------------

def test_semantic_alignment_calculation(sample_candidates):
    c1 = sample_candidates[0]
    jd = "Looking for Senior Backend Engineer with Python, FastAPI, and Docker."
    alignment = compute_semantic_alignment(c1, jd)

    assert "overall_alignment" in alignment
    assert "skills_alignment" in alignment
    assert "experience_alignment" in alignment
    assert "education_alignment" in alignment
    assert alignment["overall_alignment"] > 50.0
    assert "Python" in alignment["matched_competencies"]
    assert "High Alignment" in alignment["seniority_fit"]


# ---------------- 4. Explainable AI (XAI) Tests ----------------

def test_xai_factor_attribution(sample_candidates):
    c1 = sample_candidates[0]
    xai = explain_candidate_score(c1)

    assert xai["final_score"] == 85
    assert len(xai["factors"]) >= 4
    
    # Check positive contributions for skills and experience
    factor_names = [f["feature"] for f in xai["factors"]]
    assert "Skills Competency Match" in factor_names
    assert "Experience & Tenure Alignment" in factor_names

    # Candidate 2 with career gap and buzzwords should show deductions
    c2 = sample_candidates[1]
    xai_c2 = explain_candidate_score(c2)
    c2_factor_names = [f["feature"] for f in xai_c2["factors"]]
    assert "Employment Gap Penalty" in c2_factor_names


# ---------------- 5. Flask API Integration Tests ----------------

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_vector_search_endpoint(client):
    res = client.post("/api/vector-search", json={"query": "Python and backend", "top_k": 3})
    assert res.status_code == 200
    data = res.get_json()
    assert "candidates" in data
    assert "index_stats" in data


def test_api_vector_search_page_renders(client):
    res = client.get("/vector-search?q=Python")
    assert res.status_code == 200
    assert b"Vector Search & Candidate Intelligence" in res.data

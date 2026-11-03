import json
from app import app
from storage import get_all_results, get_result_by_id

def test_pipeline_and_endpoints():
    client = app.test_client()

    print("\n--- TEST 1: GET /pipeline ---")
    resp = client.get("/pipeline")
    assert resp.status_code == 200, f"Pipeline failed: {resp.status_code}"
    html = resp.data.decode("utf-8")
    assert "Candidate Hiring Pipeline" in html
    assert "kanban-columns-grid" in html
    assert "Tech Interview" in html
    assert "Offer Stage" in html
    print("PASS: /pipeline renders Kanban columns properly.")

    print("\n--- TEST 2: POST /candidate/<id>/stage ---")
    candidates = get_all_results()
    if not candidates:
        seed_text = """
        Jane Doe
        Email: jane.doe@example.com
        Education: B.S. in Computer Science
        Experience: 4 years as Backend Engineer
        Skills: Python, FastAPI, Docker, PostgreSQL, PyTest, Redis
        Projects: Built high-throughput microservices using FastAPI and Docker.
        """
        client.post("/screen-resume", json={
            "resume_text": seed_text,
            "job_description": "Seeking Python Backend Engineer with Docker and FastAPI experience."
        })
        candidates = get_all_results()

    assert len(candidates) > 0, "Need at least 1 candidate in database"
    test_id = candidates[0]["_id"]

    resp = client.post(f"/candidate/{test_id}/stage", json={"stage": "offer"})
    assert resp.status_code == 200
    res_json = resp.get_json()
    assert res_json.get("success") is True
    assert res_json.get("stage") == "offer"

    updated = get_result_by_id(test_id)
    assert updated["stage"] == "offer"
    print("PASS: /candidate/<id>/stage updates stage to 'offer'.")

    # Move back to tech_interview for realism
    client.post(f"/candidate/{test_id}/stage", json={"stage": "tech_interview"})

    print("\n--- TEST 3: POST /candidate/<id>/evaluate-answer ---")
    resp = client.post(f"/candidate/{test_id}/evaluate-answer", json={
        "question": "How do you optimize asynchronous worker pools in Celery/Redis?",
        "focus_area": "Distributed Systems & Concurrency",
        "suggested_answer": "Tune concurrency worker counts, use Redis sentinel/cluster, monitor queue latency, prevent task starvation",
        "candidate_answer": "I tune the concurrency concurrency pool based on CPU cores, use gevent or prefork pools, set task_acks_late=True, and monitor Redis queue length with Prometheus to prevent worker starvation."
    })
    assert resp.status_code == 200
    eval_data = resp.get_json()
    assert "score" in eval_data
    assert "verdict" in eval_data
    assert "strengths" in eval_data
    assert "drill_down" in eval_data
    assert eval_data["score"] > 5.0
    print(f"PASS: /candidate/<id>/evaluate-answer scored {eval_data['score']}/10: {eval_data['verdict']}")

    print("\n--- TEST 4: GET /analytics ---")
    resp = client.get("/analytics")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "Talent Pool Analytics" in html
    assert "Candidate Fit Score Distribution" in html
    assert "ATS Pipeline Stage Funnel" in html
    assert "Most Prevalent Candidate Skills" in html
    print("PASS: /analytics renders comprehensive KPI and funnel analytics.")

    print("\n--- TEST 5: Text Screen with Audit & Multi-Agent Integration ---")
    sample_text = """
    Jane Smith
    Email: jane.smith@example.com
    Phone: +1 555-0199
    Education: B.S. in Computer Science (2018 - 2022)
    Experience: 3 years Software Engineer
    Skills: Python, FastAPI, Docker, PostgreSQL, PyTest, Redis, AWS
    Projects:
    Engineered low-latency REST APIs in FastAPI with PyTest test coverage of 90%.
    Containerized backend services with Docker and deployed to AWS ECS.
    Utilized Redis caching layer cutting 95th percentile database queries by 50%.
    """
    resp = client.post("/screen-resume", json={
        "resume_text": sample_text,
        "job_description": "Looking for a Python Backend Engineer with Docker, PyTest, and Redis experience."
    })
    assert resp.status_code == 200
    screened_doc = resp.get_json()
    assert "integrity_score" in screened_doc
    assert "audit_report" in screened_doc
    assert "multi_agent_scorecard" in screened_doc
    assert screened_doc["integrity_score"] >= 80
    assert len(screened_doc["multi_agent_scorecard"]["agents"]) == 3
    print(f"PASS: Screened new resume with Integrity Score: {screened_doc['integrity_score']}%, 360° Consensus: {screened_doc['multi_agent_scorecard']['consensus_score']}/100")

    print("\nALL 5 ENTERPRISE ATS TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_pipeline_and_endpoints()

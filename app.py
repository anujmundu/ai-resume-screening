import os
import io
import csv
from collections import Counter
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Response, g
from dotenv import load_dotenv

load_dotenv()

from ai_extractor import extract_data, chat_with_resume, generate_candidate_email
from resume_parser import parse_resume_file
from scoring_logic import evaluate_resume
from dossier_generator import generate_pdf_dossier
from audit_engine import audit_resume
from multi_agent_evaluator import evaluate_with_agents
from prescreen_evaluator import evaluate_prescreen_answer
from storage import (
    store_result,
    get_all_results,
    get_result_by_id,
    delete_result,
    update_candidate_stage,
    get_storage_mode
)
from vector_search import get_vector_index, refresh_vector_index
from rag_engine import CandidateRAGRetriever
from semantic_alignment import compute_semantic_alignment
from xai_engine import explain_candidate_score
from knowledge_graph import get_candidate_knowledge_graph, refresh_knowledge_graph
from adversarial_debate import conduct_adversarial_debate
from adaptive_interview import evaluate_and_generate_adaptive_followup
from saas_auth import (
    init_saas_database,
    SessionLocal,
    Organization,
    User,
    JobPosting,
    CandidateApplication,
    hash_password,
    generate_jwt_token,
    decode_jwt_token,
    require_auth,
    require_roles
)

# Initialize SaaS multi-tenant database & default tenant
init_saas_database()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "talent-ai-screening-secret-key-2026")

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "png", "jpg", "jpeg", "txt"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_global_context():
    return {
        "storage_mode": get_storage_mode()
    }

# ---------------- Landing Page ----------------
@app.route("/", methods=["GET"])
def home():
    resumes = get_all_results()
    total = len(resumes)
    shortlisted = sum(1 for r in resumes if r.get("decision") == "shortlist")
    avg_score = sum(int(r.get("score", 0)) for r in resumes) / total if total > 0 else 0
    shortlist_ratio = (shortlisted / total * 100) if total > 0 else 0

    return render_template(
        "index.html",
        total_resumes=total,
        shortlist_count=shortlisted,
        avg_score=avg_score,
        shortlist_ratio=shortlist_ratio
    )

# ---------------- Text Screening ----------------
@app.route("/screen-resume", methods=["GET", "POST"])
def screen_resume():
    if request.method == "GET":
        return render_template("screen_text.html", job_description="", result=None)

    try:
        if request.is_json:
            payload = request.get_json(force=True)
            resume_text = (payload.get("resume_text") or "").strip()
            job_description = (payload.get("job_description") or "").strip()
        else:
            resume_text = (request.form.get("resume_text") or "").strip()
            job_description = (request.form.get("job_description") or "").strip()

        if not resume_text:
            if request.is_json:
                return jsonify({"error": "resume_text is required"}), 400
            flash("Please paste resume text before submitting.", "warning")
            return render_template("screen_text.html", job_description=job_description, result=None), 400

        data = extract_data(resume_text, job_description=job_description)
        evaluation = evaluate_resume(data, job_description=job_description, resume_text=resume_text)
        audit_report = audit_resume(resume_text, data)
        multi_agent = evaluate_with_agents(resume_text, data, job_description=job_description)

        result_doc = {
            "data": data,
            "score": evaluation["score"],
            "decision": evaluation["decision"],
            "semantic_fit": evaluation.get("semantic_fit", 0.0),
            "score_breakdown": evaluation["score_breakdown"],
            "recruiter_memo": data.get("recruiter_memo", ""),
            "interview_questions": data.get("interview_questions", []),
            "job_description": job_description,
            "stage": "screened",
            "integrity_score": audit_report.get("integrity_score", 100),
            "audit_report": audit_report,
            "multi_agent_scorecard": multi_agent
        }

        doc_id = store_result(result_doc)
        result_doc["_id"] = doc_id

        if request.is_json:
            return jsonify(result_doc), 200

        flash(f"Screened: {data.get('candidate_name', 'Candidate')} ({result_doc['score']}/100 - {result_doc['decision'].upper()})", "success")
        return render_template("screen_text.html", job_description=job_description, result=result_doc)

    except Exception as e:
        print(f"[Screen Text Error] {e}")
        if request.is_json:
            return jsonify({"error": "Internal server error during screening"}), 500
        flash("An error occurred during resume screening. Please try again.", "danger")
        return render_template("screen_text.html", job_description="", result=None), 500

# ---------------- File Upload Screening (Single & Batch) ----------------
@app.route("/upload-resume", methods=["GET", "POST"])
def upload_resume():
    if request.method == "GET":
        return render_template("upload.html")

    try:
        files = request.files.getlist("resume_files")
        if not files or all(f.filename == "" for f in files):
            if "resume_file" in request.files and request.files["resume_file"].filename != "":
                files = [request.files["resume_file"]]
            else:
                flash("No resume files selected. Please choose at least one PDF, DOCX, or image file.", "warning")
                return redirect(url_for("upload_resume"))

        job_description = (request.form.get("job_description") or "").strip()

        processed_count = 0
        errors = []

        for file in files:
            if not file or file.filename == "":
                continue

            if not allowed_file(file.filename):
                errors.append(f"Skipped {file.filename}: Unsupported format.")
                continue

            try:
                resume_text = parse_resume_file(file)
                if not resume_text or len(resume_text.strip()) < 10:
                    errors.append(f"Could not extract text from {file.filename}.")
                    continue

                data = extract_data(resume_text, job_description=job_description)
                evaluation = evaluate_resume(data, job_description=job_description, resume_text=resume_text)
                audit_report = audit_resume(resume_text, data)
                multi_agent = evaluate_with_agents(resume_text, data, job_description=job_description)

                result_doc = {
                    "data": data,
                    "score": evaluation["score"],
                    "decision": evaluation["decision"],
                    "semantic_fit": evaluation.get("semantic_fit", 0.0),
                    "score_breakdown": evaluation["score_breakdown"],
                    "recruiter_memo": data.get("recruiter_memo", ""),
                    "interview_questions": data.get("interview_questions", []),
                    "job_description": job_description,
                    "stage": "screened",
                    "integrity_score": audit_report.get("integrity_score", 100),
                    "audit_report": audit_report,
                    "multi_agent_scorecard": multi_agent
                }

                store_result(result_doc)
                processed_count += 1
            except Exception as file_err:
                print(f"[Upload Error - {file.filename}]: {file_err}")
                errors.append(f"Failed to screen {file.filename}.")

        if processed_count > 0:
            flash(f"Successfully processed and screened {processed_count} resume{'s' if processed_count > 1 else ''}!", "success")
        if errors:
            flash(" ".join(errors), "warning")

        return redirect(url_for("results_dashboard"))

    except Exception as e:
        print(f"[Upload Batch Error]: {e}")
        flash("Failed to process uploaded files. Please try again.", "danger")
        return redirect(url_for("upload_resume"))

# ---------------- Results Dashboard ----------------
@app.route("/results", methods=["GET"])
def results_dashboard():
    try:
        resumes = get_all_results()

        total = len(resumes)
        avg_score = sum(int(r.get("score", 0)) for r in resumes) / total if total > 0 else 0
        shortlisted = sum(1 for r in resumes if r.get("decision") == "shortlist")
        under_review = sum(1 for r in resumes if r.get("decision") == "review")
        rejected = sum(1 for r in resumes if r.get("decision") == "reject")

        return render_template(
            "dashboard.html",
            resumes=resumes,
            total=total,
            avg_score=avg_score,
            shortlisted=shortlisted,
            under_review=under_review,
            rejected=rejected
        )
    except Exception as e:
        print(f"[Dashboard Error]: {e}")
        flash("Could not load dashboard data.", "danger")
        return render_template("dashboard.html", resumes=[], total=0, avg_score=0, shortlisted=0, under_review=0, rejected=0)

# ---------------- Single Candidate Details API ----------------
@app.route("/candidate/<doc_id>", methods=["GET"])
def get_candidate(doc_id):
    candidate = get_result_by_id(doc_id)
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404
    return jsonify(candidate), 200

# ---------------- Option 1: Recruiter Copilot (Chat with Resume) ----------------
@app.route("/candidate/<doc_id>/chat", methods=["POST"])
def candidate_chat(doc_id):
    candidate = get_result_by_id(doc_id)
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    payload = request.get_json(force=True) if request.is_json else request.form
    question = (payload.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Question is required"}), 400

    answer = chat_with_resume(candidate.get("data", {}), question)
    return jsonify({"answer": answer}), 200

# ---------------- Option 2: Executive PDF Dossier Export ----------------
@app.route("/candidate/<doc_id>/dossier", methods=["GET"])
def candidate_dossier(doc_id):
    candidate = get_result_by_id(doc_id)
    if not candidate:
        flash("Candidate not found for dossier export.", "warning")
        return redirect(url_for("results_dashboard"))

    pdf_bytes = generate_pdf_dossier(candidate)
    candidate_name = candidate.get("data", {}).get("candidate_name", "candidate").replace(" ", "_").lower()

    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment;filename=dossier_{candidate_name}.pdf"}
    )

# ---------------- Option 4: Skill Gap Matrix & Heatmap ----------------
@app.route("/matrix", methods=["GET"])
def skill_matrix():
    resumes = get_all_results()

    # Tally all skills to identify top competencies across the candidate pool
    all_skills_counter = Counter()
    for r in resumes:
        for s in r.get("data", {}).get("skills", []):
            if s:
                all_skills_counter[str(s).title()] += 1

    # Pick top 12 most frequent skills across candidates
    top_skills = [skill for skill, count in all_skills_counter.most_common(12)]
    if not top_skills:
        top_skills = ["Python", "Docker", "SQL", "Git", "React", "Linux", "FastAPI", "AWS"]

    # Calculate coverage percentage for each candidate
    for r in resumes:
        c_skills = set(str(s).title() for s in r.get("data", {}).get("skills", []))
        matched_count = len(c_skills.intersection(set(top_skills)))
        r["coverage_pct"] = (matched_count / len(top_skills) * 100) if top_skills else 0

    return render_template(
        "matrix.html",
        candidates=resumes,
        all_skills=top_skills
    )

# ---------------- Option 5: Personalized Outreach / Feedback Email ----------------
@app.route("/candidate/<doc_id>/email", methods=["GET"])
def candidate_email(doc_id):
    candidate = get_result_by_id(doc_id)
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    email_type = request.args.get("type", "outreach")
    email_data = generate_candidate_email(candidate, email_type=email_type)
    return jsonify(email_data), 200

# ---------------- Candidate Comparison API ----------------
@app.route("/compare", methods=["GET", "POST"])
def compare_candidates():
    if request.is_json:
        payload = request.get_json(force=True)
        id1 = payload.get("id1")
        id2 = payload.get("id2")
    else:
        id1 = request.args.get("id1") or request.form.get("id1")
        id2 = request.args.get("id2") or request.form.get("id2")

    if not id1 or not id2:
        return jsonify({"error": "Two candidate IDs (id1, id2) are required"}), 400

    c1 = get_result_by_id(id1)
    c2 = get_result_by_id(id2)

    if not c1 or not c2:
        return jsonify({"error": "One or both candidates could not be found"}), 404

    d1 = c1.get("data", {})
    d2 = c2.get("data", {})

    s1 = set(str(s).title() for s in d1.get("skills", []))
    s2 = set(str(s).title() for s in d2.get("skills", []))

    shared_skills = sorted(list(s1.intersection(s2)))
    c1_exclusive = sorted(list(s1 - s2))
    c2_exclusive = sorted(list(s2 - s1))

    score1 = c1.get("score", 0)
    score2 = c2.get("score", 0)
    name1 = d1.get("candidate_name", "Candidate 1")
    name2 = d2.get("candidate_name", "Candidate 2")

    if score1 > score2:
        diff = score1 - score2
        summary_verdict = f"{name1} scores {diff} points higher overall, offering distinct advantages in {', '.join(c1_exclusive[:3]) or 'overall alignment'}. {name2} remains a viable alternative with strengths in {', '.join(c2_exclusive[:3]) or 'their specific domain'}."
    elif score2 > score1:
        diff = score2 - score1
        summary_verdict = f"{name2} leads by {diff} points overall, driven by depth in {', '.join(c2_exclusive[:3]) or 'core competencies'}. {name1} offers strong complementary background in {', '.join(c1_exclusive[:3]) or 'their focus areas'}."
    else:
        summary_verdict = f"Both candidates are tied at {score1}/100. Selection should be based on cultural fit and specific mastery of {name1}'s ({', '.join(c1_exclusive[:2]) or 'skills'}) vs. {name2}'s ({', '.join(c2_exclusive[:2]) or 'skills'})."

    return jsonify({
        "candidate1": c1,
        "candidate2": c2,
        "shared_skills": shared_skills,
        "c1_exclusive_skills": c1_exclusive,
        "c2_exclusive_skills": c2_exclusive,
        "verdict": summary_verdict
    }), 200

# ---------------- Option 1: Interactive ATS Kanban Pipeline ----------------
@app.route("/pipeline", methods=["GET"])
def hiring_pipeline():
    resumes = get_all_results()
    return render_template("pipeline.html", candidates=resumes)

@app.route("/candidate/<doc_id>/stage", methods=["POST"])
def update_stage(doc_id):
    payload = request.get_json(force=True) if request.is_json else request.form
    new_stage = (payload.get("stage") or "screened").strip()
    valid_stages = {"screened", "shortlisted", "phone_screen", "tech_interview", "offer", "rejected"}
    if new_stage not in valid_stages:
        return jsonify({"error": f"Invalid stage: {new_stage}"}), 400

    success = update_candidate_stage(doc_id, new_stage)
    if success:
        return jsonify({"success": True, "stage": new_stage}), 200
    return jsonify({"error": "Failed to update candidate stage"}), 500

# ---------------- Option 3: AI Technical Pre-Screening Simulator ----------------
@app.route("/candidate/<doc_id>/evaluate-answer", methods=["POST"])
def evaluate_candidate_prescreen_answer(doc_id):
    payload = request.get_json(force=True) if request.is_json else request.form
    question = (payload.get("question") or "").strip()
    focus_area = (payload.get("focus_area") or "").strip()
    suggested_answer = (payload.get("suggested_answer") or "").strip()
    candidate_answer = (payload.get("candidate_answer") or "").strip()

    eval_result = evaluate_prescreen_answer(
        question=question,
        focus_area=focus_area,
        suggested_answer=suggested_answer,
        candidate_answer=candidate_answer
    )
    return jsonify(eval_result), 200

# ---------------- Option 5: Talent Pool Analytics & Insights ----------------
@app.route("/analytics", methods=["GET"])
def talent_analytics():
    resumes = get_all_results()
    total = len(resumes)

    if total == 0:
        return render_template(
            "analytics.html",
            total_candidates=0,
            mean_score=0,
            shortlist_rate=0,
            high_integrity_rate=0,
            score_buckets=[],
            funnel_stages=[],
            top_skills_data=[],
            exp_buckets=[]
        )

    mean_score = sum(int(r.get("score", 0)) for r in resumes) / total
    shortlist_count = sum(1 for r in resumes if r.get("decision") == "shortlist")
    shortlist_rate = (shortlist_count / total) * 100
    high_integrity_count = sum(1 for r in resumes if int(r.get("integrity_score", 100)) >= 80)
    high_integrity_rate = (high_integrity_count / total) * 100

    # Score distribution buckets
    buckets = [
        {"label": "90 - 100 (Exceptional)", "min": 90, "max": 100, "color": "emerald"},
        {"label": "75 - 89 (Strong Fit)", "min": 75, "max": 89, "color": "green"},
        {"label": "60 - 74 (Moderate Fit)", "min": 60, "max": 74, "color": "amber"},
        {"label": "45 - 59 (Marginal)", "min": 45, "max": 59, "color": "orange"},
        {"label": "< 45 (Not Aligned)", "min": 0, "max": 44, "color": "rose"}
    ]
    for b in buckets:
        cnt = sum(1 for r in resumes if b["min"] <= int(r.get("score", 0)) <= b["max"])
        b["count"] = cnt
        b["pct"] = round((cnt / total) * 100, 1)

    # ATS hiring funnel stages
    funnel_defs = [
        {"key": "screened", "name": "Screened", "icon": "📥", "color": "blue"},
        {"key": "shortlisted", "name": "Shortlisted", "icon": "⭐", "color": "purple"},
        {"key": "phone_screen", "name": "Phone Screen", "icon": "📞", "color": "amber"},
        {"key": "tech_interview", "name": "Tech Interview", "icon": "💻", "color": "cyan"},
        {"key": "offer", "name": "Offer Extended", "icon": "🎉", "color": "green"},
        {"key": "rejected", "name": "Rejected", "icon": "❌", "color": "rose"}
    ]
    for f in funnel_defs:
        cnt = sum(1 for r in resumes if r.get("stage", "screened") == f["key"])
        f["count"] = cnt
        f["pct"] = round((cnt / total) * 100, 1)

    # Top skills frequency
    skills_counter = Counter()
    for r in resumes:
        for s in r.get("data", {}).get("skills", []):
            if s:
                skills_counter[str(s).title()] += 1
    top_skills_data = []
    for skill, cnt in skills_counter.most_common(10):
        top_skills_data.append({
            "name": skill,
            "count": cnt,
            "pct": round((cnt / total) * 100, 1)
        })

    # Seniority tiers
    exp_ranges = [
        {"label": "Entry (0-2 yrs)", "icon": "🌱", "min": 0, "max": 2.9},
        {"label": "Mid-Level (3-5 yrs)", "icon": "🚀", "min": 3.0, "max": 5.9},
        {"label": "Senior (6-8 yrs)", "icon": "⭐", "min": 6.0, "max": 8.9},
        {"label": "Lead / Staff (9+ yrs)", "icon": "👑", "min": 9.0, "max": 99}
    ]
    for e in exp_ranges:
        cnt = sum(1 for r in resumes if e["min"] <= float(r.get("data", {}).get("experience_years", 0) or 0) <= e["max"])
        e["count"] = cnt
        e["pct"] = round((cnt / total) * 100, 1)

    return render_template(
        "analytics.html",
        total_candidates=total,
        mean_score=mean_score,
        shortlist_rate=shortlist_rate,
        high_integrity_rate=high_integrity_rate,
        score_buckets=buckets,
        funnel_stages=funnel_defs,
        top_skills_data=top_skills_data,
        exp_buckets=exp_ranges
    )

# ---------------- Delete Candidate ----------------
@app.route("/delete/<doc_id>", methods=["POST"])
def delete_candidate(doc_id):
    success = delete_result(doc_id)
    if success:
        flash("Candidate record removed.", "info")
    else:
        flash("Failed to delete candidate record.", "danger")
    return redirect(url_for("results_dashboard"))

# ---------------- Export to CSV ----------------
@app.route("/export-csv", methods=["GET"])
def export_csv():
    resumes = get_all_results()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Candidate Name", "Email", "Phone", "Skills",
        "Experience (Years)", "Education", "Score", "Decision",
        "Semantic Fit (%)", "Recruiter Memo", "Created At"
    ])

    for r in resumes:
        d = r.get("data", {})
        skills_str = ", ".join(d.get("skills", []))
        writer.writerow([
            r.get("_id", ""),
            d.get("candidate_name", ""),
            d.get("email", ""),
            d.get("phone", ""),
            skills_str,
            d.get("experience_years", 0),
            d.get("education", ""),
            r.get("score", 0),
            r.get("decision", ""),
            r.get("semantic_fit", 0.0),
            r.get("recruiter_memo", ""),
            r.get("created_at", "")
        ])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=screened_candidates.csv"}
    )

# ---------------- Vector Search & Candidate Intelligence ----------------
@app.route("/vector-search", methods=["GET"])
def vector_search_page():
    query = (request.args.get("q") or "").strip()
    similar_to = (request.args.get("similar_to") or "").strip()

    candidates = get_all_results()
    v_index = get_vector_index()
    if not v_index.is_fitted and candidates:
        refresh_vector_index(candidates)

    results = []
    similar_target = None

    if similar_to:
        target_cand = get_result_by_id(similar_to)
        if target_cand:
            similar_target = {
                "id": similar_to,
                "name": target_cand.get("data", {}).get("candidate_name", "Candidate")
            }
            results = v_index.find_similar_candidates(similar_to, top_k=6)
    elif query:
        results = v_index.search(query, top_k=8, min_score=0.02)

    return render_template(
        "vector_search.html",
        query=query,
        results=results,
        similar_target=similar_target,
        stats=v_index.get_stats()
    )

@app.route("/api/vector-search", methods=["GET", "POST"])
def api_vector_search():
    payload = request.get_json(force=True) if request.is_json else request.args
    query = (payload.get("q") or payload.get("query") or "").strip()
    top_k = int(payload.get("top_k", 5))
    min_score = float(payload.get("min_score", 0.05))

    candidates = get_all_results()
    v_index = get_vector_index()
    if not v_index.is_fitted and candidates:
        refresh_vector_index(candidates)

    results = v_index.search(query, top_k=top_k, min_score=min_score)
    return jsonify({
        "query": query,
        "results_count": len(results),
        "candidates": results,
        "index_stats": v_index.get_stats()
    }), 200

@app.route("/api/candidate/<doc_id>/similar", methods=["GET"])
def api_similar_candidates(doc_id):
    top_k = int(request.args.get("top_k", 5))
    candidates = get_all_results()
    v_index = get_vector_index()
    if not v_index.is_fitted and candidates:
        refresh_vector_index(candidates)

    results = v_index.find_similar_candidates(doc_id, top_k=top_k)
    return jsonify({
        "target_candidate_id": doc_id,
        "similar_candidates": results
    }), 200

# ---------------- Evidence-Grounded RAG API ----------------
@app.route("/api/candidate/<doc_id>/rag", methods=["POST"])
def api_candidate_rag(doc_id):
    candidate = get_result_by_id(doc_id)
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    payload = request.get_json(force=True) if request.is_json else request.form
    question = (payload.get("question") or payload.get("q") or "").strip()
    if not question:
        return jsonify({"error": "Question is required for RAG inquiry"}), 400

    retriever = CandidateRAGRetriever(candidate)
    rag_result = retriever.query_with_grounding(question)
    return jsonify(rag_result), 200

# ---------------- Multi-Dimensional Semantic Alignment API ----------------
@app.route("/api/candidate/<doc_id>/alignment", methods=["GET", "POST"])
def api_candidate_alignment(doc_id):
    candidate = get_result_by_id(doc_id)
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    if request.is_json:
        payload = request.get_json(force=True)
        jd = payload.get("job_description") or candidate.get("job_description", "")
    elif request.method == "POST":
        jd = request.form.get("job_description") or candidate.get("job_description", "")
    else:
        jd = request.args.get("job_description") or candidate.get("job_description", "")

    alignment = compute_semantic_alignment(candidate, jd)
    return jsonify(alignment), 200

# ---------------- Explainable AI (XAI) Attribution API ----------------
@app.route("/api/candidate/<doc_id>/xai", methods=["GET"])
def api_candidate_xai(doc_id):
    candidate = get_result_by_id(doc_id)
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    xai_breakdown = explain_candidate_score(candidate)
    return jsonify(xai_breakdown), 200

# ---------------- Phase 3: Knowledge Graph & Network Intelligence ----------------
@app.route("/knowledge-graph")
def knowledge_graph_page():
    candidates = get_all_results()
    kg = get_candidate_knowledge_graph(candidates)
    stats = kg.get_graph_statistics()
    bridges = kg.find_skill_bridges()

    # Deduplicate candidate records for template dropdown so every applicant is cleanly listed once
    seen = {}
    for c in candidates:
        name = (c.get("candidate_name") or c.get("data", {}).get("candidate_name") or "").strip()
        cid = str(c.get("_id") or c.get("id") or "")
        key = name.lower() if name else cid
        if not key:
            continue
        c_score = int(c.get("score", 0) or 0)
        if key not in seen or c_score > int(seen[key].get("score", 0) or 0):
            seen[key] = c
    unique_candidates = sorted(
        seen.values(),
        key=lambda x: (x.get("candidate_name") or x.get("data", {}).get("candidate_name") or "").lower()
    )

    return render_template("knowledge_graph.html", stats=stats, bridges=bridges, candidates=unique_candidates)

@app.route("/api/graph/data", methods=["GET"])
def api_graph_data():
    candidates = get_all_results()
    kg = get_candidate_knowledge_graph(candidates)
    max_nodes = int(request.args.get("max_nodes", 160))
    network = kg.export_d3_network(max_nodes=max_nodes)
    stats = kg.get_graph_statistics()
    bridges = kg.find_skill_bridges()
    return jsonify({
        "network": network,
        "stats": stats,
        "bridges": bridges
    }), 200

@app.route("/api/candidate/<doc_id>/graph", methods=["GET"])
def api_candidate_graph(doc_id):
    candidate = get_result_by_id(doc_id)
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    candidates = get_all_results()
    kg = get_candidate_knowledge_graph(candidates)
    depth = int(request.args.get("depth", 1))
    subgraph = kg.get_candidate_subgraph(doc_id, depth=depth)
    adjacent_skills = kg.recommend_adjacent_skills(doc_id, top_n=int(request.args.get("top_n", 6)))
    return jsonify({
        "candidate_id": doc_id,
        "subgraph": subgraph,
        "adjacent_skills": adjacent_skills
    }), 200

# ---------------- Phase 3: Multi-Agent Adversarial Debate ----------------
@app.route("/api/candidate/<doc_id>/adversarial-debate", methods=["GET", "POST"])
def api_candidate_adversarial_debate(doc_id):
    candidate = get_result_by_id(doc_id)
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    jd = ""
    target_role = ""
    if request.is_json:
        payload = request.get_json(force=True)
        jd = payload.get("job_description", "")
        target_role = payload.get("target_role", "")
    elif request.method == "POST":
        jd = request.form.get("job_description", "")
        target_role = request.form.get("target_role", "")

    if not jd:
        jd = candidate.get("job_description", "")

    debate_result = conduct_adversarial_debate(candidate, job_description=jd, target_role=target_role)
    return jsonify(debate_result), 200

# ---------------- Phase 3: Dynamic Adaptive Interview Simulator ----------------
@app.route("/api/interview/adaptive-followup", methods=["POST"])
def api_interview_adaptive_followup():
    payload = request.get_json(force=True) if request.is_json else request.form
    question = (payload.get("question") or "").strip()
    focus_area = (payload.get("focus_area") or "").strip()
    answer = (payload.get("answer") or "").strip()
    candidate_id = payload.get("candidate_id")

    candidate_skills = []
    tenure = 0.0
    if candidate_id:
        cand = get_result_by_id(candidate_id)
        if cand:
            candidate_skills = cand.get("skills") or cand.get("data", {}).get("skills", [])
            tenure = float(cand.get("experience_years") or 0.0)

    if not question or not answer:
        return jsonify({"error": "question and answer are required"}), 400

    evaluation = evaluate_and_generate_adaptive_followup(
        question=question,
        focus_area=focus_area,
        candidate_answer=answer,
        candidate_skills=candidate_skills,
        candidate_tenure=tenure
    )
    return jsonify(evaluation), 200

# ---------------- Multi-Tenant SaaS & RBAC API Endpoints ----------------
@app.route("/api/auth/register", methods=["POST"])
def api_auth_register():
    payload = request.get_json(force=True) if request.is_json else request.form
    org_name = (payload.get("org_name") or "").strip()
    org_slug = (payload.get("org_slug") or "").strip().lower()
    email = (payload.get("email") or "").strip().lower()
    password = (payload.get("password") or "").strip()
    full_name = (payload.get("full_name") or "").strip()

    if not all([org_name, org_slug, email, password, full_name]):
        return jsonify({"error": "Missing required fields: org_name, org_slug, email, password, full_name"}), 400

    session = SessionLocal()
    try:
        if session.query(Organization).filter_by(slug=org_slug).first():
            return jsonify({"error": f"Organization slug '{org_slug}' already in use"}), 409
        if session.query(User).filter_by(email=email).first():
            return jsonify({"error": f"Email '{email}' is already registered"}), 409

        org = Organization(name=org_name, slug=org_slug)
        session.add(org)
        session.commit()
        session.refresh(org)

        user = User(
            org_id=org.id,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role="admin"
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        token = generate_jwt_token(user)
        return jsonify({
            "message": "Organization and Admin account registered successfully",
            "access_token": token,
            "token_type": "Bearer",
            "user": user.to_dict(),
            "organization": org.to_dict()
        }), 201
    finally:
        session.close()

@app.route("/api/auth/login", methods=["POST"])
def api_auth_login():
    payload = request.get_json(force=True) if request.is_json else request.form
    email = (payload.get("email") or "").strip().lower()
    password = (payload.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(email=email).first()
        if not user or not user.verify_password(password):
            return jsonify({"error": "Invalid email or credentials"}), 401

        token = generate_jwt_token(user)
        org = session.query(Organization).filter_by(id=user.org_id).first()

        return jsonify({
            "message": "Authentication successful",
            "access_token": token,
            "token_type": "Bearer",
            "user": user.to_dict(),
            "organization": org.to_dict() if org else None
        }), 200
    finally:
        session.close()

@app.route("/api/auth/me", methods=["GET"])
@require_auth
def api_auth_me():
    session = SessionLocal()
    try:
        user_id = g.current_user["sub"]
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        org = session.query(Organization).filter_by(id=user.org_id).first()
        return jsonify({
            "user": user.to_dict(),
            "organization": org.to_dict() if org else None
        }), 200
    finally:
        session.close()

@app.route("/api/org/jobs", methods=["GET", "POST"])
@require_auth
def api_org_jobs():
    session = SessionLocal()
    try:
        org_id = g.current_user["org_id"]
        if request.method == "POST":
            if g.current_user.get("role") not in ["admin", "recruiter", "super_admin"]:
                return jsonify({"error": "Forbidden: Hiring Managers cannot create job openings"}), 403

            payload = request.get_json(force=True) if request.is_json else request.form
            title = (payload.get("title") or "").strip()
            desc = (payload.get("job_description") or "").strip()
            dept = payload.get("department", "Engineering")
            loc = payload.get("location", "Remote")
            sen = payload.get("target_seniority", "Senior")

            if not title or not desc:
                return jsonify({"error": "Title and job_description are required"}), 400

            job = JobPosting(
                org_id=org_id,
                title=title,
                department=dept,
                location=loc,
                target_seniority=sen,
                job_description=desc
            )
            session.add(job)
            session.commit()
            session.refresh(job)
            return jsonify({"message": "Job opening created", "job": job.to_dict()}), 201

        jobs = session.query(JobPosting).filter_by(org_id=org_id).all()
        return jsonify({"jobs": [j.to_dict() for j in jobs]}), 200
    finally:
        session.close()

@app.route("/api/org/team", methods=["GET"])
@require_roles(["admin", "super_admin"])
def api_org_team():
    session = SessionLocal()
    try:
        org_id = g.current_user["org_id"]
        users = session.query(User).filter_by(org_id=org_id).all()
        return jsonify({"team": [u.to_dict() for u in users]}), 200
    finally:
        session.close()

@app.route("/api/org/invite", methods=["POST"])
@require_roles(["admin", "super_admin"])
def api_org_invite():
    payload = request.get_json(force=True) if request.is_json else request.form
    email = (payload.get("email") or "").strip().lower()
    full_name = (payload.get("full_name") or "").strip()
    role = payload.get("role", "recruiter")
    password = payload.get("password", "Welcome2026!")

    if not email or not full_name:
        return jsonify({"error": "Email and full_name are required"}), 400

    session = SessionLocal()
    try:
        org_id = g.current_user["org_id"]
        if session.query(User).filter_by(email=email).first():
            return jsonify({"error": "User already exists with this email"}), 409

        new_user = User(
            org_id=org_id,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return jsonify({"message": f"Invited {full_name} as {role}", "user": new_user.to_dict()}), 201
    finally:
        session.close()

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    port = int(os.getenv("PORT", 5000))
    print(f"[TalentAI] Starting application on http://0.0.0.0:{port} (Storage: {get_storage_mode()})")
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)

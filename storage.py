import os
import json
import sqlite3
from datetime import datetime

try:
    from bson import ObjectId
except ImportError:
    ObjectId = None

DB_FILE = os.path.join(os.path.dirname(__file__), "resumes.db")

_mongo_client = None
_mongo_collection = None
_use_mongo = None

def _init_sqlite():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_name TEXT,
                email TEXT,
                phone TEXT,
                skills TEXT,
                experience_years REAL,
                education TEXT,
                summary TEXT,
                score INTEGER,
                decision TEXT,
                score_breakdown TEXT,
                raw_data TEXT,
                job_description TEXT,
                recruiter_memo TEXT,
                interview_questions TEXT,
                semantic_fit REAL DEFAULT 0.0,
                stage TEXT DEFAULT 'screened',
                integrity_score INTEGER DEFAULT 100,
                audit_report TEXT,
                multi_agent_scorecard TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("PRAGMA table_info(resumes)")
        columns = [col[1] for col in cursor.fetchall()]
        if "recruiter_memo" not in columns:
            cursor.execute("ALTER TABLE resumes ADD COLUMN recruiter_memo TEXT")
        if "interview_questions" not in columns:
            cursor.execute("ALTER TABLE resumes ADD COLUMN interview_questions TEXT")
        if "semantic_fit" not in columns:
            cursor.execute("ALTER TABLE resumes ADD COLUMN semantic_fit REAL DEFAULT 0.0")
        if "stage" not in columns:
            cursor.execute("ALTER TABLE resumes ADD COLUMN stage TEXT DEFAULT 'screened'")
        if "integrity_score" not in columns:
            cursor.execute("ALTER TABLE resumes ADD COLUMN integrity_score INTEGER DEFAULT 100")
        if "audit_report" not in columns:
            cursor.execute("ALTER TABLE resumes ADD COLUMN audit_report TEXT")
        if "multi_agent_scorecard" not in columns:
            cursor.execute("ALTER TABLE resumes ADD COLUMN multi_agent_scorecard TEXT")
        conn.commit()

def _get_mongo_collection():
    global _mongo_client, _mongo_collection, _use_mongo
    if _use_mongo is False:
        return None
    if _mongo_collection is not None:
        return _mongo_collection

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        _use_mongo = False
        return None

    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.server_info()
        db_name = os.getenv("MONGO_DB", "resume_screening")
        coll_name = os.getenv("MONGO_COLLECTION", "resumes")
        _mongo_client = client
        _mongo_collection = client[db_name][coll_name]
        _use_mongo = True
        return _mongo_collection
    except Exception as e:
        print(f"[Storage] MongoDB unavailable ({e}). Falling back to local SQLite.")
        _use_mongo = False
        return None

_init_sqlite()

def get_storage_mode() -> str:
    coll = _get_mongo_collection()
    return "MongoDB" if coll is not None else "SQLite (Local)"

def store_result(result: dict) -> str:
    coll = _get_mongo_collection()
    if coll is not None:
        try:
            doc = dict(result)
            doc["created_at"] = datetime.utcnow().isoformat()
            if "stage" not in doc:
                doc["stage"] = "screened"
            inserted = coll.insert_one(doc)
            return str(inserted.inserted_id)
        except Exception as e:
            print(f"[Storage] MongoDB insert failed ({e}), using SQLite.")

    # SQLite fallback
    data = result.get("data", {})
    stage = result.get("stage", "screened")
    integrity_score = int(result.get("integrity_score", 100))
    audit_report = json.dumps(result.get("audit_report", {}))
    multi_agent = json.dumps(result.get("multi_agent_scorecard", {}))

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO resumes (
                candidate_name, email, phone, skills, experience_years,
                education, summary, score, decision, score_breakdown,
                raw_data, job_description, recruiter_memo,
                interview_questions, semantic_fit, stage,
                integrity_score, audit_report, multi_agent_scorecard
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("candidate_name", "Unknown Candidate"),
            data.get("email", ""),
            data.get("phone", ""),
            json.dumps(data.get("skills", [])),
            data.get("experience_years", 0),
            data.get("education", ""),
            data.get("summary", ""),
            result.get("score", 0),
            result.get("decision", "reject"),
            json.dumps(result.get("score_breakdown", {})),
            json.dumps(data),
            result.get("job_description", ""),
            data.get("recruiter_memo", result.get("recruiter_memo", "")),
            json.dumps(data.get("interview_questions", result.get("interview_questions", []))),
            float(result.get("semantic_fit", 0.0)),
            stage,
            integrity_score,
            audit_report,
            multi_agent
        ))
        conn.commit()
        return str(cursor.lastrowid)

def update_candidate_stage(doc_id: str, new_stage: str) -> bool:
    coll = _get_mongo_collection()
    if coll is not None and ObjectId is not None:
        try:
            res = coll.update_one({"_id": ObjectId(doc_id)}, {"$set": {"stage": new_stage}})
            return res.modified_count > 0
        except Exception:
            pass

    try:
        row_id = int(doc_id)
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE resumes SET stage = ? WHERE id = ?", (new_stage, row_id))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"[Storage] Stage update error: {e}")
        return False

def get_all_results() -> list[dict]:
    coll = _get_mongo_collection()
    if coll is not None:
        try:
            docs = list(coll.find().sort("_id", -1))
            for d in docs:
                d["_id"] = str(d["_id"])
            return docs
        except Exception as e:
            print(f"[Storage] MongoDB fetch failed ({e}), using SQLite.")

    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resumes ORDER BY id DESC")
        rows = cursor.fetchall()
        results = []
        for r in rows:
            raw_data = {}
            if r["raw_data"]:
                try:
                    raw_data = json.loads(r["raw_data"])
                except Exception:
                    pass

            skills = []
            if r["skills"]:
                try:
                    skills = json.loads(r["skills"])
                except Exception:
                    skills = []

            score_breakdown = {}
            if r["score_breakdown"]:
                try:
                    score_breakdown = json.loads(r["score_breakdown"])
                except Exception:
                    pass

            interview_questions = []
            if "interview_questions" in r.keys() and r["interview_questions"]:
                try:
                    interview_questions = json.loads(r["interview_questions"])
                except Exception:
                    interview_questions = []

            audit_report = {}
            if "audit_report" in r.keys() and r["audit_report"]:
                try:
                    audit_report = json.loads(r["audit_report"])
                except Exception:
                    pass

            multi_agent = {}
            if "multi_agent_scorecard" in r.keys() and r["multi_agent_scorecard"]:
                try:
                    multi_agent = json.loads(r["multi_agent_scorecard"])
                except Exception:
                    pass

            recruiter_memo = r["recruiter_memo"] if "recruiter_memo" in r.keys() and r["recruiter_memo"] else raw_data.get("recruiter_memo", "")
            semantic_fit = float(r["semantic_fit"]) if "semantic_fit" in r.keys() and r["semantic_fit"] is not None else float(raw_data.get("semantic_fit", 0.0))
            stage = r["stage"] if "stage" in r.keys() and r["stage"] else "screened"
            integrity_score = int(r["integrity_score"]) if "integrity_score" in r.keys() and r["integrity_score"] is not None else 100

            results.append({
                "_id": str(r["id"]),
                "data": {
                    "candidate_name": r["candidate_name"],
                    "email": r["email"],
                    "phone": r["phone"],
                    "skills": skills,
                    "experience_years": r["experience_years"],
                    "education": r["education"],
                    "summary": r["summary"],
                    "recruiter_memo": recruiter_memo,
                    "interview_questions": interview_questions,
                    **raw_data
                },
                "score": r["score"],
                "decision": r["decision"],
                "stage": stage,
                "integrity_score": integrity_score,
                "audit_report": audit_report,
                "multi_agent_scorecard": multi_agent,
                "semantic_fit": semantic_fit,
                "recruiter_memo": recruiter_memo,
                "interview_questions": interview_questions,
                "score_breakdown": score_breakdown,
                "job_description": r["job_description"],
                "created_at": r["created_at"]
            })
        return results

def get_result_by_id(doc_id: str) -> dict | None:
    coll = _get_mongo_collection()
    if coll is not None and ObjectId is not None:
        try:
            doc = coll.find_one({"_id": ObjectId(doc_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                return doc
        except Exception:
            pass

    try:
        row_id = int(doc_id)
    except ValueError:
        return None

    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resumes WHERE id = ?", (row_id,))
        r = cursor.fetchone()
        if not r:
            return None

        raw_data = {}
        if r["raw_data"]:
            try:
                raw_data = json.loads(r["raw_data"])
            except Exception:
                pass

        skills = []
        if r["skills"]:
            try:
                skills = json.loads(r["skills"])
            except Exception:
                skills = []

        score_breakdown = {}
        if r["score_breakdown"]:
            try:
                score_breakdown = json.loads(r["score_breakdown"])
            except Exception:
                pass

        interview_questions = []
        if "interview_questions" in r.keys() and r["interview_questions"]:
            try:
                interview_questions = json.loads(r["interview_questions"])
            except Exception:
                interview_questions = []

        audit_report = {}
        if "audit_report" in r.keys() and r["audit_report"]:
            try:
                audit_report = json.loads(r["audit_report"])
            except Exception:
                pass

        multi_agent = {}
        if "multi_agent_scorecard" in r.keys() and r["multi_agent_scorecard"]:
            try:
                multi_agent = json.loads(r["multi_agent_scorecard"])
            except Exception:
                pass

        recruiter_memo = r["recruiter_memo"] if "recruiter_memo" in r.keys() and r["recruiter_memo"] else raw_data.get("recruiter_memo", "")
        semantic_fit = float(r["semantic_fit"]) if "semantic_fit" in r.keys() and r["semantic_fit"] is not None else float(raw_data.get("semantic_fit", 0.0))
        stage = r["stage"] if "stage" in r.keys() and r["stage"] else "screened"
        integrity_score = int(r["integrity_score"]) if "integrity_score" in r.keys() and r["integrity_score"] is not None else 100

        return {
            "_id": str(r["id"]),
            "data": {
                "candidate_name": r["candidate_name"],
                "email": r["email"],
                "phone": r["phone"],
                "skills": skills,
                "experience_years": r["experience_years"],
                "education": r["education"],
                "summary": r["summary"],
                "recruiter_memo": recruiter_memo,
                "interview_questions": interview_questions,
                **raw_data
            },
            "score": r["score"],
            "decision": r["decision"],
            "stage": stage,
            "integrity_score": integrity_score,
            "audit_report": audit_report,
            "multi_agent_scorecard": multi_agent,
            "semantic_fit": semantic_fit,
            "recruiter_memo": recruiter_memo,
            "interview_questions": interview_questions,
            "score_breakdown": score_breakdown,
            "job_description": r["job_description"],
            "created_at": r["created_at"]
        }

def delete_result(doc_id: str) -> bool:
    coll = _get_mongo_collection()
    if coll is not None and ObjectId is not None:
        try:
            res = coll.delete_one({"_id": ObjectId(doc_id)})
            return res.deleted_count > 0
        except Exception:
            pass

    try:
        row_id = int(doc_id)
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM resumes WHERE id = ?", (row_id,))
            conn.commit()
            return cursor.rowcount > 0
    except Exception:
        return False

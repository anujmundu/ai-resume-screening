import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF for PDF text extraction
import pytesseract
from PIL import Image

# Load environment variables
load_dotenv()

from ai_extractor import extract_data
from storage import store_result

app = Flask(__name__)

# ---------------- Security & Config ----------------
# Limit upload size to 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------- Shared scoring (normalized to 100) ----------------
def calculate_score(data: dict) -> tuple[int, str]:
    skills = data.get("skills", [])
    experience_years = data.get("experience_years", 0)
    education = (data.get("education") or "").lower()

    # Raw scoring (simple, transparent, capped later)
    skill_score = len(skills) * 5
    experience_score = min(max(int(experience_years), 0) * 10, 30)
    education_score = 20 if "mca" in education else 10 if "bca" in education else 0

    raw_total = skill_score + experience_score + education_score
    score = min(raw_total, 100)
    decision = "shortlist" if score >= 60 else "reject"
    return score, decision

# ---------------- Reusable HTML components ----------------
NAV = """
<nav style="background:#2c3e50;padding:10px;text-align:center;">
  <a href="/" style="color:#fff;margin:0 10px;text-decoration:none;">Home</a>
  <a href="/screen-resume" style="color:#fff;margin:0 10px;text-decoration:none;">Text Screening</a>
  <a href="/results" style="color:#fff;margin:0 10px;text-decoration:none;">Results</a>
</nav>
"""

# ---------------- Landing Page ----------------
@app.route("/", methods=["GET"])
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AI Resume Screening System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f4f6f9; color: #333; }
            header { background: #2c3e50; color: #fff; padding: 20px; text-align: center; }
            h1 { margin: 0; font-size: 2.2em; }
            main { padding: 40px; max-width: 900px; margin: auto; }
            .card { background: #fff; padding: 20px; margin-bottom: 20px; border-radius: 8px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
            .btn { display: inline-block; padding: 10px 20px; background: #3498db; color: #fff;
                   text-decoration: none; border-radius: 5px; transition: background 0.3s; }
            .btn:hover { background: #2980b9; }
            footer { text-align: center; padding: 20px; background: #ecf0f1; font-size: 0.9em; color: #555; }
            nav a { color:#fff; margin:0 10px; text-decoration:none; }
            nav { background:#2c3e50; padding:10px; text-align:center; }
        </style>
    </head>
    <body>
        <header>
            <h1>AI Resume Screening System</h1>
            <p>Smart, fast, and recruiter‑friendly candidate evaluation</p>
        </header>
        <nav>
          <a href="/">Home</a>
          <a href="/screen-resume">Text Screening</a>
          <a href="/results">Results</a>
        </nav>
        <main>
            <div class="card">
                <h2>About</h2>
                <p>This tool screens resumes from text, PDFs, and images, extracts key info, scores candidates on a 0–100 scale, and stores results.</p>
                <p><a href="/results" class="btn">View Results Dashboard</a></p>
            </div>
            <div class="card">
                <h2>How to Use (Text)</h2>
                <p>Send a <strong>POST</strong> request to <code>/screen-resume</code> with JSON body:</p>
                <pre>{
  "resume_text": "Experienced Python developer with MCA degree and 2 years of SQL experience"
}</pre>
                <p><a href="/screen-resume" class="btn">Try Text Screening</a></p>
            </div>
            <div class="card">
                <h2>Upload a Resume (PDF or Image)</h2>
                <form action="/upload-resume" method="post" enctype="multipart/form-data">
                    <div id="drop-area" style="border:2px dashed #3498db; padding:20px; text-align:center;">
                        <p>Drag & drop a resume (PDF or image) here, or click to select</p>
                        <input type="file" name="resume_file" accept=".pdf,.png,.jpg,.jpeg" />
                    </div>
                    <button type="submit" class="btn">Upload & Screen</button>
                </form>
                <p style="color:#777;margin-top:10px;">Max file size: 10 MB. Supported: PDF, PNG, JPG, JPEG.</p>
            </div>
        </main>
        <footer>
            &copy; 2026 AI Resume Screening | Flask + MongoDB | Anuj Mundu
        </footer>
    </body>
    </html>
    """


# ---------------- Text Screening ----------------
@app.route("/screen-resume", methods=["GET", "POST"])
def screen_resume():
    if request.method == "GET":
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head> ...styles... </head>
        <body>
            <nav style="background:#2c3e50;padding:10px;text-align:center;">
              <a href="/" style="color:#fff;margin:0 10px;text-decoration:none;">Home</a>
              <a href="/screen-resume" style="color:#fff;margin:0 10px;text-decoration:none;">Text Screening</a>
              <a href="/results" style="color:#fff;margin:0 10px;text-decoration:none;">Results</a>
            </nav>
            <h1>Paste Resume Text</h1>
            <form action="/screen-resume" method="post">
                <textarea name="resume_text" placeholder="Paste resume text here..."></textarea><br>
                <button type="submit">Screen Resume</button>
            </form>
        </body>
        </html>
        """

    try:
        # Handle JSON or form
        if request.is_json:
            payload = request.get_json(force=True)
            resume_text = (payload.get("resume_text") or "").strip()
        else:
            resume_text = (request.form.get("resume_text") or "").strip()

        if not resume_text:
            return f"""
            <!DOCTYPE html>
            <html><body style="font-family: Arial; margin: 40px;">
                <p style="color:#c0392b;"><strong>Error:</strong> Please paste resume text before submitting.</p>
                <p><a href="/screen-resume">Go back</a></p>
            </body></html>
            """, 400

        data = extract_data(resume_text)
        if not isinstance(data, dict):
            return f"""
            <!DOCTYPE html>
            <html><body style="font-family: Arial; margin: 40px;">
                <p style="color:#c0392b;"><strong>Error:</strong> Could not extract data from the text. Please try again with clearer content.</p>
                <p><a href="/screen-resume">Go back</a></p>
            </body></html>
            """, 500

        score, decision = calculate_score(data)
        result_doc = {"data": data, "score": score, "decision": decision}

        try:
            doc_id = store_result(result_doc)
            result_doc["_id"] = doc_id
        except Exception as e:
            print("MongoDB store error:", e)

        if not request.is_json:
            return f"""
            <!DOCTYPE html>
            <html><head><title>Screening Result</title></head>
            <body style="font-family: Arial; margin: 40px;">
                {NAV}
                <h1>Screening Result</h1>
                <p><strong>Skills:</strong> {", ".join(data.get("skills", [])) or "—"}</p>
                <p><strong>Experience:</strong> {data.get("experience_years", 0)} years</p>
                <p><strong>Education:</strong> {data.get("education", "") or "—"}</p>
                <p><strong>Score:</strong> {score}</p>
                <p><strong>Decision:</strong> {decision}</p>
                <p><a href="/results">View All Results</a></p>
            </body></html>
            """
        return jsonify(result_doc), 200

    except Exception as e:
        print("Unhandled error:", e)
        return jsonify({"error": "internal server error"}), 500

# ---------------- File Upload Screening ----------------
@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    try:
        if "resume_file" not in request.files:
            return f"""
            <!DOCTYPE html>
            <html><body style="font-family: Arial; margin: 40px;">
                <p style="color:#c0392b;"><strong>Error:</strong> No file uploaded. Please select a PDF or image.</p>
                <p><a href="/">Go back</a></p>
            </body></html>
            """, 400

        file = request.files["resume_file"]
        if file.filename == "":
            return f"""
            <!DOCTYPE html>
            <html><body style="font-family: Arial; margin: 40px;">
                <p style="color:#c0392b;"><strong>Error:</strong> Empty filename. Please select a valid file.</p>
                <p><a href="/">Go back</a></p>
            </body></html>
            """, 400

        if not allowed_file(file.filename):
            return f"""
            <!DOCTYPE html>
            <html><body style="font-family: Arial; margin: 40px;">
                <p style="color:#c0392b;"><strong>Error:</strong> Unsupported file type. Allowed: PDF, PNG, JPG, JPEG.</p>
                <p><a href="/">Go back</a></p>
            </body></html>
            """, 400

        ext = file.filename.rsplit(".", 1)[1].lower()
        resume_text = ""

        if ext == "pdf":
            pdf_bytes = file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            for page in doc:
                text = page.get_text()
                if text:
                    resume_text += text
        else:
            try:
                img = Image.open(file.stream)
                resume_text = pytesseract.image_to_string(img)
            except Exception:
                return f"""
                <!DOCTYPE html>
                <html><body style="font-family: Arial; margin: 40px;">
                    <p style="color:#c0392b;"><strong>Error:</strong> Could not run OCR on the image. If you’re on Windows, ensure Tesseract OCR is installed.</p>
                    <p><a href="/">Go back</a></p>
                </body></html>
                """, 500

        if not resume_text.strip():
            return f"""
            <!DOCTYPE html>
            <html><body style="font-family: Arial; margin: 40px;">
                <p style="color:#c0392b;"><strong>Error:</strong> Could not extract text from this file. Please upload a clearer PDF or a higher‑resolution image.</p>
                <p><a href="/">Go back</a></p>
            </body></html>
            """, 500

        data = extract_data(resume_text)
        if not isinstance(data, dict):
            return f"""
            <!DOCTYPE html>
            <html><body style="font-family: Arial; margin: 40px;">
                <p style="color:#c0392b;"><strong>Error:</strong> AI extraction failed. Please try another file.</p>
                <p><a href="/">Go back</a></p>
            </body></html>
            """, 500

        score, decision = calculate_score(data)

        # Basic sanitization for storing
        clean_doc = {
            "data": {
                "skills": [str(s) for s in data.get("skills", [])],
                "experience_years": int(data.get("experience_years", 0) or 0),
                "education": str(data.get("education", "") or "")
            },
            "score": int(score),
            "decision": str(decision)
        }

        try:
            doc_id = store_result(clean_doc)
            clean_doc["_id"] = doc_id
        except Exception as e:
            print("MongoDB store error:", e)

        return f"""
        <!DOCTYPE html>
        <html><head><title>Screening Result</title></head>
        <body style="font-family: Arial; margin: 40px;">
            {NAV}
            <h1>Screening Result</h1>
            <p><strong>Skills:</strong> {", ".join(clean_doc["data"]["skills"]) or "—"}</p>
            <p><strong>Experience:</strong> {clean_doc["data"]["experience_years"]} years</p>
            <p><strong>Education:</strong> {clean_doc["data"]["education"] or "—"}</p>
            <p><strong>Score:</strong> {clean_doc["score"]}</p>
            <p><strong>Decision:</strong> {clean_doc["decision"]}</p>
            <p><a href="/results">View All Results</a></p>
        </body></html>
        """

    except Exception as e:
        print("Upload error:", e)
        return f"""
        <!DOCTYPE html>
        <html><body style="font-family: Arial; margin: 40px;">
            <p style="color:#c0392b;"><strong>Error:</strong> Failed to process file.</p>
            <p><a href="/">Go back</a></p>
        </body></html>
        """, 500

# ---------------- Results Dashboard ----------------
@app.route("/results", methods=["GET"])
def results_dashboard():
    try:
        from storage import collection  # reuse MongoDB collection
        resumes = list(collection.find().sort("_id", -1))

        total = len(resumes)
        avg_score = sum(int(r.get("score", 0)) for r in resumes) / total if total > 0 else 0
        shortlisted = sum(1 for r in resumes if r.get("decision") == "shortlist")
        shortlist_ratio = (shortlisted / total * 100) if total > 0 else 0

        rows = ""
        for r in resumes:
            data = r.get("data", {})
            rows += f"""
            <tr>
                <td>{str(r.get("_id"))}</td>
                <td>{", ".join(data.get("skills", []))}</td>
                <td>{data.get("experience_years", 0)}</td>
                <td>{data.get("education", "")}</td>
                <td>{r.get("score", 0)}</td>
                <td>{r.get("decision", "")}</td>
            </tr>
            """

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Resume Screening Results</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; background: #f4f6f9; }}
                h1 {{ text-align: center; padding-top: 20px; }}
                {""}
                .summary {{ display: flex; justify-content: space-around; margin: 20px; }}
                .summary div {{
                    background: #fff; padding: 15px; border-radius: 8px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1); text-align: center; width: 22%;
                }}
                table {{ width: 95%; margin: 0 auto 40px auto; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ccc; padding: 10px; text-align: center; }}
                th {{ background: #2c3e50; color: #fff; }}
                tr:nth-child(even) {{ background: #ecf0f1; }}
            </style>
        </head>
        <body>
            {NAV}
            <h1>Resume Screening Results</h1>
            <div class="summary">
                <div><h2>{total}</h2><p>Total Resumes</p></div>
                <div><h2>{avg_score:.1f}</h2><p>Average Score</p></div>
                <div><h2>{shortlisted}</h2><p>Shortlisted</p></div>
                <div><h2>{shortlist_ratio:.1f}%</h2><p>Shortlist Ratio</p></div>
            </div>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Skills</th>
                    <th>Experience (Years)</th>
                    <th>Education</th>
                    <th>Score</th>
                    <th>Decision</th>
                </tr>
                {rows if rows else "<tr><td colspan='6'>No resumes screened yet.</td></tr>"}
            </table>
        </body>
        </html>
        """
        return html

    except Exception as e:
        print("Dashboard error:", e)
        return f"""
        <!DOCTYPE html>
        <html><body style="font-family: Arial; margin: 40px;">
            <p style="color:#c0392b;"><strong>Error:</strong> Could not load results.</p>
            <p><a href="/">Go back</a></p>
        </body></html>
        """, 500

# ---------------- Run ----------------
if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    print("DEBUG: OPENROUTER_API_KEY =", os.getenv("OPENROUTER_API_KEY"))
    print("DEBUG: MONGO_URI =", os.getenv("MONGO_URI"))
    app.run(host="0.0.0.0", port=5000, debug=debug, use_reloader=False)

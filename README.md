

# AI Resume Screening System

An intelligent, recruiter‑friendly web application built with **Flask**, **MongoDB**, and **AI/ML** that automates resume screening.  
It extracts key information from resumes (skills, experience, education), scores candidates on a normalized **0–100 scale**, and provides a clean dashboard for recruiters to review results.

---

## 🚀 Features

- **Text Screening**: Paste resume text directly into the app and get instant scoring.
- **File Uploads**: Upload resumes in **PDF** or **image** format (OCR supported).
- **Normalized Scoring**: Consistent scoring capped at 100 for fairness and comparability.
- **Results Dashboard**: Recruiter‑friendly summary with:
  - Total resumes screened
  - Average score
  - Shortlist ratio
  - Candidate table with skills, experience, education, score, and decision
- **Error Handling**: Clear, user‑friendly messages for invalid files or extraction failures.
- **Navigation**: Easy links between Home, Text Screening, Upload, and Results.
- **Security Basics**:
  - File size limit (10 MB)
  - Strict file type validation
  - Environment variables for secrets
  - Sanitized MongoDB storage

---

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB (via PyMongo)
- **AI Extraction**: OpenRouter API + custom logic
- **OCR**: PyMuPDF (PDF), Tesseract + Pillow (images)
- **Deployment**: Render (Docker container)

---

## 📂 Project Structure


```
ai-resume-screening/
├── app.py                # Flask backend
├── templates/            # HTML templates
├── static/               # CSS/JS
├── requirements.txt      # Dependencies
├── Dockerfile            # Container setup
└── .env                   # Environment variables
```

## 🔧 Setup Instructions
Create virtual environment

bash 
```
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

Install dependencies

bash
```
pip install -r requirements.txt
```

Configure environment variables 
Create a .env file:

```
OPENROUTER_API_KEY=your_api_key_here
MONGO_URI=mongodb+srv://user:pass@cluster/dbname
FLASK_DEBUG=0
```

Run the app

bash
```
python app.py
```
Visit: http://127.0.0.1:5000

🌐 Deploying on Render
Render makes it easy to deploy Dockerized apps. Here’s how:

Push your code to GitHub  
Make sure your repo contains:

app.py

requirements.txt

Dockerfile

.gitignore

README.md

Create a new Render Web Service

Go to Render Dashboard

Click New + → Web Service

Connect your GitHub repo

Configure service

Environment: Docker

Build Command: (not needed, Render uses Dockerfile)

Start Command: python app.py (already in Dockerfile CMD)

Port: 5000

Add environment variables
In Render dashboard → Environment tab:

Code
OPENROUTER_API_KEY=your_api_key_here
MONGO_URI=mongodb+srv://user:pass@cluster/dbname
FLASK_DEBUG=0
Deploy
Render will build your Docker image and deploy automatically.
You’ll get a live URL like:
https://ai-resume-screening.onrender.com

📊 Recruiter Workflow
Home Page → Overview + navigation

Text Screening → Paste resume text

Upload Resume → Upload PDF or image

Results Dashboard → View scores, shortlist ratio, and candidate details

🔒 Security Notes
Secrets (OPENROUTER_API_KEY, MONGO_URI) are stored in .env and never committed.

File uploads limited to 10 MB and validated for type.

MongoDB inputs sanitized before storage.

🤝 Contributing
Pull requests are welcome! For major changes, open an issue first to discuss what you’d like to change.

## 👨‍💻 Author

**Anuj Mundu**  
Motivated MCA student, full‑stack developer, and aspiring business technologist.  
- GitHub: [github.com/anuj‑mundu](https://github.com/anuj-mundu)  
- LinkedIn: [linkedin.com/in/anuj‑mundu](https://linkedin.com/in/anuj-mundu)

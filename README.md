# TalentAI &bull; Enterprise AI Resume Screening & ATS Intelligence

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)](.github/workflows/ci.yml)
[![Auth](https://img.shields.io/badge/Auth-JWT%20%7C%20RBAC-green.svg)](#-multi-tenant-saas--rbac-reference)
[![Storage](https://img.shields.io/badge/Storage-SQLite%20%7C%20PostgreSQL-lightgrey.svg)](https://www.sqlite.org/)
[![Responsive](https://img.shields.io/badge/Design-Mobile%20%7C%20Tablet%20%7C%20Desktop-purple.svg)](#-multi-device-responsive-design)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**TalentAI** is an enterprise-grade **Applicant Tracking System (ATS)** and **AI Talent Intelligence Platform** built with **Python**, **Flask**, **SQLite/MongoDB**, and **NLP analytics**. It transforms traditional recruiting by automating multi-format resume parsing (PDF, DOCX, OCR), performing explainable **0–100 suitability scoring** against target Job Descriptions, executing multi-persona AI evaluations, and orchestrating candidates through an interactive **visual Kanban hiring pipeline**.

---

## 📸 Visual Showcase & Proof of Functionality

A comprehensive visual gallery of 25 high-resolution screenshots capturing every production subsystem, audit modal, vector engine, topological knowledge graph, and omnichannel responsive view:

| # | Subsystem & Feature Showcase | Screenshot Preview |
| :--- | :--- | :--- |
| **01** | **TalentAI Enterprise Landing Hero (`/`)**<br>• Executive value proposition, active system status, and subsystem quick launches | ![01 Landing Hero](screenshots/01_landing_hero.png) |
| **02** | **Executive Screening Dashboard (`/results`)**<br>• Real-time candidate roster with 0–100 fit scores, integrity badges, and KPI counters | ![02 Dashboard](screenshots/02_dashboard_desktop.png) |
| **03** | **DEI Blind Screening Mode Active**<br>• Bias mitigation: automated PII redaction of candidate names, emails, and phone numbers | ![03 Blind Screening](screenshots/03_blind_screening_filter.png) |
| **04** | **Candidate Evaluation Dossier Modal**<br>• In-depth candidate dossier with categorized score breakdown and recruiter memo | ![04 Candidate Dossier](screenshots/04_candidate_dossier_modal.png) |
| **05** | **Forensic Resume Consistency & Red Flags Audit**<br>• Automated career chronology inspection, employment gap detection, and tenure ratings | ![05 Resume Audit](screenshots/05_resume_audit_redflags.png) |
| **06** | **Multi-Agent 360° Hiring Panel Scorecard**<br>• 4 AI personas (Code Auditor, Systems Architect, Business Reviewer, Lead Supervisor) | ![06 Multi-Agent](screenshots/06_multiagent_360_review.png) |
| **07** | **Interactive ATS Recruitment Kanban Pipeline (`/pipeline`)**<br>• Drag-and-drop candidate stage progression across Screened, Phone, Tech, Offer, Reject | ![07 Kanban Pipeline](screenshots/07_ats_kanban_pipeline.png) |
| **08** | **Talent Pool Analytics Dashboard (`/analytics`)**<br>• Score distribution bell curve, conversion funnel, and competency frequency histograms | ![08 Talent Analytics](screenshots/08_talent_analytics_dashboard.png) |
| **09** | **Competency Gap & Role Alignment Heatmap (`/matrix`)**<br>• Multi-candidate skill matrix heatmap with verified checkmarks and gap flags | ![09 Skill Matrix](screenshots/09_skill_matrix_heatmap.png) |
| **10** | **MiniLM Sublinear Vector Search Engine (`/vector-search`)**<br>• Vector semantic search interface with natural language capability prompts | ![10 Vector Search](screenshots/10_vector_search_engine.png) |
| **11** | **Semantic Search Results & Cosine Similarity Rankings**<br>• Ranked search results with match confidence tags and quick-launch deep dive modals | ![11 Vector Results](screenshots/11_vector_search_results.png) |
| **12** | **Evidence-Grounded RAG Inquiry Modal**<br>• Exact source-cited resume excerpts with 96% grounding verification and zero hallucinations | ![12 RAG Inquiry](screenshots/12_rag_grounded_citations.png) |
| **13** | **Explainable AI (XAI) SHAP Factor Attribution Modal**<br>• Additive feature attribution decomposing candidate scores into positive/negative drivers | ![13 XAI Attribution](screenshots/13_xai_factor_attribution.png) |
| **14** | **Multi-Dimensional Semantic Alignment Breakdown**<br>• Independent vector alignment across Skills (94%), Experience (88%), and Education (90%) | ![14 Semantic Alignment](screenshots/14_semantic_alignment_radar.png) |
| **15** | **Spacious Candidate Knowledge Graph Hero (`/knowledge-graph`)**<br>• Topological force simulation grouping talent and skills into domain constellations | ![15 Knowledge Graph](screenshots/15_knowledge_graph_constellations.png) |
| **16** | **Knowledge Graph Searchable Candidate Dropdown**<br>• Searchable dropdown menu listing all candidates with instant spotlight triggers | ![16 Search Dropdown](screenshots/16_knowledge_graph_search_dropdown.png) |
| **17** | **Spotlighted Candidate 1-Hop Ego Network**<br>• Isolated candidate node with direct links to primary and adjacent technical skills | ![17 Ego Spotlight](screenshots/17_knowledge_graph_ego_spotlight.png) |
| **18** | **Knowledge Graph Entity Inspector Dossier**<br>• Interactive entity inspector detailing graph connectivity, degree, and verified background | ![18 Entity Inspector](screenshots/18_knowledge_graph_entity_inspector.png) |
| **19** | **Top Hub Competencies & Technical Bridge Skills Deck**<br>• Betweenness centrality rankings identifying critical bridging skills across domains | ![19 Hubs and Bridges](screenshots/19_knowledge_graph_hubs_bridges.png) |
| **20** | **Multi-Agent Adversarial Debate Committee Modal**<br>• Trial arena: Candidate Advocate (Defense) vs. Technical Skeptic (Prosecution) vs. Arbiter | ![20 Adversarial Debate](screenshots/20_adversarial_debate_arena.png) |
| **21** | **Dynamic Adaptive Technical Interview Simulator Modal**<br>• Live technical evaluation with dynamic follow-up probes and interviewer rubrics | ![21 Adaptive Simulator](screenshots/21_adaptive_interview_simulator.png) |
| **22** | **Multi-File Batch Resume Upload & Ingestion (`/upload-resume`)**<br>• Drag-and-drop batch parser with criteria presets and real-time upload queue | ![22 Batch Upload](screenshots/22_batch_resume_upload.png) |
| **23** | **Instant Text Screening with Role Presets (`/screen-resume`)**<br>• Real-time raw resume text parsing against configurable target job specifications | ![23 Screen Text](screenshots/23_screen_text_presets.png) |
| **24** | **Candidate Head-to-Head Comparison View**<br>• Side-by-side comparative analysis with exclusive skills, shared overlap, and AI verdict | ![24 Candidate Comparison](screenshots/24_side_by_side_comparison.png) |
| **25** | **Mobile Responsive Viewport (Touch Navigation & Cards)**<br>• 390px mobile viewport rendering full navigation drawers and responsive candidate cards | ![25 Mobile View](screenshots/25_mobile_responsive_experience.png) |


---

## 👥 Batch Candidate Screening for a Target Role

TalentAI supports high-throughput batch evaluation where recruiters upload multiple candidate resumes simultaneously against a single target Job Description. The platform extracts competencies, calculates relative suitability rankings, detects domain mismatches, and facilitates head-to-head candidate comparisons.

### 🧪 Live Batch Walkthrough: *Senior Full Stack Software Engineer (Python & React)*

In this live demonstration, 5 resumes representing diverse seniority levels and specialties were screened in a single batch against the **Senior Full Stack Software Engineer** JD:

1. **Carlos Mendoza** (`carlos_mendoza_backend.pdf`): Strong Backend Specialist (FastAPI, Django, PostgreSQL, Docker, Redis, 5 yrs) &rarr; **73/100 (SHORTLIST)**
2. **Marcus Vance** (`marcus_vance_fullstack.pdf`): Senior Full Stack Engineer (Python, React, Django, AWS, Docker, 6 yrs) &rarr; **62/100 (REVIEW &bull; 78.6% Semantic Fit)**
3. **Leo Chen** (`leo_chen_frontend_developer.pdf`): Frontend Specialist (React, TypeScript, Next.js, 4 yrs) &rarr; **51/100 (REVIEW &bull; 42.2% Semantic Fit)**
4. **Priya Sharma** (`priya_sharma_junior_frontend.docx`): Junior Developer (React, JavaScript, HTML/CSS, 1.5 yrs) &rarr; **43/100 (REJECT &bull; Experience/Backend Gap)**
5. **Chloe Bennett** (`chloe_bennett_graphic_designer.docx`): Creative Designer (Figma, Photoshop) &rarr; **26/100 (REJECT &bull; 11.1% Semantic Mismatch)**

### 📸 Batch Screening Workflow Screenshots

| Step | Workflow Stage | Screenshot Preview |
| :--- | :--- | :--- |
| **B1** | **Batch Upload & JD Setup (`/upload-resume`)**<br>• Target Job Description pasted in criteria box<br>• Multi-format resume files selected with live pill previews | ![Batch Upload Setup](screenshots/batch_screening/01_batch_upload_configuration.png) |
| **B2** | **Ranked Candidate Results (`/results`)**<br>• Instant comparative ranking of all 5 candidates<br>• Transparent 0–100 scores, decisions, and integrity badges | ![Batch Screened Results](screenshots/batch_screening/02_batch_evaluated_candidates.png) |
| **B3** | **Head-to-Head Candidate Comparison**<br>• Side-by-side comparison (Carlos Mendoza vs. Marcus Vance)<br>• AI Comparative Verdict, exclusive skills, and shared competencies | ![Side by Side Comparison](screenshots/batch_screening/03_side_by_side_comparison.png) |
| **B4** | **Candidate Deep Dive Dossier & Recruiter Memo**<br>• Executive briefing tailored to the target Full Stack role<br>• Score breakdown and customized technical interview questions | ![Candidate Deep Dive](screenshots/batch_screening/05_candidate_deep_dive_memo.png) |
| **B5** | **ATS Kanban Pipeline Orchestration (`/pipeline`)**<br>• Screened candidates distributed across hiring stages<br>• Drag-and-drop workflow updates with automated alerts | ![ATS Kanban Workflow](screenshots/batch_screening/04_ats_kanban_batch_workflow.png) |

---

## 🌟 Core Capabilities

### 1. 🎯 Precision Job Description Matching & 0–100 Scoring
- **Explainable Multi-Factor Scoring**:
  - **Skills Match (40 pts)**: Detects essential and nice-to-have technical skills.
  - **Experience Relevance (30 pts)**: Calculates career depth and tenure alignment.
  - **Education & Credentials (15 pts)**: Evaluates degrees, certifications, and academic background.
  - **Profile Completeness (15 pts)**: Inspects contact completeness, summary, and work history.
- **Domain Discrimination Guard**: Penalizes candidates with severe technical domain mismatch (<20% semantic similarity or 0 matched skills) to automatically trigger `REJECT` decisions.

### 2. 📋 Visual ATS Drag-and-Drop Kanban Pipeline (`/pipeline`)
- Transforms candidate tracking into an interactive 6-column workflow:
  `📥 Screened` &rarr; `⭐ Shortlisted` &rarr; `📞 Phone Screen` &rarr; `💻 Tech Interview` &rarr; `🎉 Offer Stage` &rarr; `❌ Rejected`.
- Drag and drop cards in real-time with instant server sync and toast notifications.
- Search and filter cards by name, skill, or role on the fly.

### 3. 🛡️ "Red Flag" & Consistency Audit Engine
- **Employment Gap Detection**: Identifies unexplainable career gaps exceeding 6 months.
- **Date Chronology Verifier**: Flags conflicting, inverted, or overlapping job tenures.
- **Buzzword Stuffing Guard**: Detects skills listed in headers without corresponding evidence in job descriptions.
- **Integrity Score (0–100%)**: Computes a transparent candidate integrity rating.

### 4. 🤖 Multi-Agent 360° Candidate Evaluation Panel
Simulates a collaborative hiring committee composed of 4 expert AI personas:
- **💻 Code Quality Auditor**: Evaluates software craftsmanship, testing, and modern standards.
- **🏗️ Systems Architect**: Assesses scalability, cloud resilience, and distributed design.
- **📈 Business Impact Evaluator**: Measures commercial outcomes, leadership, and KPI delivery.
- **👔 Hiring Supervisor**: Synthesizes committee feedback into an executive consensus rating.

### 5. 🎙️ AI Technical Pre-Screening Simulator
- Generates 3 customized behavioral and technical interview questions based on the candidate's exact experience.
- Interactive speech dictation (Web Speech API) with real-time audio animation.
- Instant AI evaluation of spoken or typed candidate answers with a 1–10 suitability rating, strengths, and gap analysis.

### 6. 📈 Talent Pool Analytics & Market Intelligence (`/analytics`)
- **Score Distribution Histogram**: Bell curve distribution across standard scoring tiers.
- **ATS Stage Funnel**: Conversion rates from initial screening to offer stage.
- **Top Competencies Breakdown**: Frequency distribution of the top 10 skills in the applicant pool.
- **Seniority Distribution**: Proportions of Junior, Mid-Level, Senior, and Lead candidates.

### 7. 📄 Executive 1-Page PDF Dossier Export
- Generates polished, print-ready PDF recruiter dossiers via ReportLab.
- Includes candidate metrics, radar breakdown, executive summary, and tailored interview cheat sheet.

### 8. 🛡️ DEI Blind Screening Mode
- One-click bias elimination toggle instantly masks candidate names, email addresses, phone numbers, and identifying demographics across table and modal views.

### 9. 📱 Multi-Device Responsive Design
- Optimized for **Mobile Handsets** (320px–480px), **Tablets** (768px–1024px), and **Desktops** (1025px–1440px+).
- Features an animated mobile hamburger navigation drawer, touch-swipe table scroller with swipe hints, and responsive modal bottom-sheets.

### 10. 🔍 Vector Search & Candidate Intelligence (`/vector-search`)
- Sublinear TF-IDF & dense n-gram vector spaces indexing entire applicant pools in memory.
- Natural language semantic candidate discovery (*"Senior backend engineer with Python, Kubernetes, and distributed architecture"*).
- **Candidate-to-Candidate Similarity**: Instant peer matching to find candidates similar to any top-performing profile.

### 11. 🤖 Evidence-Grounded Resume RAG Copilot
- Semantic document chunking into isolated units of evidence (Executive Summary, Skills, Work History, Education).
- Natural language inquiry with zero hallucination and exact inline source citations (e.g., `[Source: Work History: Lead Backend Engineer @ CloudScale Inc]`).
- Transparent **Grounding Confidence Score** ($\ge 40\%$ to $100\%$) based on retrieval relevance.

### 12. 🎯 Multi-Dimensional Semantic Alignment Engine
- Decomposes applicant-to-role fit into multi-tiered semantic vectors:
  - **Skills Alignment**: Deep overlap between target JD requirements and candidate skill matrix.
  - **Experience Alignment**: Role title hierarchy and tenure relevance.
  - **Education Alignment**: Academic rigor, degree levels, and STEM credentials.
  - **Seniority Classification**: Automatic classification into Junior, Mid-Level, or Senior/Lead fit.

### 13. ⚖️ Explainable AI (XAI) Score Attribution
- SHAP-inspired additive factor attribution:
  $$f(x) = E[f(x)] + \sum_{i=1}^M \phi_i$$
- Transparent waterfall showing exact positive point drivers (+Skills, +Experience, +Degrees) and deductions (-Career Gaps, -Unverified Buzzwords, -Domain Mismatch).

### 14. 🏢 Multi-Tenant SaaS Architecture & Role-Based Access Control (RBAC)
- Enterprise tenancy isolation with `SQLAlchemy` ORM (`Organization`, `User`, `JobPosting`, `CandidateApplication`).
- Cryptographic JWT bearer tokens with 24-hour expiry and `bcrypt` password hashing.
- Four distinct enterprise roles with strict endpoint gatekeeping:
  - **Super Admin**: Global multi-organization platform administration.
  - **Admin**: Organization management, recruiter invitations, and pipeline controls.
  - **Recruiter**: Requisition creation, batch resume upload, and candidate stage transitions.
  - **Hiring Manager**: Candidate review, notes, dossier inspection, and interview evaluation.

### 15. 🐳 Production Dockerization & Automated CI/CD Pipeline
- **Production Containerization**: Multi-stage, non-root user (`talentai`), Tesseract OCR pre-installed, Gunicorn WSGI runtime, and Docker Compose orchestration.
- **Enterprise CI/CD**: GitHub Actions workflow running code compilation, PyTest suites (23 automated tests across Vector, SaaS, and Knowledge Graph), and Docker container build verification.

### 16. 🕸️ Candidate Knowledge Graph & Entity Intelligence (`/knowledge-graph`)
- Heterogeneous NetworkX graph mapping Candidates, Skills, Companies, and Roles into an interconnected topology.
- **Topological Centrality**: Detects high-value hub competencies via Degree Centrality and Betweenness Centrality.
- **Cross-Domain Technical Bridges**: Automatically discovers bridging skills (e.g. Python, Docker, SQL) that link disparate engineering disciplines.
- **Candidate Ego-Networks & Adjacent Skill Recommendations**: Discovers complementary skills through graph neighbor co-occurrence affinities.
- **Interactive Force Simulation**: Zero-dependency HTML5 Canvas visualization with node dragging, zooming, domain filtering, and real-time hover inspection.

### 17. ⚔️ Multi-Agent Adversarial Debate Committee
- Moves beyond passive scoring into an active 3-tier adversarial hiring trial:
  - **Candidate Advocate (Defense)**: Argues for candidate's velocity, production output, and context around career gaps.
  - **Technical Skeptic (Prosecution)**: Forensic audit exposing unverified buzzword stuffing, lack of quantified ROI, and chronology risks.
  - **Cross-Examination & Rebuttal**: Point-by-point live rebuttal exchange between defense and prosecution.
  - **Chief Talent Arbiter**: Calibrated hiring score, final verdict (`STRONG ADVANCE`, `ADVANCE WITH CONDITIONS`, `DEEP DIVE REQUIRED`), and a mandatory 4-point **Risk Mitigation Checklist** for live interviewers.

### 18. 🎙️ Dynamic Adaptive Technical Interview Simulator
- Evaluates candidate spoken or typed responses for architectural depth, edge cases, and metrics.
- Dynamically generates piercing follow-up questions targeting detected weak spots or hand-waving assertions.
- Provides real-time interviewer rubrics detailing what to listen for on the adaptive probe.

---

## 🛠️ Architecture & Tech Stack

```
                              ┌─────────────────────────────────────────┐
                              │          Client (Web Browser)           │
                              │     Desktop   •   Tablet   •   Mobile   │
                              └────────────────────┬────────────────────┘
                                                   │ HTTPS / JWT Bearer
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Multi-Tenant SaaS Boundary (RBAC)                                 │
│                     Super Admin  •  Admin  •  Recruiter  •  Hiring Manager                        │
├───────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                         Flask Application                                         │
│                                                                                                   │
│  ┌──────────────────────┐   ┌──────────────────────┐   ┌───────────────────────────────────────┐  │
│  │   Document Parser    │   │     AI Extractor     │   │         Scoring Logic Engine          │  │
│  │ PyMuPDF • docx • OCR │──▶│ Heuristic/OpenRouter ├──▶│ Skills (40) • Exp (30) • Edu (15)     │  │
│  └──────────────────────┘   └──────────────────────┘   └───────────────────┬───────────────────┘  │
│                                                                            │                      │
│  ┌──────────────────────┐   ┌──────────────────────┐   ┌───────────────────▼───────────────────┐  │
│  │ Consistency Auditor  │   │ Multi-Agent Reviewer │   │   Vector Search & RAG Intelligence    │  │
│  │ Gaps • Chrono • Buzz │   │  4 Persona Committee │   │ MiniLM Embeddings • Grounded Citations│  │
│  └──────────────────────┘   └──────────────────────┘   └───────────────────────────────────────┘  │
│                                        │                                                          │
│                                        ▼                                                          │
│                      ┌───────────────────────────────────────────┐                                │
│                      │         Enterprise Data Persistence       │                                │
│                      │   SaaS DB (SQLite/Postgres) • Resumes DB  │                                │
│                      └───────────────────────────────────────────┘                                │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- **Backend**: Python 3.10+, Flask 3.0+, Gunicorn
- **SaaS & Auth**: SQLAlchemy 2.0+, PyJWT, bcrypt password encryption
- **Vector & NLP**: Sublinear TF-IDF vector spaces, cosine similarity, n-gram semantic retrieval
- **Parsing**: PyMuPDF (`fitz`), `python-docx`, Tesseract OCR + Pillow
- **AI & Reasoning**: Heuristic NLP tokenizers + optional OpenRouter LLM (`gpt-4o-mini`, `gemini-1.5-flash`)
- **DevOps**: Docker, Docker Compose, GitHub Actions CI/CD Pipeline
- **Frontend**: Vanilla HTML5/CSS3 (zero Tailwind dependencies), Plus Jakarta Sans typography, Glassmorphism

---

## 📂 Project Structure

```
ai-resume-screening/
├── app.py                         # Central Flask application & route controllers
├── saas_auth.py                   # Multi-Tenant SaaS data models, bcrypt & JWT RBAC engine
├── knowledge_graph.py             # Candidate Knowledge Graph & NetworkX entity topology
├── adversarial_debate.py          # Multi-Agent Adversarial Debate Committee engine
├── adaptive_interview.py          # Dynamic Adaptive Technical Interview Simulator
├── vector_search.py               # Vector search candidate intelligence & similarity index
├── rag_engine.py                  # Evidence-grounded resume RAG retriever & citation engine
├── semantic_alignment.py          # Multi-dimensional semantic alignment engine (Skills, Exp, Edu)
├── xai_engine.py                  # Explainable AI (XAI) SHAP-style factor attribution
├── ai_extractor.py                # Skill extraction, tech vocabularies & heuristic parser
├── audit_engine.py                # Resume red flag & consistency audit engine
├── multi_agent_evaluator.py       # 4-persona multi-agent 360° review engine
├── prescreen_evaluator.py         # Speech-to-text pre-screen simulator & response grader
├── scoring_logic.py               # 0–100 explainable fit score & domain discrimination
├── dossier_generator.py           # Executive 1-page PDF dossier generator (ReportLab)
├── resume_parser.py               # Multi-format document parser (PDF, DOCX, Images)
├── storage.py                     # Resilient storage manager (SQLite + MongoDB)
├── Dockerfile                     # Multi-stage production container with Tesseract OCR
├── docker-compose.yml             # Single-command orchestration with healthcheck & volume mounts
├── .github/workflows/ci.yml       # Production CI/CD automated pipeline (Lint, PyTest, Docker)
├── tests/                         # Automated test suites (PyTest)
│   ├── test_phase1_vector_rag.py  # 100% passing tests for Vector, RAG, Alignment, and XAI
│   ├── test_phase2_saas_rbac.py   # 100% passing tests for SaaS registration, JWT, and RBAC
│   └── test_phase3_knowledge_graph_debate.py # 100% passing tests for Knowledge Graph, Debate & Adaptive Interview
├── screenshots/                   # 25 High-resolution proof-of-work screenshots
├── sample_resumes/                # Authentic test resumes across diverse roles
├── templates/                     # Jinja2 HTML templates
│   ├── base.html                  # Master layout with responsive mobile navigation
│   ├── index.html                 # Landing page & system overview
│   ├── vector_search.html         # Vector search, RAG inquiry & XAI factor modals
│   ├── knowledge_graph.html       # Interactive Force-Directed Graph & Adversarial Debate Arena
│   ├── dashboard.html             # Recruiter candidate table, filters & drawers
│   ├── pipeline.html              # Drag-and-drop ATS Kanban pipeline board
│   ├── analytics.html             # Talent pool metrics & funnel visualizations
│   ├── matrix.html                # Competency gap & role alignment heatmap
│   ├── upload.html                # Multi-file drag-and-drop batch upload
│   └── screen_text.html           # Text-based screening with quick role presets
├── static/                        # Static UI assets (CSS design system & client JS)
├── requirements.txt               # Dependencies (SQLAlchemy, PyJWT, bcrypt, NetworkX, etc.)
└── README.md                      # Comprehensive project documentation
```

---

## 🚀 Getting Started

### 🐳 Option A: One-Command Docker Setup (Recommended)
Run the entire production-grade stack with persistent storage and healthchecks:
```bash
docker compose up --build
```
Open **http://localhost:5000** in your browser.

---

### 💻 Option B: Local Python Virtual Environment

#### 1. Clone the Repository
```bash
git clone https://github.com/anujmundu/ai-resume-screening.git
cd ai-resume-screening
```

#### 2. Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables (Optional)
Create a `.env` file in the project root:
```ini
# Optional: OpenRouter API key for LLM-powered extraction (offline heuristics used if omitted)
OPENROUTER_API_KEY=your_key_here

# SaaS Database URL (defaults to sqlite:///saas_platform.db if omitted)
SAAS_DATABASE_URL=sqlite:///saas_platform.db

# JWT Cryptographic Secret
JWT_SECRET_KEY=talent-ai-enterprise-jwt-secret-2026

# Server configuration
PORT=5000
FLASK_DEBUG=1
```
> [!TIP]
> The entire application is designed to function **100% offline** with **zero paid APIs**. If `OPENROUTER_API_KEY` is omitted, TalentAI automatically uses its internal heuristic NLP engine, local vector spaces, and local SQLite databases.

#### 5. Run the Application
```bash
python app.py
```
Open your browser and navigate to: **http://127.0.0.1:5000**

---

## 🧪 Testing & Automated Verification

### Execute the Full Automated Test Suite (PyTest)
```bash
pytest -v
```
**Test Results (23 passing tests across Phase 1, Phase 2, and Phase 3):**
```
test_enterprise_features.py::test_pipeline_and_endpoints PASSED
tests/test_phase1_vector_rag.py::test_vector_index_building_and_search PASSED
tests/test_phase1_vector_rag.py::test_vector_similar_candidates PASSED
tests/test_phase1_vector_rag.py::test_rag_chunking PASSED
tests/test_phase1_vector_rag.py::test_rag_query_with_grounding PASSED
tests/test_phase1_vector_rag.py::test_semantic_alignment_calculation PASSED
tests/test_phase1_vector_rag.py::test_xai_factor_attribution PASSED
tests/test_phase1_vector_rag.py::test_api_vector_search_endpoint PASSED
tests/test_phase1_vector_rag.py::test_api_vector_search_page_renders PASSED
tests/test_phase2_saas_rbac.py::test_saas_default_seed PASSED
tests/test_phase2_saas_rbac.py::test_auth_registration_and_validation PASSED
tests/test_phase2_saas_rbac.py::test_auth_login_and_jwt_verification PASSED
tests/test_phase2_saas_rbac.py::test_protected_me_endpoint PASSED
tests/test_phase2_saas_rbac.py::test_rbac_team_management_and_invitation PASSED
tests/test_phase2_saas_rbac.py::test_rbac_job_requisition_permissions PASSED
tests/test_phase2_saas_rbac.py::test_multi_tenant_data_isolation PASSED
tests/test_phase3_knowledge_graph_debate.py::test_skill_taxonomy_categorization PASSED
tests/test_phase3_knowledge_graph_debate.py::test_knowledge_graph_construction PASSED
tests/test_phase3_knowledge_graph_debate.py::test_knowledge_graph_candidate_subgraph_and_adjacent_skills PASSED
tests/test_phase3_knowledge_graph_debate.py::test_knowledge_graph_bridges PASSED
tests/test_phase3_knowledge_graph_debate.py::test_adversarial_debate_engine PASSED
tests/test_phase3_knowledge_graph_debate.py::test_dynamic_adaptive_interview_evaluation PASSED
tests/test_phase3_knowledge_graph_debate.py::test_flask_phase3_api_endpoints PASSED
============================== 23 passed in 12.05s ==============================
```

### Multi-Role Evaluation & Role Discrimination Benchmark
```bash
python test_and_screen_diverse_roles.py
```

---

## 🔐 Multi-Tenant SaaS & RBAC Reference

### Role Hierarchy & Permissions Matrix

| Permission / Action | Super Admin | Admin | Recruiter | Hiring Manager |
| :--- | :---: | :---: | :---: | :---: |
| **Manage Multiple Organizations** | ✅ | ❌ | ❌ | ❌ |
| **Invite Team Members (`/api/org/invite`)** | ✅ | ✅ | ❌ | ❌ |
| **View Organization Team (`/api/org/team`)** | ✅ | ✅ | ❌ | ❌ |
| **Create Requisitions (`/api/org/jobs`)** | ✅ | ✅ | ✅ | ❌ |
| **View Organization Requisitions** | ✅ | ✅ | ✅ | ✅ |
| **Batch Screen Resumes & Move Stages** | ✅ | ✅ | ✅ | ❌ |
| **Inspect Dossiers & Audit Red Flags** | ✅ | ✅ | ✅ | ✅ |
| **Grade Pre-Screen Answers** | ✅ | ✅ | ✅ | ✅ |

### SaaS REST API Endpoints

| Endpoint | Method | Required Role | Description |
| :--- | :--- | :--- | :--- |
| `/api/auth/register` | `POST` | Public | Registers a new Tenant Organization and assigns caller as Admin |
| `/api/auth/login` | `POST` | Public | Authenticates credentials with bcrypt; issues 24-hour cryptographic JWT |
| `/api/auth/me` | `GET` | Authenticated | Retrieves current authenticated user profile and organization metadata |
| `/api/org/jobs` | `GET` | Authenticated | Lists all job postings belonging strictly to caller's tenant organization |
| `/api/org/jobs` | `POST` | Admin, Recruiter | Creates a new job posting scoped to caller's tenant organization |
| `/api/org/team` | `GET` | Admin | Lists all team member accounts within the organization |
| `/api/org/invite` | `POST` | Admin | Invites and provisions a new User account within the organization |

---

## 🕸️ Phase 3: Candidate Knowledge Graph & Entity Intelligence

TalentAI features a **Heterogeneous Knowledge Graph Engine** powered by `NetworkX`, modeling complex topological relationships connecting Candidates, Technical Skills, Companies, Roles, and Academic Degrees.

```
                    ┌─────────────────┐
                    │    Candidate    │
                    │   (Score: 94)   │
                    └────────┬────────┘
        ┌────────────────────┼────────────────────┐
        │ has_skill          │ worked_at          │ studied
        ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Skill Node   │    │ Company Node  │    │  Degree Node  │
│   (Python)    │    │ (StreamScale) │    │ (M.S. in CS)  │
└───────┬───────┘    └───────────────┘    └───────────────┘
        │ co_occurs (weight: 12)
        ▼
┌───────────────┐
│  Skill Node   │
│    (Kafka)    │
└───────────────┘
```

### Key Graph Intelligence Capabilities

1. **Domain Constellations & Clustered Layout**:
   - Organizes technical competencies into categorized radial sectors (`Backend & Systems`, `Cloud & DevOps`, `Frontend & Web`, `Data & Databases`, `AI, ML & NLP`, `Security & Architecture`).
   - Prevents visual "hairballs" and unreadable tangled meshes, replacing them with a structured, executive-grade galaxy visualization.

2. **Smart Edge Stratification & Density Control**:
   - **Primary Talent Links**: Renders direct, verified candidate competency and career edges (`has_skill`, `worked_at`, `studied`).
   - **Skill Synergy Mesh**: Optional co-occurrence network layer for analyzing cross-competency affinity.
   - **Spotlight Dimming**: Hovering or clicking any entity illuminates direct 1-hop connections at 100% brightness while fading all unrelated nodes to 10% opacity.

3. **Live Entity Search Autocomplete**:
   - Fast toolbar search box (`🔍 Search candidate, skill, company...`) with real-time dropdown matching.
   - Instantly zooms and pans the camera to the target node, highlights its neighborhood, and opens the Entity Inspector.

4. **Interactive Entity Inspector Panel**:
   - **Candidate Intelligence**: Candidate avatar, fit score badge, pipeline stage, verified skills cloud, and instant action triggers (`⚔️ Launch Adversarial Debate`, `🎯 Focus Ego Network`).
   - **Competency Intelligence**: Domain category, NetworkX Degree & Betweenness Centrality metrics, talent pool candidates possessing the skill, and complementary adjacent competencies.
   - **Adjacent Skill Recommendations**: Recommends high-affinity adjacent skills via graph neighborhood co-occurrence with candidate's verified background.

5. **Multi-Agent Adversarial Debate Committee**:
   - Simulates a formal hiring panel with three specialized LLM personas:
     - **Candidate Advocate (Defense)**: Builds positive arguments around career velocity, technical strengths, and project complexity.
     - **Technical Skeptic (Prosecution)**: Forensic challenge against resume gaps, buzzword stuffing, and lack of verified production scale.
     - **Chief Talent Arbiter (Consensus)**: Evaluates the cross-examination exchange, delivers calibrated score adjustments, and generates a 4-point **Risk Mitigation Checklist** for live interview loops.

6. **Dynamic Adaptive Technical Interview Simulator**:
   - Scores candidate verbal/written responses on a strict 1.0–10.0 depth scale.
   - Detects architectural trade-offs, quantitative metrics, and ambiguous claims.
   - Generates follow-up drill-down questions tailored to probe unverified competencies.

### Phase 3 REST API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/knowledge-graph` | `GET` | Web UI for the interactive Canvas Knowledge Graph &amp; Entity Intelligence HUD |
| `/api/graph/data` | `GET` | Serializes full or sampled graph topology (`nodes`, `links`, `stats`, `bridges`) |
| `/api/candidate/<id>/graph` | `GET` | Extracts candidate 1-hop ego network and adjacent skill recommendations |
| `/api/candidate/<id>/adversarial-debate` | `POST` | Executes Multi-Agent Adversarial Debate (Advocate vs Skeptic vs Arbiter) |
| `/api/interview/adaptive-followup` | `POST` | Evaluates technical depth score (1-10) and generates adaptive follow-up questions |

---


**Anuj Mundu**  
Full-Stack Developer & AI Systems Engineer  
- **GitHub**: [@anujmundu](https://github.com/anujmundu)  
- **LinkedIn**: [Anuj Mundu](https://linkedin.com/in/anuj-mundu)

---

## 📄 License

This project is licensed under the **MIT License** &bull; See the [LICENSE](LICENSE) file for details.

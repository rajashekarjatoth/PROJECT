# 🧠 Cognitive Assistance & Interview Preparation Bot

An intelligent full-stack conversational AI assistant and Socratic technical mentor built with **Python, FastAPI, RAG (Retrieval-Augmented Generation), NLP, REST APIs, Vector Database (ChromaDB), and modern Glassmorphic UI**.

---

## 🌟 Key Highlights & Architecture

### 1. 🛡️ User Authentication & Profiles
- **JWT-Based Authentication**: Secure Bearer tokens with configurable expiration.
- **PBKDF2 Password Hashing with Salt**: FIPS-compliant cryptographic password protection.
- **Profile & Analytics History**: Tracks every mock interview attempt, readiness score, and metric history.
- **1-Click Demo Profiles**: Pre-seeded `Candidate (Alex)` and `Admin` users for instant testing.

### 2. 🎯 Dynamic Mock Interview Simulator
- **Multi-Domain Coverage**: Python, Java, SQL, Data Science, Machine Learning, AI, Web Development, Cloud, and HR Behavioral (STAR method).
- **Progressive Scaffolding Hints**: Unlocks Hint 1 (Direction) → Hint 2 (Core concept) → Hint 3 (Pseudocode/Formula) without giving away the full answer.
- **Voice Dictation**: Built-in Web Speech API integration for hands-free answer dictation.
- **Intelligent Evaluation Scorecard**:
  - **Correctness Score (0-100%)**
  - **Clarity & Structure Score (0-100%)**
  - **Technical Depth Score (0-100%)**
  - **Missing Concept Detection** (Identifies missing industry keywords & mechanisms)
  - **Targeted Follow-up Probing**
- **Comprehensive Preparation Report**: Final grade (A+, A, B, C), readiness level tier, actionable study recommendations, and printable summary.

### 3. 💻 Coding Problem Assistance & Step-by-Step Guidance
- **Curated Algorithm Challenges**: Two Sum, Valid Parentheses, LRU Cache, etc.
- **4-Step Progressive Accordion**:
  - **Step 1**: Intuition & Edge Cases
  - **Step 2**: Optimal Approach & Data Structure
  - **Step 3**: Step-by-Step Pseudocode
  - **Step 4**: Complete Code Implementation & **Line-by-Line Technical Breakdown**
- **In-Browser Scratchpad**: Python 3.14 syntax editor.

### 4. 📚 RAG Knowledge Retrieval Pipeline
```text
Document (PDF/MD/TXT) 
  → PyPDF / Text Extraction 
  → Recursive Chunking (500 words, 80 overlap) 
  → Feature Hashing & Dense Vector Embeddings 
  → ChromaDB Persistent Vector Index (Cosine Metric) 
  → Top-K Semantic Similarity Search 
  → Augmented Socratic Prompting with Source Citations
```
- **Document Ingestion**: Drag-and-drop file upload for PDF, Markdown, Python, and SQL files.
- **Vector Search Playground**: Live semantic search tool displaying similarity match percentages and retrieved chunk snippets.

### 5. 💬 Socratic Mentor NLP Engine
- **Ambiguity Detection**: Flags vague questions (e.g., *"which is best?"*, *"how do I fix my code?"*) and poses clarifying questions before answering.
- **Dual Personas**:
  - **Socratic Mentor**: Guided questions, step-by-step scaffolding, mental checkpoints.
  - **Direct Technical**: Standard senior engineering reference format.
- **Level Adaptation**: Explanations adjusted for **Beginner**, **Intermediate**, and **Advanced** audiences.

---

## 🚀 Quickstart & Running Locally

### 1. Start the Server
From the project root:
```bash
python run.py
```
*(Or navigate to `backend/` and run `python run.py`)*

### 2. Access the Application
- **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger REST API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc API Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 3. Pre-Seeded Demo Credentials
- **Candidate User**: `candidate@prep.ai` / `Candidate@123`
- **Admin User**: `admin@cognitivebot.ai` / `Admin@12345`
*(You can also click the 1-click demo buttons in the login modal)*

---

## 📡 REST API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register new candidate or admin account |
| `POST` | `/api/auth/login` | Authenticate and obtain JWT Bearer token |
| `GET` | `/api/auth/me` | Retrieve profile and historical stats |
| `POST` | `/api/chat` | Socratic mentor multi-turn dialogue with RAG context |
| `POST` | `/api/interview/start` | Initialize mock interview session & fetch turn 1 |
| `POST` | `/api/interview/hint` | Request progressive hints (Level 1, 2, or 3) |
| `POST` | `/api/interview/evaluate` | Evaluate candidate response & return metrics + follow-up |
| `GET` | `/api/interview/report/{id}` | Generate final interview readiness scorecard |
| `GET` | `/api/coding/problems` | List algorithm challenges |
| `POST` | `/api/coding/hint` | Progressive coding hints & line-by-line solutions |
| `POST` | `/api/documents/upload` | Upload & ingest PDF/TXT/MD into ChromaDB |
| `GET` | `/api/documents/list` | View indexed document inventory |
| `POST` | `/api/documents/search` | Live semantic vector similarity search |
| `GET` | `/api/user/history` | Historical session records and scores |
| `GET` | `/api/stats` | Aggregated platform metrics and chunk counts |

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR, BASE_DIR
from app.database import (
    init_db, get_db, SessionLocal, User, InterviewSession, InterviewTurn, DocumentRecord, ChatMessage
)
from app.auth import (
    hash_password, verify_password, create_access_token, generate_salt,
    get_current_user, get_optional_user, seed_demo_users
)
from app.models import (
    UserRegister, UserLogin, AuthResponse, UserProfile,
    StartInterviewRequest, SubmitAnswerRequest, RequestHintRequest, HintResponse,
    TurnEvaluationResponse, FinalReportResponse, ChatRequest, ChatResponse,
    SearchDocumentRequest, DocumentItem, CodingHintRequest, CodingProblemResponse
)
from app.rag_engine import (
    ingest_document, search_knowledge_base, seed_default_knowledge_base
)
from app.interview_engine import (
    get_random_or_indexed_question, evaluate_candidate_answer, generate_final_interview_report,
    QUESTION_BANK
)
from app.coding_engine import (
    get_all_coding_problems, get_coding_problem_details, get_coding_hint
)
from app.mentor_nlp import generate_mentor_reply

# Initialize database schema and pre-seed knowledge base
init_db()
seed_default_knowledge_base()

app = FastAPI(
    title="Cognitive Assistance & Interview Preparation Bot",
    description="Intelligent Socratic technical mentor with RAG-based context retrieval, dynamic mock interviews, and progressive coding guidance.",
    version="2.0.0"
)

# Enable CORS for all local development origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed demo accounts if database is empty
with SessionLocal() as db_session:
    seed_demo_users(db_session)

# -------------------------------------------------------------
# 1. USER AUTHENTICATION & PROFILE APIS
# -------------------------------------------------------------

@app.post("/api/auth/register", response_model=AuthResponse)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    
    salt = generate_salt()
    pwd_hash = hash_password(user_in.password, salt)
    user = User(
        email=user_in.email.lower(),
        full_name=user_in.full_name,
        password_hash=pwd_hash,
        salt=salt,
        role=user_in.role or "candidate"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@app.post("/api/auth/login", response_model=AuthResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if not user or not verify_password(user_in.password, user.salt, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    token = create_access_token({"sub": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@app.get("/api/auth/me", response_model=UserProfile)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(InterviewSession).filter(InterviewSession.user_id == current_user.id).all()
    avg_score = round(sum([s.score for s in sessions]) / len(sessions), 1) if sessions else 0.0

    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "created_at": current_user.created_at,
        "total_interviews": len(sessions),
        "average_score": avg_score
    }


# -------------------------------------------------------------
# 2. CHAT & SOCRATIC MENTOR APIS
# -------------------------------------------------------------

@app.post("/api/chat", response_model=ChatResponse)
def chat_with_mentor(
    req: ChatRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    reply_data = generate_mentor_reply(
        message=req.message,
        mode=req.mode,
        level=req.level,
        use_rag=req.use_rag
    )

    if current_user:
        # Save history for authenticated users
        msg_user = ChatMessage(
            user_id=current_user.id,
            role="user",
            content=req.message,
            mode=req.mode,
            level=req.level
        )
        msg_bot = ChatMessage(
            user_id=current_user.id,
            role="assistant",
            content=reply_data["reply"],
            mode=req.mode,
            level=req.level
        )
        db.add_all([msg_user, msg_bot])
        db.commit()

    return reply_data


# -------------------------------------------------------------
# 3. INTERVIEW SIMULATOR APIS
# -------------------------------------------------------------

# Active in-memory session question tracking for seamless flow
_active_session_questions: Dict[int, Dict[str, Any]] = {}

@app.post("/api/interview/start")
def start_interview(
    req: StartInterviewRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1

    session = InterviewSession(
        user_id=user_id,
        title=f"{req.domain} {req.interview_type.capitalize()} Mock Interview",
        interview_type=req.interview_type,
        domain=req.domain,
        difficulty=req.difficulty,
        status="in_progress",
        total_turns=0,
        score=0.0
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Pick initial question
    first_q = get_random_or_indexed_question(req.domain, req.interview_type, req.difficulty)
    _active_session_questions[session.id] = {
        "current_question": first_q,
        "hints_used": 0,
        "turn_index": 1,
        "used_question_ids": [first_q["id"]]
    }

    # Record turn
    turn = InterviewTurn(
        session_id=session.id,
        turn_index=1,
        question=first_q["question"]
    )
    db.add(turn)
    db.commit()

    return {
        "session_id": session.id,
        "title": session.title,
        "interview_type": session.interview_type,
        "domain": session.domain,
        "difficulty": session.difficulty,
        "turn_index": 1,
        "question": first_q["question"],
        "total_hints_available": len(first_q.get("hints", []))
    }


@app.post("/api/interview/hint", response_model=HintResponse)
def request_hint(req: RequestHintRequest, db: Session = Depends(get_db)):
    session_data = _active_session_questions.get(req.session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Active interview session not found.")

    current_q = session_data["current_question"]
    hints = current_q.get("hints", [])
    
    level = max(1, min(req.hint_level, len(hints)))
    hint_text = hints[level - 1] if hints else "Consider breaking down the problem into smaller logical steps."
    
    session_data["hints_used"] = max(session_data["hints_used"], level)

    return {
        "session_id": req.session_id,
        "hint_level": level,
        "hint_type": f"Hint Level {level}",
        "hint": hint_text,
        "hints_remaining": max(0, len(hints) - level)
    }


@app.post("/api/interview/evaluate", response_model=TurnEvaluationResponse)
def evaluate_turn(
    req: SubmitAnswerRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    session = db.query(InterviewSession).filter(InterviewSession.id == req.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    session_data = _active_session_questions.get(req.session_id)
    current_q = session_data["current_question"] if session_data else {
        "question": "Interview question",
        "rubric_keywords": ["scalability", "architecture", "trade-offs", "performance"]
    }
    hints_used = session_data["hints_used"] if session_data else 0

    evaluation = evaluate_candidate_answer(current_q, req.answer, hints_used)

    # Update turn in DB
    turn_idx = session_data["turn_index"] if session_data else 1
    turn = db.query(InterviewTurn).filter(
        InterviewTurn.session_id == session.id,
        InterviewTurn.turn_index == turn_idx
    ).first()

    if turn:
        turn.user_answer = req.answer
        turn.hints_used = hints_used
        turn.score_correctness = evaluation["score_correctness"]
        turn.score_clarity = evaluation["score_clarity"]
        turn.score_depth = evaluation["score_depth"]
        turn.overall_turn_score = evaluation["overall_turn_score"]
        turn.feedback = evaluation["feedback"]
        turn.strengths = "\n".join(evaluation["strengths"])
        turn.missing_concepts = ", ".join(evaluation["missing_concepts"])
        turn.follow_up_question = evaluation["follow_up_question"]
        db.commit()

    # Session progress check (3 turns per session by default)
    is_completed = turn_idx >= 3
    next_question = None

    if is_completed:
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        # Compute final session score
        all_turns = db.query(InterviewTurn).filter(InterviewTurn.session_id == session.id).all()
        session.score = round(sum([t.overall_turn_score for t in all_turns if t.overall_turn_score]) / len(all_turns), 1) if all_turns else 0.0
        db.commit()
    else:
        # Generate next question
        next_turn_idx = turn_idx + 1
        used_ids = session_data.get("used_question_ids", []) if session_data else []
        next_q = get_random_or_indexed_question(session.domain, session.interview_type, session.difficulty, exclude_ids=used_ids)
        next_question = next_q["question"]

        if session_data:
            session_data["current_question"] = next_q
            session_data["hints_used"] = 0
            session_data["turn_index"] = next_turn_idx
            session_data["used_question_ids"].append(next_q["id"])

        new_turn = InterviewTurn(
            session_id=session.id,
            turn_index=next_turn_idx,
            question=next_q["question"]
        )
        db.add(new_turn)
        db.commit()

    return {
        "session_id": session.id,
        "turn_index": turn_idx,
        "score_correctness": evaluation["score_correctness"],
        "score_clarity": evaluation["score_clarity"],
        "score_depth": evaluation["score_depth"],
        "overall_turn_score": evaluation["overall_turn_score"],
        "feedback": evaluation["feedback"],
        "strengths": evaluation["strengths"],
        "missing_concepts": evaluation["missing_concepts"],
        "follow_up_question": evaluation["follow_up_question"],
        "next_question": next_question,
        "is_session_completed": is_completed
    }


@app.get("/api/interview/report/{session_id}", response_model=FinalReportResponse)
def get_interview_report(session_id: int, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    user = db.query(User).filter(User.id == session.user_id).first()
    turns = db.query(InterviewTurn).filter(InterviewTurn.session_id == session.id).all()

    report_data = generate_final_interview_report(session, turns)

    history_list = []
    for t in turns:
        history_list.append({
            "turn_index": t.turn_index,
            "question": t.question,
            "user_answer": t.user_answer,
            "score": t.overall_turn_score,
            "feedback": t.feedback,
            "strengths": t.strengths.split("\n") if t.strengths else [],
            "missing": t.missing_concepts.split(",") if t.missing_concepts else []
        })

    return {
        "session_id": session.id,
        "user_email": user.email if user else "guest@prep.ai",
        "interview_type": session.interview_type,
        "domain": session.domain,
        "difficulty": session.difficulty,
        "started_at": session.started_at,
        "completed_at": session.completed_at,
        "overall_score": report_data["overall_score"],
        "readiness_level": report_data["readiness_level"],
        "grade": report_data["grade"],
        "turns_evaluated": len(turns),
        "metric_averages": report_data["metric_averages"],
        "summary_feedback": report_data["summary_feedback"],
        "key_strengths": report_data["key_strengths"],
        "recommended_topics": report_data["recommended_topics"],
        "history": history_list
    }


# -------------------------------------------------------------
# 4. CODING PROBLEM ASSISTANCE APIS
# -------------------------------------------------------------

@app.get("/api/coding/problems")
def list_coding_problems():
    return get_all_coding_problems()


@app.get("/api/coding/problem/{problem_id}")
def get_coding_problem(problem_id: str):
    problem = get_coding_problem_details(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Coding problem not found.")
    return problem


@app.post("/api/coding/hint")
def request_coding_hint(req: CodingHintRequest):
    hint = get_coding_hint(req.problem_id, req.hint_level)
    return hint


# -------------------------------------------------------------
# 5. RAG KNOWLEDGE BASE & DOCUMENT MANAGEMENT APIS
# -------------------------------------------------------------

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form("Interview Prep"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    safe_filename = file.filename.replace(" ", "_")
    target_path = UPLOAD_DIR / safe_filename

    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(target_path)
    doc_title = title if title and title.strip() else safe_filename

    # Save metadata in SQL DB
    doc_record = DocumentRecord(
        title=doc_title,
        filename=safe_filename,
        file_type=Path(safe_filename).suffix.replace(".", "").upper(),
        file_size=file_size,
        category=category or "Interview Prep",
        uploader_email=current_user.email if current_user else "admin@cognitivebot.ai"
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # Ingest into Vector Database
    num_chunks = ingest_document(
        doc_id=doc_record.id,
        title=doc_record.title,
        filepath=str(target_path),
        filename=safe_filename
    )

    doc_record.num_chunks = num_chunks
    db.commit()

    return {
        "message": f"Successfully processed '{doc_title}' into {num_chunks} vector chunks.",
        "document": {
            "id": doc_record.id,
            "title": doc_record.title,
            "filename": doc_record.filename,
            "num_chunks": num_chunks,
            "file_size": file_size,
            "category": doc_record.category
        }
    }


@app.get("/api/documents/list")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(DocumentRecord).order_by(DocumentRecord.uploaded_at.desc()).all()
    return [{
        "id": d.id,
        "title": d.title,
        "filename": d.filename,
        "file_type": d.file_type,
        "file_size": d.file_size,
        "num_chunks": d.num_chunks,
        "category": d.category,
        "uploaded_at": d.uploaded_at.strftime("%Y-%m-%d %H:%M")
    } for d in docs]


@app.post("/api/documents/search")
def search_documents(req: SearchDocumentRequest):
    results = search_knowledge_base(req.query, top_k=req.top_k)
    return {
        "query": req.query,
        "total_results": len(results),
        "results": results
    }


# -------------------------------------------------------------
# 6. USER HISTORY & SYSTEM STATS APIS
# -------------------------------------------------------------

@app.get("/api/user/history")
def get_user_history(
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    uid = current_user.id if current_user else 1
    sessions = db.query(InterviewSession).filter(InterviewSession.user_id == uid).order_by(InterviewSession.started_at.desc()).all()
    
    return [{
        "id": s.id,
        "title": s.title,
        "domain": s.domain,
        "interview_type": s.interview_type,
        "difficulty": s.difficulty,
        "score": s.score,
        "status": s.status,
        "started_at": s.started_at.strftime("%b %d, %Y %H:%M")
    } for s in sessions]


@app.get("/api/stats")
def get_system_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_interviews = db.query(InterviewSession).count()
    total_documents = db.query(DocumentRecord).count()
    total_chunks = sum([d.num_chunks for d in db.query(DocumentRecord).all()])
    
    return {
        "total_candidates": total_users,
        "total_interviews_conducted": total_interviews,
        "knowledge_documents_indexed": total_documents,
        "vector_chunks": total_chunks,
        "supported_domains": list(QUESTION_BANK.keys())
    }


# -------------------------------------------------------------
# 7. FRONTEND STATIC ASSETS MOUNTING
# -------------------------------------------------------------
FRONTEND_DIR = BASE_DIR.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")
    if (FRONTEND_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")

    @app.get("/")
    def serve_frontend_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

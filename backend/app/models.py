from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(..., min_length=6)
    role: Optional[str] = "candidate"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserProfile(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    created_at: datetime
    total_interviews: int = 0
    average_score: float = 0.0


class StartInterviewRequest(BaseModel):
    interview_type: str = Field(..., description="technical, hr, coding, sql, aiml")
    domain: str = Field(default="Python", description="Python, Java, SQL, Data Science, Machine Learning, AI, NLP, Web Development, Cloud")
    difficulty: str = Field(default="intermediate", description="beginner, intermediate, advanced")


class RequestHintRequest(BaseModel):
    session_id: int
    hint_level: int = Field(default=1, description="1, 2, or 3")


class HintResponse(BaseModel):
    session_id: int
    hint_level: int
    hint_type: str
    hint: str
    hints_remaining: int


class SubmitAnswerRequest(BaseModel):
    session_id: int
    answer: str


class TurnEvaluationResponse(BaseModel):
    session_id: int
    turn_index: int
    score_correctness: float
    score_clarity: float
    score_depth: float
    overall_turn_score: float
    feedback: str
    strengths: List[str]
    missing_concepts: List[str]
    follow_up_question: Optional[str]
    next_question: Optional[str]
    is_session_completed: bool = False


class FinalReportResponse(BaseModel):
    session_id: int
    user_email: str
    interview_type: str
    domain: str
    difficulty: str
    started_at: datetime
    completed_at: Optional[datetime]
    overall_score: float
    readiness_level: str
    grade: str
    turns_evaluated: int
    metric_averages: Dict[str, float]
    summary_feedback: str
    key_strengths: List[str]
    recommended_topics: List[str]
    history: List[Dict[str, Any]]


class ChatRequest(BaseModel):
    message: str
    mode: str = Field(default="mentor", description="mentor (Socratic guidance) or direct")
    level: str = Field(default="intermediate", description="beginner, intermediate, advanced")
    use_rag: bool = True


class ChatResponse(BaseModel):
    reply: str
    is_ambiguous: bool = False
    clarification_question: Optional[str] = None
    level: str
    mode: str
    rag_sources: List[Dict[str, Any]] = []


class SearchDocumentRequest(BaseModel):
    query: str
    top_k: int = 4


class DocumentItem(BaseModel):
    id: int
    title: str
    filename: str
    file_type: str
    file_size: int
    num_chunks: int
    uploaded_at: datetime


class CodingHintRequest(BaseModel):
    problem_id: str
    hint_level: int = 1  # 1: Concept, 2: Approach, 3: Pseudocode, 4: Solution with explanation


class CodingProblemResponse(BaseModel):
    id: str
    title: str
    difficulty: str
    category: str
    description: str
    examples: List[Dict[str, Any]]
    constraints: List[str]
    starter_code: Dict[str, str]
    test_cases: List[Dict[str, Any]]

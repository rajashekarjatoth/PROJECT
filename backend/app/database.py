import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from app.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(64), nullable=False)
    role = Column(String(50), default="candidate")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    interview_type = Column(String(50), nullable=False)  # technical, hr, coding, sql, aiml
    domain = Column(String(100), default="General")     # Python, Java, SQL, Machine Learning, etc.
    difficulty = Column(String(50), default="intermediate") # beginner, intermediate, advanced
    status = Column(String(50), default="in_progress")   # in_progress, completed
    total_turns = Column(Integer, default=0)
    score = Column(Float, default=0.0)
    summary = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")
    turns = relationship("InterviewTurn", back_populates="session", cascade="all, delete-orphan")


class InterviewTurn(Base):
    __tablename__ = "interview_turns"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    turn_index = Column(Integer, default=1)
    question = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    hints_used = Column(Integer, default=0)
    score_correctness = Column(Float, default=0.0)
    score_clarity = Column(Float, default=0.0)
    score_depth = Column(Float, default=0.0)
    overall_turn_score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)
    missing_concepts = Column(Text, nullable=True)
    follow_up_question = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("InterviewSession", back_populates="turns")


class DocumentRecord(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, default=0)
    num_chunks = Column(Integer, default=0)
    category = Column(String(100), default="Interview Prep")
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    uploader_email = Column(String(255), default="admin@cognitivebot.ai")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    mode = Column(String(50), default="mentor")  # mentor, direct, rag
    level = Column(String(50), default="intermediate")  # beginner, intermediate, advanced
    rag_sources = Column(Text, nullable=True)  # JSON formatted citations
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="chat_messages")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from core.db import Base


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


class AIChatSession(Base):
    __tablename__ = "ai_chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    messages = relationship("AIChatMessage", back_populates="session", cascade="all, delete-orphan")


class AIChatMessage(Base):
    __tablename__ = "ai_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("ai_chat_sessions.session_id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("AIChatSession", back_populates="messages")


# SmartBot Models for Job Application Analysis

class SmartBotSessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ERROR = "error"


class SmartBotMessageType(str, enum.Enum):
    BOT = "bot"
    USER = "user"
    SYSTEM = "system"
    QUESTION = "question"
    INFO = "info"
    ANSWER = "answer"
    COMPLETION = "completion"


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SmartBotSession(Base):
    """SmartBot chat session for job application analysis"""
    __tablename__ = "smartbot_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False, unique=True)
    status = Column(String(20), nullable=False, default=SmartBotSessionStatus.ACTIVE.value)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    application = relationship("JobApplication", back_populates="smartbot_session")
    messages = relationship("SmartBotMessage", back_populates="session", cascade="all, delete-orphan")
    analysis = relationship("CandidateAnalysis", back_populates="smartbot_session", uselist=False)


class SmartBotMessage(Base):
    """Messages in SmartBot conversation"""
    __tablename__ = "smartbot_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("smartbot_sessions.session_id"), nullable=False)
    message_type = Column(Enum(SmartBotMessageType, values_callable=lambda obj: [e.value for e in obj], native_enum=False), nullable=False)  # bot, user, system, question, info, answer, completion
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # Question type, analysis context, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("SmartBotSession", back_populates="messages")


class CandidateAnalysis(Base):
    """AI analysis results for candidate evaluation"""
    __tablename__ = "candidate_analyses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("smartbot_sessions.session_id"), nullable=False, unique=True)
    
    # Analysis results
    relevance_score = Column(Float, nullable=True)  # 0-100 percentage (final score)
    initial_score = Column(Float, nullable=True)  # 0-100 percentage (initial assessment)
    final_score = Column(Float, nullable=True)  # 0-100 percentage (after clarifications)
    status = Column(String(20), nullable=False, default=AnalysisStatus.PENDING.value)
    
    # Detailed analysis
    strengths = Column(JSON, nullable=True)  # List of candidate strengths
    weaknesses = Column(JSON, nullable=True)  # List of areas of concern
    missing_requirements = Column(JSON, nullable=True)  # Requirements not met
    clarifications_received = Column(JSON, nullable=True)  # Answers from candidate
    
    # Summary for employer
    summary = Column(Text, nullable=True)  # Human-readable summary
    recommendation = Column(String(50), nullable=True)  # recommend, consider, reject
    
    # Analysis metadata
    questions_asked = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    analysis_completed = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    smartbot_session = relationship("SmartBotSession", back_populates="analysis")
    categories = relationship("AnalysisCategory", back_populates="analysis", cascade="all, delete-orphan")


class AnalysisCategory(Base):
    """Categories for detailed analysis (city, experience, skills, etc.)"""
    __tablename__ = "analysis_categories"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("candidate_analyses.id"), nullable=False)
    category = Column(String(50), nullable=False)  # city, experience, skills, salary, etc.
    status = Column(String(20), nullable=False)  # match, mismatch, clarified, unknown
    details = Column(Text, nullable=True)
    score = Column(Float, nullable=True)  # Individual category score
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    analysis = relationship("CandidateAnalysis", back_populates="categories")
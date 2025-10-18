from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from models.chat import MessageRole, SmartBotMessageType, SmartBotSessionStatus, AnalysisStatus


class ChatMessageCreate(BaseModel):
    content: str


class ChatMessageResponse(BaseModel):
    id: int
    role: MessageRole
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    id: int
    session_id: str
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    message: str
    session_id: str


# SmartBot Schemas

class SmartBotMessageCreate(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None


class SmartBotMessageResponse(BaseModel):
    id: int
    message_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SmartBotSessionCreate(BaseModel):
    application_id: int


class SmartBotSessionResponse(BaseModel):
    id: int
    application_id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    messages: List[SmartBotMessageResponse] = []

    class Config:
        from_attributes = True


class AnalysisCategoryResponse(BaseModel):
    id: int
    category: str
    status: str
    details: Optional[str] = None
    score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateAnalysisResponse(BaseModel):
    id: int
    smartbot_session_id: int
    relevance_score: Optional[float] = None
    status: str
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    missing_requirements: Optional[List[str]] = None
    clarifications_received: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    recommendation: Optional[str] = None
    questions_asked: int = 0
    questions_answered: int = 0
    analysis_completed: bool = False
    created_at: datetime
    updated_at: datetime
    categories: List[AnalysisCategoryResponse] = []

    class Config:
        from_attributes = True


class SmartBotChatRequest(BaseModel):
    session_id: int
    message: str


class SmartBotChatResponse(BaseModel):
    session_id: int
    bot_message: str
    analysis_complete: bool = False
    next_question: Optional[str] = None


class SmartBotInitRequest(BaseModel):
    application_id: int


class SmartBotInitResponse(BaseModel):
    session_id: int
    initial_message: str
    questions_to_ask: List[str] = []


class EmployerAnalysisView(BaseModel):
    """Comprehensive view for employers to see candidate analysis"""
    application_id: int
    candidate_name: str
    job_title: str
    relevance_score: Optional[float] = None
    recommendation: Optional[str] = None
    summary: Optional[str] = None
    chat_completed: bool = False
    key_insights: List[str] = []
    concerns: List[str] = []
    created_at: datetime
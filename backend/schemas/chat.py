from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.chat import MessageRole


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
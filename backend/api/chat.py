from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from core.db import get_db
from core.deps import get_current_user
from models.users import User
from models.chat import AIChatSession
from schemas.chat import ChatMessageCreate, ChatResponse, ChatSessionResponse
from services.smartbot import smartbot_service
router = APIRouter(prefix='/chat', tags=['smartbot'])

@router.post('/', response_model=ChatResponse)
async def send_message(message_data: ChatMessageCreate, db: Session=Depends(get_db), current_user: Optional[User]=Depends(get_current_user)):
    user_id = current_user.id if current_user else None
    response = await smartbot_service.chat(db=db, message=message_data.message, session_id=message_data.session_id, user_id=user_id)
    return response

@router.get('/sessions/{session_id}', response_model=ChatSessionResponse)
def get_chat_session(session_id: str, db: Session=Depends(get_db), current_user: Optional[User]=Depends(get_current_user)):
    session = db.query(AIChatSession).filter(AIChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Chat session not found')
    if current_user and session.user_id and (session.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied to this chat session')
    return session

@router.get('/sessions', response_model=list[ChatSessionResponse])
def get_user_chat_sessions(current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    sessions = db.query(AIChatSession).filter(AIChatSession.user_id == current_user.id).order_by(AIChatSession.updated_at.desc()).all()
    return sessions

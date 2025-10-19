from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from core.db import get_db
from models.applications import JobApplication
from models.chat import SmartBotSession, SmartBotMessage, CandidateAnalysis, AnalysisCategory
from models.jobs import Job
from models.resumes import Resume
from models.users import User, UserType
from schemas.chat import SmartBotInitRequest, SmartBotInitResponse, SmartBotChatRequest, SmartBotChatResponse, SmartBotSessionResponse, EmployerAnalysisView
from services.application_analyzer import application_analyzer
from core.deps import get_current_active_user
import json
from fastapi import WebSocket, WebSocketDisconnect
from core.security import verify_token
from services.ws_manager import ws_manager
import asyncio
router = APIRouter(prefix='/smartbot', tags=['SmartBot'])

@router.post('/start-analysis', response_model=SmartBotInitResponse)
async def start_analysis(request: SmartBotInitRequest, db: Session=Depends(get_db), current_user: User=Depends(get_current_active_user)):
    application = db.query(JobApplication).filter(JobApplication.id == request.application_id, JobApplication.user_id == current_user.id).first()
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Application not found')
    existing_session = db.query(SmartBotSession).filter(SmartBotSession.application_id == application.id).first()
    if existing_session:
        messages = db.query(SmartBotMessage).filter(SmartBotMessage.session_id == existing_session.session_id).order_by(SmartBotMessage.created_at).all()
        return SmartBotInitResponse(session_id=existing_session.session_id, status=existing_session.status, initial_message=messages[0].content if messages else 'Добро пожаловать в SmartBot!', is_completed=existing_session.status == 'completed')
    try:
        session = await application_analyzer.start_analysis_session(db, application)
        initial_message = db.query(SmartBotMessage).filter(SmartBotMessage.session_id == session.session_id).order_by(SmartBotMessage.created_at).first()
        return SmartBotInitResponse(session_id=session.session_id, status=session.status, initial_message=initial_message.content if initial_message else 'Добро пожаловать в SmartBot!', is_completed=session.status == 'completed')
    except Exception as e:
        import traceback
        print(f'ERROR in start_analysis: {str(e)}')
        print(f'ERROR traceback: {traceback.format_exc()}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Failed to start analysis: {str(e)}')

@router.post('/chat', response_model=SmartBotChatResponse)
async def chat_with_smartbot(request: SmartBotChatRequest, db: Session=Depends(get_db), current_user: User=Depends(get_current_active_user)):
    session = db.query(SmartBotSession).filter(SmartBotSession.session_id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Session not found')
    application = db.query(JobApplication).filter(JobApplication.id == session.application_id, JobApplication.user_id == current_user.id).first()
    if not application:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied')
    try:
        result = await application_analyzer.process_candidate_response(db, request.session_id, request.message)
        return SmartBotChatResponse(message=result['message'], session_status=result['session_status'], is_completed=result['is_completed'])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Failed to process message: {str(e)}')

@router.get('/session/{session_id}', response_model=SmartBotSessionResponse)
async def get_session(session_id: str, db: Session=Depends(get_db), current_user: User=Depends(get_current_active_user)):
    session = db.query(SmartBotSession).filter(SmartBotSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Session not found')
    application = db.query(JobApplication).filter(JobApplication.id == session.application_id, JobApplication.user_id == current_user.id).first()
    if not application:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied')
    messages = db.query(SmartBotMessage).filter(SmartBotMessage.session_id == session_id).order_by(SmartBotMessage.created_at).all()
    analysis = db.query(CandidateAnalysis).filter(CandidateAnalysis.session_id == session_id).first()
    return SmartBotSessionResponse(id=session.id, application_id=session.application_id, status=session.status, started_at=session.started_at, completed_at=session.completed_at, messages=[{'id': msg.id, 'message_type': msg.message_type.value if hasattr(msg.message_type, 'value') else msg.message_type, 'content': msg.content, 'metadata': msg.message_metadata, 'created_at': msg.created_at} for msg in messages])

@router.post('/employer/start-analysis', response_model=SmartBotInitResponse)
async def start_employer_analysis(request: SmartBotInitRequest, db: Session=Depends(get_db), current_user: User=Depends(get_current_active_user)):
    if current_user.user_type != 'employer':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only employers can access this endpoint')
    application = db.query(JobApplication).filter(JobApplication.id == request.application_id).first()
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Application not found')
    job = db.query(Job).filter(Job.id == application.job_id, Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied - you don't own this job")
    existing_session = db.query(SmartBotSession).filter(SmartBotSession.application_id == application.id).first()
    if existing_session:
        messages = db.query(SmartBotMessage).filter(SmartBotMessage.session_id == existing_session.session_id).order_by(SmartBotMessage.created_at).all()
        return SmartBotInitResponse(session_id=existing_session.session_id, status=existing_session.status, initial_message=messages[0].content if messages else 'Добро пожаловать в SmartBot!', is_completed=existing_session.status == 'completed')
    try:
        session = await application_analyzer.start_analysis_session(db, application)
        initial_message = db.query(SmartBotMessage).filter(SmartBotMessage.session_id == session.session_id).order_by(SmartBotMessage.created_at).first()
        return SmartBotInitResponse(session_id=session.session_id, status=session.status, initial_message=initial_message.content if initial_message else 'Добро пожаловать в SmartBot!', is_completed=session.status == 'completed')
    except Exception as e:
        import traceback
        print(f'ERROR in start_employer_analysis: {str(e)}')
        print(f'ERROR traceback: {traceback.format_exc()}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Failed to start analysis: {str(e)}')

@router.get('/employer/applications/{job_id}', response_model=List[EmployerAnalysisView])
async def get_employer_analysis(job_id: int, db: Session=Depends(get_db), current_user: User=Depends(get_current_active_user)):
    job = db.query(Job).filter(Job.id == job_id, Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found or access denied')
    applications = db.query(JobApplication).filter(JobApplication.job_id == job_id).all()
    results = []
    for application in applications:
        user = db.query(User).filter(User.id == application.user_id).first()
        session = db.query(SmartBotSession).filter(SmartBotSession.application_id == application.id).first()
        if not session:
            continue
        analysis = db.query(CandidateAnalysis).filter(CandidateAnalysis.session_id == session.session_id).first()
        messages = db.query(SmartBotMessage).filter(SmartBotMessage.session_id == session.session_id).order_by(SmartBotMessage.created_at).all()
        categories = db.query(AnalysisCategory).filter(AnalysisCategory.analysis_id == analysis.id).all() if analysis else []
        results.append(EmployerAnalysisView(application_id=application.id, candidate_name=f'{user.first_name} {user.last_name}' if user else 'Unknown', candidate_email=user.email if user else '', session_id=session.session_id, session_status=session.status, relevance_score=analysis.final_score or analysis.initial_score if analysis else 0, recommendation=_get_recommendation_from_score(analysis.final_score or analysis.initial_score if analysis else 0), summary=analysis.summary if analysis else 'Анализ не завершен', strengths=json.loads(analysis.strengths) if analysis and analysis.strengths else [], concerns=json.loads(analysis.weaknesses) if analysis and analysis.weaknesses else [], chat_messages=[{'type': msg.message_type.value if hasattr(msg.message_type, 'value') else msg.message_type, 'content': msg.content, 'created_at': msg.created_at} for msg in messages], categories=[{'name': cat.category, 'status': cat.status, 'score': cat.score, 'details': cat.details} for cat in categories], applied_at=application.created_at, analyzed_at=session.updated_at))
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    return results

@router.get('/employer/analysis/{session_id}', response_model=EmployerAnalysisView)
async def get_single_analysis(session_id: str, db: Session=Depends(get_db), current_user: User=Depends(get_current_active_user)):
    session = db.query(SmartBotSession).filter(SmartBotSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Session not found')
    application = db.query(JobApplication).filter(JobApplication.id == session.application_id).first()
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Application not found')
    job = db.query(Job).filter(Job.id == application.job_id, Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied')
    user = db.query(User).filter(User.id == application.user_id).first()
    analysis = db.query(CandidateAnalysis).filter(CandidateAnalysis.session_id == session_id).first()
    messages = db.query(SmartBotMessage).filter(SmartBotMessage.session_id == session_id).order_by(SmartBotMessage.created_at).all()
    categories = db.query(AnalysisCategory).filter(AnalysisCategory.analysis_id == analysis.id).all() if analysis else []
    return EmployerAnalysisView(application_id=application.id, candidate_name=f'{user.first_name} {user.last_name}' if user else 'Unknown', candidate_email=user.email if user else '', session_id=session.session_id, session_status=session.status, relevance_score=analysis.final_score or analysis.initial_score if analysis else 0, recommendation=_get_recommendation_from_score(analysis.final_score or analysis.initial_score if analysis else 0), summary=analysis.summary if analysis else 'Анализ не завершен', strengths=json.loads(analysis.strengths) if analysis and analysis.strengths else [], concerns=json.loads(analysis.weaknesses) if analysis and analysis.weaknesses else [], chat_messages=[{'type': msg.message_type.value if hasattr(msg.message_type, 'value') else msg.message_type, 'content': msg.content, 'created_at': msg.created_at} for msg in messages], categories=[{'name': cat.category, 'status': cat.status, 'score': cat.score, 'details': cat.details} for cat in categories], applied_at=application.created_at, analyzed_at=session.completed_at or session.started_at)

@router.get('/employer/application-analysis/{application_id}', response_model=EmployerAnalysisView)
async def get_application_analysis(application_id: int, db: Session=Depends(get_db), current_user: User=Depends(get_current_active_user)):
    application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Application not found')
    job = db.query(Job).filter(Job.id == application.job_id, Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied')
    session = db.query(SmartBotSession).filter(SmartBotSession.application_id == application_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Analysis not found for this application')
    user = db.query(User).filter(User.id == application.user_id).first()
    analysis = db.query(CandidateAnalysis).filter(CandidateAnalysis.session_id == session.session_id).first()
    messages = db.query(SmartBotMessage).filter(SmartBotMessage.session_id == session.session_id).order_by(SmartBotMessage.created_at).all()
    categories = db.query(AnalysisCategory).filter(AnalysisCategory.analysis_id == analysis.id).all() if analysis else []
    return EmployerAnalysisView(application_id=application.id, candidate_name=user.full_name if user else 'Unknown', candidate_email=user.email if user else None, session_id=session.session_id, session_status=session.status, relevance_score=analysis.final_score if analysis else None, recommendation=_get_recommendation_from_score(analysis.final_score) if analysis and analysis.final_score else None, summary=analysis.summary if analysis else None, strengths=json.loads(analysis.strengths) if analysis and analysis.strengths else [], concerns=json.loads(analysis.weaknesses) if analysis and analysis.weaknesses else [], chat_messages=[{'id': msg.id, 'role': msg.message_type, 'content': msg.content, 'created_at': msg.created_at.isoformat()} for msg in messages], categories=[{'name': cat.category, 'score': cat.score, 'details': cat.details} for cat in categories], applied_at=application.created_at, analyzed_at=session.completed_at or session.started_at)

def _get_recommendation_from_score(score: int) -> str:
    if score >= 80:
        return 'recommend'
    elif score >= 60:
        return 'consider'
    else:
        return 'reject'

@router.websocket('/employer/ws/jobs/{job_id}')
async def employer_jobs_ws(websocket: WebSocket, job_id: int, db: Session=Depends(get_db)):
    await websocket.accept()
    auth_header = websocket.headers.get('authorization')
    token = None
    if auth_header and auth_header.lower().startswith('bearer '):
        token = auth_header.split(' ', 1)[1].strip()
    if not token:
        token = websocket.query_params.get('token')
    payload = verify_token(token) if token else None
    if not payload:
        await websocket.send_json({'event': 'error', 'message': 'Unauthorized'})
        await websocket.close(code=1008)
        return
    email = payload.get('sub')
    user = db.query(User).filter(User.email == email).first()
    if not user or user.user_type != UserType.EMPLOYER:
        await websocket.send_json({'event': 'error', 'message': 'Forbidden'})
        await websocket.close(code=1008)
        return
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or job.employer_id != user.id:
        await websocket.send_json({'event': 'error', 'message': 'Job not found or not owned'})
        await websocket.close(code=1008)
        return
    await ws_manager.connect_job(job_id, websocket)
    await websocket.send_json({'event': 'subscribed', 'job_id': job_id})
    try:
        while True:
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        await ws_manager.disconnect_job(job_id, websocket)

@router.websocket('/employer/ws/sessions/{session_id}')
async def employer_session_ws(websocket: WebSocket, session_id: str, db: Session=Depends(get_db)):
    await websocket.accept()
    auth_header = websocket.headers.get('authorization')
    token = None
    if auth_header and auth_header.lower().startswith('bearer '):
        token = auth_header.split(' ', 1)[1].strip()
    if not token:
        token = websocket.query_params.get('token')
    payload = verify_token(token) if token else None
    if not payload:
        await websocket.send_json({'event': 'error', 'message': 'Unauthorized'})
        await websocket.close(code=1008)
        return
    email = payload.get('sub')
    user = db.query(User).filter(User.email == email).first()
    if not user or user.user_type != UserType.EMPLOYER:
        await websocket.send_json({'event': 'error', 'message': 'Forbidden'})
        await websocket.close(code=1008)
        return
    session = db.query(SmartBotSession).filter(SmartBotSession.session_id == session_id).first()
    if not session:
        await websocket.send_json({'event': 'error', 'message': 'Session not found'})
        await websocket.close(code=1008)
        return
    application = db.query(JobApplication).filter(JobApplication.id == session.application_id).first()
    if not application:
        await websocket.send_json({'event': 'error', 'message': 'Application not found'})
        await websocket.close(code=1008)
        return
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job or job.employer_id != user.id:
        await websocket.send_json({'event': 'error', 'message': 'Forbidden'})
        await websocket.close(code=1008)
        return
    await ws_manager.connect_session(session_id, websocket)
    await websocket.send_json({'event': 'subscribed', 'session_id': session_id})
    try:
        while True:
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        await ws_manager.disconnect_session(session_id, websocket)

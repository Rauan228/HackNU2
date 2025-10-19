from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from core.db import get_db
from models.applications import JobApplication
from models.chat import SmartBotSession, SmartBotMessage, CandidateAnalysis, AnalysisCategory
from models.jobs import Job
from models.resumes import Resume
from models.users import User
from schemas.chat import (
    SmartBotInitRequest, SmartBotInitResponse, SmartBotChatRequest, 
    SmartBotChatResponse, SmartBotSessionResponse, EmployerAnalysisView
)
from services.application_analyzer import application_analyzer
from core.deps import get_current_active_user
import json

router = APIRouter(prefix="/smartbot", tags=["SmartBot"])


@router.post("/start-analysis", response_model=SmartBotInitResponse)
async def start_analysis(
    request: SmartBotInitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Start SmartBot analysis session for a job application
    """
    # Get the application
    application = db.query(JobApplication).filter(
        JobApplication.id == request.application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if analysis session already exists
    existing_session = db.query(SmartBotSession).filter(
        SmartBotSession.application_id == application.id
    ).first()
    
    if existing_session:
        # Return existing session
        messages = db.query(SmartBotMessage).filter(
            SmartBotMessage.session_id == existing_session.session_id
        ).order_by(SmartBotMessage.created_at).all()
        
        return SmartBotInitResponse(
            session_id=existing_session.session_id,
            status=existing_session.status,
            initial_message=messages[0].content if messages else "Добро пожаловать в SmartBot!",
            is_completed=existing_session.status == "completed"
        )
    
    try:
        # Start new analysis session
        session = await application_analyzer.start_analysis_session(db, application)
        
        # Get the initial message
        initial_message = db.query(SmartBotMessage).filter(
            SmartBotMessage.session_id == session.session_id
        ).order_by(SmartBotMessage.created_at).first()
        
        return SmartBotInitResponse(
        session_id=session.session_id,
        status=session.status,
        initial_message=initial_message.content if initial_message else "Добро пожаловать в SmartBot!",
        is_completed=session.status == "completed"
    )
        
    except Exception as e:
        import traceback
        print(f"ERROR in start_analysis: {str(e)}")
        print(f"ERROR traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start analysis: {str(e)}"
        )


@router.post("/chat", response_model=SmartBotChatResponse)
async def chat_with_smartbot(
    request: SmartBotChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Send message to SmartBot and get response
    """
    # Verify session belongs to current user
    session = db.query(SmartBotSession).filter(
        SmartBotSession.session_id == request.session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Verify user owns the application
    application = db.query(JobApplication).filter(
        JobApplication.id == session.application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Process the message
        result = await application_analyzer.process_candidate_response(
            db, request.session_id, request.message
        )
        
        return SmartBotChatResponse(
            message=result["message"],
            session_status=result["session_status"],
            is_completed=result["is_completed"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=SmartBotSessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get SmartBot session details and message history
    """
    # Get session
    session = db.query(SmartBotSession).filter(
        SmartBotSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Verify user owns the application
    application = db.query(JobApplication).filter(
        JobApplication.id == session.application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get messages
    messages = db.query(SmartBotMessage).filter(
        SmartBotMessage.session_id == session_id
    ).order_by(SmartBotMessage.created_at).all()
    
    # Get analysis
    analysis = db.query(CandidateAnalysis).filter(
        CandidateAnalysis.session_id == session_id
    ).first()
    
    return SmartBotSessionResponse(
        session_id=session.session_id,
        application_id=session.application_id,
        status=session.status,
        messages=[
            {
                "id": msg.id,
                "type": msg.message_type.value if hasattr(msg.message_type, 'value') else msg.message_type,
                "content": msg.content,
                "created_at": msg.created_at
            }
            for msg in messages
        ],
        analysis={
            "initial_score": analysis.initial_score if analysis else None,
            "final_score": analysis.final_score if analysis else None,
            "summary": analysis.summary if analysis else None,
            "status": analysis.status if analysis else None
        } if analysis else None,
        created_at=session.created_at,
        updated_at=session.updated_at
    )


@router.post("/employer/start-analysis", response_model=SmartBotInitResponse)
async def start_employer_analysis(
    request: SmartBotInitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Start SmartBot analysis session for a job application (for employers)
    """
    # Verify user is an employer
    if current_user.user_type != 'employer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can access this endpoint"
        )
    
    # Get the application
    application = db.query(JobApplication).filter(
        JobApplication.id == request.application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Verify employer owns the job
    job = db.query(Job).filter(
        Job.id == application.job_id,
        Job.employer_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - you don't own this job"
        )
    
    # Check if analysis session already exists
    existing_session = db.query(SmartBotSession).filter(
        SmartBotSession.application_id == application.id
    ).first()
    
    if existing_session:
        # Return existing session
        messages = db.query(SmartBotMessage).filter(
            SmartBotMessage.session_id == existing_session.session_id
        ).order_by(SmartBotMessage.created_at).all()
        
        return SmartBotInitResponse(
            session_id=existing_session.session_id,
            status=existing_session.status,
            initial_message=messages[0].content if messages else "Добро пожаловать в SmartBot!",
            is_completed=existing_session.status == "completed"
        )
    
    try:
        # Start new analysis session
        session = await application_analyzer.start_analysis_session(db, application)
        
        # Get the initial message
        initial_message = db.query(SmartBotMessage).filter(
            SmartBotMessage.session_id == session.session_id
        ).order_by(SmartBotMessage.created_at).first()
        
        return SmartBotInitResponse(
            session_id=session.session_id,
            status=session.status,
            initial_message=initial_message.content if initial_message else "Добро пожаловать в SmartBot!",
            is_completed=session.status == "completed"
        )
        
    except Exception as e:
        import traceback
        print(f"ERROR in start_employer_analysis: {str(e)}")
        print(f"ERROR traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start analysis: {str(e)}"
        )


@router.get("/employer/applications/{job_id}", response_model=List[EmployerAnalysisView])
async def get_employer_analysis(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get analysis results for all applications to a job (for employers)
    """
    # Verify user owns the job
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.employer_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or access denied"
        )
    
    # Get all applications with SmartBot sessions
    applications = db.query(JobApplication).filter(
        JobApplication.job_id == job_id
    ).all()
    
    results = []
    
    for application in applications:
        # Get user info
        user = db.query(User).filter(User.id == application.user_id).first()
        
        # Get SmartBot session
        session = db.query(SmartBotSession).filter(
            SmartBotSession.application_id == application.id
        ).first()
        
        if not session:
            continue
        
        # Get analysis
        analysis = db.query(CandidateAnalysis).filter(
            CandidateAnalysis.session_id == session.session_id
        ).first()
        
        # Get messages
        messages = db.query(SmartBotMessage).filter(
            SmartBotMessage.session_id == session.session_id
        ).order_by(SmartBotMessage.created_at).all()
        
        # Get categories
        categories = db.query(AnalysisCategory).filter(
            AnalysisCategory.analysis_id == analysis.id
        ).all() if analysis else []
        
        results.append(EmployerAnalysisView(
            application_id=application.id,
            candidate_name=f"{user.first_name} {user.last_name}" if user else "Unknown",
            candidate_email=user.email if user else "",
            session_id=session.session_id,
            session_status=session.status,
            relevance_score=analysis.final_score or analysis.initial_score if analysis else 0,
            recommendation=_get_recommendation_from_score(
                analysis.final_score or analysis.initial_score if analysis else 0
            ),
            summary=analysis.summary if analysis else "Анализ не завершен",
            strengths=json.loads(analysis.strengths) if analysis and analysis.strengths else [],
            concerns=json.loads(analysis.weaknesses) if analysis and analysis.weaknesses else [],
            chat_messages=[
                {
                    "type": msg.message_type.value if hasattr(msg.message_type, 'value') else msg.message_type,
                    "content": msg.content,
                    "created_at": msg.created_at
                }
                for msg in messages
            ],
            categories=[
                {
                    "name": cat.category,
                    "status": cat.status,
                    "score": cat.score,
                    "details": cat.details
                }
                for cat in categories
            ],
            applied_at=application.created_at,
            analyzed_at=session.updated_at
        ))
    
    # Sort by relevance score (highest first)
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    
    return results


@router.get("/employer/analysis/{session_id}", response_model=EmployerAnalysisView)
async def get_single_analysis(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed analysis for a specific candidate (for employers)
    """
    # Get session
    session = db.query(SmartBotSession).filter(
        SmartBotSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get application and verify job ownership
    application = db.query(JobApplication).filter(
        JobApplication.id == session.application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    job = db.query(Job).filter(
        Job.id == application.job_id,
        Job.employer_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get user info
    user = db.query(User).filter(User.id == application.user_id).first()
    
    # Get analysis
    analysis = db.query(CandidateAnalysis).filter(
        CandidateAnalysis.session_id == session_id
    ).first()
    
    # Get messages
    messages = db.query(SmartBotMessage).filter(
        SmartBotMessage.session_id == session_id
    ).order_by(SmartBotMessage.created_at).all()
    
    # Get categories
    categories = db.query(AnalysisCategory).filter(
        AnalysisCategory.analysis_id == analysis.id
    ).all() if analysis else []
    
    return EmployerAnalysisView(
        application_id=application.id,
        candidate_name=f"{user.first_name} {user.last_name}" if user else "Unknown",
        candidate_email=user.email if user else "",
        session_id=session.session_id,
        session_status=session.status,
        relevance_score=analysis.final_score or analysis.initial_score if analysis else 0,
        recommendation=_get_recommendation_from_score(
            analysis.final_score or analysis.initial_score if analysis else 0
        ),
        summary=analysis.summary if analysis else "Анализ не завершен",
        strengths=json.loads(analysis.strengths) if analysis and analysis.strengths else [],
        concerns=json.loads(analysis.weaknesses) if analysis and analysis.weaknesses else [],
        chat_messages=[
            {
                "type": msg.message_type.value if hasattr(msg.message_type, 'value') else msg.message_type,
                "content": msg.content,
                "created_at": msg.created_at
            }
            for msg in messages
        ],
        categories=[
            {
                "name": cat.category,
                "status": cat.status,
                "score": cat.score,
                "details": cat.details
            }
            for cat in categories
        ],
        applied_at=application.created_at,
        analyzed_at=session.updated_at
    )


def _get_recommendation_from_score(score: int) -> str:
    """Convert numeric score to recommendation"""
    if score >= 80:
        return "recommend"
    elif score >= 60:
        return "consider"
    else:
        return "reject"
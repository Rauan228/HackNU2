from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from core.db import get_db
from core.deps import get_current_active_user
from models.users import User, UserType
from models.jobs import Job
from models.resumes import Resume
from models.applications import JobApplication
from schemas.applications import ApplicationCreate, ApplicationUpdate, ApplicationResponse, ApplicationWithDetailsResponse
from services.application_analyzer import application_analyzer
from services.ws_manager import ws_manager

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/", response_model=list[ApplicationWithDetailsResponse])
def get_applications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type == UserType.JOB_SEEKER:
        # Job seekers see their own applications
        applications = (
            db.query(JobApplication)
            .options(
                joinedload(JobApplication.job),
                joinedload(JobApplication.resume),
                joinedload(JobApplication.user)
            )
            .filter(JobApplication.user_id == current_user.id)
            .order_by(desc(JobApplication.created_at))
            .all()
        )
    else:
        # Employers see applications for their jobs
        applications = (
            db.query(JobApplication)
            .options(
                joinedload(JobApplication.job),
                joinedload(JobApplication.resume),
                joinedload(JobApplication.user)
            )
            .join(Job)
            .filter(Job.employer_id == current_user.id)
            .order_by(desc(JobApplication.created_at))
            .all()
        )
    
    # Convert to response format with details
    result = []
    for app in applications:
        result.append(ApplicationWithDetailsResponse(
            id=app.id,
            cover_letter=app.cover_letter,
            status=app.status,
            user_id=app.user_id,
            job_id=app.job_id,
            resume_id=app.resume_id,
            created_at=app.created_at,
            updated_at=app.updated_at,
            job_title=app.job.title,
            company_name=app.job.company_name,
            resume_title=app.resume.title,
            user_name=app.user.full_name
        ))
    
    return result


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check permissions
    if current_user.user_type == UserType.JOB_SEEKER:
        if application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own applications"
            )
    else:  # Employer
        job = db.query(Job).filter(Job.id == application.job_id).first()
        if job.employer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view applications for your jobs"
            )
    
    return application


@router.post("/", response_model=ApplicationResponse)
async def create_application(
    application_data: ApplicationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != UserType.JOB_SEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can create applications"
        )
    
    # Check if job exists and is active
    job = db.query(Job).filter(Job.id == application_data.job_id, Job.is_active == True).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or inactive"
        )
    
    # Check if resume exists and belongs to user
    resume = db.query(Resume).filter(
        Resume.id == application_data.resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Check if user already applied for this job
    existing_application = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.job_id == application_data.job_id
    ).first()
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job"
        )
    
    db_application = JobApplication(
        **application_data.dict(),
        user_id=current_user.id
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    # Broadcast job-level event: new application
    try:
        await ws_manager.broadcast_job(db_application.job_id, {
            "event": "application_created",
            "application_id": db_application.id,
            "job_id": db_application.job_id,
            "user_id": db_application.user_id,
            "created_at": db_application.created_at.isoformat() if hasattr(db_application, 'created_at') and db_application.created_at else None
        })
    except Exception as e:
        print(f"WS broadcast failed (application_created): {e}")
    
    # Start SmartBot analysis session automatically after application creation
    try:
        await application_analyzer.start_analysis_session(db, db_application)
    except Exception as e:
        # Log error but don't fail the application creation
        print(f"Failed to start SmartBot analysis: {e}")
    
    return db_application


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    application_data: ApplicationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check permissions
    if current_user.user_type == UserType.JOB_SEEKER:
        if application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own applications"
            )
        # Job seekers can only update cover letter
        if application_data.status is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot update application status"
            )
    else:  # Employer
        job = db.query(Job).filter(Job.id == application.job_id).first()
        if job.employer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update applications for your jobs"
            )
        # Employers can only update status
        if application_data.cover_letter is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot update cover letter"
            )
    
    update_data = application_data.dict(exclude_unset=True)
    # Ensure status is stored as lowercase string
    if 'status' in update_data and update_data['status'] is not None:
        # Pydantic provides ApplicationStatus enum; convert to its value
        update_data['status'] = update_data['status'].value if hasattr(update_data['status'], 'value') else str(update_data['status']).lower()

    for field, value in update_data.items():
        setattr(application, field, value)
    
    db.commit()
    db.refresh(application)
    
    return application


@router.get("/{application_id}/resume")
def get_application_resume(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get resume for a specific application (for employers to view candidate resumes)"""
    application = (
        db.query(JobApplication)
        .options(
            joinedload(JobApplication.resume),
            joinedload(JobApplication.job),
            joinedload(JobApplication.user)
        )
        .filter(JobApplication.id == application_id)
        .first()
    )
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Only employers can view resumes for applications to their jobs
    if current_user.user_type != UserType.EMPLOYER or application.job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view resumes for applications to your jobs"
        )
    
    if not application.resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found for this application"
        )
    
    return application.resume


@router.delete("/{application_id}")
def delete_application(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own applications"
        )
    
    db.delete(application)
    db.commit()
    
    return {"message": "Application deleted successfully"}
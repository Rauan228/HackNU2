from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from core.db import get_db
from core.deps import get_current_active_user
from models.users import User, UserType
from models.resumes import Resume
from schemas.resumes import ResumeCreate, ResumeUpdate, ResumeResponse

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.get("/", response_model=list[ResumeResponse])
def get_my_resumes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != UserType.JOB_SEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can view resumes"
        )
    
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(desc(Resume.created_at)).all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Job seekers can only view their own resumes, employers can view any resume
    if current_user.user_type == UserType.JOB_SEEKER and resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own resumes"
        )
    
    return resume


@router.post("/", response_model=ResumeResponse)
def create_resume(
    resume_data: ResumeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != UserType.JOB_SEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can create resumes"
        )
    
    db_resume = Resume(**resume_data.dict(), user_id=current_user.id)
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    
    return db_resume


@router.put("/{resume_id}", response_model=ResumeResponse)
def update_resume(
    resume_id: int,
    resume_data: ResumeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own resumes"
        )
    
    update_data = resume_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resume, field, value)
    
    db.commit()
    db.refresh(resume)
    
    return resume


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own resumes"
        )
    
    db.delete(resume)
    db.commit()
    
    return {"message": "Resume deleted successfully"}
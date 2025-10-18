from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from core.db import get_db
from core.deps import get_current_active_user
from models.users import User, UserType
from models.jobs import Job
from schemas.jobs import JobCreate, JobUpdate, JobResponse, JobListResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=JobListResponse)
def get_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Job).filter(Job.is_active == True)
    
    if search:
        query = query.filter(
            Job.title.ilike(f"%{search}%") | 
            Job.description.ilike(f"%{search}%") |
            Job.company_name.ilike(f"%{search}%")
        )
    
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    total = query.count()
    jobs = query.order_by(desc(Job.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    return JobListResponse(
        jobs=jobs,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return job


@router.post("/", response_model=JobResponse)
def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != UserType.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can create jobs"
        )
    
    db_job = Job(**job_data.dict(), employer_id=current_user.id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return db_job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own jobs"
        )
    
    update_data = job_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    
    return job


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own jobs"
        )
    
    job.is_active = False
    db.commit()
    
    return {"message": "Job deleted successfully"}


@router.get("/my/jobs", response_model=list[JobResponse])
def get_my_jobs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != UserType.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can view their jobs"
        )
    
    jobs = db.query(Job).filter(Job.employer_id == current_user.id).order_by(desc(Job.created_at)).all()
    return jobs
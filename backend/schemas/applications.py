from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.applications import ApplicationStatus

class ApplicationBase(BaseModel):
    cover_letter: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    job_id: int
    resume_id: int

class ApplicationUpdate(BaseModel):
    cover_letter: Optional[str] = None
    status: Optional[ApplicationStatus] = None

class ApplicationResponse(ApplicationBase):
    id: int
    status: ApplicationStatus
    user_id: int
    job_id: int
    resume_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ApplicationWithDetailsResponse(ApplicationResponse):
    job_title: str
    company_name: str
    resume_title: str
    user_name: str

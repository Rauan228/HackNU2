from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobBase(BaseModel):
    title: str
    description: str
    requirements: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = "KZT"
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    company_name: str


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    company_name: Optional[str] = None
    is_active: Optional[bool] = None


class JobResponse(JobBase):
    id: int
    is_active: bool
    employer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    per_page: int
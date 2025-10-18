from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ResumeBase(BaseModel):
    title: str
    summary: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None


class ResumeResponse(ResumeBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
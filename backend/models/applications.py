from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from core.db import Base


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    cover_letter = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default=ApplicationStatus.PENDING.value)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
    smartbot_session = relationship("SmartBotSession", back_populates="application", uselist=False)
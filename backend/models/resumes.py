from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.db import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)
    languages = Column(Text, nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    desired_position = Column(String(255), nullable=True)
    desired_salary = Column(Numeric(15,2), nullable=True)
    location = Column(String(255), nullable=True)
    is_public = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="resumes")
    applications = relationship("JobApplication", back_populates="resume")
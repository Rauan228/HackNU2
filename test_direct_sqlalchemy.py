import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.chat import SmartBotMessage, SmartBotMessageType, SmartBotSession
from models.applications import JobApplication
import uuid

# Create engine and session
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Create a test job application
    job_app = JobApplication(
        cover_letter="Test cover letter",
        user_id=1,  # Assuming user with ID 1 exists
        job_id=1,   # Assuming job with ID 1 exists
        resume_id=1 # Assuming resume with ID 1 exists
    )
    db.add(job_app)
    db.flush()  # Get the ID
    
    # Create a test session
    session_id = str(uuid.uuid4())
    session = SmartBotSession(
        session_id=session_id,
        application_id=job_app.id,
        status="active"
    )
    db.add(session)
    db.flush()
    
    # Test direct message creation with enum value
    print(f"Creating message with SmartBotMessageType.ANSWER.value = {SmartBotMessageType.ANSWER.value}")
    
    message = SmartBotMessage(
        session_id=session_id,
        message_type=SmartBotMessageType.ANSWER.value,
        content="Test message",
        message_metadata=None
    )
    
    db.add(message)
    db.commit()
    
    print("Message created successfully!")
    
    # Clean up
    db.delete(message)
    db.delete(session)
    db.delete(job_app)
    db.commit()
    
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
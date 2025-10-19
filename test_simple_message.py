import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.chat import SmartBotMessage, SmartBotMessageType
import uuid

# Create engine and session
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # First, create a minimal test session directly in the database
    session_id = str(uuid.uuid4())
    
    # Insert test session directly
    db.execute(text("""
        INSERT INTO smartbot_sessions (session_id, application_id, status)
        VALUES (:session_id, 1, 'active')
    """), {"session_id": session_id})
    
    # Test direct message creation with enum value
    print(f"Creating message with SmartBotMessageType.ANSWER.value = '{SmartBotMessageType.ANSWER.value}'")
    
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
    db.execute(text("DELETE FROM smartbot_messages WHERE session_id = :session_id"), {"session_id": session_id})
    db.execute(text("DELETE FROM smartbot_sessions WHERE session_id = :session_id"), {"session_id": session_id})
    db.commit()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
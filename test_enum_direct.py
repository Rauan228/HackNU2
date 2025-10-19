import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings
from backend.models.chat import SmartBotMessage, SmartBotMessageType, SmartBotSession, SmartBotSessionStatus
import uuid

# Create database connection
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

print("Testing SmartBotMessage creation with SQLAlchemy ORM...")

try:
    db = SessionLocal()
    
    # First create a session
    session_id = str(uuid.uuid4())
    session = SmartBotSession(
        session_id=session_id,
        application_id=93,  # Using our test application
        status=SmartBotSessionStatus.ACTIVE.value
    )
    db.add(session)
    db.flush()  # Flush to get the session created
    
    print(f"Created session: {session_id}")
    
    # Now create a message
    message = SmartBotMessage(
        session_id=session_id,
        message_type=SmartBotMessageType.QUESTION.value,
        content="Test message with enum value"
    )
    
    print(f"Creating message with message_type: {message.message_type!r}")
    print(f"Type of message_type: {type(message.message_type)}")
    
    db.add(message)
    db.commit()
    
    print("✓ Message created successfully!")
    
    # Clean up
    db.delete(message)
    db.delete(session)
    db.commit()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("Test complete.")
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.chat import SmartBotMessageType
import uuid

# Create engine and session
engine = create_engine(settings.database_url)

print("Testing SQLAlchemy enum handling...")

# Test direct SQL with enum value
with engine.connect() as conn:
    trans = conn.begin()
    try:
        # Test what happens when we pass the enum value directly
        enum_value = SmartBotMessageType.ANSWER.value
        print(f"Enum value: {enum_value} (type: {type(enum_value)})")
        
        # Try inserting with the enum value
        result = conn.execute(
            text("INSERT INTO smartbot_messages (session_id, message_type, content) VALUES (:session_id, :message_type, :content)"),
            {
                "session_id": str(uuid.uuid4()),
                "message_type": enum_value,
                "content": "Test message"
            }
        )
        
        trans.commit()
        print("✓ Direct enum value insertion successful")
        
    except Exception as e:
        trans.rollback()
        print(f"✗ Direct enum value insertion failed: {e}")

print("SQLAlchemy enum test complete.")
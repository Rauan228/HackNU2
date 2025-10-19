import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from backend.core.config import settings
from backend.models.chat import SmartBotMessageType

# Create database connection
engine = create_engine(settings.database_url)

print("Testing enum insertion with SQLAlchemy...")

try:
    with engine.connect() as conn:
        # First, create a test session directly
        session_id = 'test-enum-session-123'
        
        # Check if session already exists and delete it with cascade
        conn.execute(text("DELETE FROM candidate_analyses WHERE session_id IN (SELECT session_id FROM smartbot_sessions WHERE application_id = 93)"))
        conn.execute(text("DELETE FROM smartbot_messages WHERE session_id IN (SELECT session_id FROM smartbot_sessions WHERE application_id = 93)"))
        conn.execute(text("DELETE FROM smartbot_sessions WHERE application_id = 93"))
        conn.commit()
        
        # Insert session first
        conn.execute(text("""
            INSERT INTO smartbot_sessions (session_id, application_id, status)
            VALUES (:session_id, 93, 'active')
        """), {"session_id": session_id})
        
        print(f"Created test session: {session_id}")
        
        # Now test enum insertion
        enum_value = SmartBotMessageType.QUESTION.value
        print(f"Inserting with enum value: {enum_value!r} (type: {type(enum_value)})")
        
        # Test 1: Direct string insertion
        conn.execute(text("""
            INSERT INTO smartbot_messages (session_id, message_type, content)
            VALUES (:session_id, :message_type, 'Test message 1')
        """), {"session_id": session_id, "message_type": enum_value})
        
        print("✓ Test 1: Direct string insertion successful")
        
        # Test 2: With explicit casting (fix syntax)
        conn.execute(text("""
            INSERT INTO smartbot_messages (session_id, message_type, content)
            VALUES (:session_id, CAST(:message_type AS smartbotmessagetype), 'Test message 2')
        """), {"session_id": session_id, "message_type": enum_value})
        
        print("✓ Test 2: Explicit casting successful")
        
        # Clean up
        conn.execute(text("DELETE FROM smartbot_messages WHERE session_id = :session_id"), {"session_id": session_id})
        conn.execute(text("DELETE FROM smartbot_sessions WHERE session_id = :session_id"), {"session_id": session_id})
        conn.commit()
        
        print("✓ All tests passed!")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("Test complete.")
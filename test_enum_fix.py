#!/usr/bin/env python3
"""
Test enum fix by using string values directly instead of enum conversion
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text, Column, Integer, String, Enum
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings
import enum

# Create a simple base and enum for testing
TestBase = declarative_base()

class TestMessageType(str, enum.Enum):
    ANSWER = "answer"
    COMPLETION = "completion"

class TestMessage(TestBase):
    __tablename__ = "test_messages_fix"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255))
    # Use String column instead of Enum to avoid SQLAlchemy's enum conversion
    message_type = Column(String(50))
    content = Column(String(255))

def test_enum_fix():
    """Test enum behavior with string column"""
    
    # Create engine and session
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🔍 Testing enum fix with string column...")
        
        # Create test table
        print("\n=== Creating test table ===")
        try:
            db.execute(text("DROP TABLE IF EXISTS test_messages_fix"))
            db.execute(text("""
                CREATE TABLE test_messages_fix (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255),
                    message_type VARCHAR(50),
                    content VARCHAR(255)
                )
            """))
            db.commit()
            print("✅ Test table created")
        except Exception as e:
            print(f"❌ Table creation failed: {e}")
            return
        
        # Test 1: Single insert
        print("\n=== Test 1: Single Insert ===")
        msg1 = TestMessage(
            session_id="test-1",
            message_type=TestMessageType.ANSWER.value,
            content="Test message 1"
        )
        print(f"Message type value: {msg1.message_type!r}")
        
        db.add(msg1)
        db.flush()
        print("✅ Single insert successful")
        
        # Test 2: Bulk insert
        print("\n=== Test 2: Bulk Insert ===")
        messages = [
            TestMessage(
                session_id="test-2",
                message_type=TestMessageType.ANSWER.value,
                content="Bulk message 1"
            ),
            TestMessage(
                session_id="test-2", 
                message_type=TestMessageType.COMPLETION.value,
                content="Bulk message 2"
            )
        ]
        
        for i, msg in enumerate(messages):
            print(f"Message {i+1} type: {msg.message_type!r}")
        
        db.add_all(messages)
        db.flush()
        print("✅ Bulk insert successful")
        
        # Check what was inserted
        print("\n=== Checking inserted values ===")
        result = db.execute(text("SELECT session_id, message_type, content FROM test_messages_fix"))
        for row in result:
            print(f"Row: session_id={row[0]}, message_type={row[1]!r}, content={row[2]}")
        
        # Clean up
        db.execute(text("DROP TABLE test_messages_fix"))
        db.commit()
        print("\n✅ Test completed and cleaned up")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_enum_fix()
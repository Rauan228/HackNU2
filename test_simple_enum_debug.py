#!/usr/bin/env python3
"""
Simple test for enum behavior without complex relationships
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import settings

def test_enum_directly():
    """Test enum behavior directly with SQL"""
    
    # Create engine and session
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🔍 Testing enum behavior directly...")
        
        # Test 1: Check enum values in database
        print("\n=== Test 1: Check Enum Values ===")
        result = db.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (
                SELECT oid 
                FROM pg_type 
                WHERE typname = 'smartbotmessagetype'
            )
            ORDER BY enumsortorder
        """))
        
        enum_values = [row[0] for row in result]
        print(f"Database enum values: {enum_values}")
        
        # Test 2: Try inserting with correct lowercase values
        print("\n=== Test 2: Insert with Lowercase Values ===")
        try:
            db.execute(text("""
                INSERT INTO smartbot_messages (session_id, message_type, content)
                VALUES ('test-session-1', 'answer', 'Test message 1')
            """))
            print("✅ Lowercase 'answer' insert successful")
        except Exception as e:
            print(f"❌ Lowercase 'answer' insert failed: {e}")
        
        # Test 3: Try inserting with uppercase values
        print("\n=== Test 3: Insert with Uppercase Values ===")
        try:
            db.execute(text("""
                INSERT INTO smartbot_messages (session_id, message_type, content)
                VALUES ('test-session-2', 'ANSWER', 'Test message 2')
            """))
            print("✅ Uppercase 'ANSWER' insert successful")
        except Exception as e:
            print(f"❌ Uppercase 'ANSWER' insert failed: {e}")
        
        # Test 4: Try with explicit cast
        print("\n=== Test 4: Insert with Explicit Cast ===")
        try:
            db.execute(text("""
                INSERT INTO smartbot_messages (session_id, message_type, content)
                VALUES ('test-session-3', CAST('answer' AS smartbotmessagetype), 'Test message 3')
            """))
            print("✅ Explicit cast insert successful")
        except Exception as e:
            print(f"❌ Explicit cast insert failed: {e}")
        
        # Clean up test data
        db.execute(text("DELETE FROM smartbot_messages WHERE session_id LIKE 'test-session-%'"))
        db.commit()
        print("\n✅ Test completed (cleaned up)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_enum_directly()
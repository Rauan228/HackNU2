#!/usr/bin/env python3
"""
Test SQLAlchemy bulk insert behavior with enums
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from sqlalchemy import text
from core.db import get_db
from models.chat import SmartBotMessage, SmartBotMessageType

def test_bulk_insert():
    """Test how SQLAlchemy handles bulk insert with enums"""
    
    db = next(get_db())
    
    try:
        print("🔍 Testing SQLAlchemy bulk insert behavior with enums...")
        
        # Test 1: Single insert
        print("\n=== Test 1: Single Insert ===")
        single_msg = SmartBotMessage(
            session_id="test-single",
            message_type=SmartBotMessageType.ANSWER.value,
            content="Single insert test"
        )
        
        print(f"Before add: message_type = {single_msg.message_type!r}")
        db.add(single_msg)
        db.flush()  # Don't commit yet
        print(f"After flush: message_type = {single_msg.message_type!r}")
        
        # Test 2: Bulk insert using add_all
        print("\n=== Test 2: Bulk Insert with add_all ===")
        bulk_messages = [
            SmartBotMessage(
                session_id="test-bulk-1",
                message_type=SmartBotMessageType.ANSWER.value,
                content="Bulk message 1"
            ),
            SmartBotMessage(
                session_id="test-bulk-2", 
                message_type=SmartBotMessageType.COMPLETION.value,
                content="Bulk message 2"
            )
        ]
        
        for i, msg in enumerate(bulk_messages):
            print(f"Before add_all [{i}]: message_type = {msg.message_type!r}")
        
        db.add_all(bulk_messages)
        db.flush()
        
        for i, msg in enumerate(bulk_messages):
            print(f"After flush [{i}]: message_type = {msg.message_type!r}")
        
        # Test 3: Check what's actually in the database
        print("\n=== Test 3: Database Values ===")
        result = db.execute(text("""
            SELECT session_id, message_type, content 
            FROM smartbot_messages 
            WHERE session_id LIKE 'test-%'
            ORDER BY session_id
        """))
        
        for row in result:
            print(f"DB Row: session_id={row[0]}, message_type={row[1]!r}, content={row[2]}")
        
        # Test 4: Check enum column type info
        print("\n=== Test 4: Column Type Info ===")
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        columns = inspector.get_columns('smartbot_messages')
        
        for col in columns:
            if col['name'] == 'message_type':
                print(f"Column info: {col}")
        
        # Rollback to clean up
        db.rollback()
        print("\n✅ Test completed (rolled back)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_bulk_insert()
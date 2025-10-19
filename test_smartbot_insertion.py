#!/usr/bin/env python3
"""
Test SmartBot message insertion to reproduce the 500 error
"""

import sys
import os
import json
import uuid

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

from sqlalchemy import text
from core.db import get_db
from models.chat import SmartBotSession, SmartBotMessage, SmartBotMessageType

def test_smartbot_insertion():
    """Test SmartBot message insertion with proper session setup"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("🔍 Testing SmartBot message insertion...")
        
        # Create a test session first
        session_id = str(uuid.uuid4())
        print(f"📋 Creating test session: {session_id}")
        
        # Insert test session (we need application_id, so let's get one)
        result = db.execute(text("SELECT id FROM job_applications LIMIT 1"))
        app_row = result.fetchone()
        
        if not app_row:
            print("❌ No job applications found - creating test data first")
            # Create minimal test data
            db.execute(text("""
                INSERT INTO users (email, hashed_password, full_name, user_type) 
                VALUES ('test@example.com', 'hash', 'Test User', 'job_seeker')
                ON CONFLICT (email) DO NOTHING
            """))
            
            db.execute(text("""
                INSERT INTO job_applications (user_id, job_id, cover_letter, status) 
                VALUES (
                    (SELECT id FROM users WHERE email = 'test@example.com' LIMIT 1),
                    1, 
                    'Test application', 
                    'pending'
                )
            """))
            
            result = db.execute(text("SELECT id FROM job_applications ORDER BY id DESC LIMIT 1"))
            app_row = result.fetchone()
        
        application_id = app_row[0]
        print(f"📋 Using application_id: {application_id}")
        
        # Insert test session
        db.execute(text("""
            INSERT INTO smartbot_sessions (session_id, application_id, status) 
            VALUES (:session_id, :app_id, 'active')
        """), {"session_id": session_id, "app_id": application_id})
        
        print("✅ Test session created successfully")
        
        # Now test the problematic message insertions
        test_cases = [
            {
                "description": "Answer message with None metadata",
                "message_type": "answer",
                "content": "я работал с React 3+ года",
                "metadata": None
            },
            {
                "description": "Completion message with None metadata", 
                "message_type": "completion",
                "content": "Спасибо за ответы! Анализ завершен.",
                "metadata": None
            },
            {
                "description": "Answer message with string 'null'",
                "message_type": "answer", 
                "content": "Test with string null",
                "metadata": "null"  # This is the problematic case
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🧪 Testing: {test_case['description']}")
            
            try:
                # Test individual insertion
                result = db.execute(text("""
                    INSERT INTO smartbot_messages (session_id, message_type, content, message_metadata)
                    VALUES (:session_id, :msg_type, :content, :metadata)
                    RETURNING id, message_metadata
                """), {
                    "session_id": session_id,
                    "msg_type": test_case["message_type"],
                    "content": test_case["content"],
                    "metadata": test_case["metadata"]
                })
                
                inserted_row = result.fetchone()
                print(f"✅ Individual insertion successful: ID={inserted_row[0]}, metadata={inserted_row[1]}")
                
            except Exception as e:
                print(f"❌ Individual insertion failed: {e}")
                return False
        
        # Test batch insertion (the problematic case from the logs)
        print(f"\n🧪 Testing batch insertion (the problematic case)")
        
        try:
            # This simulates the batch insert that's causing the 500 error
            batch_values = [
                (session_id, 'answer', 'я работал с React 3+ года', 'null'),
                (session_id, 'completion', 'Спасибо за ответы! Анализ завершен.', 'null')
            ]
            
            for session_id_val, msg_type, content, metadata in batch_values:
                result = db.execute(text("""
                    INSERT INTO smartbot_messages (session_id, message_type, content, message_metadata)
                    VALUES (:session_id, :msg_type, :content, :metadata)
                    RETURNING id, message_metadata
                """), {
                    "session_id": session_id_val,
                    "msg_type": msg_type,
                    "content": content,
                    "metadata": metadata
                })
                
                inserted_row = result.fetchone()
                print(f"✅ Batch item inserted: ID={inserted_row[0]}, metadata={inserted_row[1]}")
            
        except Exception as e:
            print(f"❌ Batch insertion failed: {e}")
            print("This is likely the source of the 500 error!")
            return False
        
        db.commit()
        print("\n✅ All SmartBot insertion tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error in SmartBot insertion test: {e}")
        db.rollback()
        return False
    
    finally:
        # Clean up test data
        try:
            db.execute(text("DELETE FROM smartbot_messages WHERE session_id = :session_id"), {"session_id": session_id})
            db.execute(text("DELETE FROM smartbot_sessions WHERE session_id = :session_id"), {"session_id": session_id})
            db.commit()
        except:
            pass
        db.close()

if __name__ == "__main__":
    success = test_smartbot_insertion()
    sys.exit(0 if success else 1)
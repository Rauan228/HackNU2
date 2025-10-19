#!/usr/bin/env python3
"""
Test message_metadata column handling with NULL values
"""

import sys
import os
import json

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

from sqlalchemy import text
from core.db import get_db
from models.chat import SmartBotMessage, SmartBotMessageType

def test_metadata_handling():
    """Test message_metadata column handling with different values"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("🔍 Testing message_metadata column handling...")
        
        # Check column definition
        result = db.execute(
            text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'smartbot_messages' 
                AND column_name = 'message_metadata'
            """)
        )
        
        column_info = result.fetchone()
        if column_info:
            print(f"📋 Column info: name={column_info[0]}, type={column_info[1]}, nullable={column_info[2]}, default={column_info[3]}")
        else:
            print("❌ message_metadata column not found!")
            return False
        
        # Test different metadata values
        test_cases = [
            ("None (Python)", None),
            ("Empty dict", {}),
            ("Dict with data", {"test": "value"}),
        ]
        
        session_id = "test-session-123"
        
        for description, metadata_value in test_cases:
            print(f"\n🧪 Testing {description}: {metadata_value}")
            
            try:
                # Test direct SQL insertion
                if metadata_value is None:
                    sql_value = None
                else:
                    sql_value = json.dumps(metadata_value)
                
                result = db.execute(
                    text("""
                        INSERT INTO smartbot_messages (session_id, message_type, content, message_metadata)
                        VALUES (:session_id, :msg_type, :content, :metadata)
                        RETURNING id, message_metadata
                    """),
                    {
                        "session_id": session_id,
                        "msg_type": "system",
                        "content": f"Test message for {description}",
                        "metadata": sql_value
                    }
                )
                
                inserted_row = result.fetchone()
                print(f"✅ SQL insertion successful: ID={inserted_row[0]}, metadata={inserted_row[1]}")
                
                # Clean up
                db.execute(
                    text("DELETE FROM smartbot_messages WHERE id = :id"),
                    {"id": inserted_row[0]}
                )
                
            except Exception as e:
                print(f"❌ SQL insertion failed: {e}")
                return False
        
        # Test the specific case that's causing issues
        print(f"\n🧪 Testing problematic case: string 'null'")
        try:
            result = db.execute(
                text("""
                    INSERT INTO smartbot_messages (session_id, message_type, content, message_metadata)
                    VALUES (:session_id, :msg_type, :content, :metadata)
                    RETURNING id, message_metadata
                """),
                {
                    "session_id": session_id,
                    "msg_type": "system",
                    "content": "Test message with string null",
                    "metadata": "null"  # This is the problematic case
                }
            )
            
            inserted_row = result.fetchone()
            print(f"✅ String 'null' insertion successful: ID={inserted_row[0]}, metadata={inserted_row[1]}")
            
            # Clean up
            db.execute(
                text("DELETE FROM smartbot_messages WHERE id = :id"),
                {"id": inserted_row[0]}
            )
            
        except Exception as e:
            print(f"❌ String 'null' insertion failed: {e}")
            print("This might be the source of the 500 error!")
            return False
        
        db.commit()
        print("\n✅ All metadata handling tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing metadata handling: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = test_metadata_handling()
    sys.exit(0 if success else 1)
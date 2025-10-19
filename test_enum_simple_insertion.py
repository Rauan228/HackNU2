import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.chat import SmartBotMessageType

def test_enum_insertion_simple():
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        print("=== Testing enum values ===")
        print(f"SmartBotMessageType.ANSWER = {SmartBotMessageType.ANSWER!r}")
        print(f"SmartBotMessageType.ANSWER.value = {SmartBotMessageType.ANSWER.value!r}")
        print(f"SmartBotMessageType.COMPLETION = {SmartBotMessageType.COMPLETION!r}")
        print(f"SmartBotMessageType.COMPLETION.value = {SmartBotMessageType.COMPLETION.value!r}")
        
        print("\n=== Testing direct SQL insertion ===")
        
        # Test inserting with enum values directly
        for enum_val in [SmartBotMessageType.ANSWER, SmartBotMessageType.COMPLETION, SmartBotMessageType.QUESTION]:
            print(f"\nTesting {enum_val.name}:")
            print(f"  enum_val.value = {enum_val.value!r}")
            
            try:
                # Test direct insertion with the enum value
                result = db.execute(text("""
                    INSERT INTO smartbot_messages (session_id, message_type, content) 
                    VALUES (:session_id, :message_type, :content) 
                    RETURNING id, message_type
                """), {
                    "session_id": f"test-session-{enum_val.name.lower()}",
                    "message_type": enum_val.value,
                    "content": f"Test message for {enum_val.name}"
                })
                
                row = result.fetchone()
                print(f"  ✓ {enum_val.name} insertion successful: id={row[0]}, message_type='{row[1]}'")
                
                # Clean up
                db.execute(text("DELETE FROM smartbot_messages WHERE id = :id"), {"id": row[0]})
                
            except Exception as e:
                print(f"  ✗ {enum_val.name} insertion failed: {e}")
                db.rollback()
        
        print("\n=== Testing what happens with uppercase values ===")
        
        # Test what happens if we accidentally pass uppercase
        test_values = ['ANSWER', 'COMPLETION', 'answer', 'completion']
        
        for test_val in test_values:
            print(f"\nTesting '{test_val}':")
            try:
                result = db.execute(text("""
                    INSERT INTO smartbot_messages (session_id, message_type, content) 
                    VALUES (:session_id, :message_type, :content) 
                    RETURNING id, message_type
                """), {
                    "session_id": f"test-session-{test_val}",
                    "message_type": test_val,
                    "content": f"Test message for {test_val}"
                })
                
                row = result.fetchone()
                print(f"  ✓ '{test_val}' insertion successful: id={row[0]}, message_type='{row[1]}'")
                
                # Clean up
                db.execute(text("DELETE FROM smartbot_messages WHERE id = :id"), {"id": row[0]})
                
            except Exception as e:
                print(f"  ✗ '{test_val}' insertion failed: {e}")
                db.rollback()
        
        db.commit()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_enum_insertion_simple()
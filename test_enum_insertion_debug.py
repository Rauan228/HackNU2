import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.chat import SmartBotMessage, SmartBotMessageType

def test_enum_insertion():
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        print("=== Testing enum values ===")
        print(f"SmartBotMessageType.ANSWER = {SmartBotMessageType.ANSWER!r}")
        print(f"SmartBotMessageType.ANSWER.value = {SmartBotMessageType.ANSWER.value!r}")
        print(f"SmartBotMessageType.COMPLETION = {SmartBotMessageType.COMPLETION!r}")
        print(f"SmartBotMessageType.COMPLETION.value = {SmartBotMessageType.COMPLETION.value!r}")
        
        print("\n=== Testing direct insertion ===")
        
        # Test creating a SmartBotMessage object
        test_message = SmartBotMessage(
            session_id="test-session-123",
            message_type=SmartBotMessageType.ANSWER.value,
            content="Test message",
            message_metadata=None
        )
        
        print(f"Created message object with message_type: {test_message.message_type!r}")
        print(f"Type of message_type: {type(test_message.message_type)}")
        
        # Try to add and flush to see what happens
        db.add(test_message)
        print("Added to session...")
        
        try:
            db.flush()
            print("✓ Flush successful")
            db.rollback()  # Don't actually commit
        except Exception as e:
            print(f"✗ Flush failed: {e}")
            db.rollback()
        
        print("\n=== Testing with different enum values ===")
        
        for enum_val in [SmartBotMessageType.ANSWER, SmartBotMessageType.COMPLETION, SmartBotMessageType.QUESTION]:
            print(f"\nTesting {enum_val.name}:")
            print(f"  enum_val = {enum_val!r}")
            print(f"  enum_val.value = {enum_val.value!r}")
            print(f"  str(enum_val) = {str(enum_val)!r}")
            
            test_msg = SmartBotMessage(
                session_id="test-session-456",
                message_type=enum_val.value,
                content=f"Test for {enum_val.name}",
                message_metadata=None
            )
            
            print(f"  Created message_type: {test_msg.message_type!r}")
            
            db.add(test_msg)
            try:
                db.flush()
                print(f"  ✓ {enum_val.name} insertion successful")
                db.rollback()
            except Exception as e:
                print(f"  ✗ {enum_val.name} insertion failed: {e}")
                db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_enum_insertion()
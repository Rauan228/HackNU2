import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Create engine and session
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_enum_insertion():
    db = SessionLocal()
    try:
        # First, let's see what's in the database enum type
        result = db.execute(text("SELECT unnest(enum_range(NULL::smartbotmessagetype))"))
        enum_values = [row[0] for row in result.fetchall()]
        print(f"Database enum values: {enum_values}")
        
        # Test direct insertion with different values
        test_values = [
            'question',
            'QUESTION',
            '"question"',
            '"QUESTION"'
        ]
        
        for test_value in test_values:
            try:
                print(f"\nTesting insertion with value: {test_value!r}")
                
                # Try to insert directly
                result = db.execute(text("""
                    SELECT :test_value::smartbotmessagetype
                """), {"test_value": test_value})
                
                fetched = result.fetchone()[0]
                print(f"  Success! Converted to: {fetched!r}")
                
            except Exception as e:
                print(f"  Failed: {e}")
        
        # Test what happens when we use SQLAlchemy's enum handling
        print(f"\nTesting SQLAlchemy enum column behavior...")
        
        # Import the enum
        from models.chat import SmartBotMessageType
        
        print(f"SmartBotMessageType.QUESTION = {SmartBotMessageType.QUESTION!r}")
        print(f"SmartBotMessageType.QUESTION.value = {SmartBotMessageType.QUESTION.value!r}")
        print(f"str(SmartBotMessageType.QUESTION) = {str(SmartBotMessageType.QUESTION)!r}")
        
        # Test what SQLAlchemy would actually send
        from sqlalchemy import Enum
        enum_type = Enum(SmartBotMessageType, name='smartbotmessagetype', native_enum=False)
        
        # Test the enum type's process_bind_param method
        processed_value = enum_type.process_bind_param(SmartBotMessageType.QUESTION.value, None)
        print(f"SQLAlchemy processed value: {processed_value!r}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_enum_insertion()
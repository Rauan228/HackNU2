import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text, Enum
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.chat import SmartBotMessageType

# Create engine and session
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_enum_behavior():
    db = SessionLocal()
    try:
        print("=== Testing SmartBotMessageType enum behavior ===")
        
        # Test the enum values
        print(f"SmartBotMessageType.QUESTION = {SmartBotMessageType.QUESTION!r}")
        print(f"SmartBotMessageType.QUESTION.value = {SmartBotMessageType.QUESTION.value!r}")
        print(f"SmartBotMessageType.QUESTION.name = {SmartBotMessageType.QUESTION.name!r}")
        
        # Test SQLAlchemy Enum type
        enum_type = Enum(SmartBotMessageType, name='smartbotmessagetype', native_enum=False)
        print(f"SQLAlchemy Enum type: {enum_type}")
        
        # Test what happens when we pass the enum value to a query
        print("\n=== Testing direct SQL with enum value ===")
        try:
            result = db.execute(text("SELECT 'question'::smartbotmessagetype"))
            print(f"Direct 'question' cast: {result.fetchone()[0]}")
        except Exception as e:
            print(f"Failed to cast 'question': {e}")
            
        try:
            result = db.execute(text("SELECT 'QUESTION'::smartbotmessagetype"))
            print(f"Direct 'QUESTION' cast: {result.fetchone()[0]}")
        except Exception as e:
            print(f"Failed to cast 'QUESTION': {e}")
        
        # Test what happens when we use the enum value in a parameterized query
        print("\n=== Testing parameterized query ===")
        try:
            result = db.execute(
                text("SELECT CAST(:value AS smartbotmessagetype)"),
                {"value": SmartBotMessageType.QUESTION.value}
            )
            print(f"Parameterized with .value: {result.fetchone()[0]}")
        except Exception as e:
            print(f"Failed parameterized with .value: {e}")
            
        try:
            result = db.execute(
                text("SELECT CAST(:value AS smartbotmessagetype)"),
                {"value": str(SmartBotMessageType.QUESTION)}
            )
            print(f"Parameterized with str(): {result.fetchone()[0]}")
        except Exception as e:
            print(f"Failed parameterized with str(): {e}")
        
        # Check what the actual database enum values are
        print("\n=== Database enum values ===")
        result = db.execute(text("SELECT unnest(enum_range(NULL::smartbotmessagetype))"))
        enum_values = [row[0] for row in result.fetchall()]
        print(f"Database enum values: {enum_values}")
        
        # Test if there's any case sensitivity issue
        print("\n=== Case sensitivity test ===")
        for test_val in ['question', 'QUESTION', 'Question']:
            try:
                result = db.execute(
                    text("SELECT CAST(:value AS smartbotmessagetype)"),
                    {"value": test_val}
                )
                print(f"'{test_val}' -> {result.fetchone()[0]}")
            except Exception as e:
                print(f"'{test_val}' -> ERROR: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_enum_behavior()
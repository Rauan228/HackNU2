import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from backend.core.config import settings
from backend.models.chat import SmartBotMessageType

# Create database connection
engine = create_engine(settings.database_url)

print("Checking database enum configuration...")

try:
    with engine.connect() as conn:
        # Check the enum type definition in the database
        result = conn.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (
                SELECT oid 
                FROM pg_type 
                WHERE typname = 'smartbotmessagetype'
            )
            ORDER BY enumsortorder;
        """))
        
        db_enum_values = [row.enumlabel for row in result.fetchall()]
        print(f"Database enum values: {db_enum_values}")
        
        # Check Python enum values
        python_enum_values = [e.value for e in SmartBotMessageType]
        print(f"Python enum values: {python_enum_values}")
        
        # Check if they match
        if set(db_enum_values) == set(python_enum_values):
            print("✓ Enum values match!")
        else:
            print("✗ Enum values don't match!")
            print(f"  Missing in DB: {set(python_enum_values) - set(db_enum_values)}")
            print(f"  Extra in DB: {set(db_enum_values) - set(python_enum_values)}")
        
        # Test what SQLAlchemy actually sends
        print(f"\nTesting enum value conversion:")
        print(f"SmartBotMessageType.QUESTION = {SmartBotMessageType.QUESTION!r}")
        print(f"SmartBotMessageType.QUESTION.value = {SmartBotMessageType.QUESTION.value!r}")
        print(f"str(SmartBotMessageType.QUESTION) = {str(SmartBotMessageType.QUESTION)!r}")
        
        # Test direct insertion with the enum value
        print(f"\nTesting direct SQL insertion...")
        try:
            conn.execute(text("""
                INSERT INTO smartbot_messages (session_id, message_type, content) 
                VALUES ('test-session-123', :message_type, 'Test message')
            """), {"message_type": SmartBotMessageType.QUESTION.value})
            print("✓ Direct insertion with .value works")
            
            # Clean up
            conn.execute(text("DELETE FROM smartbot_messages WHERE session_id = 'test-session-123'"))
            conn.commit()
        except Exception as e:
            print(f"✗ Direct insertion failed: {e}")
            conn.rollback()
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("Database enum check complete.")
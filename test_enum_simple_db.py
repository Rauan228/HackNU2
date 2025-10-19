import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from core.config import settings

def test_enum_simple():
    # Create a fresh engine for each test
    engine = create_engine(settings.database_url)
    
    print("=== Testing database enum values ===")
    
    with engine.connect() as conn:
        # Check what enum values exist in the database
        result = conn.execute(text("SELECT unnest(enum_range(NULL::smartbotmessagetype))"))
        enum_values = [row[0] for row in result.fetchall()]
        print(f"Database enum values: {enum_values}")
    
    print("\n=== Testing case sensitivity ===")
    
    test_values = ['question', 'QUESTION', 'Question']
    
    for test_val in test_values:
        with engine.connect() as conn:
            try:
                result = conn.execute(
                    text("SELECT CAST(:value AS smartbotmessagetype)"),
                    {"value": test_val}
                )
                converted = result.fetchone()[0]
                print(f"'{test_val}' -> '{converted}' ✓")
            except Exception as e:
                print(f"'{test_val}' -> ERROR: {e}")
    
    print("\n=== Testing what happens with uppercase ===")
    
    # Test if 'QUESTION' is somehow valid
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT 'QUESTION'::smartbotmessagetype"))
            print(f"Direct 'QUESTION' cast succeeded: {result.fetchone()[0]}")
        except Exception as e:
            print(f"Direct 'QUESTION' cast failed: {e}")
    
    # Test if there's a different enum type
    with engine.connect() as conn:
        try:
            result = conn.execute(text("""
                SELECT t.typname, e.enumlabel 
                FROM pg_type t 
                JOIN pg_enum e ON t.oid = e.enumtypid 
                WHERE t.typname LIKE '%message%'
                ORDER BY t.typname, e.enumsortorder
            """))
            print("\nAll enum types with 'message' in name:")
            for row in result.fetchall():
                print(f"  {row[0]}: {row[1]}")
        except Exception as e:
            print(f"Failed to query enum types: {e}")

if __name__ == "__main__":
    test_enum_simple()
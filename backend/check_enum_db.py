#!/usr/bin/env python3
"""
Check database enum values for smartbotmessagetype
"""

from core.db import engine
from sqlalchemy import text

def check_enum_values():
    """Check the current enum values in the database"""
    
    try:
        with engine.connect() as conn:
            # Check enum values
            result = conn.execute(text("SELECT unnest(enum_range(NULL::smartbotmessagetype))"))
            print("Database enum values:")
            for row in result:
                print(f"  '{row[0]}'")
                
    except Exception as e:
        print(f"Error checking enum values: {e}")

if __name__ == "__main__":
    check_enum_values()
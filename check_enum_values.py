#!/usr/bin/env python3
"""
Check current ENUM values in database for smartbotmessagetype
"""

import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

from sqlalchemy import text
from core.db import get_db

def check_enum_values():
    """Check current ENUM values for smartbotmessagetype"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("🔍 Checking current ENUM values for smartbotmessagetype...")
        
        # Check if the ENUM type exists
        result = db.execute(
            text("SELECT typname FROM pg_type WHERE typname = 'smartbotmessagetype'")
        )
        enum_exists = result.fetchone()
        
        if not enum_exists:
            print("❌ ENUM type 'smartbotmessagetype' does not exist!")
            return False
        
        print("✅ ENUM type 'smartbotmessagetype' exists")
        
        # Get current ENUM values
        result = db.execute(
            text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'smartbotmessagetype') 
                ORDER BY enumsortorder
            """)
        )
        
        current_values = [row[0] for row in result.fetchall()]
        
        print(f"📋 Current ENUM values: {current_values}")
        
        # Check for required values
        required_values = ['bot', 'user', 'system', 'question', 'info', 'answer', 'completion']
        missing_values = [val for val in required_values if val not in current_values]
        
        if missing_values:
            print(f"❌ Missing ENUM values: {missing_values}")
            return False
        else:
            print("✅ All required ENUM values are present")
            return True
        
    except Exception as e:
        print(f"❌ Error checking ENUM values: {e}")
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = check_enum_values()
    sys.exit(0 if success else 1)
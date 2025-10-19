#!/usr/bin/env python3
"""
Update database schema to change message_type from enum to varchar
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from core.config import settings

def update_schema():
    """Update the database schema"""
    
    # Create engine
    engine = create_engine(settings.database_url)
    
    try:
        print("🔄 Updating database schema...")
        
        with engine.connect() as conn:
            trans = conn.begin()
            
            try:
                # Step 1: Add a temporary column
                print("1. Adding temporary varchar column...")
                conn.execute(text("""
                    ALTER TABLE smartbot_messages 
                    ADD COLUMN message_type_temp VARCHAR(50)
                """))
                
                # Step 2: Copy data from enum to varchar
                print("2. Copying data to temporary column...")
                conn.execute(text("""
                    UPDATE smartbot_messages 
                    SET message_type_temp = message_type::text
                """))
                
                # Step 3: Drop the old enum column
                print("3. Dropping old enum column...")
                conn.execute(text("""
                    ALTER TABLE smartbot_messages 
                    DROP COLUMN message_type
                """))
                
                # Step 4: Rename the temporary column
                print("4. Renaming temporary column...")
                conn.execute(text("""
                    ALTER TABLE smartbot_messages 
                    RENAME COLUMN message_type_temp TO message_type
                """))
                
                # Step 5: Add NOT NULL constraint
                print("5. Adding NOT NULL constraint...")
                conn.execute(text("""
                    ALTER TABLE smartbot_messages 
                    ALTER COLUMN message_type SET NOT NULL
                """))
                
                # Step 6: Drop the enum type (if no other tables use it)
                print("6. Dropping enum type...")
                try:
                    conn.execute(text("DROP TYPE smartbotmessagetype"))
                    print("   ✅ Enum type dropped")
                except Exception as e:
                    print(f"   ⚠️ Could not drop enum type (may be in use): {e}")
                
                trans.commit()
                print("✅ Schema update completed successfully!")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Schema update failed: {e}")
                raise
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_schema()
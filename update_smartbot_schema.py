#!/usr/bin/env python3
"""
Update SmartBot database schema to add session_id field and fix foreign key relationships
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import text
from core.db import engine

def update_schema():
    """Update the database schema for SmartBot tables"""
    
    try:
        with engine.connect() as conn:
            # Add session_id column to smartbot_sessions
            print("Adding session_id column to smartbot_sessions...")
            conn.execute(text("""
                ALTER TABLE smartbot_sessions 
                ADD COLUMN IF NOT EXISTS session_id VARCHAR(255) UNIQUE
            """))
            
            # Update existing rows with UUID values
            print("Updating existing rows with UUID values...")
            conn.execute(text("""
                UPDATE smartbot_sessions 
                SET session_id = gen_random_uuid()::text 
                WHERE session_id IS NULL
            """))
            
            # Make session_id NOT NULL
            print("Making session_id NOT NULL...")
            conn.execute(text("""
                ALTER TABLE smartbot_sessions 
                ALTER COLUMN session_id SET NOT NULL
            """))
            
            # Create unique index
            print("Creating unique index on session_id...")
            conn.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS ix_smartbot_sessions_session_id 
                ON smartbot_sessions (session_id)
            """))
            
            # Update smartbot_messages table
            print("Updating smartbot_messages foreign key...")
            
            # First, add a temporary column
            conn.execute(text("""
                ALTER TABLE smartbot_messages 
                ADD COLUMN IF NOT EXISTS temp_session_id VARCHAR(255)
            """))
            
            # Update the temporary column with session_id values
            conn.execute(text("""
                UPDATE smartbot_messages 
                SET temp_session_id = s.session_id 
                FROM smartbot_sessions s 
                WHERE smartbot_messages.session_id = s.id
            """))
            
            # Drop the old foreign key constraint
            conn.execute(text("""
                ALTER TABLE smartbot_messages 
                DROP CONSTRAINT IF EXISTS smartbot_messages_session_id_fkey
            """))
            
            # Drop the old session_id column
            conn.execute(text("""
                ALTER TABLE smartbot_messages 
                DROP COLUMN session_id
            """))
            
            # Rename temp column to session_id
            conn.execute(text("""
                ALTER TABLE smartbot_messages 
                RENAME COLUMN temp_session_id TO session_id
            """))
            
            # Add new foreign key constraint
            conn.execute(text("""
                ALTER TABLE smartbot_messages 
                ADD CONSTRAINT smartbot_messages_session_id_fkey 
                FOREIGN KEY (session_id) REFERENCES smartbot_sessions (session_id)
            """))
            
            # Update candidate_analyses table
            print("Updating candidate_analyses table...")
            
            # Add temporary column
            conn.execute(text("""
                ALTER TABLE candidate_analyses 
                ADD COLUMN IF NOT EXISTS temp_session_id VARCHAR(255)
            """))
            
            # Update the temporary column with session_id values
            conn.execute(text("""
                UPDATE candidate_analyses 
                SET temp_session_id = s.session_id 
                FROM smartbot_sessions s 
                WHERE candidate_analyses.smartbot_session_id = s.id
            """))
            
            # Drop old foreign key constraint
            conn.execute(text("""
                ALTER TABLE candidate_analyses 
                DROP CONSTRAINT IF EXISTS candidate_analyses_smartbot_session_id_fkey
            """))
            
            # Drop old column
            conn.execute(text("""
                ALTER TABLE candidate_analyses 
                DROP COLUMN smartbot_session_id
            """))
            
            # Rename temp column
            conn.execute(text("""
                ALTER TABLE candidate_analyses 
                RENAME COLUMN temp_session_id TO session_id
            """))
            
            # Add new foreign key constraint
            conn.execute(text("""
                ALTER TABLE candidate_analyses 
                ADD CONSTRAINT candidate_analyses_session_id_fkey 
                FOREIGN KEY (session_id) REFERENCES smartbot_sessions (session_id)
            """))
            
            conn.commit()
            print("✅ Database schema updated successfully!")
            
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = update_schema()
    sys.exit(0 if success else 1)
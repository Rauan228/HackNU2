import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from core.config import settings

# Create engine
engine = create_engine(settings.database_url)

print("Checking smartbot_messages table schema...")

with engine.connect() as conn:
    result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'smartbot_messages' ORDER BY ordinal_position"))
    columns = result.fetchall()
    
    if columns:
        print("Columns in smartbot_messages table:")
        for col_name, col_type in columns:
            print(f"  {col_name}: {col_type}")
    else:
        print("No columns found or table doesn't exist")
        
    # Also check if table exists
    result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'smartbot_messages')"))
    exists = result.fetchone()[0]
    print(f"\nTable exists: {exists}")
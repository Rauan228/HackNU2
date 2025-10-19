import psycopg2
import sys
import os
from urllib.parse import urlparse

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.config import settings

def update_enum():
    try:
        # Parse database URL
        parsed = urlparse(settings.database_url)
        
        conn = psycopg2.connect(
            host=parsed.hostname,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password,
            port=parsed.port
        )
        cur = conn.cursor()
        
        print("🔧 Updating smartbotmessagetype enum...")
        
        # Add missing enum values
        cur.execute("ALTER TYPE smartbotmessagetype ADD VALUE IF NOT EXISTS 'bot'")
        cur.execute("ALTER TYPE smartbotmessagetype ADD VALUE IF NOT EXISTS 'user'")
        cur.execute("ALTER TYPE smartbotmessagetype ADD VALUE IF NOT EXISTS 'system'")
        
        conn.commit()
        print('✅ Successfully updated smartbotmessagetype enum')
        
        # Verify the enum values
        cur.execute("SELECT unnest(enum_range(NULL::smartbotmessagetype))")
        values = [row[0] for row in cur.fetchall()]
        print(f'📋 Current enum values: {values}')
        
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = update_enum()
    sys.exit(0 if success else 1)
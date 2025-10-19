import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.config import settings
import psycopg2
from urllib.parse import urlparse

# Parse database URL
parsed = urlparse(settings.database_url)
conn = psycopg2.connect(
    host=parsed.hostname,
    database=parsed.path[1:],
    user=parsed.username,
    password=parsed.password,
    port=parsed.port
)

cursor = conn.cursor()

# Test enum values directly
try:
    # Test if 'answer' is a valid enum value
    cursor.execute("SELECT 'answer'::smartbotmessagetype")
    result = cursor.fetchone()
    print(f"'answer' as enum: {result[0]}")
    
    # Test if 'ANSWER' is a valid enum value
    cursor.execute("SELECT 'ANSWER'::smartbotmessagetype")
    result = cursor.fetchone()
    print(f"'ANSWER' as enum: {result[0]}")
    
except Exception as e:
    print(f"Error: {e}")

cursor.close()
conn.close()
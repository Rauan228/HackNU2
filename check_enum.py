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
cursor.execute("SELECT unnest(enum_range(NULL::smartbotmessagetype))")
values = cursor.fetchall()
print('Database enum values:', [v[0] for v in values])
cursor.close()
conn.close()
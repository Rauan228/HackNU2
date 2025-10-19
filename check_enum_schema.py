import psycopg2
from urllib.parse import urlparse
import os

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://hacknu_user:hacknu_password@localhost:5432/hacknu_smartbot')
parsed = urlparse(DATABASE_URL)

try:
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path[1:],
        user=parsed.username,
        password=parsed.password
    )

    cur = conn.cursor()

    # Check enum types
    print('=== ENUM TYPES ===')
    cur.execute("""
    SELECT typname, enumlabel 
    FROM pg_type t 
    JOIN pg_enum e ON t.oid = e.enumtypid 
    WHERE typname LIKE '%smartbot%' OR typname LIKE '%message%'
    ORDER BY typname, enumsortorder;
    """)
    for row in cur.fetchall():
        print(f'{row[0]}: {row[1]}')

    print('\n=== SMARTBOT_MESSAGES SCHEMA ===')
    cur.execute("""
    SELECT column_name, data_type, udt_name 
    FROM information_schema.columns 
    WHERE table_name = 'smartbot_messages' 
    ORDER BY ordinal_position;
    """)
    for row in cur.fetchall():
        print(f'{row[0]}: {row[1]} ({row[2]})')

    print('\n=== ALL ENUM TYPES ===')
    cur.execute("""
    SELECT typname, array_agg(enumlabel ORDER BY enumsortorder) as labels
    FROM pg_type t 
    JOIN pg_enum e ON t.oid = e.enumtypid 
    GROUP BY typname
    ORDER BY typname;
    """)
    for row in cur.fetchall():
        print(f'{row[0]}: {row[1]}')

    conn.close()
    print('\nДанные получены успешно!')

except Exception as e:
    print(f'Ошибка подключения к БД: {e}')
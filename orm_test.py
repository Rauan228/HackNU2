import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from core.db import SessionLocal, engine
from sqlalchemy import text

print('URL:', engine.url)

session = SessionLocal()
try:
    print('Testing connection via SessionLocal...')
    result = session.execute(text('SELECT 1'))
    print('Result:', result.scalar())
finally:
    session.close()
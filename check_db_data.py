import sqlite3

def check_database():
    conn = sqlite3.connect('hacknu_smartbot.db')
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('Tables:', tables)
    
    # Check if we're using PostgreSQL instead
    try:
        import psycopg2
        from core.config import settings
        
        # Try to connect to PostgreSQL
        pg_conn = psycopg2.connect(settings.database_url)
        pg_cursor = pg_conn.cursor()
        
        # Check job application 32
        pg_cursor.execute('SELECT * FROM job_applications WHERE id = 32')
        app = pg_cursor.fetchone()
        print('Application 32:', app)
        
        if app:
            job_id, user_id, resume_id = app[4], app[3], app[5]
            
            # Check if job exists
            pg_cursor.execute('SELECT id, title FROM jobs WHERE id = %s', (job_id,))
            job = pg_cursor.fetchone()
            print('Job:', job)
            
            # Check if user exists
            pg_cursor.execute('SELECT id, full_name FROM users WHERE id = %s', (user_id,))
            user = pg_cursor.fetchone()
            print('User:', user)
            
            # Check if resume exists
            pg_cursor.execute('SELECT id, skills FROM resumes WHERE id = %s', (resume_id,))
            resume = pg_cursor.fetchone()
            print('Resume:', resume)
        
        pg_conn.close()
        
    except Exception as e:
        print(f"PostgreSQL error: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_database()
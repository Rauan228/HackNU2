import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='hacknu_job_portal',
        user='postgres',
        password='12345'
    )
    cursor = conn.cursor()
    
    # First, check the table structure
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'job_applications' 
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    print('Job applications table structure:')
    for col in columns:
        print(f'  {col[0]}: {col[1]}')
    
    # Check the most recent job application for job 88
    cursor.execute('SELECT * FROM job_applications WHERE job_id = 88 ORDER BY created_at DESC LIMIT 1')
    app = cursor.fetchone()
    print('\nLatest application for job 88:', app)
    
    if app:
        # Based on the structure, parse correctly
        app_id = app[0]  # id
        user_id = app[1]  # user_id  
        job_id = app[2]   # job_id
        resume_id = app[3] # resume_id
        cover_letter = app[4] # cover_letter
        status = app[5]   # status
        
        print(f'Application ID: {app_id}, User ID: {user_id}, Job ID: {job_id}, Resume ID: {resume_id}, Status: {status}')
        
        # Check if job exists
        cursor.execute('SELECT id, title FROM jobs WHERE id = %s', (job_id,))
        job = cursor.fetchone()
        print('Job exists:', job is not None, job)
        
        # Check if user exists
        cursor.execute('SELECT id, full_name FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        print('User exists:', user is not None, user)
        
        # Check if resume exists
        cursor.execute('SELECT * FROM resumes WHERE id = %s', (resume_id,))
        resume = cursor.fetchone()
        print('Resume exists:', resume is not None)
        if resume:
            print('Resume skills:', resume[5] if len(resume) > 5 else 'N/A')
            print('Resume experience:', resume[3] if len(resume) > 3 else 'N/A')
    
    conn.close()
    
except Exception as e:
    print(f'Database error: {e}')
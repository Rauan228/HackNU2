import sqlite3
db_files = ['hacknu_smartbot.db', 'smartbot.db']
for db_file in db_files:
    print(f'\n=== Checking {db_file} ===')
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print('Available tables:', [table[0] for table in tables])
        table_names = [table[0] for table in tables]
        if 'job_applications' in table_names:
            cursor.execute('\n                SELECT ja.id, ja.user_id, ja.job_id, j.employer_id, \n                       u.email as applicant_email, e.email as employer_email \n                FROM job_applications ja \n                JOIN jobs j ON ja.job_id = j.id \n                JOIN users u ON ja.user_id = u.id \n                JOIN users e ON j.employer_id = e.id \n                WHERE ja.id = 141\n            ')
            result = cursor.fetchone()
            if result:
                print(f'Application 141:')
                print(f'  - Application ID: {result[0]}')
                print(f'  - Applicant User ID: {result[1]}')
                print(f'  - Job ID: {result[2]}')
                print(f'  - Employer User ID: {result[3]}')
                print(f'  - Applicant Email: {result[4]}')
                print(f'  - Employer Email: {result[5]}')
            else:
                print('Application 141 not found')
        else:
            print("No 'job_applications' table found")
        conn.close()
    except Exception as e:
        print(f'Error with {db_file}: {e}')
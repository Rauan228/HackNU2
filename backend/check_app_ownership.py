import sqlite3

# Try both database files
db_files = ['hacknu_smartbot.db', 'smartbot.db']

for db_file in db_files:
    print(f"\n=== Checking {db_file} ===")
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Check table names first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Available tables:", [table[0] for table in tables])

        # Check if applications table exists
        table_names = [table[0] for table in tables]
        if 'job_applications' in table_names:
            # Check application 141 ownership
            cursor.execute("""
                SELECT ja.id, ja.user_id, ja.job_id, j.employer_id, 
                       u.email as applicant_email, e.email as employer_email 
                FROM job_applications ja 
                JOIN jobs j ON ja.job_id = j.id 
                JOIN users u ON ja.user_id = u.id 
                JOIN users e ON j.employer_id = e.id 
                WHERE ja.id = 141
            """)

            result = cursor.fetchone()
            if result:
                print(f"Application 141:")
                print(f"  - Application ID: {result[0]}")
                print(f"  - Applicant User ID: {result[1]}")
                print(f"  - Job ID: {result[2]}")
                print(f"  - Employer User ID: {result[3]}")
                print(f"  - Applicant Email: {result[4]}")
                print(f"  - Employer Email: {result[5]}")
            else:
                print("Application 141 not found")
        else:
            print("No 'job_applications' table found")

        conn.close()
    except Exception as e:
        print(f"Error with {db_file}: {e}")
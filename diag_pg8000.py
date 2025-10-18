import pg8000

print('pg8000 version:', pg8000.__version__)

def try_connect(password: str, database: str):
    print(f'Connecting as postgres to {database} with password={password!r}...')
    try:
        conn = pg8000.connect(user='postgres', password=password, host='127.0.0.1', port=5432, database=database)
        print('Connected OK')
        conn.close()
    except Exception as e:
        print('Error type:', type(e).__name__)
        print('Error:', e)

for pwd in ['postgres', '12345']:
    for db in ['postgres', 'hacknu_job_portal']:
        try_connect(pwd, db)
import psycopg2, sys
print('Connecting to postgres with 12345...')
try:
    conn = psycopg2.connect(host='127.0.0.1', port=5432, user='postgres', password='12345', dbname='postgres')
    print('Connected to postgres OK')
    sys.exit(0)
except Exception as e:
    print('Type:', type(e).__name__)
    print('Args:', e.args)
    print('Repr:', repr(e))
    print('PGError:', getattr(e, 'pgerror', None))
    diag = getattr(e, 'diag', None)
    if diag:
        try:
            print('diag.message_primary:', getattr(diag, 'message_primary', None))
            print('diag.message_detail:', getattr(diag, 'message_detail', None))
            print('diag.sqlstate:', getattr(diag, 'sqlstate', None))
            print('diag.severity:', getattr(diag, 'severity', None))
        except Exception:
            pass
    sys.exit(1)

print('Connecting...')
try:
    conn = psycopg2.connect(host='127.0.0.1', port=5432, user='postgres', password='postgres', dbname='hacknu_job_portal')
    print('Connected OK')
    sys.exit(0)
except Exception as e:
    print('Type:', type(e).__name__)
    print('Args:', e.args)
    print('Repr:', repr(e))
    print('PGError:', getattr(e, 'pgerror', None))
    diag = getattr(e, 'diag', None)
    if diag:
        try:
            print('diag.message_primary:', getattr(diag, 'message_primary', None))
            print('diag.message_detail:', getattr(diag, 'message_detail', None))
            print('diag.sqlstate:', getattr(diag, 'sqlstate', None))
            print('diag.severity:', getattr(diag, 'severity', None))
        except Exception:
            pass
    sys.exit(1)
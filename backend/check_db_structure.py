import pg8000

def check_database_structure():
    try:
        conn = pg8000.connect(host='localhost', port=5432, database='hacknu_job_portal', user='postgres', password='12345')
        cursor = conn.cursor()
        cursor.execute("SELECT proname FROM pg_proc WHERE proname = 'update_updated_at_column'")
        function_exists = cursor.fetchall()
        print('Function exists:', function_exists)
        cursor.execute("\n            SELECT column_name, data_type \n            FROM information_schema.columns \n            WHERE table_name = 'smartbot_sessions' \n            ORDER BY ordinal_position\n        ")
        columns = cursor.fetchall()
        print('SmartBot sessions columns:', columns)
        cursor.execute("\n            SELECT trigger_name, event_manipulation, action_statement \n            FROM information_schema.triggers \n            WHERE event_object_table = 'smartbot_sessions'\n        ")
        triggers = cursor.fetchall()
        print('SmartBot sessions triggers:', triggers)
        conn.close()
    except Exception as e:
        print(f'Error: {e}')
if __name__ == '__main__':
    check_database_structure()

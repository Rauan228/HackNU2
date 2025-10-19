import pg8000

def check_database_structure():
    try:
        conn = pg8000.connect(
            host='localhost', 
            port=5432, 
            database='hacknu_job_portal', 
            user='postgres', 
            password='12345'
        )
        cursor = conn.cursor()

        # Check if the function exists
        cursor.execute("SELECT proname FROM pg_proc WHERE proname = 'update_updated_at_column'")
        function_exists = cursor.fetchall()
        print('Function exists:', function_exists)

        # Check table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'smartbot_sessions' 
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print('SmartBot sessions columns:', columns)

        # Check if triggers exist
        cursor.execute("""
            SELECT trigger_name, event_manipulation, action_statement 
            FROM information_schema.triggers 
            WHERE event_object_table = 'smartbot_sessions'
        """)
        triggers = cursor.fetchall()
        print('SmartBot sessions triggers:', triggers)

        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database_structure()
import pg8000

def fix_smartbot_table():
    try:
        conn = pg8000.connect(
            host='localhost', 
            port=5432, 
            database='hacknu_job_portal', 
            user='postgres', 
            password='12345'
        )
        cursor = conn.cursor()

        print("Fixing smartbot_sessions table structure...")

        # Add missing columns
        try:
            cursor.execute("""
                ALTER TABLE smartbot_sessions 
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            """)
            print("Added created_at column")
        except Exception as e:
            print(f"Error adding created_at: {e}")

        try:
            cursor.execute("""
                ALTER TABLE smartbot_sessions 
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            """)
            print("Added updated_at column")
        except Exception as e:
            print(f"Error adding updated_at: {e}")

        # Update existing rows
        try:
            cursor.execute("""
                UPDATE smartbot_sessions 
                SET created_at = COALESCE(started_at, NOW()),
                    updated_at = COALESCE(started_at, NOW())
                WHERE created_at IS NULL OR updated_at IS NULL
            """)
            print("Updated existing rows with timestamps")
        except Exception as e:
            print(f"Error updating rows: {e}")

        # Recreate trigger
        try:
            cursor.execute("DROP TRIGGER IF EXISTS trg_smartbot_sessions_updated ON smartbot_sessions")
            cursor.execute("""
                CREATE TRIGGER trg_smartbot_sessions_updated 
                    BEFORE UPDATE ON smartbot_sessions
                    FOR EACH ROW 
                    EXECUTE FUNCTION update_updated_at_column()
            """)
            print("Recreated trigger")
        except Exception as e:
            print(f"Error with trigger: {e}")

        # Commit changes
        conn.commit()

        # Verify the table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'smartbot_sessions' 
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print("\nUpdated table structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")

        conn.close()
        print("\nSmartBot table structure fixed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_smartbot_table()
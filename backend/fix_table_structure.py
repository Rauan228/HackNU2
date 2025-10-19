import pg8000

def fix_smartbot_table():
    try:
        conn = pg8000.connect(host='localhost', port=5432, database='hacknu_job_portal', user='postgres', password='12345')
        cursor = conn.cursor()
        print('Fixing smartbot_sessions table structure...')
        try:
            cursor.execute('\n                ALTER TABLE smartbot_sessions \n                ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()\n            ')
            print('Added created_at column')
        except Exception as e:
            print(f'Error adding created_at: {e}')
        try:
            cursor.execute('\n                ALTER TABLE smartbot_sessions \n                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()\n            ')
            print('Added updated_at column')
        except Exception as e:
            print(f'Error adding updated_at: {e}')
        try:
            cursor.execute('\n                UPDATE smartbot_sessions \n                SET created_at = COALESCE(started_at, NOW()),\n                    updated_at = COALESCE(started_at, NOW())\n                WHERE created_at IS NULL OR updated_at IS NULL\n            ')
            print('Updated existing rows with timestamps')
        except Exception as e:
            print(f'Error updating rows: {e}')
        try:
            cursor.execute('DROP TRIGGER IF EXISTS trg_smartbot_sessions_updated ON smartbot_sessions')
            cursor.execute('\n                CREATE TRIGGER trg_smartbot_sessions_updated \n                    BEFORE UPDATE ON smartbot_sessions\n                    FOR EACH ROW \n                    EXECUTE FUNCTION update_updated_at_column()\n            ')
            print('Recreated trigger')
        except Exception as e:
            print(f'Error with trigger: {e}')
        conn.commit()
        cursor.execute("\n            SELECT column_name, data_type, is_nullable, column_default\n            FROM information_schema.columns \n            WHERE table_name = 'smartbot_sessions' \n            ORDER BY ordinal_position\n        ")
        columns = cursor.fetchall()
        print('\nUpdated table structure:')
        for col in columns:
            print(f'  {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})')
        conn.close()
        print('\nSmartBot table structure fixed successfully!')
    except Exception as e:
        print(f'Error: {e}')
if __name__ == '__main__':
    fix_smartbot_table()

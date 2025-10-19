import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2

# Direct connection string
DATABASE_URL = "postgresql://postgres:12345@localhost:5432/hacknu_job_portal"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("=== SMARTBOT_SESSIONS TABLE STRUCTURE ===")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'smartbot_sessions' 
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
    
    print("\n=== SMARTBOT_MESSAGES TABLE STRUCTURE ===")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'smartbot_messages' 
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
    print("\n=== CANDIDATE_ANALYSES TABLE STRUCTURE ===")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'candidate_analyses' 
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
    print("\n=== ANALYSIS_CATEGORIES TABLE STRUCTURE ===")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'analysis_categories' 
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
    print("\n=== FOREIGN KEY CONSTRAINTS ===")
    cursor.execute("""
        SELECT 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' 
        AND tc.table_name IN ('smartbot_sessions', 'smartbot_messages', 'candidate_analyses', 'analysis_categories')
        ORDER BY tc.table_name, kcu.column_name
    """)
    fks = cursor.fetchall()
    for fk in fks:
        print(f"  {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]}")
        
    conn.close()
    
except Exception as e:
    print(f"Database error: {e}")
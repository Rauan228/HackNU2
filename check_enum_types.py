#!/usr/bin/env python3
"""
Проверка enum типов в PostgreSQL для SmartBot
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import psycopg2
from core.config import settings

def check_enum_types():
    try:
        # Подключение к БД - используем pg8000 напрямую
        import pg8000
        conn = pg8000.connect(
            user='postgres',
            password='12345',
            host='localhost',
            port=5432,
            database='hacknu_job_portal'
        )
        cursor = conn.cursor()
        
        print("=== ENUM TYPES ===")
        cursor.execute("""
            SELECT t.typname, e.enumlabel 
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid 
            WHERE t.typname LIKE '%smartbot%' OR t.typname LIKE '%message%'
            ORDER BY t.typname, e.enumsortorder
        """)
        enums = cursor.fetchall()
        
        if enums:
            current_type = None
            for enum_type, enum_value in enums:
                if current_type != enum_type:
                    print(f"\n{enum_type}:")
                    current_type = enum_type
                print(f"  - {enum_value}")
        else:
            print("Enum типы не найдены")
        
        print("\n=== SMARTBOT_MESSAGES TABLE ===")
        cursor.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns 
            WHERE table_name = 'smartbot_messages'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        if columns:
            for col in columns:
                print(f"  {col[0]}: {col[1]} ({col[2]})")
        else:
            print("Таблица smartbot_messages не найдена")
        
        # Проверяем существующие записи
        print("\n=== SAMPLE DATA ===")
        cursor.execute("SELECT COUNT(*) FROM smartbot_messages")
        count = cursor.fetchone()[0]
        print(f"Записей в smartbot_messages: {count}")
        
        if count > 0:
            cursor.execute("""
                SELECT message_type, COUNT(*) 
                FROM smartbot_messages 
                GROUP BY message_type 
                ORDER BY COUNT(*) DESC
            """)
            types = cursor.fetchall()
            print("Типы сообщений:")
            for msg_type, cnt in types:
                print(f"  {msg_type}: {cnt}")
        
        conn.close()
        print("\n✅ Проверка завершена успешно")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_enum_types()
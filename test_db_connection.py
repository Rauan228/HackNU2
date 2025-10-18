#!/usr/bin/env python3
"""
Скрипт для диагностики подключения к PostgreSQL
"""
import psycopg2
import sys
from psycopg2 import sql

def test_connection():
    """Тестирует подключение к PostgreSQL"""
    
    # Параметры подключения
    connection_params = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'postgres',
        'database': 'postgres'  # Подключаемся к системной БД
    }
    
    try:
        print("🔍 Тестирование подключения к PostgreSQL...")
        print(f"   Хост: {connection_params['host']}")
        print(f"   Порт: {connection_params['port']}")
        print(f"   Пользователь: {connection_params['user']}")
        print(f"   База данных: {connection_params['database']}")
        
        # Попытка подключения
        conn = psycopg2.connect(**connection_params)
        print("✅ Подключение к PostgreSQL успешно!")
        
        # Проверяем версию PostgreSQL
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"📊 Версия PostgreSQL: {version}")
        
        # Проверяем существование базы данных hacknu_job_portal
        cur.execute("SELECT datname FROM pg_database WHERE datname = %s", ('hacknu_job_portal',))
        db_exists = cur.fetchone()
        
        if db_exists:
            print("✅ База данных 'hacknu_job_portal' существует")
            
            # Подключаемся к целевой базе данных
            conn.close()
            connection_params['database'] = 'hacknu_job_portal'
            conn = psycopg2.connect(**connection_params)
            cur = conn.cursor()
            
            # Проверяем таблицы
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cur.fetchall()
            
            if tables:
                print(f"📋 Найдено таблиц: {len(tables)}")
                for table in tables:
                    print(f"   - {table[0]}")
                    
                # Проверяем таблицу users
                cur.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'users'
                    ORDER BY ordinal_position;
                """)
                user_columns = cur.fetchall()
                
                if user_columns:
                    print("👤 Структура таблицы 'users':")
                    for col in user_columns:
                        print(f"   - {col[0]}: {col[1]} (nullable: {col[2]})")
                else:
                    print("❌ Таблица 'users' не найдена")
            else:
                print("❌ Таблицы не найдены в базе данных")
        else:
            print("❌ База данных 'hacknu_job_portal' не существует")
            print("💡 Создание базы данных...")
            
            # Создаем базу данных
            conn.autocommit = True
            cur.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier('hacknu_job_portal')
            ))
            print("✅ База данных 'hacknu_job_portal' создана")
        
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        print("\n🔧 Возможные решения:")
        print("1. Убедитесь, что PostgreSQL запущен")
        print("2. Проверьте правильность пароля пользователя 'postgres'")
        print("3. Убедитесь, что PostgreSQL слушает на порту 5432")
        print("4. Проверьте настройки pg_hba.conf для локальных подключений")
        return False
        
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
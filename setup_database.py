#!/usr/bin/env python3
"""
Скрипт для настройки базы данных PostgreSQL для HackNU SmartBot
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from pathlib import Path

def create_database():
    """Создает базу данных если она не существует"""
    try:
        # Подключаемся к PostgreSQL (к базе postgres по умолчанию)
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="password",  # Изменил пароль
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Проверяем существует ли база данных
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='jobboard'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Создаю базу данных 'jobboard'...")
            cursor.execute("CREATE DATABASE jobboard")
            print("✅ База данных 'jobboard' создана успешно!")
        else:
            print("✅ База данных 'jobboard' уже существует")
            
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Ошибка при создании базы данных: {e}")
        print("💡 Попробуйте:")
        print("   - Проверить что PostgreSQL запущен")
        print("   - Проверить пароль пользователя postgres")
        print("   - Изменить пароль в скрипте setup_database.py")
        return False
    
    return True

def run_sql_script(script_path):
    """Выполняет SQL скрипт"""
    try:
        # Подключаемся к нашей базе данных
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="password",  # Изменил пароль
            database="jobboard"
        )
        cursor = conn.cursor()
        
        # Читаем и выполняем SQL скрипт
        with open(script_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
            
        cursor.execute(sql_script)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f"✅ SQL скрипт {script_path} выполнен успешно!")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Ошибка при выполнении SQL скрипта {script_path}: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Файл {script_path} не найден!")
        return False

def main():
    """Основная функция настройки базы данных"""
    print("🚀 Настройка базы данных для HackNU SmartBot...")
    
    # Создаем базу данных
    if not create_database():
        return
    
    # Путь к SQL скриптам
    backend_dir = Path(__file__).parent / "backend"
    sql_dir = backend_dir / "sql"
    
    # Выполняем скрипты создания таблиц
    create_tables_script = sql_dir / "create_tables.sql"
    if create_tables_script.exists():
        print("Создаю таблицы...")
        if not run_sql_script(create_tables_script):
            return
    else:
        print(f"❌ Файл {create_tables_script} не найден!")
        return
    
    # Выполняем скрипт с тестовыми данными (если есть)
    seed_script = sql_dir / "insert_seed.sql"
    if seed_script.exists():
        print("Добавляю тестовые данные...")
        if not run_sql_script(seed_script):
            return
    else:
        print("⚠️ Файл с тестовыми данными не найден, пропускаю...")
    
    print("🎉 База данных настроена успешно!")
    print("\n📋 Следующие шаги:")
    print("1. Убедитесь что PostgreSQL запущен")
    print("2. Установите зависимости: pip install -r requirements.txt")
    print("3. Запустите backend: cd backend && python -m uvicorn main:app --reload")

if __name__ == "__main__":
    main()
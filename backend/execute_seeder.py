import sqlite3
import os

# Подключение к базе данных
db_path = 'hacknu_smartbot.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Читаем и выполняем SQL-сидер
    with open('sql/realistic_jobs_seed.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Выполняем SQL команды
    cursor.executescript(sql_content)
    conn.commit()
    
    # Проверяем количество добавленных вакансий
    cursor.execute('SELECT COUNT(*) FROM jobs')
    total_jobs = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE user_type = "employer"')
    total_employers = cursor.fetchone()[0]
    
    print('✅ Сидер успешно выполнен!')
    print(f'📊 Общее количество вакансий в БД: {total_jobs}')
    print(f'👥 Общее количество работодателей: {total_employers}')
    
    # Показываем примеры добавленных вакансий по категориям
    cursor.execute('SELECT title, company_name, location FROM jobs WHERE title LIKE "%разработчик%" OR title LIKE "%DevOps%" OR title LIKE "%Data%" LIMIT 5')
    it_jobs = cursor.fetchall()
    print('\n💻 ИТ вакансии:')
    for job in it_jobs:
        print(f'  - {job[0]} в {job[1]} ({job[2]})')
    
    cursor.execute('SELECT title, company_name, location FROM jobs WHERE title LIKE "%Контент%" OR title LIKE "%Переводчик%" OR title LIKE "%HR%" OR title LIKE "%Журналист%" OR title LIKE "%Психолог%" LIMIT 5')
    humanities_jobs = cursor.fetchall()
    print('\n📚 Гуманитарные вакансии:')
    for job in humanities_jobs:
        print(f'  - {job[0]} в {job[1]} ({job[2]})')
    
    cursor.execute('SELECT title, company_name, location FROM jobs WHERE title LIKE "%юрист%" OR title LIKE "%Юрист%" LIMIT 5')
    legal_jobs = cursor.fetchall()
    print('\n⚖️ Юридические вакансии:')
    for job in legal_jobs:
        print(f'  - {job[0]} в {job[1]} ({job[2]})')
    
    conn.close()
else:
    print('❌ База данных не найдена. Убедитесь, что сервер запущен и БД создана.')
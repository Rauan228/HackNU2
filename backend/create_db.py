from sqlalchemy import create_engine, text
from core.db import Base, engine
from models.users import User, UserType
from models.jobs import Job
from models.resumes import Resume
from models.applications import JobApplication

def create_database():
    print('Создание таблиц...')
    Base.metadata.create_all(bind=engine)
    print('Таблицы созданы успешно!')
    with engine.connect() as conn:
        result = conn.execute(text("\n            SELECT table_name \n            FROM information_schema.tables \n            WHERE table_schema = 'public'\n            ORDER BY table_name;\n        "))
        print('\nСозданные таблицы:')
        for row in result:
            print(f'  - {row[0]}')
        constraints = conn.execute(text("\n            SELECT constraint_name, check_clause \n            FROM information_schema.check_constraints \n            WHERE constraint_name LIKE '%user_type%';\n        "))
        print('\nОграничения для user_type:')
        for row in constraints:
            print(f'  {row[0]}: {row[1]}')
if __name__ == '__main__':
    create_database()

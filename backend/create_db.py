from sqlalchemy import create_engine, text
from core.db import Base, engine
from models.users import User, UserType
from models.jobs import Job
from models.resumes import Resume
from models.applications import JobApplication

def create_database():
    """Создает базу данных и все таблицы"""
    
    # Создаем все таблицы
    print("Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы созданы успешно!")
    
    # Проверяем созданные таблицы
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        
        print("\nСозданные таблицы:")
        for row in result:
            print(f"  - {row[0]}")
        
        # Проверяем ограничения для user_type
        constraints = conn.execute(text("""
            SELECT constraint_name, check_clause 
            FROM information_schema.check_constraints 
            WHERE constraint_name LIKE '%user_type%';
        """))
        
        print("\nОграничения для user_type:")
        for row in constraints:
            print(f"  {row[0]}: {row[1]}")

if __name__ == "__main__":
    create_database()
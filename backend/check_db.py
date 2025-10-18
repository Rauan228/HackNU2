from sqlalchemy import create_engine, text
from core.config import settings

def check_users_table():
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Проверяем структуру таблицы users
        result = conn.execute(text("""
            SELECT column_name, data_type, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position;
        """))
        
        print("Структура таблицы users:")
        for row in result:
            print(f"  {row[0]}: {row[1]} (default: {row[2]})")
        
        # Проверяем ограничения на таблице users
        constraints_result = conn.execute(text("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'users';
        """))
        
        print("\nОграничения таблицы users:")
        for row in constraints_result:
            print(f"  {row[0]}: {row[1]}")
        
        # Проверяем конкретное ограничение user_type_check
        check_constraint = conn.execute(text("""
            SELECT check_clause 
            FROM information_schema.check_constraints 
            WHERE constraint_name = 'users_user_type_check';
        """))
        
        print("\nОграничение users_user_type_check:")
        for row in check_constraint:
            print(f"  {row[0]}")

if __name__ == "__main__":
    check_users_table()
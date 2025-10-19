from sqlalchemy import create_engine, text
from core.config import settings

def check_users_table():
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        result = conn.execute(text("\n            SELECT column_name, data_type, column_default \n            FROM information_schema.columns \n            WHERE table_name = 'users' \n            ORDER BY ordinal_position;\n        "))
        print('Структура таблицы users:')
        for row in result:
            print(f'  {row[0]}: {row[1]} (default: {row[2]})')
        constraints_result = conn.execute(text("\n            SELECT constraint_name, constraint_type \n            FROM information_schema.table_constraints \n            WHERE table_name = 'users';\n        "))
        print('\nОграничения таблицы users:')
        for row in constraints_result:
            print(f'  {row[0]}: {row[1]}')
        check_constraint = conn.execute(text("\n            SELECT check_clause \n            FROM information_schema.check_constraints \n            WHERE constraint_name = 'users_user_type_check';\n        "))
        print('\nОграничение users_user_type_check:')
        for row in check_constraint:
            print(f'  {row[0]}')
if __name__ == '__main__':
    check_users_table()

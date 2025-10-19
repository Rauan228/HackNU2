# HackNU SmartBot - Быстрый старт

## Минимальные шаги для запуска

### 1. Установка зависимостей

#### Backend
```bash
# Создайте и активируйте виртуальное окружение
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Установите зависимости
pip install -r requirements_updated.txt
```

#### Frontend
```bash
cd frontend
npm install
```

### 2. Настройка базы данных

```bash
# Создайте базу данных PostgreSQL
createdb hacknu_smartbot

# Выполните SQL скрипт
psql -d hacknu_smartbot -f FULL_DATABASE_SETUP.sql
```

### 3. Настройка переменных окружения

Создайте файл `.env`:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/hacknu_smartbot
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
```

### 4. Запуск

#### Backend (терминал 1)
```bash
python run_backend.py
```

#### Frontend (терминал 2)
```bash
cd frontend
npm run dev
```

### 5. Доступ к приложению

- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Основные библиотеки для установки

### Backend Python пакеты:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
pydantic==2.5.0
openai==1.3.7
```

### Frontend Node.js пакеты:
```
react
react-dom
typescript
vite
tailwindcss
axios
react-router-dom
```

## SQL для базы данных

Используйте файл `FULL_DATABASE_SETUP.sql` который содержит:
- Создание всех необходимых таблиц
- Настройка ENUM типов
- Создание индексов и триггеров
- Тестовые данные

Этот файл учитывает все изменения, включая исправления enum типов для SmartBot функциональности.
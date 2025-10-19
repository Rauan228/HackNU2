# HackNU SmartBot - Полное руководство по установке

## Обзор проекта
HackNU SmartBot - это веб-приложение для анализа резюме и подбора кандидатов с использованием ИИ. Проект состоит из:
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL

## Предварительные требования

### Системные требования
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Git

### Установка системных зависимостей

#### Windows
```bash
# Установите Python с официального сайта: https://python.org
# Установите Node.js с официального сайта: https://nodejs.org
# Установите PostgreSQL: https://www.postgresql.org/download/windows/
```

#### macOS
```bash
brew install python node postgresql
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip nodejs npm postgresql postgresql-contrib
```

## Установка проекта

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd HackNUSmartBot
```

### 2. Настройка базы данных

#### Создание базы данных
```bash
# Войдите в PostgreSQL
psql -U postgres

# Создайте базу данных и пользователя
CREATE DATABASE hacknu_smartbot;
CREATE USER smartbot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE hacknu_smartbot TO smartbot_user;
\q
```

#### Инициализация схемы базы данных
```bash
# Выполните SQL скрипт для создания таблиц
psql -U smartbot_user -d hacknu_smartbot -f FULL_DATABASE_SETUP.sql
```

### 3. Настройка Backend

#### Создание виртуального окружения
```bash
# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### Установка зависимостей
```bash
# Установите все зависимости
pip install -r requirements_updated.txt
```

#### Настройка переменных окружения
Создайте файл `.env` в корневой директории:
```env
# Database
DATABASE_URL=postgresql://smartbot_user:your_password@localhost:5432/hacknu_smartbot

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (если используется)
OPENAI_API_KEY=your-openai-api-key

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### 4. Настройка Frontend

#### Установка зависимостей
```bash
cd frontend
npm install
```

#### Настройка переменных окружения
Создайте файл `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Запуск проекта

### 1. Запуск Backend
```bash
# Из корневой директории проекта
python run_backend.py
```
Backend будет доступен по адресу: http://localhost:8000
API документация: http://localhost:8000/docs

### 2. Запуск Frontend
```bash
# В новом терминале, из директории frontend
cd frontend
npm run dev
```
Frontend будет доступен по адресу: http://localhost:5174

## Структура проекта

```
HackNUSmartBot/
├── backend/                 # Backend код
│   ├── services/           # Бизнес-логика
│   ├── models/             # SQLAlchemy модели
│   ├── schemas/            # Pydantic схемы
│   ├── sql/                # SQL скрипты
│   └── ...
├── frontend/               # Frontend код
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   ├── pages/          # Страницы
│   │   └── ...
├── requirements_updated.txt # Python зависимости
├── FULL_DATABASE_SETUP.sql # SQL для инициализации БД
├── .env                    # Переменные окружения
└── run_backend.py          # Запуск backend сервера
```

## Основные библиотеки

### Backend (Python)
- **fastapi**: Веб-фреймворк
- **uvicorn**: ASGI сервер
- **sqlalchemy**: ORM для работы с БД
- **psycopg2-binary**: PostgreSQL драйвер
- **python-jose**: JWT токены
- **passlib**: Хеширование паролей
- **openai**: Интеграция с OpenAI API
- **pydantic**: Валидация данных

### Frontend (JavaScript/TypeScript)
- **react**: UI библиотека
- **typescript**: Типизация
- **vite**: Сборщик и dev сервер
- **tailwindcss**: CSS фреймворк
- **axios**: HTTP клиент
- **react-router-dom**: Маршрутизация

## Тестирование

### Backend тесты
```bash
# Установите тестовые зависимости (уже включены в requirements_updated.txt)
pytest
```

### Frontend тесты
```bash
cd frontend
npm test
```

## Развертывание

### Production настройки
1. Измените `DEBUG=False` в `.env`
2. Используйте production базу данных
3. Настройте CORS для production домена
4. Используйте HTTPS

### Docker (опционально)
Создайте `Dockerfile` для контейнеризации приложения.

## Устранение неполадок

### Частые проблемы

1. **Ошибка подключения к БД**
   - Проверьте, что PostgreSQL запущен
   - Проверьте правильность DATABASE_URL в .env

2. **Ошибки импорта Python**
   - Убедитесь, что виртуальное окружение активировано
   - Переустановите зависимости: `pip install -r requirements_updated.txt`

3. **Frontend не запускается**
   - Проверьте версию Node.js (должна быть 16+)
   - Удалите node_modules и переустановите: `rm -rf node_modules && npm install`

4. **CORS ошибки**
   - Убедитесь, что backend настроен для разрешения запросов с frontend домена

## Поддержка
Для получения помощи создайте issue в репозитории проекта.
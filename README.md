# HackNU SmartBot — Руководство по запуску

Проект состоит из двух частей:
- Frontend: React + Vite + TypeScript + Tailwind
- Backend: FastAPI + SQLAlchemy + PostgreSQL + WebSocket

Ниже — пошаговая инструкция по установке и запуску на Windows.

## Требования
- Node.js ≥ 18 и npm
- Python ≥ 3.10 и pip
- PostgreSQL ≥ 13 (локально)

## Backend — установка и запуск
1) Создайте файл `.env` в корне репозитория:
```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/hacknu_job_portal
SECRET_KEY=devsecret
OPENAI_API_KEY=<опционально>
```
2) Установите зависимости:
```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```
3) Создайте базу данных в PostgreSQL:
- Создайте БД `hacknu_job_portal`
- Примените схему:
```
psql -U postgres -h localhost -d hacknu_job_portal -f backend/sql/create_tables.sql
```
- (Опционально) Загрузите тестовые данные:
```
psql -U postgres -h localhost -d hacknu_job_portal -f backend/sql/extended_jobs_seed.sql
```
4) Запустите сервер:
```
python run_backend.py
```
- API: `http://localhost:8000/`
- Документация: `http://localhost:8000/docs`

## Frontend — установка и запуск
1) Создайте `frontend/.env` (или `.env.local`):
```
VITE_API_BASE_URL=http://localhost:8000
```
2) Установите зависимости и запустите dev-сервер:
```
cd frontend
npm install
npm run dev
```
- UI доступен на: `http://localhost:5173`

## Аутентификация и роли
- Зарегистрируйтесь через UI, затем выполните вход.
- Для функционала работодателя (`SmartBot`, отчёты) используйте роль `employer`.

## WebSocket (SmartBot)
- Используется `ws://localhost:8000/ws/employer/...` с токеном в query-параметре.
- Токен добавляется автоматически после входа. Убедитесь, что backend запущен.

## Частые проблемы и решения
- 401 при запросах: повторно выполните вход; проверьте токен в `localStorage`.
- `net::ERR_ABORTED` на фронтенде: проверьте `VITE_API_BASE_URL` и что бэкенд доступен.
- Ошибки БД: проверьте `DATABASE_URL` в `.env` и создание таблиц через `create_tables.sql`.

## Альтернатива: SQLite (быстрый старт)
Не рекомендуется для production. Вы можете указать в `.env`:
```
DATABASE_URL=sqlite:///backend/hacknu_smartbot.db
```
Учтите, что SQL-скрипты в `backend/sql/*.sql` рассчитаны на PostgreSQL. Для SQLite таблицы придётся создавать через ORM вручную либо собственным SQL.

## Структура
- `backend/` — FastAPI, модели, схемы, сервисы
- `frontend/` — React + Vite, страницы, компоненты, сервисы
- `run_backend.py` — удобный запуск бэкенда

## Готово
Запустите backend, затем frontend и используйте UI на `http://localhost:5173`. Если возникнут вопросы — см. `/docs` бэкенда и раздел «Частые проблемы».
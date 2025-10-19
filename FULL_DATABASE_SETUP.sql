-- =========================================
-- ПОЛНАЯ ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ HackNU SmartBot
-- =========================================

-- Создание базы данных (выполнить от имени суперпользователя)
-- CREATE DATABASE hacknu_job_portal;
-- \c hacknu_job_portal;

-- 1) Утилита для updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =========================
-- ENUM ТИПЫ
-- =========================

-- Enum для ролей сообщений
CREATE TYPE messagerole AS ENUM ('system', 'assistant', 'candidate');

-- Enum для типов SmartBot сообщений
CREATE TYPE smartbotmessagetype AS ENUM ('question', 'answer', 'info', 'completion');

-- Enum для статусов SmartBot сессий
CREATE TYPE smartbotsessionstatus AS ENUM ('active', 'completed', 'error');

-- Enum для статусов анализа
CREATE TYPE analysisstatus AS ENUM ('pending', 'in_progress', 'completed', 'error');

-- =========================
-- USERS
-- =========================
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    phone           VARCHAR(50),
    user_type       VARCHAR(20) NOT NULL CHECK (user_type IN ('job_seeker','employer')),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
DROP TRIGGER IF EXISTS trg_users_updated ON users;
CREATE TRIGGER trg_users_updated BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =========================
-- JOBS
-- =========================
CREATE TABLE IF NOT EXISTS jobs (
    id               SERIAL PRIMARY KEY,
    employer_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title            VARCHAR(255) NOT NULL,
    description      TEXT NOT NULL,
    requirements     TEXT,
    location         VARCHAR(255),
    employment_type  VARCHAR(20) CHECK (employment_type IN ('full_time','part_time','contract','internship')),
    experience_level VARCHAR(20) CHECK (experience_level IN ('junior','middle','senior')),
    salary_min       NUMERIC(12,2),
    salary_max       NUMERIC(12,2),
    salary_currency  VARCHAR(10) DEFAULT 'KZT',
    company_name     VARCHAR(255),
    remote_work      BOOLEAN DEFAULT FALSE,
    is_active        BOOLEAN DEFAULT TRUE,
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_jobs_employer_id ON jobs(employer_id);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_employment_type ON jobs(employment_type);
CREATE INDEX IF NOT EXISTS idx_jobs_experience_level ON jobs(experience_level);
DROP TRIGGER IF EXISTS trg_jobs_updated ON jobs;
CREATE TRIGGER trg_jobs_updated BEFORE UPDATE ON jobs
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =========================
-- RESUMES
-- =========================
CREATE TABLE IF NOT EXISTS resumes (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title            VARCHAR(255) NOT NULL,
    summary          TEXT,
    experience       TEXT,
    education        TEXT,
    skills           TEXT,
    languages        TEXT,
    portfolio_url    VARCHAR(500),
    desired_position VARCHAR(255),
    desired_salary   NUMERIC(12,2),
    location         VARCHAR(255),
    is_public        BOOLEAN DEFAULT TRUE,
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
DROP TRIGGER IF EXISTS trg_resumes_updated ON resumes;
CREATE TRIGGER trg_resumes_updated BEFORE UPDATE ON resumes
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =========================
-- JOB APPLICATIONS
-- =========================
CREATE TABLE IF NOT EXISTS job_applications (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id        INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    resume_id     INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    cover_letter  TEXT,
    status        VARCHAR(20) NOT NULL DEFAULT 'pending'
                   CHECK (status IN ('pending','in_review','accepted','rejected')),
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (user_id, job_id)
);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON job_applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON job_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON job_applications(status);
DROP TRIGGER IF EXISTS trg_job_applications_updated ON job_applications;
CREATE TRIGGER trg_job_applications_updated BEFORE UPDATE ON job_applications
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =========================
-- SMARTBOT SESSIONS
-- =========================
CREATE TABLE IF NOT EXISTS smartbot_sessions (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL UNIQUE REFERENCES job_applications(id) ON DELETE CASCADE,
    status smartbotsessionstatus NOT NULL DEFAULT 'active',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_smartbot_sessions_application_id ON smartbot_sessions(application_id);
DROP TRIGGER IF EXISTS trg_smartbot_sessions_updated ON smartbot_sessions;
CREATE TRIGGER trg_smartbot_sessions_updated BEFORE UPDATE ON smartbot_sessions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =========================
-- SMARTBOT MESSAGES
-- =========================
CREATE TABLE IF NOT EXISTS smartbot_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES smartbot_sessions(id) ON DELETE CASCADE,
    message_type smartbotmessagetype NOT NULL,
    content TEXT NOT NULL,
    message_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_smartbot_messages_session_id ON smartbot_messages(session_id);

-- =========================
-- CANDIDATE ANALYSES
-- =========================
CREATE TABLE IF NOT EXISTS candidate_analyses (
    id SERIAL PRIMARY KEY,
    smartbot_session_id INTEGER NOT NULL UNIQUE REFERENCES smartbot_sessions(id) ON DELETE CASCADE,
    initial_score FLOAT,
    relevance_score FLOAT,
    status analysisstatus NOT NULL DEFAULT 'pending',
    strengths JSONB,
    weaknesses JSONB,
    missing_requirements JSONB,
    clarifications_received JSONB,
    summary TEXT,
    recommendation VARCHAR(50),
    questions_asked INTEGER DEFAULT 0,
    questions_answered INTEGER DEFAULT 0,
    analysis_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_candidate_analyses_session_id ON candidate_analyses(smartbot_session_id);
DROP TRIGGER IF EXISTS trg_candidate_analyses_updated ON candidate_analyses;
CREATE TRIGGER trg_candidate_analyses_updated BEFORE UPDATE ON candidate_analyses
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =========================
-- ANALYSIS CATEGORIES
-- =========================
CREATE TABLE IF NOT EXISTS analysis_categories (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER NOT NULL REFERENCES candidate_analyses(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    details TEXT,
    score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_analysis_categories_analysis_id ON analysis_categories(analysis_id);

-- =========================
-- AI CHAT SESSIONS (Legacy - для совместимости)
-- =========================
CREATE TABLE IF NOT EXISTS ai_chat_sessions (
    id               SERIAL PRIMARY KEY,
    application_id   INTEGER NOT NULL UNIQUE REFERENCES job_applications(id) ON DELETE CASCADE,
    lang             VARCHAR(2) NOT NULL CHECK (lang IN ('ru','kk')),
    model            VARCHAR(64) NOT NULL DEFAULT 'gpt-4o-mini',
    started_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at     TIMESTAMP WITH TIME ZONE,
    is_completed     BOOLEAN NOT NULL DEFAULT FALSE,
    relevance_score  NUMERIC(5,2),
    summary_text     TEXT,
    reasons_json     JSONB,
    transcript_cache TEXT,
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ai_sessions_relevance ON ai_chat_sessions(relevance_score);
DROP TRIGGER IF EXISTS trg_ai_sessions_updated ON ai_chat_sessions;
CREATE TRIGGER trg_ai_sessions_updated BEFORE UPDATE ON ai_chat_sessions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =========================
-- AI CHAT MESSAGES (Legacy - для совместимости)
-- =========================
CREATE TABLE IF NOT EXISTS ai_chat_messages (
    id          SERIAL PRIMARY KEY,
    session_id  INTEGER NOT NULL REFERENCES ai_chat_sessions(id) ON DELETE CASCADE,
    role        messagerole NOT NULL,
    content     TEXT NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ai_messages_session_time ON ai_chat_messages(session_id, created_at);

-- =========================
-- ПРЕДСТАВЛЕНИЯ
-- =========================
CREATE OR REPLACE VIEW employer_applications_view AS
SELECT 
    ja.id as application_id,
    ja.job_id,
    j.title as job_title,
    ja.user_id as candidate_id,
    u.full_name as candidate_name,
    u.email as candidate_email,
    ja.status,
    ja.cover_letter,
    ja.created_at as applied_at,
    r.title as resume_title,
    acs.relevance_score,
    acs.summary_text,
    acs.is_completed as chat_completed
FROM job_applications ja
JOIN jobs j ON ja.job_id = j.id
JOIN users u ON ja.user_id = u.id
LEFT JOIN resumes r ON ja.resume_id = r.id
LEFT JOIN ai_chat_sessions acs ON ja.id = acs.application_id;

-- =========================
-- ТЕСТОВЫЕ ДАННЫЕ
-- =========================

-- Пользователи (пароль: secret)
INSERT INTO users (email, hashed_password, full_name, phone, user_type) VALUES
('employer1@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Айгуль Нурланова', '+7 701 123 4567', 'employer'),
('employer2@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Данияр Касымов', '+7 702 987 6543', 'employer'),
('jobseeker1@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Асель Токтарова', '+7 705 111 2233', 'job_seeker'),
('jobseeker2@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Ерлан Жумабеков', '+7 707 444 5566', 'job_seeker');

-- Вакансии
INSERT INTO jobs (employer_id, title, description, requirements, location, employment_type, experience_level, salary_min, salary_max, company_name, remote_work) VALUES
(1, 'Frontend разработчик React', 
 'Ищем опытного Frontend разработчика для работы над современными веб-приложениями.',
 'Опыт работы с React 2+ года, знание TypeScript, HTML5, CSS3, опыт работы с REST API',
 'Алматы', 'full_time', 'middle', 350000.00, 500000.00, 'TechCorp KZ', false),

(1, 'Backend разработчик Python', 
 'Требуется Backend разработчик для создания высоконагруженных API и микросервисов.',
 'Python 3.8+, FastAPI/Django, PostgreSQL, Docker, опыт с облачными платформами',
 'Нур-Султан', 'full_time', 'senior', 500000.00, 700000.00, 'TechCorp KZ', true),

(2, 'Fullstack разработчик', 
 'Ищем универсального разработчика для работы над полным циклом разработки веб-приложений.',
 'React, Node.js/Python, базы данных, опыт DevOps будет плюсом',
 'Алматы', 'full_time', 'middle', 400000.00, 600000.00, 'StartupHub', false);

-- Резюме
INSERT INTO resumes (user_id, title, summary, experience, education, skills, languages, desired_position, desired_salary, location) VALUES
(3, 'Frontend разработчик React/TypeScript',
 'Опытный frontend разработчик с 3+ годами коммерческого опыта разработки современных веб-приложений.',
 'ТОО "WebStudio" (2021-2024) - Frontend разработчик. Разработка SPA на React/TypeScript.',
 'КазНТУ им. К.И. Сатпаева, Информационные системы, Бакалавр (2016-2020)',
 'React, TypeScript, JavaScript, HTML5, CSS3, SASS, Redux, Next.js, Webpack, Git',
 'Казахский (родной), Русский (свободно), Английский (B2)',
 'Frontend разработчик', 400000.00, 'Алматы'),

(4, 'Fullstack разработчик Python/React',
 'Универсальный разработчик с опытом работы как с frontend, так и с backend технологиями.',
 'ТОО "TechSolutions" (2022-2024) - Fullstack разработчик. Разработка веб-приложений на Python/Django + React.',
 'КБТУ, Компьютерные науки, Бакалавр (2017-2021)',
 'Python, Django, FastAPI, React, JavaScript, PostgreSQL, Docker, AWS, Git, Linux',
 'Казахский (родной), Русский (свободно), Английский (B2+)',
 'Fullstack разработчик', 500000.00, 'Нур-Султан');

-- Отклики
INSERT INTO job_applications (user_id, job_id, resume_id, cover_letter, status) VALUES
(3, 1, 1, 'Здравствуйте! Меня заинтересовала ваша вакансия Frontend разработчика. У меня есть опыт работы с React и TypeScript, который идеально подходит для данной позиции.', 'pending'),
(4, 2, 2, 'Добрый день! Хочу откликнуться на вакансию Backend разработчика. Имею опыт работы с Python, FastAPI и PostgreSQL.', 'pending');

-- Завершение
COMMIT;
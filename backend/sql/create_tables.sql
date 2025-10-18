-- =========================================
-- Minimal Job Board + SmartBot (PostgreSQL)
-- =========================================

-- 1) утилита для updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =========================
-- USERS
-- =========================
-- одна таблица пользователей с типом: соискатель / работодатель(рекрутер)
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
-- вакансии привязываем напрямую к employer (users.id)
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
    remote_work      BOOLEAN DEFAULT FALSE,
    is_active        BOOLEAN DEFAULT TRUE,
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_jobs_employer_id ON jobs(employer_id);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_is_active ON jobs(is_active);
DROP TRIGGER IF EXISTS trg_jobs_updated ON jobs;
CREATE TRIGGER trg_jobs_updated BEFORE UPDATE ON jobs
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =========================
-- RESUMES
-- =========================
-- простая «плоская» модель резюме (без разнормализации)
CREATE TABLE IF NOT EXISTS resumes (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title            VARCHAR(255) NOT NULL,
    summary          TEXT,
    experience       TEXT,           -- произвольный текст: опыт
    education        TEXT,           -- произвольный текст: образование
    skills           TEXT,           -- запятая/JSON по желанию
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
-- APPLICATIONS (отклики)
-- =========================
-- связь соискатель ↔ вакансия, + статус и сопроводительное
CREATE TABLE IF NOT EXISTS job_applications (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,   -- кандидат
    job_id        INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    resume_id     INTEGER REFERENCES resumes(id) ON DELETE SET NULL,
    cover_letter  TEXT,
    status        VARCHAR(20) NOT NULL DEFAULT 'pending'
                   CHECK (status IN ('pending','in_review','accepted','rejected')),
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (user_id, job_id)  -- 1 отклик на вакансию
);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON job_applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON job_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON job_applications(status);
DROP TRIGGER IF EXISTS trg_job_applications_updated ON job_applications;
CREATE TRIGGER trg_job_applications_updated BEFORE UPDATE ON job_applications
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =========================
-- SMARTBOT: СЕССИИ и СООБЩЕНИЯ
-- =========================
-- Сессия SmartBot создаётся на каждый отклик (1:1)
CREATE TABLE IF NOT EXISTS ai_chat_sessions (
    id               SERIAL PRIMARY KEY,
    application_id   INTEGER NOT NULL UNIQUE REFERENCES job_applications(id) ON DELETE CASCADE,
    lang             VARCHAR(2) NOT NULL CHECK (lang IN ('ru','kk')),
    model            VARCHAR(64) NOT NULL DEFAULT 'gpt-4o-mini',
    started_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at     TIMESTAMP WITH TIME ZONE,
    is_completed     BOOLEAN NOT NULL DEFAULT FALSE,
    relevance_score  NUMERIC(5,2),     -- 0..100
    summary_text     TEXT,             -- итоговая выжимка для работодателя
    reasons_json     JSONB,            -- { "experience": "...", "location": "...", ... } (опционально)
    transcript_cache TEXT,             -- сводка диалога (опционально для быстрого поиска)
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ai_sessions_relevance ON ai_chat_sessions(relevance_score);
DROP TRIGGER IF EXISTS trg_ai_sessions_updated ON ai_chat_sessions;
CREATE TRIGGER trg_ai_sessions_updated BEFORE UPDATE ON ai_chat_sessions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Сообщения диалога (хронологический лог)
CREATE TABLE IF NOT EXISTS ai_chat_messages (
    id          SERIAL PRIMARY KEY,
    session_id  INTEGER NOT NULL REFERENCES ai_chat_sessions(id) ON DELETE CASCADE,
    role        VARCHAR(16) NOT NULL CHECK (role IN ('system','assistant','candidate')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ai_messages_session_time ON ai_chat_messages(session_id, created_at);

-- =========================
-- УДОБНЫЕ ПРЕДСТАВЛЕНИЯ (для кабинета работодателя)
-- =========================

-- Список откликов с релевантностью и краткой информацией о кандидате
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
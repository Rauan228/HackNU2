-- SmartBot Tables for Job Application Analysis

-- SmartBot Sessions
CREATE TABLE IF NOT EXISTS smartbot_sessions (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL UNIQUE REFERENCES job_applications(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- SmartBot Messages
CREATE TABLE IF NOT EXISTS smartbot_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES smartbot_sessions(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    message_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Candidate Analysis
CREATE TABLE IF NOT EXISTS candidate_analyses (
    id SERIAL PRIMARY KEY,
    smartbot_session_id INTEGER NOT NULL UNIQUE REFERENCES smartbot_sessions(id) ON DELETE CASCADE,
    relevance_score FLOAT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
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

-- Analysis Categories
CREATE TABLE IF NOT EXISTS analysis_categories (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER NOT NULL REFERENCES candidate_analyses(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    details TEXT,
    score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_smartbot_sessions_application_id ON smartbot_sessions(application_id);
CREATE INDEX IF NOT EXISTS idx_smartbot_messages_session_id ON smartbot_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_candidate_analyses_session_id ON candidate_analyses(smartbot_session_id);
CREATE INDEX IF NOT EXISTS idx_analysis_categories_analysis_id ON analysis_categories(analysis_id);
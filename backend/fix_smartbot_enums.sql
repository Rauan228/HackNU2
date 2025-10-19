-- Fix SmartBot enum types and tables
-- This script creates the missing enum types and tables for SmartBot functionality

-- Create enum types
CREATE TYPE smartbotsessionstatus AS ENUM ('active', 'completed', 'abandoned', 'error');
CREATE TYPE smartbotmessagetype AS ENUM ('bot', 'user', 'system', 'question', 'info', 'answer', 'completion');
CREATE TYPE analysisstatus AS ENUM ('pending', 'in_progress', 'completed', 'failed');

-- Create SmartBot sessions table
CREATE TABLE IF NOT EXISTS smartbot_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    application_id INTEGER NOT NULL UNIQUE REFERENCES job_applications(id) ON DELETE CASCADE,
    status smartbotsessionstatus NOT NULL DEFAULT 'active',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_smartbot_sessions_session_id ON smartbot_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_smartbot_sessions_application_id ON smartbot_sessions(application_id);

-- Create SmartBot messages table
CREATE TABLE IF NOT EXISTS smartbot_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES smartbot_sessions(session_id) ON DELETE CASCADE,
    message_type smartbotmessagetype NOT NULL,
    content TEXT NOT NULL,
    message_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_smartbot_messages_session_id ON smartbot_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_smartbot_messages_created_at ON smartbot_messages(created_at);

-- Create candidate analyses table
CREATE TABLE IF NOT EXISTS candidate_analyses (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES smartbot_sessions(session_id) ON DELETE CASCADE,
    relevance_score NUMERIC(5,2),
    initial_score NUMERIC(5,2),
    final_score NUMERIC(5,2),
    status analysisstatus NOT NULL DEFAULT 'pending',
    strengths TEXT,
    weaknesses TEXT,
    missing_requirements TEXT,
    clarifications_received JSONB,
    summary TEXT,
    recommendation VARCHAR(50),
    questions_asked INTEGER DEFAULT 0,
    questions_answered INTEGER DEFAULT 0,
    analysis_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_candidate_analyses_session_id ON candidate_analyses(session_id);

-- Create analysis categories table
CREATE TABLE IF NOT EXISTS analysis_categories (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER NOT NULL REFERENCES candidate_analyses(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    status VARCHAR(50),
    score NUMERIC(5,2),
    details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analysis_categories_analysis_id ON analysis_categories(analysis_id);

-- Add triggers for updated_at
DROP TRIGGER IF EXISTS trg_smartbot_sessions_updated ON smartbot_sessions;
CREATE TRIGGER trg_smartbot_sessions_updated BEFORE UPDATE ON smartbot_sessions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_candidate_analyses_updated ON candidate_analyses;
CREATE TRIGGER trg_candidate_analyses_updated BEFORE UPDATE ON candidate_analyses
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
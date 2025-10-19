-- Fix smartbot_sessions table by adding missing columns
-- The table is missing created_at and updated_at columns that the trigger expects

-- Add missing columns to smartbot_sessions table
ALTER TABLE smartbot_sessions 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Update existing rows to have proper timestamps
UPDATE smartbot_sessions 
SET created_at = COALESCE(started_at, NOW()),
    updated_at = COALESCE(started_at, NOW())
WHERE created_at IS NULL OR updated_at IS NULL;

-- Recreate the trigger to ensure it works properly
DROP TRIGGER IF EXISTS trg_smartbot_sessions_updated ON smartbot_sessions;
CREATE TRIGGER trg_smartbot_sessions_updated 
    BEFORE UPDATE ON smartbot_sessions
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Verify the table structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'smartbot_sessions' 
ORDER BY ordinal_position;
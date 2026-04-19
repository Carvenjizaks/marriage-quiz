-- Marriage Quiz Database Schema for Supabase
-- Run this in the Supabase SQL Editor

-- Create the quiz_responses table
CREATE TABLE IF NOT EXISTS quiz_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location TEXT NOT NULL,
    pressure TEXT NOT NULL,
    financial_tension INTEGER NOT NULL CHECK (financial_tension BETWEEN 1 AND 10),
    impact_area TEXT NOT NULL,
    difficult_talks INTEGER NOT NULL CHECK (difficult_talks BETWEEN 1 AND 10),
    greatest_need TEXT NOT NULL,
    open_to_help TEXT NOT NULL,
    biggest_challenge TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add comment for documentation
COMMENT ON TABLE quiz_responses IS 'Stores responses from the marriage financial pressure quiz';

-- Create index on created_at for efficient sorting
CREATE INDEX IF NOT EXISTS idx_quiz_responses_created_at 
    ON quiz_responses(created_at DESC);

-- Create index on location for filtering
CREATE INDEX IF NOT EXISTS idx_quiz_responses_location 
    ON quiz_responses(location);

-- Enable Row Level Security
ALTER TABLE quiz_responses ENABLE ROW LEVEL SECURITY;

-- Policy: Allow anyone to insert (for quiz submissions)
CREATE POLICY "Allow anonymous inserts" 
    ON quiz_responses 
    FOR INSERT 
    TO anon, authenticated 
    WITH CHECK (true);

-- Policy: Only allow select for authenticated users (admin dashboard)
-- Note: Use service_role key in admin dashboard to bypass RLS
CREATE POLICY "Allow authenticated selects" 
    ON quiz_responses 
    FOR SELECT 
    TO authenticated 
    USING (true);

-- Policy: Allow service_role to do everything (for admin operations)
CREATE POLICY "Allow service_role all operations" 
    ON quiz_responses 
    FOR ALL 
    TO service_role 
    USING (true) 
    WITH CHECK (true);

-- Optional: Create a view for statistics
CREATE OR REPLACE VIEW quiz_stats AS
SELECT 
    COUNT(*) as total_responses,
    AVG(financial_tension) as avg_financial_tension,
    AVG(difficult_talks) as avg_difficult_talks,
    COUNT(DISTINCT location) as unique_locations,
    MODE() WITHIN GROUP (ORDER BY impact_area) as most_common_impact_area,
    MODE() WITHIN GROUP (ORDER BY greatest_need) as most_common_need,
    MAX(created_at) as latest_response,
    MIN(created_at) as first_response
FROM quiz_responses;

-- Grant access to the view
GRANT SELECT ON quiz_stats TO authenticated;
GRANT SELECT ON quiz_stats TO service_role;

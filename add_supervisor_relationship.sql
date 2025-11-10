-- Add supervisor relationship to users table
ALTER TABLE users ADD COLUMN supervisor_id UUID REFERENCES users(id);
ALTER TABLE users ADD COLUMN level_rank INTEGER DEFAULT 1; -- For comparing levels

-- Add indexes for performance
CREATE INDEX idx_users_supervisor_id ON users(supervisor_id);
CREATE INDEX idx_users_level_rank ON users(level_rank);

-- Add constraint to prevent self-supervision
ALTER TABLE users ADD CONSTRAINT chk_no_self_supervision CHECK (supervisor_id != id);

-- Update level_rank based on job levels (you can adjust these mappings)
UPDATE users SET level_rank = CASE
    WHEN level::text ILIKE '%intern%' OR level::text ILIKE '%trainee%' THEN 1
    WHEN level::text ILIKE '%junior%' OR level::text ILIKE '%associate%' THEN 2
    WHEN level::text ILIKE '%senior%' OR level::text ILIKE '%specialist%' THEN 3
    WHEN level::text ILIKE '%lead%' OR level::text ILIKE '%supervisor%' THEN 4
    WHEN level::text ILIKE '%manager%' OR level::text ILIKE '%head%' THEN 5
    WHEN level::text ILIKE '%director%' OR level::text ILIKE '%executive%' THEN 6
    WHEN level::text ILIKE '%ceo%' OR level::text ILIKE '%president%' THEN 7
    ELSE 2 -- Default to level 2 for unspecified levels
END;

COMMIT;
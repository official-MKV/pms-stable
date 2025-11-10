-- Migration: Update Goals and Tasks structure
-- 1. Remove departmental goals (only yearly and quarterly remain)
-- 2. Add goal_id to tasks table for linking tasks to goals

BEGIN;

-- Step 1: Add goal_id column to tasks table
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS goal_id UUID REFERENCES goals(id) ON DELETE SET NULL;

-- Step 2: Create index on goal_id for performance
CREATE INDEX IF NOT EXISTS idx_tasks_goal_id ON tasks(goal_id);

-- Step 3: Drop organization_id from goals (if exists)
-- First, check if there are any departmental goals and convert them or delete them
UPDATE goals
SET type = 'quarterly'
WHERE type = 'departmental' AND parent_goal_id IS NOT NULL;

-- Delete orphaned departmental goals (those without parent)
DELETE FROM goals
WHERE type = 'departmental' AND parent_goal_id IS NULL;

-- Now safe to drop the organization_id column
ALTER TABLE goals
DROP COLUMN IF EXISTS organization_id;

-- Step 4: Update the goaltype enum to remove 'departmental'
-- First create new enum type
DO $$
BEGIN
    -- Create new enum type
    CREATE TYPE goaltype_new AS ENUM ('yearly', 'quarterly');

    -- Alter the column to use the new type
    ALTER TABLE goals
    ALTER COLUMN type TYPE goaltype_new
    USING type::text::goaltype_new;

    -- Drop the old enum type
    DROP TYPE IF EXISTS goaltype;

    -- Rename the new type to the original name
    ALTER TYPE goaltype_new RENAME TO goaltype;

EXCEPTION WHEN duplicate_object THEN
    -- If goaltype already exists without departmental, do nothing
    NULL;
END $$;

-- Step 5: Update permissions - remove departmental goal permissions
UPDATE roles
SET permissions = (
    SELECT jsonb_agg(elem)
    FROM jsonb_array_elements_text(permissions::jsonb) elem
    WHERE elem::text != 'goal_create_departmental'
)::json
WHERE permissions::jsonb ? 'goal_create_departmental';

COMMIT;

-- Verification queries
SELECT 'Goals table structure:' as info;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'goals'
ORDER BY ordinal_position;

SELECT 'Tasks table structure (goal_id):' as info;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'tasks' AND column_name = 'goal_id';

SELECT 'Goal types in use:' as info;
SELECT type, COUNT(*) as count FROM goals GROUP BY type;

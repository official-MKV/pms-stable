-- Migration: Update Goals and Tasks structure
-- 1. Remove departmental goals (only yearly and quarterly remain)
-- 2. Add goal_id to tasks table for linking tasks to goals

-- Step 1: Add goal_id column to tasks table
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS goal_id UUID;

-- Step 2: Add foreign key constraint
DO $$
BEGIN
    ALTER TABLE tasks
    ADD CONSTRAINT fk_tasks_goal_id
    FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE SET NULL;
EXCEPTION WHEN duplicate_object THEN
    NULL;
END $$;

-- Step 3: Create index on goal_id for performance
CREATE INDEX IF NOT EXISTS idx_tasks_goal_id ON tasks(goal_id);

-- Step 4: Check if there are any departmental goals
SELECT 'Checking for departmental goals...' as status;
SELECT COUNT(*) as departmental_goal_count FROM goals WHERE type = 'DEPARTMENTAL';

-- Step 5: Drop organization_id from goals table
ALTER TABLE goals DROP COLUMN IF EXISTS organization_id;

-- Step 6: Remove DEPARTMENTAL from goaltype enum
-- This requires creating a new enum and migrating

-- First check if there are NO departmental goals
DO $$
DECLARE
    dept_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO dept_count FROM goals WHERE type = 'DEPARTMENTAL';

    IF dept_count = 0 THEN
        -- Safe to proceed with enum change

        -- Create new enum
        CREATE TYPE goaltype_new AS ENUM ('YEARLY', 'QUARTERLY');

        -- Change column type
        ALTER TABLE goals ALTER COLUMN type TYPE goaltype_new
        USING type::text::goaltype_new;

        -- Drop old enum
        DROP TYPE goaltype;

        -- Rename new enum
        ALTER TYPE goaltype_new RENAME TO goaltype;

        RAISE NOTICE 'Successfully updated goaltype enum';
    ELSE
        RAISE NOTICE 'Cannot update enum - % departmental goals exist', dept_count;
    END IF;
END $$;

-- Step 7: Update permissions - remove goal_create_departmental
UPDATE roles
SET permissions = (
    SELECT json_agg(elem)
    FROM json_array_elements_text(permissions::json) elem
    WHERE elem != 'goal_create_departmental'
)
WHERE permissions::text LIKE '%goal_create_departmental%';

-- Verification
SELECT '=== MIGRATION COMPLETE ===' as status;

SELECT 'Goals table columns:' as info;
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'goals' AND column_name IN ('organization_id', 'goal_id', 'type')
ORDER BY column_name;

SELECT 'Tasks table columns:' as info;
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'tasks' AND column_name = 'goal_id';

SELECT 'Goal type enum values:' as info;
SELECT enumlabel
FROM pg_enum
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'goaltype')
ORDER BY enumsortorder;

SELECT 'Roles without departmental permission:' as info;
SELECT name,
    CASE WHEN permissions::text LIKE '%goal_create_departmental%'
         THEN 'HAS departmental'
         ELSE 'OK'
    END as status
FROM roles;

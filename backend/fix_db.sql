-- Database Schema Fix Script
-- Run this with: psql -h localhost -U postgres -d pms_db -f fix_db.sql

-- Start transaction
BEGIN;

-- Fix Users table - add missing columns if they don't exist
DO $$
BEGIN
    -- Add supervisor_id column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='supervisor_id') THEN
        ALTER TABLE users ADD COLUMN supervisor_id UUID REFERENCES users(id);
        CREATE INDEX IF NOT EXISTS idx_users_supervisor_id ON users(supervisor_id);
        RAISE NOTICE 'Added supervisor_id column to users table';
    END IF;

    -- Add level_rank column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='level_rank') THEN
        ALTER TABLE users ADD COLUMN level_rank INTEGER;
        CREATE INDEX IF NOT EXISTS idx_users_level_rank ON users(level_rank);
        RAISE NOTICE 'Added level_rank column to users table';
    END IF;
END $$;

-- Fix Tasks table enum types
DO $$
BEGIN
    -- Recreate TaskStatus enum if needed
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'taskstatus') THEN
        CREATE TYPE TaskStatus AS ENUM ('PENDING', 'ONGOING', 'COMPLETED', 'APPROVED', 'OVERDUE');
        RAISE NOTICE 'Created TaskStatus enum';
    END IF;

    -- Recreate TaskUrgency enum if needed
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'taskurgency') THEN
        CREATE TYPE TaskUrgency AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'URGENT');
        RAISE NOTICE 'Created TaskUrgency enum';
    END IF;

    -- Recreate TaskType enum if needed
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tasktype') THEN
        CREATE TYPE TaskType AS ENUM ('INDIVIDUAL', 'GROUP');
        RAISE NOTICE 'Created TaskType enum';
    END IF;
END $$;

-- Fix Tasks table columns
DO $$
BEGIN
    -- Ensure team_head_id column exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='tasks' AND column_name='team_head_id') THEN
        ALTER TABLE tasks ADD COLUMN team_head_id UUID REFERENCES users(id);
        RAISE NOTICE 'Added team_head_id column to tasks table';
    END IF;

    -- Fix urgency column type if it's wrong
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='tasks'
        AND column_name='urgency'
        AND data_type != 'USER-DEFINED'
    ) THEN
        ALTER TABLE tasks ALTER COLUMN urgency TYPE TaskUrgency USING urgency::TaskUrgency;
        RAISE NOTICE 'Fixed urgency column type';
    END IF;

    -- Fix status column type if it's wrong
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='tasks'
        AND column_name='status'
        AND data_type != 'USER-DEFINED'
    ) THEN
        ALTER TABLE tasks ALTER COLUMN status TYPE TaskStatus USING status::TaskStatus;
        RAISE NOTICE 'Fixed status column type';
    END IF;

    -- Fix type column type if it's wrong
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='tasks'
        AND column_name='type'
        AND data_type != 'USER-DEFINED'
    ) THEN
        ALTER TABLE tasks ALTER COLUMN type TYPE TaskType USING type::TaskType;
        RAISE NOTICE 'Fixed type column type';
    END IF;
END $$;

-- Verify all review-related tables exist
DO $$
BEGIN
    -- Verify review_cycles table
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'review_cycles') THEN
        RAISE EXCEPTION 'review_cycles table does not exist! Run full migration.';
    END IF;

    -- Verify review_traits table
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'review_traits') THEN
        RAISE EXCEPTION 'review_traits table does not exist! Run full migration.';
    END IF;

    -- Verify review_questions table
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'review_questions') THEN
        RAISE EXCEPTION 'review_questions table does not exist! Run full migration.';
    END IF;

    -- Verify review_assignments table
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'review_assignments') THEN
        RAISE EXCEPTION 'review_assignments table does not exist! Run full migration.';
    END IF;

    -- Verify review_cycle_traits table
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'review_cycle_traits') THEN
        RAISE EXCEPTION 'review_cycle_traits table does not exist! Run full migration.';
    END IF;

    RAISE NOTICE 'All review tables exist';
END $$;

-- Show summary
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Database schema fix completed!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables verified:';
    RAISE NOTICE '  - users (with supervisor_id, level_rank)';
    RAISE NOTICE '  - tasks (with proper enum types)';
    RAISE NOTICE '  - review_cycles, review_traits, review_questions';
    RAISE NOTICE '  - review_assignments, review_cycle_traits';
    RAISE NOTICE '========================================';
END $$;

COMMIT;

-- Show current schema status
\echo '\n=== Users Table Schema ==='
\d users

\echo '\n=== Tasks Table Schema ==='
\d tasks

\echo '\n=== Review Tables ==='
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE 'review%'
ORDER BY table_name;

\echo '\n=== All Enum Types ==='
SELECT t.typname, e.enumlabel
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
WHERE t.typname IN ('taskstatus', 'taskurgency', 'tasktype', 'userstatus')
ORDER BY t.typname, e.enumsortorder;
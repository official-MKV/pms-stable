-- Database Schema Verification and Fix Script
-- Run this to verify and fix common schema issues

-- Check if supervisor_id column exists
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'supervisor_id';

-- Check if level_rank column exists
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'level_rank';

-- Check review-related tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('review_cycles', 'review_traits', 'review_questions', 'review_assignments', 'review_cycle_traits');

-- Check task-related columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'tasks' AND column_name IN ('urgency', 'type', 'status', 'team_head_id');

-- Check for any constraints issues
SELECT conname, contype, conrelid::regclass
FROM pg_constraint
WHERE conrelid = 'users'::regclass;

-- List all enum types
SELECT t.typname, e.enumlabel
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
WHERE t.typname IN ('taskstatus', 'taskurgency', 'tasktype', 'userstatus')
ORDER BY t.typname, e.enumsortorder;
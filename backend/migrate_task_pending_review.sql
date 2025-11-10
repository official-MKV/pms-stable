-- Add pending_review status to task workflow
-- This status indicates a task has been submitted and is awaiting creator review

-- Add new value to taskstatus enum (PostgreSQL adds at the end by default)
ALTER TYPE taskstatus ADD VALUE IF NOT EXISTS 'pending_review';

COMMIT;

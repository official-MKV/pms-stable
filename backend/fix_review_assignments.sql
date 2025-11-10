-- Check existing review-related tables
SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename LIKE '%review%';

-- Check review_assignments table structure
\d review_assignments;

-- Count assignments
SELECT COUNT(*) as total_assignments FROM review_assignments;

-- Check sample assignments
SELECT * FROM review_assignments LIMIT 5;

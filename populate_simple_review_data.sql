-- Simple script to populate review responses with dummy data
-- Run this to see performance data

-- Insert dummy responses for all incomplete assignments
INSERT INTO review_responses (assignment_id, question_id, rating, comments, created_at, updated_at)
SELECT
    ra.id as assignment_id,
    rq.id as question_id,
    (6 + floor(random() * 5))::int as rating,  -- Random rating 6-10
    'Sample feedback for performance evaluation.' as comments,
    NOW() as created_at,
    NOW() as updated_at
FROM review_assignments ra
CROSS JOIN review_questions rq
INNER JOIN review_cycle_traits rct ON rq.trait_id = rct.trait_id AND ra.cycle_id = rct.cycle_id
WHERE ra.status != 'completed'
AND (
    (ra.review_type = 'self' AND rq.applies_to_self = TRUE) OR
    (ra.review_type = 'peer' AND rq.applies_to_peer = TRUE) OR
    (ra.review_type = 'supervisor' AND rq.applies_to_supervisor = TRUE)
)
AND NOT EXISTS (
    SELECT 1 FROM review_responses rr2
    WHERE rr2.assignment_id = ra.id AND rr2.question_id = rq.id
)
LIMIT 1000;  -- Limit to prevent too many inserts

-- Mark assignments as completed
UPDATE review_assignments
SET status = 'completed', completed_at = NOW()
WHERE status != 'completed'
AND EXISTS (
    SELECT 1 FROM review_responses rr
    WHERE rr.assignment_id = review_assignments.id
);

-- Show summary
SELECT
    'Assignments Completed' as metric,
    COUNT(*) as count
FROM review_assignments
WHERE status = 'completed'
UNION ALL
SELECT
    'Total Responses' as metric,
    COUNT(*) as count
FROM review_responses;

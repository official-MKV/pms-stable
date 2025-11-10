-- Quick test: Insert 10 dummy responses for the first assignment
WITH first_assignment AS (
    SELECT id, cycle_id, review_type
    FROM review_assignments
    WHERE status != 'completed'
    LIMIT 1
),
relevant_questions AS (
    SELECT rq.id
    FROM review_questions rq
    INNER JOIN review_cycle_traits rct ON rq.trait_id = rct.trait_id
    INNER JOIN first_assignment fa ON rct.cycle_id = fa.cycle_id
    WHERE (
        (fa.review_type = 'self' AND rq.applies_to_self = TRUE) OR
        (fa.review_type = 'peer' AND rq.applies_to_peer = TRUE) OR
        (fa.review_type = 'supervisor' AND rq.applies_to_supervisor = TRUE)
    )
    LIMIT 10
)
INSERT INTO review_responses (assignment_id, question_id, rating, comments, created_at, updated_at)
SELECT
    fa.id,
    rq.id,
    8,
    'Good performance',
    NOW(),
    NOW()
FROM first_assignment fa
CROSS JOIN relevant_questions rq
ON CONFLICT (assignment_id, question_id) DO NOTHING;

SELECT 'Responses inserted' as status, COUNT(*) as count FROM review_responses;

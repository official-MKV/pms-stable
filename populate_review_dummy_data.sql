-- Populate dummy review data for testing performance page
-- This script adds review responses for existing assignments

-- First, let's check what we have
DO $$
DECLARE
    v_cycle_id UUID;
    v_assignment_id UUID;
    v_question_id UUID;
    v_trait_id UUID;
    rating_value INT;
BEGIN
    -- Get the first active or completed review cycle
    SELECT id INTO v_cycle_id
    FROM review_cycles
    WHERE status IN ('active', 'completed')
    ORDER BY created_at DESC
    LIMIT 1;

    IF v_cycle_id IS NULL THEN
        RAISE NOTICE 'No active or completed review cycles found';
        RETURN;
    END IF;

    RAISE NOTICE 'Using cycle: %', v_cycle_id;

    -- Loop through all assignments for this cycle
    FOR v_assignment_id IN
        SELECT id FROM review_assignments
        WHERE cycle_id = v_cycle_id
        AND status != 'completed'
    LOOP
        RAISE NOTICE 'Processing assignment: %', v_assignment_id;

        -- Get all questions for this assignment based on review type
        FOR v_question_id IN
            SELECT DISTINCT rq.id
            FROM review_questions rq
            INNER JOIN review_cycle_traits rct ON rq.trait_id = rct.trait_id
            INNER JOIN review_assignments ra ON ra.cycle_id = rct.cycle_id
            WHERE ra.id = v_assignment_id
            AND (
                (ra.review_type = 'self' AND rq.applies_to_self = TRUE) OR
                (ra.review_type = 'peer' AND rq.applies_to_peer = TRUE) OR
                (ra.review_type = 'supervisor' AND rq.applies_to_supervisor = TRUE)
            )
        LOOP
            -- Generate random rating between 6-10 (realistic performance ratings)
            rating_value := 6 + floor(random() * 5)::int;

            -- Insert or update response
            INSERT INTO review_responses (
                assignment_id,
                question_id,
                rating,
                comments,
                created_at,
                updated_at
            ) VALUES (
                v_assignment_id,
                v_question_id,
                rating_value,
                CASE
                    WHEN rating_value >= 9 THEN 'Excellent performance, consistently exceeds expectations.'
                    WHEN rating_value >= 7 THEN 'Good performance, meets expectations well.'
                    ELSE 'Satisfactory performance, room for improvement.'
                END,
                NOW(),
                NOW()
            )
            ON CONFLICT (assignment_id, question_id)
            DO UPDATE SET
                rating = EXCLUDED.rating,
                comments = EXCLUDED.comments,
                updated_at = NOW();

        END LOOP;

        -- Mark assignment as completed
        UPDATE review_assignments
        SET status = 'completed',
            completed_at = NOW()
        WHERE id = v_assignment_id;

        RAISE NOTICE 'Completed assignment: %', v_assignment_id;
    END LOOP;

    -- Now calculate scores for all users in this cycle
    RAISE NOTICE 'Calculating scores for cycle: %', v_cycle_id;

    -- Loop through each trait in the cycle
    FOR v_trait_id IN
        SELECT trait_id FROM review_cycle_traits WHERE cycle_id = v_cycle_id
    LOOP
        -- Insert review scores for each user
        INSERT INTO review_scores (
            cycle_id,
            user_id,
            trait_id,
            self_score,
            peer_avg_score,
            supervisor_score,
            weighted_score,
            created_at,
            updated_at
        )
        SELECT
            v_cycle_id,
            ra.reviewee_id,
            v_trait_id,
            -- Self score (average of self review ratings for this trait)
            (SELECT AVG(rr.rating)
             FROM review_responses rr
             INNER JOIN review_assignments ra2 ON rr.assignment_id = ra2.id
             INNER JOIN review_questions rq ON rr.question_id = rq.id
             WHERE ra2.reviewee_id = ra.reviewee_id
             AND ra2.cycle_id = v_cycle_id
             AND ra2.review_type = 'self'
             AND rq.trait_id = v_trait_id
            ) as self_score,
            -- Peer average score
            (SELECT AVG(rr.rating)
             FROM review_responses rr
             INNER JOIN review_assignments ra2 ON rr.assignment_id = ra2.id
             INNER JOIN review_questions rq ON rr.question_id = rq.id
             WHERE ra2.reviewee_id = ra.reviewee_id
             AND ra2.cycle_id = v_cycle_id
             AND ra2.review_type = 'peer'
             AND rq.trait_id = v_trait_id
            ) as peer_avg_score,
            -- Supervisor score
            (SELECT AVG(rr.rating)
             FROM review_responses rr
             INNER JOIN review_assignments ra2 ON rr.assignment_id = ra2.id
             INNER JOIN review_questions rq ON rr.question_id = rq.id
             WHERE ra2.reviewee_id = ra.reviewee_id
             AND ra2.cycle_id = v_cycle_id
             AND ra2.review_type = 'supervisor'
             AND rq.trait_id = v_trait_id
            ) as supervisor_score,
            -- Weighted score: 20% self, 40% peer, 40% supervisor
            (
                COALESCE((SELECT AVG(rr.rating) FROM review_responses rr
                         INNER JOIN review_assignments ra2 ON rr.assignment_id = ra2.id
                         INNER JOIN review_questions rq ON rr.question_id = rq.id
                         WHERE ra2.reviewee_id = ra.reviewee_id AND ra2.cycle_id = v_cycle_id
                         AND ra2.review_type = 'self' AND rq.trait_id = v_trait_id), 0) * 0.2 +
                COALESCE((SELECT AVG(rr.rating) FROM review_responses rr
                         INNER JOIN review_assignments ra2 ON rr.assignment_id = ra2.id
                         INNER JOIN review_questions rq ON rr.question_id = rq.id
                         WHERE ra2.reviewee_id = ra.reviewee_id AND ra2.cycle_id = v_cycle_id
                         AND ra2.review_type = 'peer' AND rq.trait_id = v_trait_id), 0) * 0.4 +
                COALESCE((SELECT AVG(rr.rating) FROM review_responses rr
                         INNER JOIN review_assignments ra2 ON rr.assignment_id = ra2.id
                         INNER JOIN review_questions rq ON rr.question_id = rq.id
                         WHERE ra2.reviewee_id = ra.reviewee_id AND ra2.cycle_id = v_cycle_id
                         AND ra2.review_type = 'supervisor' AND rq.trait_id = v_trait_id), 0) * 0.4
            ) as weighted_score,
            NOW(),
            NOW()
        FROM review_assignments ra
        WHERE ra.cycle_id = v_cycle_id
        GROUP BY ra.reviewee_id
        ON CONFLICT (cycle_id, user_id, trait_id)
        DO UPDATE SET
            self_score = EXCLUDED.self_score,
            peer_avg_score = EXCLUDED.peer_avg_score,
            supervisor_score = EXCLUDED.supervisor_score,
            weighted_score = EXCLUDED.weighted_score,
            updated_at = NOW();
    END LOOP;

    -- Calculate overall performance scores
    INSERT INTO performance_scores (
        cycle_id,
        user_id,
        overall_score,
        review_score,
        task_score,
        goal_score,
        final_rating,
        created_at,
        updated_at
    )
    SELECT
        v_cycle_id,
        ra.reviewee_id,
        -- Overall score (average of all weighted scores)
        (SELECT AVG(weighted_score)
         FROM review_scores
         WHERE cycle_id = v_cycle_id AND user_id = ra.reviewee_id
        ) as overall_score,
        -- Review score component
        (SELECT AVG(weighted_score)
         FROM review_scores
         WHERE cycle_id = v_cycle_id AND user_id = ra.reviewee_id
        ) as review_score,
        -- Task score (placeholder - would come from task system)
        8.0 as task_score,
        -- Goal score (placeholder - would come from goal system)
        7.5 as goal_score,
        -- Final rating calculation (weighted: 50% reviews, 30% tasks, 20% goals)
        (
            COALESCE((SELECT AVG(weighted_score) FROM review_scores
                     WHERE cycle_id = v_cycle_id AND user_id = ra.reviewee_id), 0) * 0.5 +
            8.0 * 0.3 +
            7.5 * 0.2
        ) as final_rating,
        NOW(),
        NOW()
    FROM review_assignments ra
    WHERE ra.cycle_id = v_cycle_id
    GROUP BY ra.reviewee_id
    ON CONFLICT (cycle_id, user_id)
    DO UPDATE SET
        overall_score = EXCLUDED.overall_score,
        review_score = EXCLUDED.review_score,
        task_score = EXCLUDED.task_score,
        goal_score = EXCLUDED.goal_score,
        final_rating = EXCLUDED.final_rating,
        updated_at = NOW();

    RAISE NOTICE 'Successfully populated dummy review data for cycle: %', v_cycle_id;

END $$;

-- Verify the data
SELECT
    rc.name as cycle_name,
    COUNT(DISTINCT ra.id) as total_assignments,
    COUNT(DISTINCT CASE WHEN ra.status = 'completed' THEN ra.id END) as completed_assignments,
    COUNT(DISTINCT rr.id) as total_responses,
    COUNT(DISTINCT rs.id) as review_scores_generated,
    COUNT(DISTINCT ps.id) as performance_scores_generated
FROM review_cycles rc
LEFT JOIN review_assignments ra ON rc.id = ra.cycle_id
LEFT JOIN review_responses rr ON ra.id = rr.assignment_id
LEFT JOIN review_scores rs ON rc.id = rs.cycle_id
LEFT JOIN performance_scores ps ON rc.id = ps.cycle_id
WHERE rc.status IN ('active', 'completed')
GROUP BY rc.id, rc.name
ORDER BY rc.created_at DESC;

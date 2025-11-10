-- Create missing tables for Review & Performance Management System
-- Based on the FinalPhase.md specification

-- Performance Traits Table
CREATE TABLE IF NOT EXISTS review_traits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_active_trait_name UNIQUE (name)
);

-- Trait-Specific Questions Table
CREATE TABLE IF NOT EXISTS review_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trait_id UUID NOT NULL REFERENCES review_traits(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    applies_to_self BOOLEAN DEFAULT TRUE,
    applies_to_peer BOOLEAN DEFAULT TRUE,
    applies_to_supervisor BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Review Cycle Traits Junction Table
CREATE TABLE IF NOT EXISTS review_cycle_traits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_id UUID NOT NULL REFERENCES review_cycles(id) ON DELETE CASCADE,
    trait_id UUID NOT NULL REFERENCES review_traits(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_cycle_trait UNIQUE (cycle_id, trait_id)
);

-- Review Assignments Table
CREATE TABLE IF NOT EXISTS review_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_id UUID NOT NULL REFERENCES review_cycles(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES users(id),
    reviewee_id UUID NOT NULL REFERENCES users(id),
    review_type VARCHAR(20) NOT NULL CHECK (review_type IN ('self', 'peer', 'supervisor')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'overdue')),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_assignment UNIQUE (cycle_id, reviewer_id, reviewee_id, review_type)
);

-- Review Responses Table
CREATE TABLE IF NOT EXISTS review_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES review_assignments(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES review_questions(id),
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_response UNIQUE (assignment_id, question_id)
);

-- Review Scores Table
CREATE TABLE IF NOT EXISTS review_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_id UUID NOT NULL REFERENCES review_cycles(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    trait_id UUID NOT NULL REFERENCES review_traits(id),
    self_score DECIMAL(3,2),
    peer_score DECIMAL(3,2),
    supervisor_score DECIMAL(3,2),
    weighted_score DECIMAL(3,2),
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_user_trait_score UNIQUE (cycle_id, user_id, trait_id)
);

-- Performance Scores Table
CREATE TABLE IF NOT EXISTS performance_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    cycle_id UUID NOT NULL REFERENCES review_cycles(id) ON DELETE CASCADE,
    task_performance_score DECIMAL(5,2),
    review_performance_score DECIMAL(5,2),
    overall_performance_score DECIMAL(5,2),
    performance_band VARCHAR(30) CHECK (performance_band IN ('outstanding', 'exceeds_expectations', 'meets_expectations', 'below_expectations', 'needs_improvement')),
    organization_rank INTEGER,
    department_rank INTEGER,
    directorate_rank INTEGER,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_user_cycle_performance UNIQUE (user_id, cycle_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_review_traits_display_order ON review_traits(display_order);
CREATE INDEX IF NOT EXISTS idx_review_traits_active ON review_traits(is_active);
CREATE INDEX IF NOT EXISTS idx_review_questions_trait ON review_questions(trait_id);
CREATE INDEX IF NOT EXISTS idx_review_assignments_cycle ON review_assignments(cycle_id);
CREATE INDEX IF NOT EXISTS idx_review_assignments_reviewer ON review_assignments(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_review_assignments_reviewee ON review_assignments(reviewee_id);
CREATE INDEX IF NOT EXISTS idx_review_assignments_status ON review_assignments(status);
CREATE INDEX IF NOT EXISTS idx_review_responses_assignment ON review_responses(assignment_id);
CREATE INDEX IF NOT EXISTS idx_review_scores_cycle_user ON review_scores(cycle_id, user_id);
CREATE INDEX IF NOT EXISTS idx_performance_scores_user ON performance_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_performance_scores_cycle ON performance_scores(cycle_id);
CREATE INDEX IF NOT EXISTS idx_performance_scores_band ON performance_scores(performance_band);

-- Insert default traits if none exist
INSERT INTO review_traits (name, description, display_order, created_by)
SELECT 'Communication Skills', 'Ability to communicate effectively with colleagues and stakeholders', 1, u.id
FROM users u
WHERE u.email = 'superadmin@nigcomsat.gov.ng'
AND NOT EXISTS (SELECT 1 FROM review_traits WHERE name = 'Communication Skills');

INSERT INTO review_traits (name, description, display_order, created_by)
SELECT 'Technical Competence', 'Technical skills and knowledge relevant to job responsibilities', 2, u.id
FROM users u
WHERE u.email = 'superadmin@nigcomsat.gov.ng'
AND NOT EXISTS (SELECT 1 FROM review_traits WHERE name = 'Technical Competence');

INSERT INTO review_traits (name, description, display_order, created_by)
SELECT 'Leadership & Initiative', 'Ability to lead projects and take initiative', 3, u.id
FROM users u
WHERE u.email = 'superadmin@nigcomsat.gov.ng'
AND NOT EXISTS (SELECT 1 FROM review_traits WHERE name = 'Leadership & Initiative');

INSERT INTO review_traits (name, description, display_order, created_by)
SELECT 'Collaboration & Teamwork', 'Ability to work effectively in team environments', 4, u.id
FROM users u
WHERE u.email = 'superadmin@nigcomsat.gov.ng'
AND NOT EXISTS (SELECT 1 FROM review_traits WHERE name = 'Collaboration & Teamwork');

INSERT INTO review_traits (name, description, display_order, created_by)
SELECT 'Problem Solving', 'Ability to analyze problems and develop effective solutions', 5, u.id
FROM users u
WHERE u.email = 'superadmin@nigcomsat.gov.ng'
AND NOT EXISTS (SELECT 1 FROM review_traits WHERE name = 'Problem Solving');

-- Insert default questions for Communication Skills trait
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by)
SELECT rt.id, 'How effectively does this person communicate ideas and information?', FALSE, TRUE, TRUE, u.id
FROM review_traits rt, users u
WHERE rt.name = 'Communication Skills'
AND u.email = 'superadmin@nigcomsat.gov.ng'
AND NOT EXISTS (
    SELECT 1 FROM review_questions rq
    WHERE rq.trait_id = rt.id
    AND rq.question_text = 'How effectively does this person communicate ideas and information?'
);

INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by)
SELECT rt.id, 'Rate your ability to explain complex concepts clearly', TRUE, FALSE, FALSE, u.id
FROM review_traits rt, users u
WHERE rt.name = 'Communication Skills'
AND u.email = 'superadmin@nigcomsat.gov.ng'
AND NOT EXISTS (
    SELECT 1 FROM review_questions rq
    WHERE rq.trait_id = rt.id
    AND rq.question_text = 'Rate your ability to explain complex concepts clearly'
);

INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by)
SELECT rt.id, 'How well does this person listen and respond to feedback?', FALSE, TRUE, TRUE, u.id
FROM review_traits rt, users u
WHERE rt.name = 'Communication Skills'
AND u.email = 'superadmin@nigcomsat.gov.ng'
AND NOT EXISTS (
    SELECT 1 FROM review_questions rq
    WHERE rq.trait_id = rt.id
    AND rq.question_text = 'How well does this person listen and respond to feedback?'
);

-- Insert questions for other traits
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by)
SELECT rt.id, 'How would you rate the technical skills demonstrated in daily work?', FALSE, TRUE, TRUE, u.id
FROM review_traits rt, users u
WHERE rt.name = 'Technical Competence'
AND u.email = 'superadmin@nigcomsat.gov.ng'
AND NOT EXISTS (
    SELECT 1 FROM review_questions rq
    WHERE rq.trait_id = rt.id
    AND rq.question_text = 'How would you rate the technical skills demonstrated in daily work?'
);

INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by)
SELECT rt.id, 'How often does this person take initiative on projects and tasks?', FALSE, TRUE, TRUE, u.id
FROM review_traits rt, users u
WHERE rt.name = 'Leadership & Initiative'
AND u.email = 'superadmin@nigcomsat.gov.ng'
AND NOT EXISTS (
    SELECT 1 FROM review_questions rq
    WHERE rq.trait_id = rt.id
    AND rq.question_text = 'How often does this person take initiative on projects and tasks?'
);

INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by)
SELECT rt.id, 'How effectively does this person collaborate with team members?', FALSE, TRUE, TRUE, u.id
FROM review_traits rt, users u
WHERE rt.name = 'Collaboration & Teamwork'
AND u.email = 'superadmin@nigcomsat.gov.ng'
AND NOT EXISTS (
    SELECT 1 FROM review_questions rq
    WHERE rq.trait_id = rt.id
    AND rq.question_text = 'How effectively does this person collaborate with team members?'
);

INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by)
SELECT rt.id, 'How well does this person analyze problems and develop solutions?', FALSE, TRUE, TRUE, u.id
FROM review_traits rt, users u
WHERE rt.name = 'Problem Solving'
AND u.email = 'superadmin@nigcomsat.gov.ng'
AND NOT EXISTS (
    SELECT 1 FROM review_questions rq
    WHERE rq.trait_id = rt.id
    AND rq.question_text = 'How well does this person analyze problems and develop solutions?'
);

COMMIT;
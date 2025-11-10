-- Fix Review System - Make traits fixed company standards and update rating scale

-- First, let's see what traits we currently have
SELECT name, description FROM review_traits;

-- Clear existing data and reset with proper company traits
TRUNCATE TABLE review_responses CASCADE;
TRUNCATE TABLE review_assignments CASCADE;
TRUNCATE TABLE review_cycle_traits CASCADE;
TRUNCATE TABLE review_questions CASCADE;
TRUNCATE TABLE review_traits CASCADE;

-- Insert fixed company performance traits
INSERT INTO review_traits (id, name, description, is_active, display_order, created_by) VALUES
(gen_random_uuid(), 'Communication Skills', 'Ability to communicate effectively with colleagues, stakeholders, and clients', true, 1, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
(gen_random_uuid(), 'Technical Competence', 'Technical skills and knowledge relevant to job responsibilities and industry standards', true, 2, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
(gen_random_uuid(), 'Leadership & Initiative', 'Ability to lead projects, take initiative, and guide team members effectively', true, 3, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
(gen_random_uuid(), 'Collaboration & Teamwork', 'Ability to work effectively in team environments and contribute to group success', true, 4, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
(gen_random_uuid(), 'Problem Solving', 'Ability to analyze complex problems and develop effective, innovative solutions', true, 5, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
(gen_random_uuid(), 'Quality of Work', 'Consistency in delivering high-quality output that meets or exceeds standards', true, 6, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
(gen_random_uuid(), 'Adaptability', 'Ability to adapt to changing circumstances, new technologies, and evolving requirements', true, 7, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
(gen_random_uuid(), 'Time Management', 'Ability to manage time effectively, meet deadlines, and prioritize tasks appropriately', true, 8, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Insert template questions for each trait, organized by review type

-- Communication Skills Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Communication Skills'), 'How effectively do I communicate my ideas and thoughts to others?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Communication Skills'), 'How well does this person communicate ideas and information clearly?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Communication Skills'), 'How effectively does this person listen and respond to feedback?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Communication Skills'), 'How well does this employee present information to different audiences?', false, false, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Technical Competence Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Technical Competence'), 'How would I rate my technical skills and knowledge in my field?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Technical Competence'), 'How would you rate this person''s technical expertise and skills?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Technical Competence'), 'How effectively does this person apply technical knowledge to solve problems?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Technical Competence'), 'How well does this employee stay updated with latest technical developments?', false, false, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Leadership & Initiative Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Leadership & Initiative'), 'How often do I take initiative on projects and propose new ideas?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Leadership & Initiative'), 'How often does this person take leadership roles and show initiative?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Leadership & Initiative'), 'How effectively does this person motivate and guide team members?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Leadership & Initiative'), 'How well does this employee demonstrate leadership potential and growth?', false, false, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Collaboration & Teamwork Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Collaboration & Teamwork'), 'How effectively do I collaborate and work with team members?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Collaboration & Teamwork'), 'How well does this person collaborate and contribute to team goals?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Collaboration & Teamwork'), 'How supportive is this person of colleagues and team initiatives?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Collaboration & Teamwork'), 'How effectively does this employee build relationships across teams?', false, false, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Problem Solving Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Problem Solving'), 'How effectively do I analyze and solve complex problems?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Problem Solving'), 'How well does this person identify and solve workplace challenges?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Problem Solving'), 'How creative and innovative is this person in finding solutions?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Problem Solving'), 'How effectively does this employee handle complex, multi-faceted problems?', false, false, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Quality of Work Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Quality of Work'), 'How would I rate the quality and accuracy of my work output?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Quality of Work'), 'How would you rate the quality and accuracy of this person''s work?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Quality of Work'), 'How consistent is this person in delivering high-quality results?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Quality of Work'), 'How well does this employee meet or exceed quality standards?', false, false, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Adaptability Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Adaptability'), 'How well do I adapt to changes and new situations?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Adaptability'), 'How well does this person adapt to changing requirements and priorities?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Adaptability'), 'How flexible is this person when facing unexpected challenges?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Adaptability'), 'How effectively does this employee embrace new technologies and processes?', false, false, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Time Management Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Time Management'), 'How effectively do I manage my time and meet deadlines?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Time Management'), 'How well does this person manage time and meet deadlines?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Time Management'), 'How effectively does this person prioritize tasks and responsibilities?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Time Management'), 'How well does this employee balance multiple projects and deadlines?', false, false, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Update review_responses constraint to use 1-10 scale instead of 1-5
ALTER TABLE review_responses DROP CONSTRAINT IF EXISTS valid_rating;
ALTER TABLE review_responses ADD CONSTRAINT valid_rating CHECK (rating BETWEEN 1 AND 10);

-- Update review_scores to use 1-10 scale calculations
ALTER TABLE review_scores ALTER COLUMN self_score TYPE DECIMAL(4,2);
ALTER TABLE review_scores ALTER COLUMN peer_score TYPE DECIMAL(4,2);
ALTER TABLE review_scores ALTER COLUMN supervisor_score TYPE DECIMAL(4,2);
ALTER TABLE review_scores ALTER COLUMN weighted_score TYPE DECIMAL(4,2);

COMMIT;
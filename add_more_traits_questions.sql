-- Add more comprehensive traits and questions for each review type

-- First, add more traits (in addition to the existing 8)
INSERT INTO review_traits (id, name, description, is_active, display_order, created_by) VALUES
(gen_random_uuid(), 'Customer Focus', 'Ability to understand and meet customer needs, both internal and external customers', true, 9, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
(gen_random_uuid(), 'Innovation & Creativity', 'Ability to think creatively and develop innovative solutions to business challenges', true, 10, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
(gen_random_uuid(), 'Professional Development', 'Commitment to continuous learning and professional growth', true, 11, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
(gen_random_uuid(), 'Accountability', 'Takes responsibility for actions, decisions, and results', true, 12, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Add more questions for existing and new traits

-- Customer Focus Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Customer Focus'), 'How well do I understand and respond to customer needs?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Customer Focus'), 'How effectively does this person serve internal and external customers?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Customer Focus'), 'How well does this person anticipate customer requirements?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Customer Focus'), 'How effectively does this employee handle customer complaints and feedback?', false, false, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Innovation & Creativity Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Innovation & Creativity'), 'How often do I propose creative solutions to problems?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Innovation & Creativity'), 'How innovative is this person in their approach to work?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Innovation & Creativity'), 'How well does this person think outside the box when solving problems?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Innovation & Creativity'), 'How effectively does this employee contribute new ideas to the team?', false, false, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Professional Development Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Professional Development'), 'How actively do I pursue learning opportunities and skill development?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Professional Development'), 'How committed is this person to their professional growth?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Professional Development'), 'How well does this person apply new skills and knowledge?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Professional Development'), 'How effectively does this employee seek feedback for improvement?', false, false, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Accountability Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Accountability'), 'How well do I take responsibility for my actions and decisions?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Accountability'), 'How accountable is this person for their work and commitments?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Accountability'), 'How well does this person own mistakes and learn from them?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Accountability'), 'How effectively does this employee deliver on promises and commitments?', false, false, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Add more questions to existing traits for better coverage

-- Additional Communication Skills Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Communication Skills'), 'How well do I adapt my communication style to different audiences?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Communication Skills'), 'How clearly does this person express complex ideas?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Additional Technical Competence Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Technical Competence'), 'How effectively do I share technical knowledge with others?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Technical Competence'), 'How well does this person troubleshoot technical problems?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

-- Additional Leadership Questions
INSERT INTO review_questions (trait_id, question_text, applies_to_self, applies_to_peer, applies_to_supervisor, created_by) VALUES
((SELECT id FROM review_traits WHERE name = 'Leadership & Initiative'), 'How effectively do I delegate tasks and responsibilities?', true, false, false, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng')),
((SELECT id FROM review_traits WHERE name = 'Leadership & Initiative'), 'How well does this person inspire and motivate others?', false, true, true, (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng'));

COMMIT;
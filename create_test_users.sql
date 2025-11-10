-- Create Test Users with Different Permissions and Departments
-- Run this SQL script against your PMS database

-- First, let's see current organizations to ensure we have departments
-- Assuming we have organizations like:
-- - Technical Department (ID will be retrieved)
-- - HR Department
-- - Marketing Department
-- - Finance Department

-- Create additional departments if needed
INSERT INTO organizations (id, name, description, level, parent_id) VALUES
  (gen_random_uuid(), 'Engineering', 'Software Development and Engineering', 'department', (SELECT id FROM organizations WHERE level = 'directorate' LIMIT 1)),
  (gen_random_uuid(), 'Marketing', 'Marketing and Communications', 'department', (SELECT id FROM organizations WHERE level = 'directorate' LIMIT 1)),
  (gen_random_uuid(), 'Finance', 'Finance and Accounting', 'department', (SELECT id FROM organizations WHERE level = 'directorate' LIMIT 1)),
  (gen_random_uuid(), 'Operations', 'Operations and Support', 'department', (SELECT id FROM organizations WHERE level = 'directorate' LIMIT 1))
ON CONFLICT (name) DO NOTHING;

-- Create roles with different permissions
INSERT INTO roles (id, name, description, is_leadership, scope_override, permissions) VALUES
  (gen_random_uuid(), 'Task Creator', 'Can create and manage tasks', false, 'none', '["task_create", "task_edit", "task_view_all"]'),
  (gen_random_uuid(), 'Task Worker', 'Can work on assigned tasks only', false, 'none', '["task_submit", "task_request_extension"]'),
  (gen_random_uuid(), 'Team Lead', 'Can create tasks and manage team', true, 'none', '["task_create", "task_edit", "task_view_all", "task_review", "user_view_all"]'),
  (gen_random_uuid(), 'Department Manager', 'Can manage department tasks and users', true, 'cross_directorate', '["task_create", "task_edit", "task_view_all", "task_review", "user_create", "user_edit", "user_view_all"]'),
  (gen_random_uuid(), 'Project Manager', 'Can create and review tasks across departments', false, 'global', '["task_create", "task_edit", "task_view_all", "task_review", "goal_create_departmental"]')
ON CONFLICT (name) DO NOTHING;

-- Get organization IDs for reference
WITH org_ids AS (
  SELECT
    id as org_id,
    name as org_name
  FROM organizations
  WHERE level = 'department'
),
role_ids AS (
  SELECT
    id as role_id,
    name as role_name
  FROM roles
)

-- Create test users
INSERT INTO users (id, email, name, phone, address, skillset, level, job_title, organization_id, role_id, status, password_hash, email_verified_at)
SELECT
  gen_random_uuid(),
  email,
  name,
  phone,
  address,
  skillset,
  level,
  job_title,
  org_id,
  role_id,
  'active',
  -- Default password: 'password123' hashed with bcrypt
  '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewGbqNyU.8W0Z5TW',
  NOW()
FROM (
  VALUES
    -- Engineering Department
    ('john.smith@nigcomsat.com', 'John Smith', '+234-801-234-5678', '15 Victoria Island Lagos', 'React, Node.js, Python', 'Senior', 'Senior Software Engineer', 'Engineering', 'Task Creator'),
    ('sarah.jones@nigcomsat.com', 'Sarah Jones', '+234-802-345-6789', '22 Ikoyi Lagos', 'JavaScript, UI/UX, Design Systems', 'Mid', 'Frontend Developer', 'Engineering', 'Task Worker'),
    ('mike.wilson@nigcomsat.com', 'Mike Wilson', '+234-803-456-7890', '8 Allen Avenue Ikeja', 'DevOps, AWS, Docker, K8s', 'Senior', 'DevOps Engineer', 'Engineering', 'Task Creator'),
    ('lisa.brown@nigcomsat.com', 'Lisa Brown', '+234-804-567-8901', '45 Surulere Lagos', 'Java, Spring Boot, Databases', 'Lead', 'Engineering Team Lead', 'Engineering', 'Team Lead'),

    -- Marketing Department
    ('david.clark@nigcomsat.com', 'David Clark', '+234-805-678-9012', '12 Lekki Phase 1', 'Digital Marketing, SEO, Analytics', 'Senior', 'Marketing Manager', 'Marketing', 'Department Manager'),
    ('emma.davis@nigcomsat.com', 'Emma Davis', '+234-806-789-0123', '33 Ajah Lagos', 'Content Creation, Social Media', 'Mid', 'Content Specialist', 'Marketing', 'Task Worker'),
    ('james.taylor@nigcomsat.com', 'James Taylor', '+234-807-890-1234', '67 Maryland Lagos', 'Brand Management, Strategy', 'Senior', 'Brand Manager', 'Marketing', 'Task Creator'),

    -- Finance Department
    ('nancy.white@nigcomsat.com', 'Nancy White', '+234-808-901-2345', '89 Yaba Lagos', 'Accounting, Financial Analysis, Excel', 'Senior', 'Finance Manager', 'Finance', 'Department Manager'),
    ('robert.lee@nigcomsat.com', 'Robert Lee', '+234-809-012-3456', '21 Gbagada Lagos', 'Accounting, Payroll, Budgeting', 'Mid', 'Accountant', 'Finance', 'Task Worker'),
    ('grace.johnson@nigcomsat.com', 'Grace Johnson', '+234-810-123-4567', '54 Ogudu Lagos', 'Financial Planning, Reporting', 'Senior', 'Financial Analyst', 'Finance', 'Task Creator'),

    -- Operations Department
    ('peter.adams@nigcomsat.com', 'Peter Adams', '+234-811-234-5678', '76 Festac Lagos', 'Operations Management, Process Improvement', 'Lead', 'Operations Manager', 'Operations', 'Department Manager'),
    ('mary.wilson@nigcomsat.com', 'Mary Wilson', '+234-812-345-6789', '31 Apapa Lagos', 'Customer Support, Documentation', 'Mid', 'Operations Specialist', 'Operations', 'Task Worker'),

    -- Cross-functional roles
    ('alex.garcia@nigcomsat.com', 'Alex Garcia', '+234-813-456-7890', '98 Magodo Lagos', 'Project Management, Agile, Scrum', 'Senior', 'Project Manager', 'Engineering', 'Project Manager'),
    ('sophia.martinez@nigcomsat.com', 'Sophia Martinez', '+234-814-567-8901', '43 Ojodu Lagos', 'Product Management, Strategy', 'Senior', 'Product Manager', 'Engineering', 'Project Manager')
) AS user_data(email, name, phone, address, skillset, level, job_title, org_name, role_name)
CROSS JOIN (
  SELECT org_id, org_name FROM org_ids
) orgs
CROSS JOIN (
  SELECT role_id, role_name FROM role_ids
) roles
WHERE orgs.org_name = user_data.org_name
  AND roles.role_name = user_data.role_name;

-- Create some sample tasks with different urgency levels
INSERT INTO tasks (id, title, description, type, urgency, due_date, status, created_by)
SELECT
  gen_random_uuid(),
  title,
  description,
  type,
  urgency,
  due_date,
  'created',
  creator_id
FROM (
  VALUES
    ('Fix login authentication bug', 'Users are unable to login due to session timeout issues', 'individual', 'urgent', '2025-01-30 17:00:00', (SELECT id FROM users WHERE email = 'lisa.brown@nigcomsat.com')),
    ('Update user dashboard UI', 'Improve the user dashboard interface based on user feedback', 'individual', 'medium', '2025-02-15 17:00:00', (SELECT id FROM users WHERE email = 'lisa.brown@nigcomsat.com')),
    ('Q1 Marketing Campaign Planning', 'Plan and coordinate Q1 marketing campaigns across all channels', 'group', 'high', '2025-02-01 17:00:00', (SELECT id FROM users WHERE email = 'david.clark@nigcomsat.com')),
    ('Database performance optimization', 'Optimize database queries to improve application performance', 'individual', 'high', '2025-02-10 17:00:00', (SELECT id FROM users WHERE email = 'mike.wilson@nigcomsat.com')),
    ('Monthly financial report', 'Prepare monthly financial statements and analysis', 'individual', 'medium', '2025-01-31 17:00:00', (SELECT id FROM users WHERE email = 'nancy.white@nigcomsat.com')),
    ('Customer feedback analysis', 'Analyze customer feedback from last quarter and create action plan', 'individual', 'low', '2025-02-20 17:00:00', (SELECT id FROM users WHERE email = 'mary.wilson@nigcomsat.com')),
    ('API documentation update', 'Update API documentation for new endpoints', 'individual', 'low', '2025-02-25 17:00:00', (SELECT id FROM users WHERE email = 'john.smith@nigcomsat.com'))
) AS task_data(title, description, type, urgency, due_date, creator_id);

-- Assign tasks to users
INSERT INTO task_assignments (id, task_id, user_id)
SELECT
  gen_random_uuid(),
  t.id,
  CASE
    WHEN t.title = 'Fix login authentication bug' THEN (SELECT id FROM users WHERE email = 'john.smith@nigcomsat.com')
    WHEN t.title = 'Update user dashboard UI' THEN (SELECT id FROM users WHERE email = 'sarah.jones@nigcomsat.com')
    WHEN t.title = 'Q1 Marketing Campaign Planning' THEN (SELECT id FROM users WHERE email = 'emma.davis@nigcomsat.com')
    WHEN t.title = 'Database performance optimization' THEN (SELECT id FROM users WHERE email = 'mike.wilson@nigcomsat.com')
    WHEN t.title = 'Monthly financial report' THEN (SELECT id FROM users WHERE email = 'grace.johnson@nigcomsat.com')
    WHEN t.title = 'Customer feedback analysis' THEN (SELECT id FROM users WHERE email = 'mary.wilson@nigcomsat.com')
    WHEN t.title = 'API documentation update' THEN (SELECT id FROM users WHERE email = 'john.smith@nigcomsat.com')
  END
FROM tasks t;

-- Add team head for group task
UPDATE tasks
SET team_head_id = (SELECT id FROM users WHERE email = 'emma.davis@nigcomsat.com')
WHERE title = 'Q1 Marketing Campaign Planning';

-- Add additional group task assignments
INSERT INTO task_assignments (id, task_id, user_id)
SELECT
  gen_random_uuid(),
  (SELECT id FROM tasks WHERE title = 'Q1 Marketing Campaign Planning'),
  u.id
FROM users u
WHERE u.email IN ('david.clark@nigcomsat.com', 'james.taylor@nigcomsat.com');
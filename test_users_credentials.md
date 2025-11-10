# PMS Test Users Credentials - CREATED SUCCESSFULLY!

🎉 **14 diverse test users and 7 sample tasks have been created in the database!**

All users have the default password: **`password123`**

## Users by Department & Permission Level

### 🏢 Engineering Department

#### Team Lead
- **Email:** lisa.brown@nigcomsat.com
- **Name:** Lisa Brown
- **Role:** Engineering Team Lead
- **Permissions:** Can create tasks, manage team, review submissions
- **Phone:** +234-804-567-8901

#### Task Creators (Can create and assign tasks)
- **Email:** john.smith@nigcomsat.com
- **Name:** John Smith
- **Role:** Senior Software Engineer
- **Skills:** React, Node.js, Python
- **Phone:** +234-801-234-5678

- **Email:** mike.wilson@nigcomsat.com
- **Name:** Mike Wilson
- **Role:** DevOps Engineer
- **Skills:** DevOps, AWS, Docker, K8s
- **Phone:** +234-803-456-7890

#### Task Workers (Can only work on assigned tasks)
- **Email:** sarah.jones@nigcomsat.com
- **Name:** Sarah Jones
- **Role:** Frontend Developer
- **Skills:** JavaScript, UI/UX, Design Systems
- **Phone:** +234-802-345-6789

### 📢 Marketing Department

#### Department Manager (Can manage across departments)
- **Email:** david.clark@nigcomsat.com
- **Name:** David Clark
- **Role:** Marketing Manager
- **Permissions:** Can create tasks, manage users, view all tasks
- **Phone:** +234-805-678-9012

#### Task Creators
- **Email:** james.taylor@nigcomsat.com
- **Name:** James Taylor
- **Role:** Brand Manager
- **Skills:** Brand Management, Strategy
- **Phone:** +234-807-890-1234

#### Task Workers
- **Email:** emma.davis@nigcomsat.com
- **Name:** Emma Davis
- **Role:** Content Specialist
- **Skills:** Content Creation, Social Media
- **Phone:** +234-806-789-0123

### 💰 Finance Department

#### Department Manager
- **Email:** nancy.white@nigcomsat.com
- **Name:** Nancy White
- **Role:** Finance Manager
- **Permissions:** Can manage department tasks and users
- **Phone:** +234-808-901-2345

#### Task Creators
- **Email:** grace.johnson@nigcomsat.com
- **Name:** Grace Johnson
- **Role:** Financial Analyst
- **Skills:** Financial Planning, Reporting
- **Phone:** +234-810-123-4567

#### Task Workers
- **Email:** robert.lee@nigcomsat.com
- **Name:** Robert Lee
- **Role:** Accountant
- **Skills:** Accounting, Payroll, Budgeting
- **Phone:** +234-809-012-3456

### ⚙️ Operations Department

#### Department Manager
- **Email:** peter.adams@nigcomsat.com
- **Name:** Peter Adams
- **Role:** Operations Manager
- **Permissions:** Can manage department tasks and users
- **Phone:** +234-811-234-5678

#### Task Workers
- **Email:** mary.wilson@nigcomsat.com
- **Name:** Mary Wilson
- **Role:** Operations Specialist
- **Skills:** Customer Support, Documentation
- **Phone:** +234-812-345-6789

### 🎯 Cross-Functional Project Managers (Global Access)

- **Email:** alex.garcia@nigcomsat.com
- **Name:** Alex Garcia
- **Role:** Project Manager
- **Permissions:** Can create and review tasks across all departments
- **Skills:** Project Management, Agile, Scrum
- **Phone:** +234-813-456-7890

- **Email:** sophia.martinez@nigcomsat.com
- **Name:** Sophia Martinez
- **Role:** Product Manager
- **Permissions:** Can create and review tasks across all departments
- **Skills:** Product Management, Strategy
- **Phone:** +234-814-567-8901

## Sample Tasks Created

The script also creates several sample tasks with different urgency levels:

1. **URGENT:** Fix login authentication bug (Engineering - John Smith)
2. **HIGH:** Q1 Marketing Campaign Planning (Marketing - Group task led by Emma Davis)
3. **HIGH:** Database performance optimization (Engineering - Mike Wilson)
4. **MEDIUM:** Update user dashboard UI (Engineering - Sarah Jones)
5. **MEDIUM:** Monthly financial report (Finance - Grace Johnson)
6. **LOW:** Customer feedback analysis (Operations - Mary Wilson)
7. **LOW:** API documentation update (Engineering - John Smith)

## Testing Scenarios

### 1. Permission Testing
- Login as **sarah.jones@nigcomsat.com** (Task Worker) - Should NOT see "Create Task" button
- Login as **john.smith@nigcomsat.com** (Task Creator) - Should see "Create Task" button
- Login as **lisa.brown@nigcomsat.com** (Team Lead) - Should see all team tasks and can review them

### 2. Cross-Department Access Testing
- Login as **david.clark@nigcomsat.com** (Department Manager) - Can see tasks from multiple departments
- Login as **alex.garcia@nigcomsat.com** (Project Manager) - Can see tasks from all departments

### 3. Task Assignment Testing
- Task Creators can only assign tasks to users within their department scope
- Department Managers can assign tasks across their directorate
- Project Managers can assign tasks to anyone

### 4. Urgency Visualization Testing
- Tasks are displayed with color-coded priority badges
- Urgent tasks show red indicators
- High priority tasks show orange indicators
- Medium priority tasks show yellow indicators
- Low priority tasks show gray indicators

## Setup Instructions

1. Run the SQL script `create_test_users.sql` against your PostgreSQL database
2. The script will create:
   - Additional departments if they don't exist
   - Roles with appropriate permissions
   - 14 test users with different permission levels
   - Sample tasks with various urgency levels
3. Use any of the email addresses above with password `password123` to login
4. Test different permission scenarios by logging in as different user types

## Recommended Testing Flow

1. **Start as Task Worker** (sarah.jones@nigcomsat.com) - See limited functionality
2. **Switch to Task Creator** (john.smith@nigcomsat.com) - See task creation abilities
3. **Try Department Manager** (david.clark@nigcomsat.com) - See broader access
4. **Test Project Manager** (alex.garcia@nigcomsat.com) - See global access
5. **Use Team Lead** (lisa.brown@nigcomsat.com) - See task review and approval features
# Nigcomsat Performance Management System - Complete Technical Specification

## System Overview & Architecture

Nigcomsat is a comprehensive performance management system designed to capture and track both organizational and individual employee performance through a structured, hierarchical approach. The system is built around a **4-level organizational structure** that provides flexible access control and clear reporting chains.

### Core Design Principles

**1. Hierarchical Organization Structure**
- **Fixed 4-Level Hierarchy**: Global → Directorate → Department → Unit
- This structure ensures consistency while providing granular control over access and reporting
- Global level represents the entire company (e.g., "Nigcomsat Management Office")
- Directorate level represents major business divisions (e.g., "Marketing", "Operations", "Technical")
- Department level represents functional units (e.g., "Human Resources", "Finance", "Engineering")
- Unit level represents teams or sub-groups within departments

**2. Scope-Based Access Control with Overrides**
- **Base Permissions**: Users inherit access based on their organizational position
- **Scope Overrides**: Special roles can access data beyond their organizational level
- **Cross-Cutting Permissions**: Departments like HR can access global data despite being department-level
- This hybrid approach solves the common challenge of departmental roles needing company-wide access

**3. Goal-Driven Performance Management**
- **Cascading Goals**: Yearly → Quarterly → Departmental goals create alignment
- **Auto-Achievement Logic**: Child goal completion automatically triggers parent goal achievement
- **Progress Tracking**: Both percentage-based (with reports) and binary achievement tracking

**4. Comprehensive Task Management**
- **Scope-Limited Creation**: Users can only create tasks within their organizational scope
- **Individual and Group Tasks**: Flexible assignment with team head coordination for groups
- **Approval Workflow**: Submit → Review → Score → Approve/Redo cycle
- **Performance Integration**: Task scores feed directly into individual performance data

---

## Database Schema Design & Explanations

### **Core Tables with Business Logic**

#### **organizations** - The Foundation of Access Control
```sql
id: UUID (Primary Key)
name: VARCHAR(255) NOT NULL
description: TEXT
level: ENUM('global', 'directorate', 'department', 'unit') NOT NULL
parent_id: UUID (Foreign Key → organizations.id)
created_at: TIMESTAMP
updated_at: TIMESTAMP

Indexes: parent_id, level
Constraints: 
- Only one global level allowed
- parent_id required except for global
- No circular references
```

**Purpose**: This table defines the entire organizational structure and serves as the foundation for all access control decisions. Every user is assigned to exactly one organizational unit, which determines their base access permissions.

**Business Logic**: 
- The hierarchy is strictly enforced - you cannot have departments without directorates, or units without departments
- Parent-child relationships enable tree traversal for access control (e.g., directorate users can access all departments under them)
- The single global constraint ensures there's always one clear top-level organization

#### **roles** - Permission Templates with Scope Overrides
```sql
id: UUID (Primary Key)
name: VARCHAR(255) NOT NULL UNIQUE
description: TEXT
is_leadership: BOOLEAN DEFAULT FALSE
scope_override: ENUM('none', 'global', 'cross_directorate') DEFAULT 'none'
permissions: JSON (Array of permission strings)
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

**Purpose**: Roles are permission templates that can be assigned to users. The `scope_override` field is the key innovation that solves cross-cutting access challenges.

**Business Logic**:
- **is_leadership**: When TRUE, users with this role automatically become leaders of their organizational level
- **scope_override**: Overrides the user's organizational scope for data access
  - `none`: Use organizational scope only
  - `global`: Access all organizational data regardless of position
  - `cross_directorate`: Access data across multiple directorates
- **permissions**: JSON array enables flexible permission assignment without rigid role hierarchies

**Example Usage**:
```json
// HR Manager Role
{
  "name": "HR Manager",
  "is_leadership": true,
  "scope_override": "global",
  "permissions": ["user_create", "user_edit", "user_view_all", "goal_create_departmental"]
}
```

#### **users** - Complete User Profiles with Status Management
```sql
id: UUID (Primary Key)
email: VARCHAR(255) NOT NULL UNIQUE
name: VARCHAR(255) NOT NULL
phone: VARCHAR(20)
address: TEXT
skillset: TEXT
level: VARCHAR(100)
job_title: VARCHAR(255)
organization_id: UUID (Foreign Key → organizations.id)
role_id: UUID (Foreign Key → roles.id)
status: ENUM('active', 'suspended', 'on_leave', 'archived') DEFAULT 'active'
password_hash: VARCHAR(255)
email_verified_at: TIMESTAMP
onboarding_token: VARCHAR(255)
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

**Purpose**: Stores complete user profiles with organizational assignment and status management that affects system behavior.

**Business Logic**:
- **organization_id + role_id**: Combined, these determine the user's effective permissions (role permissions + organizational scope + any overrides)
- **Status Impact on System Behavior**:
  - `active`: Full system access, appears in task assignment lists
  - `suspended`: No login, no task assignments, effectively blocked
  - `on_leave`: Can login and view but hidden from task assignments
  - `archived`: Historical preservation only, no system access
- **onboarding_token**: Enables secure first-time setup without exposing passwords

#### **user_history** - Comprehensive Audit Trail
```sql
id: UUID (Primary Key)
user_id: UUID (Foreign Key → users.id)
action: VARCHAR(100) NOT NULL (role_change, status_change, profile_edit, etc.)
old_value: JSON
new_value: JSON
admin_id: UUID (Foreign Key → users.id)
created_at: TIMESTAMP
```

**Purpose**: Maintains complete audit trail of all user changes for compliance and troubleshooting.

**Business Logic**: Every significant user change is logged with before/after values and the administrator who made the change. This enables rollback capabilities and compliance reporting.

#### **goals** - Hierarchical Goal Management
```sql
id: UUID (Primary Key)
title: VARCHAR(255) NOT NULL
description: TEXT
type: ENUM('yearly', 'quarterly', 'departmental') NOT NULL
evaluation_method: VARCHAR(255)
difficulty_level: INTEGER (1-5)
start_date: DATE NOT NULL
end_date: DATE NOT NULL
progress_percentage: INTEGER DEFAULT 0
status: ENUM('active', 'achieved', 'discarded') DEFAULT 'active'
parent_goal_id: UUID (Foreign Key → goals.id)
organization_id: UUID (Foreign Key → organizations.id, nullable for yearly/quarterly)
created_by: UUID (Foreign Key → users.id)
achieved_at: TIMESTAMP
discarded_at: TIMESTAMP
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

**Purpose**: Implements cascading goal system where quarterly goals support yearly goals, and departmental goals can support either.

**Business Logic**:
- **Goal Type Hierarchy**: Yearly (company-wide) → Quarterly (company-wide) → Departmental (specific departments)
- **parent_goal_id**: Creates parent-child relationships enabling cascading achievement
- **organization_id**: NULL for yearly/quarterly goals (company-wide), specific department ID for departmental goals
- **Auto-Achievement Logic**: When all non-discarded children are achieved, parent automatically achieves
- **Progress Tracking**: Goals without children can have manual percentage updates (requires reports)

#### **goal_progress_reports** - Progress Documentation
```sql
id: UUID (Primary Key)
goal_id: UUID (Foreign Key → goals.id)
old_percentage: INTEGER
new_percentage: INTEGER
report: TEXT NOT NULL
updated_by: UUID (Foreign Key → users.id)
created_at: TIMESTAMP
```

**Purpose**: Maintains history of manual progress updates with required justification reports.

**Business Logic**: Every manual progress update must include a report explaining the change. This ensures accountability and provides context for progress decisions.

#### **tasks** - Core Task Management
```sql
id: UUID (Primary Key)
title: VARCHAR(255) NOT NULL
description: TEXT
type: ENUM('individual', 'group') NOT NULL
due_date: DATETIME NOT NULL
status: ENUM('created', 'started', 'completed', 'approved', 'overdue') DEFAULT 'created'
score: INTEGER (1-10, nullable until reviewed)
feedback: TEXT
team_head_id: UUID (Foreign Key → users.id, nullable for individual tasks)
created_by: UUID (Foreign Key → users.id)
reviewed_at: TIMESTAMP
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

**Purpose**: Central task management with individual and group support, including performance scoring.

**Business Logic**:
- **Task Types**: Individual tasks assign to one person, group tasks require team head selection
- **Status Flow**: created → started → completed → approved (with overdue as parallel state)
- **Scoring System**: 1-10 scale applied after completion, feeds into performance evaluation
- **team_head_id**: For group tasks, the team head submits on behalf of entire group

#### **task_assignments** - Assignment Management
```sql
id: UUID (Primary Key)
task_id: UUID (Foreign Key → tasks.id)
user_id: UUID (Foreign Key → users.id)
created_at: TIMESTAMP

Composite Index: (task_id, user_id)
```

**Purpose**: Many-to-many relationship between tasks and users, enabling group task assignments.

**Business Logic**: Individual tasks have one assignment record, group tasks have multiple. All assigned users can view the task, but only the team head (for group tasks) can submit.

#### **task_submissions** - Submission Management
```sql
id: UUID (Primary Key)
task_id: UUID (Foreign Key → tasks.id)
report: TEXT NOT NULL
submitted_by: UUID (Foreign Key → users.id)
submitted_at: TIMESTAMP
```

**Purpose**: Stores task completion reports from assignees.

**Business Logic**: One submission per task. For individual tasks, the assignee submits. For group tasks, the team head submits on behalf of the group.

#### **task_documents** - Document Attachments
```sql
id: UUID (Primary Key)
task_id: UUID (Foreign Key → tasks.id)
file_name: VARCHAR(255) NOT NULL
file_path: VARCHAR(500) NOT NULL
uploaded_by: UUID (Foreign Key → users.id)
uploaded_at: TIMESTAMP
```

**Purpose**: Manages file attachments for task submissions.

**Business Logic**: Multiple documents can be attached to each task submission. File paths should be secure and access-controlled based on task visibility rules.

#### **task_extensions** - Deadline Management
```sql
id: UUID (Primary Key)
task_id: UUID (Foreign Key → tasks.id)
requested_by: UUID (Foreign Key → users.id)
new_due_date: DATETIME NOT NULL
reason: TEXT NOT NULL
status: ENUM('pending', 'approved', 'denied') DEFAULT 'pending'
reviewed_by: UUID (Foreign Key → users.id)
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

**Purpose**: Handles deadline extension requests and approvals.

**Business Logic**: When tasks become overdue, submissions are blocked until an extension is approved. Users can request extensions before or during overdue status. Only the task creator can approve extensions.

---

## API Endpoints with Business Logic

### **Authentication & Onboarding**
```
POST /api/auth/login - Standard login with email/password
POST /api/auth/logout - Session invalidation
POST /api/auth/onboard - Token-based first-time setup (password creation)
POST /api/auth/reset-password - Password reset via email
```

**Onboarding Flow**: New users receive email with secure token → use token to access onboarding page → set password → gain system access. This eliminates password distribution security issues.

### **Organization Management** (Super Admin Only)
```
GET    /api/organizations - Returns tree structure of entire organization
POST   /api/organizations - Create new organizational unit
PUT    /api/organizations/{id} - Edit existing unit (name, description)
DELETE /api/organizations/{id} - Delete unit (with dependency checking)
GET    /api/organizations/{id}/children - Get direct children of a unit
```

**Business Logic**: 
- DELETE operations must check for active users, goals, or tasks before allowing deletion
- Tree structure returned as nested JSON for frontend visualization
- Only users with `organization_create` permission can access these endpoints

### **Roles & Permissions**
```
GET    /api/roles - List all roles (filtered by admin scope)
POST   /api/roles - Create new role (admin only)
PUT    /api/roles/{id} - Modify existing role (admin only)
DELETE /api/roles/{id} - Remove role (check for active users first)
GET    /api/permissions - List all available permissions for role creation
```

**Business Logic**: Permission list is dynamically generated from all available system permissions. Role deletion blocked if assigned to active users.

### **User Management**
```
GET    /api/users - List users (filtered by requester's scope)
POST   /api/users - Create new user and send onboarding email
PUT    /api/users/{id} - Update user profile (scope-limited)
PUT    /api/users/{id}/status - Change user status (active/suspended/etc.)
GET    /api/users/{id}/history - View user change history
GET    /api/users/me - Current user's profile
PUT    /api/users/me - Self-edit limited fields (phone, address, etc.)
```

**Business Logic**: 
- Scope filtering ensures users only see other users within their organizational reach
- Status changes trigger email notifications and affect task assignment availability
- Self-edit capabilities are limited to non-critical fields (can't change role, organization)

### **Goals Management**
```
GET    /api/goals - List goals (filtered by scope and permissions)
POST   /api/goals - Create new goal (permission-gated by type)
PUT    /api/goals/{id} - Edit goal details
PUT    /api/goals/{id}/progress - Update progress percentage (requires report)
PUT    /api/goals/{id}/status - Mark achieved or discard
GET    /api/goals/{id}/children - Get child goals
POST   /api/goals/{id}/progress-report - Add progress report
```

**Business Logic**:
- Goal creation permissions: `goal_create_yearly`, `goal_create_quarterly`, `goal_create_departmental`
- Progress updates for goals without children require accompanying reports
- Status changes to 'achieved' trigger parent goal achievement check

### **Task Management**
```
GET    /api/tasks - List tasks (filtered by visibility rules)
POST   /api/tasks - Create new task (scope-limited assignment)
PUT    /api/tasks/{id}/status - Update task status (start/complete)
POST   /api/tasks/{id}/submit - Submit task report and documents
POST   /api/tasks/{id}/review - Review and score completed task
POST   /api/tasks/{id}/extension-request - Request deadline extension
PUT    /api/tasks/{id}/extension/{extension_id} - Approve/deny extension
GET    /api/tasks/{id}/submissions - View task submission details
```

**Business Logic**:
- Task visibility: Users see tasks they created, are assigned to, or lead (for group tasks)
- Scope-limited assignment: Can only assign users within creator's organizational scope
- Review process: Only task creators can review and score submissions
- Extension workflow: Overdue tasks block submission until extension approved

---

## Frontend User Flows with Detailed UX Logic

### **Organization Management Flow** (Super Admin)
1. **Dashboard Entry**: Super Admin Dashboard → "Organization Structure" tab
2. **Tree Visualization**: 
   - Display hierarchical tree with expand/collapse functionality
   - Color-coding by level (Global=blue, Directorate=green, Department=orange, Unit=gray)
   - Show user counts at each level
3. **Add Node Workflow**:
   - Click "Add Unit" → Modal opens
   - Select parent unit from dropdown (filtered by level constraints)
   - Choose level (automatically filtered based on parent)
   - Enter name and description
   - Validation: Prevent duplicate names within same parent
   - Save → Tree updates with new node
4. **Edit Node**: Click node → Inline edit or modal → Update details → Tree refreshes
5. **Delete Node**: 
   - Click node → Delete button
   - Confirmation modal showing impact (children count, user count)
   - Options: Delete all children OR Reassign children to different parent
   - Execute → Tree updates

**UX Considerations**: Tree should be visually intuitive with drag-and-drop future capability. Show loading states during operations. Provide undo capability for accidental deletions.

### **Role & Permission Flow** (Admin)
1. **Roles Dashboard**: Admin Dashboard → "Roles Management" tab
2. **Role List**: 
   - Searchable/filterable table of existing roles
   - Show role name, permission count, user count, leadership status
   - Quick actions: Edit, Delete, Duplicate
3. **Create Role Workflow**:
   - Click "Create Role" → Step-by-step wizard
   - Step 1: Basic info (name, description, leadership flag)
   - Step 2: Permission selection with grouped checkboxes (Organization, User, Goal, Task permissions)
   - Step 3: Scope override selection with explanations
   - Step 4: Review and save
4. **Permission Matrix View**: 
   - Grid showing all roles vs all permissions
   - Quick visual overview of role capabilities
   - Click cells to toggle permissions
5. **Role Assignment**: Handled during user creation/editing with role dropdown

**UX Considerations**: Permission selection should be intuitive with search, grouping, and descriptions. Provide role templates for common positions.

### **User Management Flow**
1. **User Dashboard**: 
   - Filterable user list (status, role, department)
   - Scope-limited view (can't see users outside organizational reach)
   - Quick actions: Edit, Suspend, Archive, View History
2. **Create User Workflow**:
   - Click "Add User" → Multi-step form
   - Step 1: Personal details (name, email, phone, address)
   - Step 2: Professional info (skillset, level, job title)
   - Step 3: Organizational assignment (department dropdown based on admin scope)
   - Step 4: Role selection (filtered by what admin can assign)
   - Save → Send onboarding email automatically
3. **User Profile Pages**:
   - Complete profile with edit capabilities (scope-limited)
   - History tab showing all changes with timestamps
   - Performance tab (task history, scores, goal participation)
   - Status management with one-click actions
4. **Bulk Operations**: Select multiple users → Bulk status change, role assignment

**UX Considerations**: Clear indication of scope limitations. Status changes should show immediate visual feedback. Onboarding email status tracking.

### **Goal Management Flow**
1. **Goals Dashboard**:
   - Hierarchical goal view with parent-child relationships
   - Filter by type, status, date range
   - Progress visualization with percentage bars
   - Goal timeline/Gantt chart view option
2. **Create Goal Workflow**:
   - Click "Create Goal" → Goal type selection (determines available options)
   - Basic info: Title, description, dates
   - Evaluation method and difficulty level
   - Parent goal selection (if applicable)
   - Department assignment (for departmental goals)
   - Save → Goal appears in hierarchy
3. **Goal Detail Pages**:
   - Complete goal information with edit capabilities
   - Progress tracking section
   - Child goals list (if any)
   - Progress reports history
   - Achievement timeline
4. **Progress Update**:
   - Manual percentage update with required report field
   - Auto-progress calculation for goals with children
   - Visual progress indicators throughout

**UX Considerations**: Goal relationships should be visually clear with tree/network diagrams. Progress updates need clear reporting requirements. Auto-achievement notifications.

### **Task Management Flow**
1. **Task Dashboard**:
   - Multiple views: My Tasks, Created Tasks, All Tasks (permission-dependent)
   - Kanban board by status (Created → Started → Completed → Approved)
   - Filter by due date, assignee, type, status
   - Overdue tasks prominently highlighted
2. **Create Task Workflow**:
   - Click "Create Task" → Task details form
   - Individual vs Group selection changes assignment UI
   - For groups: Multi-select users → Select team head from chosen users
   - Scope validation: Only show users within creator's organizational reach
   - Save → Notifications sent to assigned users
3. **Task Detail Pages**:
   - Complete task information
   - Assignment details with user profiles
   - Submission section (for assignees)
   - Review section (for creators)
   - Document attachments
   - Extension requests
4. **Task Workflows**:
   - **Start Task**: Simple status update
   - **Submit Task**: Upload report + documents → Notify creator
   - **Review Task**: Score (1-10) + feedback → Approve/Request redo
   - **Extension Request**: New date + reason → Awaits creator approval

**UX Considerations**: Clear visual indicators for task states. Drag-and-drop file upload. Real-time notifications. Overdue tasks need prominent warnings.

---

## Core Business Logic with Implementation Details

### **Permission System Architecture**

The permission system combines role-based permissions with organizational scope and overrides:

```javascript
// User Effective Permissions Calculation
function calculateUserPermissions(user) {
  const rolePermissions = user.role.permissions;
  const baseScope = getUserOrganizationalScope(user.organization_id);
  const effectiveScope = user.role.scope_override || baseScope;
  
  return {
    permissions: rolePermissions,
    scope: effectiveScope,
    isLeader: user.role.is_leadership
  };
}

// Scope Access Check
function userCanAccessOrganization(user, targetOrgId) {
  const userPerms = calculateUserPermissions(user);
  
  switch(userPerms.scope) {
    case 'global':
      return true;
    case 'cross_directorate':
      return isWithinDirectorateNetwork(user.organization_id, targetOrgId);
    default:
      return isWithinOrganizationalTree(user.organization_id, targetOrgId);
  }
}
```

### **Goal Achievement Cascade Logic**

Goals automatically achieve when all non-discarded children are achieved:

```javascript
// Auto-Achievement Check (run after any child goal status change)
function checkGoalAutoAchievement(goalId) {
  const goal = getGoal(goalId);
  const children = getChildGoals(goalId);
  
  if (children.length === 0) return; // No auto-achievement for leaf goals
  
  const nonDiscardedChildren = children.filter(child => child.status !== 'discarded');
  const achievedChildren = nonDiscardedChildren.filter(child => child.status === 'achieved');
  
  if (achievedChildren.length === nonDiscardedChildren.length && nonDiscardedChildren.length > 0) {
    goal.status = 'achieved';
    goal.achieved_at = new Date();
    goal.progress_percentage = 100;
    updateGoal(goal);
    
    // Recursively check parent goal
    if (goal.parent_goal_id) {
      checkGoalAutoAchievement(goal.parent_goal_id);
    }
    
    // Send notifications
    notifyGoalStakeholders(goal, 'auto_achieved');
  }
}
```

### **Task Visibility & Access Logic**

Tasks have complex visibility rules based on involvement and permissions:

```javascript
// Task Visibility Check
function userCanSeeTask(user, task) {
  // Creator can always see their tasks
  if (task.created_by === user.id) return true;
  
  // Assigned users can see their tasks
  if (task.assignments.some(assignment => assignment.user_id === user.id)) return true;
  
  // Team heads can see group tasks they lead
  if (task.type === 'group' && task.team_head_id === user.id) return true;
  
  // Special permission holders within scope
  if (user.permissions.includes('task_view_all')) {
    return userCanAccessOrganization(user, getTaskOrganizationalScope(task));
  }
  
  return false;
}

// Task Creation Scope Validation
function validateTaskAssignment(creator, assigneeIds) {
  for (const assigneeId of assigneeIds) {
    const assignee = getUser(assigneeId);
    if (!userCanAccessOrganization(creator, assignee.organization_id)) {
      throw new Error(`Cannot assign task to user outside your scope`);
    }
    if (assignee.status !== 'active') {
      throw new Error(`Cannot assign task to inactive user: ${assignee.name}`);
    }
  }
}
```

### **Overdue Task Management**

Daily cron job manages overdue status and submission blocking:

```javascript
// Daily Task Status Update (Cron Job)
function updateOverdueTasks() {
  const now = new Date();
  const activeTasks = getTasksByStatus(['created', 'started', 'completed']);
  
  for (const task of activeTasks) {
    if (task.due_date < now && task.status !== 'approved') {
      task.status = 'overdue';
      updateTask(task);
      
      // Notify stakeholders
      notifyTaskStakeholders(task, 'overdue');
    }
  }
}

// Submission Blocking for Overdue Tasks
function canSubmitTask(task) {
  if (task.status === 'overdue') {
    const pendingExtensions = getTaskExtensions(task.id, 'pending');
    return pendingExtensions.length === 0; // Can only submit if no pending extensions
  }
  return task.status === 'started';
}
```

---

## Integration Points & Data Flow

### **Cross-Feature Dependencies**

The system has several critical integration points:

**1. User → Organization → Role Chain**
- User profiles depend on valid organizational assignment
- Role permissions are meaningless without organizational scope context
- Changes to any component affect user access across entire system

**2. Goal → Organization Hierarchy**
- Departmental goals must belong to valid departments
- Goal access permissions depend on organizational scope
- Goal reporting follows organizational reporting chains

**3. Task → User → Organization Scope**
- Task creation is limited by organizational scope
- Task assignment must respect organizational boundaries
- Task visibility follows organizational access rules

**4. Performance Data Flow**
- Task scores feed into individual performance metrics
- Goal achievement contributes to organizational KPIs
- User status affects task assignment and goal participation

### **Real-time Notification System**

Key events that trigger notifications:

```javascript
// Notification Triggers
const notificationTriggers = {
  // Goal-related
  'goal_auto_achieved': (goal) => notifyGoalStakeholders(goal),
  'goal_progress_updated': (goal, report) => notifyGoalOwners(goal),
  'goal_discarded': (goal, reason) => notifyGoalStakeholders(goal),
  
  // Task-related
  'task_assigned': (task, assignees) => notifyUsers(assignees),
  'task_submitted': (task, submission) => notifyTaskCreator(task),
  'task_approved': (task, score) => notifyTaskAssignees(task),
  'task_redo_requested': (task, feedback) => notifyTaskAssignees(task),
  'task_overdue': (task) => notifyTaskStakeholders(task),
  'task_extension_requested': (task, extension) => notifyTaskCreator(task),
  
  // User-related
  'user_status_changed': (user, oldStatus, newStatus) => notifyRelevantUsers(user),
  'user_role_changed': (user, oldRole, newRole) => notifyAdministrators(user)
};
```

### **Data Consistency Rules**

Critical constraints that maintain system integrity:

**1. Organizational Hierarchy Integrity**
- Cannot delete organization with active users or sub-organizations
- Moving organizations must maintain valid parent-child relationships
- No circular references allowed in organizational tree

**2. User-Role-Organization Consistency**
- Cannot assign user to organization outside admin's scope
- Cannot assign role with higher permissions than admin possesses
- User status changes must update all related entities (task assignments, etc.)

**3. Goal Relationship Integrity**
- Goal parent-child relationships must be acyclic
- Cannot delete goal with active child goals
- Date ranges must be logical (start < end, children within parent range)

**4. Task Assignment Validity**
- Cannot assign tasks to users outside creator's scope
- Cannot assign tasks to inactive users
- Team head must be selected from assigned group members

---

## Validation Rules & Error Handling

### **Organization Management Validation**

```javascript
// Organization Creation Validation
function validateOrganizationCreation(org) {
  // Level-specific validation
  if (org.level === 'global' && globalOrganizationExists()) {
    throw new ValidationError('Only one global organization allowed');
  }
  
  if (org.level !== 'global' && !org.parent_id) {
    throw new ValidationError('Non-global organizations must have a parent');
  }
  
  // Hierarchy validation
  if (org.parent_id) {
    const parent = getOrganization(org.parent_id);
    if (!isValidParentChild(parent.level, org.level)) {
      throw new ValidationError('Invalid parent-child relationship');
    }
  }
  
  // Name uniqueness within parent
  if (siblingWithNameExists(org.parent_id, org.name)) {
    throw new ValidationError('Organization name must be unique within parent');
  }
}
```

### **User Management Validation**

```javascript
// User Creation Validation
function validateUserCreation(user, creator) {
  // Email uniqueness
  if (emailExists(user.email)) {
    throw new ValidationError('Email already exists');
  }
  
  // Scope validation
  if (!userCanAccessOrganization(creator, user.organization_id)) {
    throw new ValidationError('Cannot create user outside your organizational scope');
  }
  
  // Role assignment validation
  if (!canAssignRole(creator, user.role_id)) {
    throw new ValidationError('Cannot assign role with higher permissions than yours');
  }
  
  // Leadership conflict check
  const role = getRole(user.role_id);
  if (role.is_leadership && leadershipConflictExists(user.organization_id, role)) {
    throw new ValidationError('Leadership role conflict - position already filled');
  }
}
```

### **Goal Management Validation**

```javascript
// Goal Creation Validation
function validateGoalCreation(goal, creator) {
  // Permission check
  const requiredPermission = `goal_create_${goal.type}`;
  if (!creator.permissions.includes(requiredPermission)) {
    throw new ValidationError(`Missing permission: ${requiredPermission}`);
  }
  
  // Date validation
  if (goal.start_date >= goal.end_date) {
    throw new ValidationError('Start date must be before end date');
  }
  
  // Parent relationship validation
  if (goal.parent_goal_id) {
    const parent = getGoal(goal.parent_goal_id);
    if (!isValidGoalParentChild(parent, goal)) {
      throw new ValidationError('Invalid parent-child goal relationship');
    }
  }
  
  // Organizational scope validation
  if (goal.organization_id && !userCanAccessOrganization(creator, goal.organization_id)) {
    throw new ValidationError('Cannot create goal for organization outside your scope');
  }
}
```

### **Task Management Validation**

```javascript
// Task Creation Validation
function validateTaskCreation(task, creator) {
  // Assignment scope validation
  validateTaskAssignment(creator, task.assignee_ids);
  
  // Group task validation
  if (task.type === 'group') {
    if (task.assignee_ids.length < 2) {
      throw new ValidationError('Group tasks must have at least 2 assignees');
    }
    if (!task.assignee_ids.includes(task.team_head_id)) {
      throw new ValidationError('Team head must be selected from assigned group members');
    }
  }
  
  // Due date validation
  if (task.due_date <= new Date()) {
    throw new ValidationError('Due date must be in the future');
  }
  
  // Individual task validation
  if (task.type === 'individual' && task.assignee_ids.length !== 1) {
    throw new ValidationError('Individual tasks must have exactly one assignee');
  }
}
```

---

## Complete Permission Definitions

### **Organization Permissions**
- `organization_create` - Create new organizational units at any level
- `organization_edit` - Modify existing organizational unit details
- `organization_delete` - Remove organizational units (with dependency checks)
- `organization_view_all` - View complete organizational structure regardless of scope

### **Role Management Permissions**
- `role_create` - Create new role definitions
- `role_edit` - Modify existing role permissions and settings
- `role_delete` - Remove roles (blocked if assigned to active users)
- `role_assign` - Assign roles to users within scope
- `role_view_all` - View all roles regardless of scope limitations

### **User Management Permissions**
- `user_create` - Add new users to the system
- `user_edit` - Modify user profiles and assignments
- `user_suspend` - Temporarily suspend user access
- `user_activate` - Reactivate suspended users
- `user_archive` - Permanently archive user accounts
- `user_view_all` - View users outside organizational scope
- `user_history_view` - Access user change history logs

### **Goal Management Permissions**
- `goal_create_yearly` - Create company-wide yearly goals
- `goal_create_quarterly` - Create company-wide quarterly goals
- `goal_create_departmental` - Create department-specific goals
- `goal_edit` - Modify goal details and settings
- `goal_progress_update` - Update manual goal progress percentages
- `goal_status_change` - Mark goals as achieved or discarded
- `goal_view_all` - View goals outside organizational scope

### **Task Management Permissions**
- `task_create` - Create new tasks within scope
- `task_assign` - Assign tasks to users within scope
- `task_edit` - Modify task details and assignments
- `task_review` - Review completed tasks and assign scores
- `task_view_all` - View all tasks within organizational scope
- `task_extend_deadline` - Approve deadline extension requests
- `task_delete` - Remove tasks (limited conditions)

### **System Administration Permissions**
- `system_admin` - Full system access (super admin capabilities)
- `reports_generate` - Generate system-wide reports
- `audit_access` - Access system audit logs
- `notification_manage` - Configure system notifications
- `backup_access` - Access system backup functions

---

## Implementation Recommendations

### **Development Phases**

**Phase 1: Foundation (Organization + Roles + Users)**
- Implement organizational structure with tree management
- Build role-based permission system with scope overrides
- Create user management with status tracking and onboarding
- Essential for all other features to function

**Phase 2: Goal System**
- Implement hierarchical goal management
- Build auto-achievement cascade logic
- Add progress tracking with reporting requirements
- Provides performance direction framework

**Phase 3: Task Management**
- Build task creation with scope validation
- Implement individual and group task workflows
- Add submission, review, and scoring system
- Creates performance data through task completion

**Phase 4: Integration & Optimization**
- Add real-time notifications across all features
- Implement comprehensive audit logging
- Build performance analytics preparation layer
- Optimize queries and add caching where needed

### **Security Considerations**

**Authentication & Authorization**
- Implement JWT tokens with appropriate expiration
- Use secure password hashing (bcrypt with high cost factor)
- Add rate limiting on authentication endpoints
- Implement proper session management

**Data Access Control**
- Always validate organizational scope before data access
- Implement row-level security for sensitive operations
- Add audit logging for all data modification operations
- Use parameterized queries to prevent SQL injection

**File Upload Security**
- Validate file types and sizes for task attachments
- Store files outside web root with access controls
- Scan uploaded files for malware
- Implement proper access controls based on task visibility

### **Performance Optimization**

**Database Optimization**
- Add proper indexes on frequently queried columns
- Consider materialized views for complex organizational queries
- Implement query caching for organizational tree structures
- Use database-level constraints to maintain data integrity

**Application Optimization**
- Cache user permissions to avoid repeated calculations
- Implement efficient organizational tree traversal algorithms
- Use background jobs for non-critical operations (notifications, reports)
- Consider Redis for session management and caching

 
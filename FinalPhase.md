# Nigcomsat PMS - Review & Performance Management System Implementation

## System Overview

This document outlines the implementation of the Review and Performance Management system for the Nigcomsat Performance Management System, built on the 4-level organizational hierarchy (Global → Directorate → Department → Unit) with scope-based access control.

## Database Schema for Review & Performance

### **review_traits** - Configurable Performance Traits
```sql
id: UUID (Primary Key)
name: VARCHAR(255) NOT NULL
description: TEXT
is_active: BOOLEAN DEFAULT TRUE
display_order: INTEGER
created_by: UUID (Foreign Key → users.id)
created_at: TIMESTAMP
updated_at: TIMESTAMP

Indexes: display_order, is_active
Constraints: Unique name across active traits
```

**Purpose**: Allows administrators to define custom performance traits (e.g., "Communication", "Leadership", "Technical Skills") rather than hard-coded categories.

### **review_questions** - Trait-Specific Questions
```sql
id: UUID (Primary Key)
trait_id: UUID (Foreign Key → review_traits.id)
question_text: TEXT NOT NULL
applies_to_self: BOOLEAN DEFAULT TRUE
applies_to_peer: BOOLEAN DEFAULT TRUE
applies_to_supervisor: BOOLEAN DEFAULT TRUE
is_active: BOOLEAN DEFAULT TRUE
created_by: UUID (Foreign Key → users.id)
created_at: TIMESTAMP
updated_at: TIMESTAMP

Indexes: trait_id, is_active
```

**Purpose**: Stores questions linked to traits, with flags indicating which review types (self/peer/supervisor) should use each question.

### **review_cycles** - Review Period Management
```sql
id: UUID (Primary Key)
name: VARCHAR(255) NOT NULL
description: TEXT
year: INTEGER NOT NULL
quarter: INTEGER NOT NULL (1-4)
start_date: DATE NOT NULL
end_date: DATE NOT NULL
status: ENUM('draft', 'active', 'completed', 'archived') DEFAULT 'draft'
peer_review_count: INTEGER DEFAULT 5
auto_assign_peers: BOOLEAN DEFAULT TRUE
created_by: UUID (Foreign Key → users.id)
created_at: TIMESTAMP
updated_at: TIMESTAMP

Indexes: year, quarter, status
Constraints: Unique (year, quarter)
```

**Purpose**: Defines review periods with configurable settings for peer assignment counts and automation.

### **review_cycle_traits** - Cycle-Specific Trait Selection
```sql
id: UUID (Primary Key)
cycle_id: UUID (Foreign Key → review_cycles.id)
trait_id: UUID (Foreign Key → review_traits.id)
is_active: BOOLEAN DEFAULT TRUE
created_at: TIMESTAMP

Indexes: cycle_id, trait_id
Constraints: Unique (cycle_id, trait_id)
```

**Purpose**: Links specific traits to review cycles, allowing different cycles to measure different traits.

### **review_assignments** - Individual Review Tasks
```sql
id: UUID (Primary Key)
cycle_id: UUID (Foreign Key → review_cycles.id)
reviewer_id: UUID (Foreign Key → users.id)
reviewee_id: UUID (Foreign Key → users.id)
review_type: ENUM('self', 'peer', 'supervisor') NOT NULL
status: ENUM('pending', 'in_progress', 'completed', 'overdue') DEFAULT 'pending'
completed_at: TIMESTAMP
created_at: TIMESTAMP
updated_at: TIMESTAMP

Indexes: cycle_id, reviewer_id, reviewee_id, review_type, status
Constraints: Unique (cycle_id, reviewer_id, reviewee_id, review_type)
```

**Purpose**: Tracks individual review assignments with completion status.

**Business Logic**:
- Self reviews: reviewer_id = reviewee_id
- Peer reviews: Different users within same organizational scope
- Supervisor reviews: Direct manager reviews direct report

### **review_responses** - Question Responses
```sql
id: UUID (Primary Key)
assignment_id: UUID (Foreign Key → review_assignments.id)
question_id: UUID (Foreign Key → review_questions.id)
rating: INTEGER NOT NULL (1-5)
comment: TEXT
created_at: TIMESTAMP
updated_at: TIMESTAMP

Indexes: assignment_id, question_id
Constraints: Unique (assignment_id, question_id), rating BETWEEN 1 AND 5
```

**Purpose**: Stores individual question responses with 1-5 rating scale and optional comments.

### **review_scores** - Calculated Performance Scores
```sql
id: UUID (Primary Key)
cycle_id: UUID (Foreign Key → review_cycles.id)
user_id: UUID (Foreign Key → users.id)
trait_id: UUID (Foreign Key → review_traits.id)
self_score: DECIMAL(3,2) (Average of self-assessment responses for this trait)
peer_score: DECIMAL(3,2) (Average of peer responses for this trait)
supervisor_score: DECIMAL(3,2) (Supervisor score for this trait)
weighted_score: DECIMAL(3,2) (Final calculated score: self*0.2 + peer*0.3 + supervisor*0.5)
calculated_at: TIMESTAMP
created_at: TIMESTAMP
updated_at: TIMESTAMP

Indexes: cycle_id, user_id, trait_id
Constraints: Unique (cycle_id, user_id, trait_id)
```

**Purpose**: Stores calculated trait scores using the weighted formula defined in the documentation.

### **performance_scores** - Overall Performance Tracking
```sql
id: UUID (Primary Key)
user_id: UUID (Foreign Key → users.id)
cycle_id: UUID (Foreign Key → review_cycles.id)
task_performance_score: DECIMAL(5,2) (Calculated from task scores)
review_performance_score: DECIMAL(5,2) (Average of all trait weighted_scores)
overall_performance_score: DECIMAL(5,2) (task_score*0.6 + review_score*0.4)
performance_band: ENUM('outstanding', 'exceeds_expectations', 'meets_expectations', 'below_expectations', 'needs_improvement')
organization_rank: INTEGER
department_rank: INTEGER
directorate_rank: INTEGER
calculated_at: TIMESTAMP
created_at: TIMESTAMP
updated_at: TIMESTAMP

Indexes: user_id, cycle_id, overall_performance_score, performance_band
Constraints: Unique (user_id, cycle_id)
```

**Purpose**: Combines task performance and review performance into overall scores with organizational rankings.

## Business Logic Implementation

### **Review Cycle Management**

#### **Cycle Creation Process**
1. **Admin creates cycle** with basic information (year, quarter, dates)
2. **Trait selection** from available active traits
3. **Question configuration** - system shows questions linked to selected traits
4. **Assignment settings** - peer count, department filtering rules
5. **Cycle activation** - generates all review assignments automatically

#### **Automatic Assignment Generation**
```javascript
function generateReviewAssignments(cycleId) {
  const cycle = getReviewCycle(cycleId);
  const activeUsers = getActiveUsers();

  for (const user of activeUsers) {
    // Generate self-review assignment
    createReviewAssignment(cycleId, user.id, user.id, 'self');

    // Generate supervisor review if user has supervisor
    if (user.supervisor_id) {
      createReviewAssignment(cycleId, user.supervisor_id, user.id, 'supervisor');
    }

    // Generate peer reviews within same department
    const peers = getDepartmentPeers(user.organization_id, user.id);
    const selectedPeers = selectRandomPeers(peers, cycle.peer_review_count);

    for (const peer of selectedPeers) {
      createReviewAssignment(cycleId, peer.id, user.id, 'peer');
    }
  }

  // Update cycle status to active
  updateReviewCycle(cycleId, { status: 'active' });
}
```

### **Score Calculation Logic**

#### **Trait Score Calculation**
```javascript
function calculateTraitScores(cycleId, userId, traitId) {
  // Get all responses for this user/trait combination
  const selfResponses = getReviewResponses(cycleId, userId, userId, traitId);
  const peerResponses = getPeerReviewResponses(cycleId, userId, traitId);
  const supervisorResponses = getSupervisorReviewResponses(cycleId, userId, traitId);

  // Calculate averages
  const selfScore = calculateAverage(selfResponses.map(r => r.rating));
  const peerScore = calculateAverage(peerResponses.map(r => r.rating));
  const supervisorScore = calculateAverage(supervisorResponses.map(r => r.rating));

  // Apply weighting: Self 20%, Peer 30%, Supervisor 50%
  const weightedScore = (selfScore * 0.2) + (peerScore * 0.3) + (supervisorScore * 0.5);

  // Store calculated scores
  createOrUpdateReviewScore(cycleId, userId, traitId, {
    self_score: selfScore,
    peer_score: peerScore,
    supervisor_score: supervisorScore,
    weighted_score: weightedScore
  });

  return weightedScore;
}
```

#### **Overall Performance Score Calculation**
```javascript
function calculateOverallPerformance(cycleId, userId) {
  // Get task performance score from task system
  const taskScore = calculateTaskPerformanceScore(userId, cycleId);

  // Get review performance score (average of all trait scores)
  const traitScores = getTraitScores(cycleId, userId);
  const reviewScore = calculateAverage(traitScores.map(t => t.weighted_score));

  // Combine scores: Task 60%, Review 40%
  const overallScore = (taskScore * 0.6) + (reviewScore * 0.4);

  // Determine performance band
  const performanceBand = determinePerformanceBand(overallScore);

  // Calculate rankings within organizational levels
  const rankings = calculateRankings(userId, overallScore);

  // Store performance record
  createOrUpdatePerformanceScore(userId, cycleId, {
    task_performance_score: taskScore,
    review_performance_score: reviewScore,
    overall_performance_score: overallScore,
    performance_band: performanceBand,
    organization_rank: rankings.organization,
    department_rank: rankings.department,
    directorate_rank: rankings.directorate
  });
}
```

### **Performance Band Determination**
```javascript
function determinePerformanceBand(score) {
  if (score >= 4.5) return 'outstanding';
  if (score >= 4.0) return 'exceeds_expectations';
  if (score >= 3.0) return 'meets_expectations';
  if (score >= 2.0) return 'below_expectations';
  return 'needs_improvement';
}
```

### **Task Performance Integration**
```javascript
function calculateTaskPerformanceScore(userId, cycleId) {
  const cycle = getReviewCycle(cycleId);
  const tasks = getUserTasksInPeriod(userId, cycle.start_date, cycle.end_date);

  if (tasks.length === 0) return 3.0; // Default baseline score

  const completedTasks = tasks.filter(t => t.status === 'approved');
  const completionRate = completedTasks.length / tasks.length;

  // Calculate average task score (convert 1-10 scale to 1-5 scale)
  const averageScore = calculateAverage(completedTasks.map(t => t.score)) / 2;

  // Combine completion rate and quality
  return (completionRate * 0.3) + (averageScore * 0.7);
}
```

## API Endpoints

### **Trait Management** (Admin Only)
```
GET    /api/review/traits - List all traits with question counts
POST   /api/review/traits - Create new performance trait
PUT    /api/review/traits/{id} - Update trait details
DELETE /api/review/traits/{id} - Deactivate trait (preserve data)
POST   /api/review/traits/reorder - Update display order

GET    /api/review/traits/{id}/questions - Get questions for trait
POST   /api/review/traits/{id}/questions - Add question to trait
PUT    /api/review/questions/{id} - Update question
DELETE /api/review/questions/{id} - Remove question
```

### **Review Cycle Management**
```
GET    /api/review/cycles - List cycles (filtered by user scope)
POST   /api/review/cycles - Create new review cycle
PUT    /api/review/cycles/{id} - Update cycle (draft only)
POST   /api/review/cycles/{id}/activate - Generate assignments and activate
GET    /api/review/cycles/{id}/analytics - Cycle completion and score analytics
```

### **Review Completion**
```
GET    /api/review/assignments/me - My pending review assignments
GET    /api/review/assignments/{id}/form - Review form with trait questions
POST   /api/review/assignments/{id}/submit - Submit completed review
PUT    /api/review/assignments/{id}/save - Save draft responses
```

### **Performance Analytics**
```
GET    /api/performance/overview - Organization-wide performance metrics
GET    /api/performance/rankings - Employee rankings with filters
GET    /api/performance/departments - Department performance comparison
GET    /api/performance/users/{id} - Individual performance profile
GET    /api/performance/me - Personal performance dashboard
```

## Access Control & Permissions

### **Review-Specific Permissions**
- `review_cycle_create` - Create and manage review cycles
- `review_trait_manage` - Create and edit performance traits
- `review_assign` - Manually assign additional reviewers
- `review_analytics_view` - Access organization-wide review analytics
- `performance_view_all` - View performance data outside organizational scope

### **Review Visibility Rules**
- **Employees** can see their own reviews and performance
- **Supervisors** can see direct reports' reviews and performance
- **Admins** can see reviews within their organizational scope
- **HR roles** with scope overrides can see global review data

## Integration with Existing Systems

### **Task System Integration**
- Task scores feed into performance calculations
- Task completion rates affect overall performance scores
- Task performance contributes 60% of overall score

### **Goal System Integration**
- Goal achievement can influence performance band determination
- Exceptional goal achievement may boost performance scores
- Goal participation tracked as part of performance evaluation

### **Organizational Hierarchy Integration**
- Performance rankings calculated at each organizational level
- Review assignments respect organizational boundaries
- Access control follows existing scope-based permissions

This implementation provides a comprehensive review and performance management system that integrates seamlessly with the existing Nigcomsat PMS architecture while maintaining the flexible, configurable approach defined in the main documentation.
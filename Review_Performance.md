# Nigcomsat PMS - Review & Performance Management with Custom Traits & Visualizations

## Review Management System - Flexible Trait Configuration

### **Custom Trait Management**

#### **Trait Configuration by Admin**
Instead of hard-coded traits, admins can fully customize what to measure:

**Trait Management Interface:**
- **Add New Trait**: Create custom traits like "Communication", "Innovation", "Customer Focus"  
- **Edit Existing Traits**: Modify trait names and descriptions
- **Delete Traits**: Remove traits no longer needed (with data preservation)
- **Reorder Traits**: Set priority order for display in reviews

**Question Bank Management:**
- **Question Creation**: Write custom questions for each trait
- **Trait Assignment**: Link questions to specific traits they measure
- **Question Types**: All questions use 1-5 rating scale + optional comments
- **Review Type Targeting**: Set which review types (self/peer/supervisor) use which questions

**Example Trait Configuration:**
```
Trait: "Communication Skills"
├── Question 1: "How effectively does this person communicate ideas?" (Peer + Supervisor)
├── Question 2: "Rate your ability to explain complex concepts clearly" (Self only)
└── Question 3: "How well does this person listen and respond to feedback?" (All types)

Trait: "Leadership Potential"  
├── Question 1: "How often does this person take initiative on projects?" (Peer + Supervisor)
├── Question 2: "Rate your comfort level leading team discussions" (Self only)
└── Question 3: "How effectively does this person motivate others?" (Supervisor only)
```

### **Review Cycle Creation with Custom Traits**

#### **Enhanced Cycle Setup Process**
**Step 1: Basic Cycle Information**
- Quarter/Year selection
- Review period dates
- Cycle name and description

**Step 2: Trait Selection & Configuration**  
- **Select Active Traits**: Choose which traits to measure in this cycle (from available trait library)
- **Question Assignment**: System shows questions linked to selected traits
- **Review Type Configuration**: Confirm which review types use which questions
- **Preview Mode**: Admin can preview how review forms will look to employees

**Step 3: Assignment Settings**
- **Peer Review Count**: Set how many peers each person reviews (default: 5)
- **Department Filtering**: Confirm peer assignments stay within departments
- **Supervisor Validation**: Ensure supervisor relationships are current

### **Review Scoring with Custom Traits**

#### **Trait-Specific Scoring Logic**
Each trait gets calculated separately using the weighted formula:

**Per-Trait Calculation:**
- **Self Review Score**: Average of self-assessment questions for this trait
- **Peer Review Score**: Average across all peer reviewers for this trait  
- **Supervisor Score**: Supervisor's assessment for this trait
- **Final Trait Score**: (Self × 20%) + (Peer × 30%) + (Supervisor × 50%)

**Overall Review Performance:**
- **Trait Averages**: Calculate final score for each selected trait
- **Overall Score**: Average of all trait scores for the employee
- **Trait Rankings**: Individual ranking per trait across organization

---

## Review Visualization & Navigation System

### **Review Management Dashboard Hierarchy**

#### **Top Level: Review Cycles Overview** (`/reviews`)
**Visual Layout:**
- **Cycle Timeline**: Horizontal timeline showing all review cycles (past, current, future)
- **Active Cycle Card**: Large prominent card showing current active cycle with progress metrics
- **Cycle Status Indicators**: Visual progress bars and completion percentages
- **Quick Actions**: "Create New Cycle", "View All Cycles", "Analytics"

**Cycle Cards Display:**
```
┌─── Q1 2024 Review Cycle ────┐
│ Status: Completed ✓         │
│ Participation: 94% (188/200)│  
│ Avg Score: 3.8/5           │
│ Duration: Jan 15 - Feb 5    │
│ [View Details] [Analytics]  │
└────────────────────────────┘
```

#### **Cycle Detail View** (`/reviews/cycles/{cycle-id}`)

**Navigation Tabs:**
- **Overview**: Cycle summary and key metrics
- **Participation**: Employee completion tracking  
- **Analytics**: Cycle-wide performance insights
- **Settings**: Cycle configuration (if still in draft)

**Overview Tab Visualizations:**

**Participation Tracking Section:**
- **Completion Progress Ring**: Circular progress showing overall completion %
- **Department Breakdown**: Horizontal bar charts showing completion by department
- **Review Type Progress**: Separate tracking for self, peer, supervisor completion rates
- **Late Submissions Alert**: Red-flagged employees with overdue reviews

**Performance Analytics Section:**  
- **Trait Distribution Charts**: Box plots showing score distribution for each trait across organization
- **Department Comparison**: Radar charts comparing department averages per trait
- **Score Trending**: Line graphs showing how trait scores compare to previous cycles

#### **Individual Employee Review Detail** (`/reviews/cycles/{cycle-id}/employees/{user-id}`)

**Employee Review Profile:**
- **Employee Header**: Photo, name, department, role, supervisor
- **Review Status Dashboard**: Visual grid showing completed/pending reviews

**Review Status Grid:**
```
┌─ Self Review ─┐  ┌─ Peer Reviews ─┐  ┌─ Supervisor ─┐
│ ✓ Completed   │  │ ✓ ✓ ✓ ○ ○     │  │ ✓ Completed  │  
│ Score: 3.9/5  │  │ 3 of 5 Done   │  │ Score: 4.2/5 │
└───────────────┘  └───────────────┘  └──────────────┘
```

**Trait Breakdown Visualization:**
- **Trait Performance Radar**: Spider/radar chart showing all trait scores
- **Score Source Breakdown**: Stacked bar chart showing self/peer/supervisor contribution per trait
- **Historical Comparison**: Line chart comparing trait scores across quarters

**Detailed Response View:**
- **Question-by-Question Analysis**: Expandable sections showing responses to each question
- **Peer Response Consistency**: Show range and average of peer responses
- **Comment Compilation**: All text feedback organized by trait and reviewer type

---

## Performance Management Visualizations

### **Organization-Wide Performance Dashboard** (`/performance`)

#### **Admin/Manager Performance Overview**

**Top-Level Metrics Cards:**
- **Company Average Score**: Large prominent display (e.g., 78.5/100)
- **Performance Distribution**: Bell curve showing score ranges across organization  
- **Top Performers Count**: Number of employees in "Outstanding" category
- **Improvement Needed**: Count of employees requiring performance plans

**Performance Visualization Suite:**

**Department Performance Comparison:**
- **Department Scoreboard**: Table with sortable columns (Avg Score, Task Performance, Review Performance, Employee Count)
- **Department Radar Chart**: Multi-axis comparison of departmental averages
- **Performance Trend Lines**: Department performance trends over last 4 quarters

**Employee Rankings Interface:**
- **Organization Leaderboard**: Sortable table with search and filtering
- **Filter Controls**: 
  - Department dropdown (Marketing, Operations, Technical, HR)
  - Directorate dropdown (based on selected departments)  
  - Performance band filter (Outstanding, Exceeds, Meets, Below, Needs Improvement)
  - Date range selector for historical views

**Ranking Table Columns:**
```
Rank | Name | Department | Overall Score | Task Score | Review Score | Band | Trend
-----|------|------------|---------------|------------|--------------|------|------  
  1  | Sarah Johnson | Marketing | 92.3 | 90.1 | 95.2 | Outstanding | ↗
  2  | Mike Chen     | Technical | 89.7 | 95.2 | 82.1 | Outstanding | ↘
```

#### **Individual Performance Deep Dive** (`/performance/employees/{user-id}`)

**Performance Profile Header:**
- **Employee Details**: Photo, name, role, department, supervisor
- **Performance Score**: Large circular progress indicator showing overall score
- **Performance Band**: Color-coded badge (Outstanding=Green, Exceeds=Blue, etc.)
- **Department Ranking**: "15th out of 45 employees"

**Performance Breakdown Visualizations:**

**Score Component Analysis:**
- **Performance Pie Chart**: Visual split of Task Performance (60%) vs Review Performance (40%)
- **Component Drill-Down**: Expandable sections showing detailed breakdowns

**Task Performance Section:**
- **Task Metrics Cards**: Completion Rate, Average Rating, Speed Score, Quality Score
- **Task Timeline**: Calendar view showing task completion patterns
- **Performance Trend**: Line chart showing task performance over time

**Review Performance Section:**  
- **Trait Performance Radar**: Spider chart showing all trait scores from latest review
- **Quarterly Review Trend**: Line chart showing review scores across quarters
- **Trait History Table**: Detailed view of how each trait score has evolved

**Historical Performance Analysis:**
- **Performance Journey**: Timeline showing performance progression over employment
- **Goal Achievement Integration**: Visual connection between achieved goals and performance spikes
- **Peer Comparison**: Anonymous comparison with department average and similar roles

### **Individual Employee Self-View** (`/my-performance`)

#### **Personal Performance Dashboard**

**My Performance Overview:**
- **Current Score Display**: Large, prominent performance score with context
- **Performance Band**: Personal badge with explanation of what it means
- **Progress Message**: Encouraging message about improvement or maintaining performance

**Personal Development Insights:**

**Strengths & Development Areas:**
- **Top Strengths**: Visual highlight of highest-scoring traits with specific examples
- **Development Opportunities**: Clear identification of lower-scoring areas with improvement suggestions
- **Peer Feedback Summary**: Anonymized compilation of peer review feedback

**Performance History:**
- **My Journey**: Personal performance timeline showing growth over time
- **Goal Impact Analysis**: How achieving goals has influenced performance scores
- **Next Quarter Preview**: Preview of upcoming review cycle and development opportunities

---

## API Endpoint Structure

### **Trait & Question Management**
```
GET    /api/traits - List all available traits
POST   /api/traits - Create new trait (admin only)
PUT    /api/traits/{id} - Update trait details
DELETE /api/traits/{id} - Remove trait (preserve historical data)

GET    /api/traits/{id}/questions - Questions for specific trait  
POST   /api/traits/{id}/questions - Add question to trait
PUT    /api/questions/{id} - Update question text/settings
DELETE /api/questions/{id} - Remove question
```

### **Review Cycle Management**
```
GET    /api/reviews/cycles - List all review cycles
POST   /api/reviews/cycles - Create new cycle with selected traits
PUT    /api/reviews/cycles/{id} - Update cycle settings (if draft)
POST   /api/reviews/cycles/{id}/activate - Launch cycle and generate assignments

GET    /api/reviews/cycles/{id}/overview - Cycle metrics and analytics
GET    /api/reviews/cycles/{id}/participation - Completion tracking data
GET    /api/reviews/cycles/{id}/employees - Employee-specific review data
```

### **Review Completion**
```
GET    /api/reviews/assignments/me - My pending reviews
GET    /api/reviews/assignments/{id}/form - Review form with questions
POST   /api/reviews/assignments/{id}/submit - Submit completed review
GET    /api/reviews/employees/{id}/cycle/{cycle-id} - Individual review details
```

### **Performance Analytics**
```
GET    /api/performance/organization - Organization-wide performance data
GET    /api/performance/organization/rankings - Employee rankings with filtering
GET    /api/performance/departments - Department performance comparison
GET    /api/performance/employees/{id} - Individual performance profile
GET    /api/performance/me - Personal performance dashboard data
```

---

## Page Navigation Structure

### **Admin Navigation Flow**
```
Performance Management
├── Reviews
│   ├── Trait Management → Add/Edit traits and questions
│   ├── Review Cycles → Create and manage cycles  
│   │   └── Cycle Details → Analytics and participation tracking
│   │       └── Employee Reviews → Individual review breakdowns
│   └── Review Analytics → Cross-cycle performance insights
├── Performance
│   ├── Organization Overview → Company-wide performance metrics
│   ├── Employee Rankings → Filterable performance leaderboards
│   │   └── Employee Profile → Individual performance deep dive
│   ├── Department Analytics → Department comparison and trends
│   └── Performance Reports → Exportable analytics and insights
└── Settings
    └── Performance Configuration → Weights and calculation parameters
```

### **Employee Navigation Flow**
```
My Performance
├── Current Performance → Personal performance dashboard
├── Review History → Past review scores and feedback
├── My Reviews → Pending review assignments (during active cycles)
│   ├── Self Review → Personal assessment form
│   ├── Peer Reviews → Colleague assessment forms
│   └── Review Status → Completion tracking
└── Development Plan → Performance improvement suggestions
```

### **Manager Navigation Flow**  
```
Team Performance
├── Team Overview → Direct reports performance summary
├── Individual Reviews → Team member performance profiles
├── Review Management → Supervisor review assignments
└── Team Analytics → Department/team performance trends
```

This system provides complete flexibility in defining what to measure while delivering rich visualizations that help administrators understand organizational performance and help employees track their professional development with clear, actionable insights.
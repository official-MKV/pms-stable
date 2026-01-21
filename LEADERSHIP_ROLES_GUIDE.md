# Leadership Roles in 5-Level Organization Structure

## Overview

The Nigcomsat PMS supports a **5-level organizational hierarchy**:
1. **GLOBAL** - Entire company (e.g., "Nigcomsat Management Office")
2. **DIRECTORATE** - Major business divisions (e.g., "Technical Directorate")
3. **DEPARTMENT** - Functional units (e.g., "Engineering Department")
4. **DIVISION** - Sub-departments (e.g., "Software Development Division")
5. **UNIT** - Teams or working groups (e.g., "Backend Development Unit")

## How Leadership Assignment Works

### 1. **User Assignment to Organizations**
- Users can be assigned to **ANY level** of the organization hierarchy
- Each user has exactly ONE `organization_id` field pointing to their organizational unit
- Users belong to the specific level they're assigned to (not automatically to parent levels)

**Example:**
```python
# User assigned to a Division
user = User(
    name="Jane Doe",
    organization_id=software_dev_division_id,  # Division level
    role_id=division_head_role_id
)

# User assigned to a Unit
user = User(
    name="John Smith",
    organization_id=backend_unit_id,  # Unit level
    role_id=unit_leader_role_id
)
```

### 2. **Leadership Roles**
- Roles can have the `is_leadership = True` flag
- When a user with a leadership role is assigned to an organizational unit, they become the **leader/head** of that unit
- Leadership applies at the specific organizational level where the user is assigned

**Example Leadership Roles:**
```python
# Global Level Leadership
ceo_role = Role(
    name="CEO",
    is_leadership=True,
    scope_override="global",
    permissions=[...]
)

# Directorate Level Leadership
directorate_head_role = Role(
    name="Directorate Head",
    is_leadership=True,
    scope_override="cross_directorate",
    permissions=[...]
)

# Department Level Leadership
department_head_role = Role(
    name="Department Head / HOD",
    is_leadership=True,
    scope_override="none",  # Can only access their department
    permissions=[...]
)

# Division Level Leadership
division_head_role = Role(
    name="Division Head",
    is_leadership=True,
    scope_override="none",
    permissions=[...]
)

# Unit Level Leadership
unit_leader_role = Role(
    name="Unit Leader / Team Lead",
    is_leadership=True,
    scope_override="none",
    permissions=[...]
)
```

### 3. **Supervisor Hierarchy**
- In addition to organizational hierarchy, users have a `supervisor_id` field
- This creates a **reporting chain** that can cross organizational boundaries
- Supervisors can approve goals, review initiatives, and manage their direct reports
- The `supervisor_id` is independent of organizational structure

**Example:**
```python
# User A reports to User B, even though they're in different departments
user_a = User(
    name="Junior Developer",
    organization_id=unit_1_id,
    supervisor_id=senior_developer_id  # In a different unit/division
)
```

## Current Implementation

### Database Schema
```python
# models.py
class Organization(Base):
    id = UUID
    name = String
    level = Enum('GLOBAL', 'DIRECTORATE', 'DEPARTMENT', 'DIVISION', 'UNIT')
    parent_id = UUID (Foreign Key to organizations.id)

class User(Base):
    id = UUID
    name = String
    organization_id = UUID (Foreign Key to organizations.id)  # Can be at ANY level
    role_id = UUID (Foreign Key to roles.id)
    supervisor_id = UUID (Foreign Key to users.id, nullable)

class Role(Base):
    id = UUID
    name = String
    is_leadership = Boolean  # TRUE for leadership roles
    scope_override = Enum('none', 'global', 'cross_directorate')
    permissions = JSON[]
```

### How to Identify Leaders
To find the leader of a specific organizational unit:

```python
def get_organization_leader(db: Session, organization_id: UUID) -> Optional[User]:
    """Get the leader of a specific organizational unit"""
    # Find user assigned to this org with a leadership role
    leader = db.query(User).join(Role).filter(
        User.organization_id == organization_id,
        Role.is_leadership == True,
        User.status == UserStatus.ACTIVE
    ).first()

    return leader
```

### How to Check Leadership Status
```python
def is_leader_of_organization(user: User, organization_id: UUID) -> bool:
    """Check if user is the leader of a specific organization"""
    return (
        user.role.is_leadership and
        user.organization_id == organization_id
    )
```

## Best Practices & Recommendations

### 1. **One Leader Per Organization Unit**
While the system doesn't enforce this at the database level, it's recommended to have:
- **ONE primary leader** per organizational unit
- Additional deputy/assistant roles can exist but should not have `is_leadership=True`

**Implementation Options:**
- **Option A (Current)**: Rely on application logic and user management practices
  - Train administrators to only assign one leadership role per unit
  - Show warnings in UI when multiple leaders exist

- **Option B (Strict Enforcement)**: Add database constraint or validation
  ```python
  # In user creation/update validation
  def validate_leadership_uniqueness(db: Session, user: User):
      if user.role.is_leadership:
          existing_leader = db.query(User).join(Role).filter(
              User.organization_id == user.organization_id,
              Role.is_leadership == True,
              User.id != user.id,
              User.status == UserStatus.ACTIVE
          ).first()

          if existing_leader:
              raise ValueError(
                  f"Organization '{user.organization.name}' already has a leader: {existing_leader.name}"
              )
  ```

### 2. **Leadership Permissions**
Leaders typically need permissions to:
- Manage users in their organizational unit
- Create and approve goals for their unit
- Review initiatives/tasks
- Access reports for their unit

**Recommended Permission Sets:**
```python
# Division/Unit Leader Permissions
[
    "user_create",  # Can add team members
    "user_edit",    # Can update team member details
    "goal_create_departmental",  # Can create goals for their unit
    "goal_approve",  # Can approve subordinate goals
    "initiative_review",  # Can review team initiatives
    "initiative_approve",  # Can approve initiatives
    "reports_generate",  # Can generate team reports
]
```

### 3. **Scope Override for Cross-Level Access**
- **Global leaders** (CEO, Managing Director): `scope_override = "global"`
- **Directorate heads**: `scope_override = "cross_directorate"`
- **Department/Division/Unit leaders**: `scope_override = "none"` (access only their subtree)

### 4. **Handling Leadership Transitions**
When a leader changes:
```python
def transfer_leadership(
    db: Session,
    old_leader_id: UUID,
    new_leader_id: UUID,
    new_leadership_role_id: UUID
):
    """Transfer leadership from one user to another"""
    # Update old leader to non-leadership role
    old_leader = db.query(User).filter(User.id == old_leader_id).first()
    old_leader.role_id = get_non_leadership_role_id()  # Assign appropriate role

    # Assign leadership role to new leader
    new_leader = db.query(User).filter(User.id == new_leader_id).first()
    new_leader.role_id = new_leadership_role_id
    new_leader.organization_id = old_leader.organization_id  # Same org unit

    # Update supervisor relationships if needed
    # Transfer any pending approvals, etc.

    db.commit()
```

## Common Use Cases

### Use Case 1: Assign Unit Leader
```python
# 1. Create a Unit Leader role (if not exists)
unit_leader_role = Role(
    name="Unit Leader",
    is_leadership=True,
    scope_override="none",
    permissions=["user_edit", "goal_approve", "initiative_review"]
)

# 2. Assign user to unit with leadership role
user = User(
    name="Alice Johnson",
    organization_id=backend_unit_id,  # Unit level
    role_id=unit_leader_role.id
)
```

### Use Case 2: Assign Department Head (HOD)
```python
# 1. Create HOD role
hod_role = Role(
    name="Head of Department",
    is_leadership=True,
    scope_override="none",  # Can access all divisions/units under department
    permissions=["user_create", "user_edit", "goal_create_departmental", ...]
)

# 2. Assign user to department with HOD role
hod = User(
    name="Bob Smith",
    organization_id=engineering_department_id,  # Department level
    role_id=hod_role.id
)
```

### Use Case 3: Staff Member (No Leadership)
```python
# 1. Use regular staff role
staff_role = Role(
    name="Software Engineer",
    is_leadership=False,  # Not a leader
    scope_override="none",
    permissions=["goal_create_individual", "initiative_create"]
)

# 2. Assign to unit/division/department
engineer = User(
    name="Charlie Davis",
    organization_id=backend_unit_id,  # Can be at any level
    role_id=staff_role.id,
    supervisor_id=unit_leader_id  # Reports to unit leader
)
```

## Summary

✅ **Current System Supports:**
- 5-level organization structure (GLOBAL → DIRECTORATE → DEPARTMENT → DIVISION → UNIT)
- Users can be assigned at ANY organizational level
- Leadership roles via `is_leadership` flag
- Flexible scope control via `scope_override`
- Independent supervisor hierarchy via `supervisor_id`

⚠️ **Recommendations:**
- Enforce "one leader per unit" in application logic or add validation
- Create distinct leadership roles for each level (Unit Leader, Division Head, HOD, etc.)
- Set appropriate `scope_override` based on leadership level
- Use supervisor hierarchy for cross-organizational reporting chains

📝 **Action Items:**
1. Create leadership roles for each level (if not already created)
2. Document role creation guidelines for administrators
3. Add UI warnings when assigning multiple leaders to same unit
4. Consider adding validation to prevent multiple active leaders per unit

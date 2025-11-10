"""
Create diverse test users with different permissions and departments for testing
Based on the organizational structure from seed_data.py
"""

from sqlalchemy.orm import Session
from database import engine, get_db
from models import (
    Organization, Role, User, Task, TaskAssignment,
    OrganizationLevel, ScopeOverride, UserStatus, TaskType, TaskStatus,
    TaskUrgency  # Add urgency enum
)
from utils.auth import get_password_hash
import uuid
from datetime import datetime, date

def create_test_users(db: Session):
    """Create diverse test users across different departments with various permissions"""

    # Get departments
    departments = {
        'IT': db.query(Organization).filter(Organization.name == "Information Technology").first(),
        'HR': db.query(Organization).filter(Organization.name == "Human Resources").first(),
        'Marketing': db.query(Organization).filter(Organization.name == "Marketing").first(),
        'Finance': db.query(Organization).filter(Organization.name == "Finance").first(),
        'Satellite': db.query(Organization).filter(Organization.name == "Satellite Operations").first(),
    }

    # Get roles
    roles = {
        'Department Head': db.query(Role).filter(Role.name == "Department Head").first(),
        'Team Lead': db.query(Role).filter(Role.name == "Team Lead").first(),
        'Senior Employee': db.query(Role).filter(Role.name == "Senior Employee").first(),
        'Employee': db.query(Role).filter(Role.name == "Employee").first(),
    }

    # Create additional specialized roles for testing
    test_roles = [
        {
            "name": "Project Manager",
            "description": "Can create and manage tasks across departments",
            "is_leadership": False,
            "scope_override": ScopeOverride.GLOBAL,
            "permissions": ["task_create", "task_assign", "task_review", "task_view_all", "goal_create_departmental"]
        },
        {
            "name": "Task Creator",
            "description": "Can create tasks within department",
            "is_leadership": False,
            "scope_override": ScopeOverride.NONE,
            "permissions": ["task_create", "task_assign", "task_view_all"]
        }
    ]

    # Create test roles
    for role_data in test_roles:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing:
            role = Role(
                id=uuid.uuid4(),
                name=role_data["name"],
                description=role_data["description"],
                is_leadership=role_data["is_leadership"],
                scope_override=role_data["scope_override"],
                permissions=role_data["permissions"]
            )
            db.add(role)
            roles[role_data["name"]] = role
        else:
            roles[role_data["name"]] = existing

    db.commit()

    # Test users data
    test_users = [
        # IT Department - Various levels
        {
            "email": "john.smith@nigcomsat.gov.ng",
            "name": "John Smith",
            "phone": "+234-801-234-5678",
            "address": "15 Victoria Island Lagos",
            "skillset": "React, Node.js, Python, DevOps",
            "level": "Senior",
            "job_title": "Senior Software Engineer",
            "department": "IT",
            "role": "Task Creator"
        },
        {
            "email": "sarah.jones@nigcomsat.gov.ng",
            "name": "Sarah Jones",
            "phone": "+234-802-345-6789",
            "address": "22 Ikoyi Lagos",
            "skillset": "JavaScript, UI/UX, Design Systems",
            "level": "Mid",
            "job_title": "Frontend Developer",
            "department": "IT",
            "role": "Employee"
        },
        {
            "email": "mike.wilson@nigcomsat.gov.ng",
            "name": "Mike Wilson",
            "phone": "+234-803-456-7890",
            "address": "8 Allen Avenue Ikeja",
            "skillset": "DevOps, AWS, Docker, Kubernetes",
            "level": "Senior",
            "job_title": "DevOps Engineer",
            "department": "IT",
            "role": "Senior Employee"
        },
        {
            "email": "lisa.brown@nigcomsat.gov.ng",
            "name": "Lisa Brown",
            "phone": "+234-804-567-8901",
            "address": "45 Surulere Lagos",
            "skillset": "Team Management, Software Architecture",
            "level": "Lead",
            "job_title": "IT Team Lead",
            "department": "IT",
            "role": "Team Lead"
        },

        # Marketing Department
        {
            "email": "david.clark@nigcomsat.gov.ng",
            "name": "David Clark",
            "phone": "+234-805-678-9012",
            "address": "12 Lekki Phase 1",
            "skillset": "Digital Marketing, Strategy, Team Management",
            "level": "Manager",
            "job_title": "Marketing Manager",
            "department": "Marketing",
            "role": "Department Head"
        },
        {
            "email": "emma.davis@nigcomsat.gov.ng",
            "name": "Emma Davis",
            "phone": "+234-806-789-0123",
            "address": "33 Ajah Lagos",
            "skillset": "Content Creation, Social Media Marketing",
            "level": "Mid",
            "job_title": "Content Specialist",
            "department": "Marketing",
            "role": "Employee"
        },
        {
            "email": "james.taylor@nigcomsat.gov.ng",
            "name": "James Taylor",
            "phone": "+234-807-890-1234",
            "address": "67 Maryland Lagos",
            "skillset": "Brand Management, Marketing Strategy",
            "level": "Senior",
            "job_title": "Brand Manager",
            "department": "Marketing",
            "role": "Senior Employee"
        },

        # HR Department
        {
            "email": "nancy.white@nigcomsat.gov.ng",
            "name": "Nancy White",
            "phone": "+234-808-901-2345",
            "address": "89 Yaba Lagos",
            "skillset": "HR Management, Recruitment, Policy Development",
            "level": "Manager",
            "job_title": "HR Manager",
            "department": "HR",
            "role": "Department Head"
        },
        {
            "email": "robert.lee@nigcomsat.gov.ng",
            "name": "Robert Lee",
            "phone": "+234-809-012-3456",
            "address": "21 Gbagada Lagos",
            "skillset": "Recruitment, Employee Relations",
            "level": "Mid",
            "job_title": "HR Specialist",
            "department": "HR",
            "role": "Employee"
        },

        # Finance Department
        {
            "email": "grace.johnson@nigcomsat.gov.ng",
            "name": "Grace Johnson",
            "phone": "+234-810-123-4567",
            "address": "54 Ogudu Lagos",
            "skillset": "Financial Analysis, Budgeting, Reporting",
            "level": "Senior",
            "job_title": "Financial Analyst",
            "department": "Finance",
            "role": "Task Creator"
        },
        {
            "email": "peter.adams@nigcomsat.gov.ng",
            "name": "Peter Adams",
            "phone": "+234-811-234-5678",
            "address": "76 Festac Lagos",
            "skillset": "Accounting, Financial Management",
            "level": "Mid",
            "job_title": "Accountant",
            "department": "Finance",
            "role": "Employee"
        },

        # Satellite Operations Department
        {
            "email": "mary.wilson@nigcomsat.gov.ng",
            "name": "Mary Wilson",
            "phone": "+234-812-345-6789",
            "address": "31 Apapa Lagos",
            "skillset": "Satellite Operations, Technical Support",
            "level": "Senior",
            "job_title": "Operations Specialist",
            "department": "Satellite",
            "role": "Senior Employee"
        },

        # Cross-functional Project Managers
        {
            "email": "alex.garcia@nigcomsat.gov.ng",
            "name": "Alex Garcia",
            "phone": "+234-813-456-7890",
            "address": "98 Magodo Lagos",
            "skillset": "Project Management, Agile, Cross-team Coordination",
            "level": "Senior",
            "job_title": "Project Manager",
            "department": "IT",  # Assigned to IT but has global access
            "role": "Project Manager"
        },
        {
            "email": "sophia.martinez@nigcomsat.gov.ng",
            "name": "Sophia Martinez",
            "phone": "+234-814-567-8901",
            "address": "43 Ojodu Lagos",
            "skillset": "Product Management, Strategy, Stakeholder Management",
            "level": "Senior",
            "job_title": "Product Manager",
            "department": "Marketing",  # Assigned to Marketing but has global access
            "role": "Project Manager"
        }
    ]

    created_users = {}

    # Create users
    for user_data in test_users:
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            print(f"* User {user_data['email']} already exists - skipping")
            created_users[user_data["email"]] = existing_user
            continue

        department = departments[user_data["department"]]
        role = roles[user_data["role"]]

        if not department or not role:
            print(f"x Missing department or role for {user_data['email']}")
            continue

        # Split name into first and last name
        name_parts = user_data["name"].split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        # Convert level to integer
        level_map = {"Mid": 5, "Senior": 10, "Lead": 12, "Manager": 14, "Executive": 16}
        level_int = level_map.get(user_data["level"], 5)

        user = User(
            id=uuid.uuid4(),
            email=user_data["email"],
            name=user_data["name"],  # Full name for display
            first_name=first_name,
            last_name=last_name,
            phone=user_data["phone"],
            address=user_data["address"],
            skillset=user_data["skillset"],
            level=level_int,
            job_title=user_data["job_title"],
            organization_id=department.id,
            role_id=role.id,
            status=UserStatus.ACTIVE,
            password_hash=get_password_hash("password123"),
            email_verified_at=datetime.now()
        )

        db.add(user)
        created_users[user_data["email"]] = user
        print(f"* Created user: {user_data['name']} ({user_data['email']})")

    db.commit()
    return created_users

def create_sample_tasks_with_urgency(db: Session, users: dict):
    """Create sample tasks with different urgency levels"""

    # Sample tasks with various urgency levels
    sample_tasks = [
        {
            "title": "Fix critical authentication bug",
            "description": "Users unable to login due to session timeout issues - blocking production",
            "type": TaskType.INDIVIDUAL,
            "urgency": "urgent",  # Will be converted to enum
            "due_date": datetime(2025, 1, 30, 17, 0, 0),
            "creator": "lisa.brown@nigcomsat.gov.ng",
            "assignee": "john.smith@nigcomsat.gov.ng"
        },
        {
            "title": "Update user dashboard UI",
            "description": "Improve the user dashboard interface based on user feedback and usability testing",
            "type": TaskType.INDIVIDUAL,
            "urgency": "medium",
            "due_date": datetime(2025, 2, 15, 17, 0, 0),
            "creator": "lisa.brown@nigcomsat.gov.ng",
            "assignee": "sarah.jones@nigcomsat.gov.ng"
        },
        {
            "title": "Q1 Marketing Campaign Launch",
            "description": "Plan and execute Q1 marketing campaigns across all digital channels",
            "type": TaskType.GROUP,
            "urgency": "high",
            "due_date": datetime(2025, 2, 1, 17, 0, 0),
            "creator": "david.clark@nigcomsat.gov.ng",
            "assignees": ["emma.davis@nigcomsat.gov.ng", "james.taylor@nigcomsat.gov.ng"],
            "team_head": "emma.davis@nigcomsat.gov.ng"
        },
        {
            "title": "Database performance optimization",
            "description": "Analyze and optimize database queries causing application slowdowns",
            "type": TaskType.INDIVIDUAL,
            "urgency": "high",
            "due_date": datetime(2025, 2, 10, 17, 0, 0),
            "creator": "alex.garcia@nigcomsat.gov.ng",  # Project manager creating cross-dept task
            "assignee": "mike.wilson@nigcomsat.gov.ng"
        },
        {
            "title": "Monthly financial report preparation",
            "description": "Prepare comprehensive monthly financial statements and analysis",
            "type": TaskType.INDIVIDUAL,
            "urgency": "medium",
            "due_date": datetime(2025, 1, 31, 17, 0, 0),
            "creator": "nancy.white@nigcomsat.gov.ng",  # HR manager creating task for Finance
            "assignee": "grace.johnson@nigcomsat.gov.ng"
        },
        {
            "title": "Employee satisfaction survey",
            "description": "Conduct quarterly employee satisfaction survey and compile results",
            "type": TaskType.INDIVIDUAL,
            "urgency": "low",
            "due_date": datetime(2025, 2, 20, 17, 0, 0),
            "creator": "nancy.white@nigcomsat.gov.ng",
            "assignee": "robert.lee@nigcomsat.gov.ng"
        },
        {
            "title": "API documentation update",
            "description": "Update API documentation for new endpoints and authentication changes",
            "type": TaskType.INDIVIDUAL,
            "urgency": "low",
            "due_date": datetime(2025, 2, 25, 17, 0, 0),
            "creator": "lisa.brown@nigcomsat.gov.ng",
            "assignee": "john.smith@nigcomsat.gov.ng"
        }
    ]

    # Convert urgency strings to enum values
    urgency_map = {
        "low": TaskUrgency.LOW,
        "medium": TaskUrgency.MEDIUM,
        "high": TaskUrgency.HIGH,
        "urgent": TaskUrgency.URGENT
    }

    for task_data in sample_tasks:
        creator = users.get(task_data["creator"])
        if not creator:
            print(f"x Creator not found for task: {task_data['title']}")
            continue

        task = Task(
            id=uuid.uuid4(),
            title=task_data["title"],
            description=task_data["description"],
            type=task_data["type"],
            urgency=task_data["urgency"],  # Use string directly since we added as VARCHAR
            due_date=task_data["due_date"],
            status=TaskStatus.CREATED,
            created_by=creator.id
        )

        db.add(task)
        db.flush()  # Get task ID

        # Handle assignments
        if task_data["type"] == TaskType.INDIVIDUAL:
            assignee = users.get(task_data["assignee"])
            if assignee:
                assignment = TaskAssignment(
                    id=uuid.uuid4(),
                    task_id=task.id,
                    user_id=assignee.id
                )
                db.add(assignment)
        else:  # Group task
            assignees = task_data.get("assignees", [])
            team_head = users.get(task_data.get("team_head"))

            if team_head:
                task.team_head_id = team_head.id

            for assignee_email in assignees:
                assignee = users.get(assignee_email)
                if assignee:
                    assignment = TaskAssignment(
                        id=uuid.uuid4(),
                        task_id=task.id,
                        user_id=assignee.id
                    )
                    db.add(assignment)

        print(f"* Created task: {task_data['title']} (Priority: {task_data['urgency']})")

    db.commit()

def create_test_data():
    """Main function to create test users and sample tasks"""
    print("Creating diverse test users and sample tasks...")

    db = next(get_db())
    try:
        users = create_test_users(db)
        create_sample_tasks_with_urgency(db, users)

        print("\n" + "="*60)
        print("TEST USERS CREATED SUCCESSFULLY!")
        print("="*60)
        print("\nAll users have password: password123")
        print("\nUsers by Department and Role:")
        print("\n🏢 IT Department:")
        print("  • john.smith@nigcomsat.gov.ng - Senior Software Engineer (Task Creator)")
        print("  • sarah.jones@nigcomsat.gov.ng - Frontend Developer (Employee)")
        print("  • mike.wilson@nigcomsat.gov.ng - DevOps Engineer (Senior Employee)")
        print("  • lisa.brown@nigcomsat.gov.ng - IT Team Lead (Team Lead)")
        print("  • alex.garcia@nigcomsat.gov.ng - Project Manager (Global Access)")

        print("\n📢 Marketing Department:")
        print("  • david.clark@nigcomsat.gov.ng - Marketing Manager (Department Head)")
        print("  • emma.davis@nigcomsat.gov.ng - Content Specialist (Employee)")
        print("  • james.taylor@nigcomsat.gov.ng - Brand Manager (Senior Employee)")
        print("  • sophia.martinez@nigcomsat.gov.ng - Product Manager (Global Access)")

        print("\n👥 HR Department:")
        print("  • nancy.white@nigcomsat.gov.ng - HR Manager (Department Head)")
        print("  • robert.lee@nigcomsat.gov.ng - HR Specialist (Employee)")

        print("\n💰 Finance Department:")
        print("  • grace.johnson@nigcomsat.gov.ng - Financial Analyst (Task Creator)")
        print("  • peter.adams@nigcomsat.gov.ng - Accountant (Employee)")

        print("\n🛰️ Satellite Operations:")
        print("  • mary.wilson@nigcomsat.gov.ng - Operations Specialist (Senior Employee)")

        print("\n" + "="*60)
        print("SAMPLE TASKS WITH URGENCY LEVELS CREATED:")
        print("="*60)
        print("URGENT: Fix critical authentication bug")
        print("HIGH: Q1 Marketing Campaign Launch, Database optimization")
        print("MEDIUM: Update UI, Monthly financial report")
        print("LOW: Employee survey, API documentation")

        print(f"\nSUCCESS: Created {len(users)} test users and 7 sample tasks!")
        print("Ready for comprehensive testing!")

    except Exception as e:
        print(f"ERROR: Error creating test data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
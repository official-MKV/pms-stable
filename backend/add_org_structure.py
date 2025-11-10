"""
Add organizational structure and roles for Nigcomsat
Creates Directorates, Departments, Units, and various Roles
"""
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Organization, Role, OrganizationLevel, ScopeOverride
import uuid

def add_organizational_structure():
    db = SessionLocal()
    try:
        print("="*60)
        print("ADDING ORGANIZATIONAL STRUCTURE & ROLES")
        print("="*60)

        # Get Nigcomsat global organization
        nigcomsat = db.query(Organization).filter(
            Organization.level == OrganizationLevel.GLOBAL
        ).first()

        if not nigcomsat:
            print("ERROR: Nigcomsat global organization not found!")
            print("Please run init_basic_data.py first")
            return

        print(f"\nBase Organization: {nigcomsat.name}")

        # ============================================================
        # DIRECTORATES
        # ============================================================
        print("\n" + "="*60)
        print("CREATING DIRECTORATES")
        print("="*60)

        directorates_data = [
            {
                "name": "Operations Directorate",
                "description": "Oversees all satellite operations and technical services"
            },
            {
                "name": "Commercial Directorate",
                "description": "Manages commercial activities, sales, and business development"
            },
            {
                "name": "Engineering Directorate",
                "description": "Responsible for engineering and technical infrastructure"
            },
            {
                "name": "Corporate Services Directorate",
                "description": "Handles corporate support functions including HR, Finance, and Admin"
            }
        ]

        directorates = {}
        for dir_data in directorates_data:
            existing = db.query(Organization).filter(
                Organization.name == dir_data["name"]
            ).first()

            if not existing:
                directorate = Organization(
                    id=uuid.uuid4(),
                    name=dir_data["name"],
                    description=dir_data["description"],
                    level=OrganizationLevel.DIRECTORATE,
                    parent_id=nigcomsat.id
                )
                db.add(directorate)
                db.commit()
                directorates[dir_data["name"]] = directorate
                print(f"[+] Created: {dir_data['name']}")
            else:
                directorates[dir_data["name"]] = existing
                print(f"[=] Already exists: {dir_data['name']}")

        # ============================================================
        # DEPARTMENTS
        # ============================================================
        print("\n" + "="*60)
        print("CREATING DEPARTMENTS")
        print("="*60)

        departments_data = [
            # Operations Directorate Departments
            {
                "name": "Satellite Operations",
                "description": "Manages day-to-day satellite operations and monitoring",
                "parent": "Operations Directorate"
            },
            {
                "name": "Network Operations Center",
                "description": "24/7 network monitoring and management",
                "parent": "Operations Directorate"
            },
            {
                "name": "Technical Support",
                "description": "Provides technical support to customers and internal teams",
                "parent": "Operations Directorate"
            },

            # Commercial Directorate Departments
            {
                "name": "Sales & Marketing",
                "description": "Drives sales and marketing initiatives",
                "parent": "Commercial Directorate"
            },
            {
                "name": "Business Development",
                "description": "Identifies and develops new business opportunities",
                "parent": "Commercial Directorate"
            },
            {
                "name": "Customer Relations",
                "description": "Manages customer relationships and satisfaction",
                "parent": "Commercial Directorate"
            },

            # Engineering Directorate Departments
            {
                "name": "Systems Engineering",
                "description": "Designs and maintains satellite systems",
                "parent": "Engineering Directorate"
            },
            {
                "name": "Information Technology",
                "description": "Manages IT infrastructure and software development",
                "parent": "Engineering Directorate"
            },
            {
                "name": "Research & Development",
                "description": "Conducts R&D for new technologies and solutions",
                "parent": "Engineering Directorate"
            },

            # Corporate Services Directorate Departments
            {
                "name": "Human Resources",
                "description": "Manages HR operations, recruitment, and employee welfare",
                "parent": "Corporate Services Directorate"
            },
            {
                "name": "Finance & Accounts",
                "description": "Handles financial operations, accounting, and budgeting",
                "parent": "Corporate Services Directorate"
            },
            {
                "name": "Administration",
                "description": "Provides administrative and facility management services",
                "parent": "Corporate Services Directorate"
            },
            {
                "name": "Legal & Compliance",
                "description": "Manages legal affairs and regulatory compliance",
                "parent": "Corporate Services Directorate"
            }
        ]

        departments = {}
        for dept_data in departments_data:
            existing = db.query(Organization).filter(
                Organization.name == dept_data["name"]
            ).first()

            if not existing:
                parent_directorate = directorates.get(dept_data["parent"])
                if parent_directorate:
                    department = Organization(
                        id=uuid.uuid4(),
                        name=dept_data["name"],
                        description=dept_data["description"],
                        level=OrganizationLevel.DEPARTMENT,
                        parent_id=parent_directorate.id
                    )
                    db.add(department)
                    db.commit()
                    departments[dept_data["name"]] = department
                    print(f"[+] Created: {dept_data['name']} (under {dept_data['parent']})")
                else:
                    print(f"[!] Skipped: {dept_data['name']} - Parent not found")
            else:
                departments[dept_data["name"]] = existing
                print(f"[=] Already exists: {dept_data['name']}")

        # ============================================================
        # UNITS (Sample units under some departments)
        # ============================================================
        print("\n" + "="*60)
        print("CREATING UNITS")
        print("="*60)

        units_data = [
            # IT Department Units
            {
                "name": "Software Development Unit",
                "description": "Develops and maintains software applications",
                "parent": "Information Technology"
            },
            {
                "name": "Infrastructure & Security Unit",
                "description": "Manages IT infrastructure and cybersecurity",
                "parent": "Information Technology"
            },

            # HR Department Units
            {
                "name": "Recruitment & Talent Acquisition",
                "description": "Handles recruitment and talent management",
                "parent": "Human Resources"
            },
            {
                "name": "Learning & Development",
                "description": "Manages training and employee development programs",
                "parent": "Human Resources"
            },

            # Finance Department Units
            {
                "name": "Financial Planning & Analysis",
                "description": "Handles budgeting, forecasting, and financial analysis",
                "parent": "Finance & Accounts"
            },
            {
                "name": "Accounts Payable & Receivable",
                "description": "Manages payment processing and collections",
                "parent": "Finance & Accounts"
            },

            # Sales & Marketing Units
            {
                "name": "Digital Marketing Unit",
                "description": "Manages digital marketing campaigns and social media",
                "parent": "Sales & Marketing"
            },
            {
                "name": "Sales Operations Unit",
                "description": "Supports sales activities and customer outreach",
                "parent": "Sales & Marketing"
            }
        ]

        for unit_data in units_data:
            existing = db.query(Organization).filter(
                Organization.name == unit_data["name"]
            ).first()

            if not existing:
                parent_department = departments.get(unit_data["parent"])
                if parent_department:
                    unit = Organization(
                        id=uuid.uuid4(),
                        name=unit_data["name"],
                        description=unit_data["description"],
                        level=OrganizationLevel.UNIT,
                        parent_id=parent_department.id
                    )
                    db.add(unit)
                    db.commit()
                    print(f"[+] Created: {unit_data['name']} (under {unit_data['parent']})")
                else:
                    print(f"[!] Skipped: {unit_data['name']} - Parent not found")
            else:
                print(f"[=] Already exists: {unit_data['name']}")

        # ============================================================
        # ROLES
        # ============================================================
        print("\n" + "="*60)
        print("CREATING ROLES")
        print("="*60)

        roles_data = [
            {
                "name": "Director",
                "description": "Directorate leader with cross-directorate visibility",
                "is_leadership": True,
                "scope_override": ScopeOverride.CROSS_DIRECTORATE,
                "permissions": [
                    "user_create", "user_edit", "user_view_all",
                    "goal_create_departmental", "goal_edit", "goal_view_all",
                    "task_create", "task_assign", "task_review", "task_view_all",
                    "review_create_cycle", "review_manage_cycle", "review_view_all",
                    "performance_view_all", "reports_generate"
                ]
            },
            {
                "name": "Department Head",
                "description": "Department leader with departmental scope",
                "is_leadership": True,
                "scope_override": ScopeOverride.NONE,
                "permissions": [
                    "user_create", "user_edit", "user_view_all",
                    "goal_create_departmental", "goal_edit", "goal_view_all",
                    "task_create", "task_assign", "task_review", "task_view_all",
                    "review_conduct", "performance_view_all"
                ]
            },
            {
                "name": "Team Lead",
                "description": "Team leader within a unit or department",
                "is_leadership": True,
                "scope_override": ScopeOverride.NONE,
                "permissions": [
                    "task_create", "task_assign", "task_review", "task_view_all",
                    "goal_create_departmental", "review_conduct"
                ]
            },
            {
                "name": "HR Manager",
                "description": "HR manager with global user access",
                "is_leadership": False,
                "scope_override": ScopeOverride.GLOBAL,
                "permissions": [
                    "user_create", "user_edit", "user_suspend", "user_activate",
                    "user_view_all", "user_history_view",
                    "review_create_cycle", "review_manage_cycle", "review_view_all",
                    "performance_view_all", "reports_generate"
                ]
            },
            {
                "name": "Finance Manager",
                "description": "Finance manager with reporting access",
                "is_leadership": False,
                "scope_override": ScopeOverride.GLOBAL,
                "permissions": [
                    "user_view_all", "performance_view_all", "reports_generate",
                    "audit_access"
                ]
            },
            {
                "name": "Senior Employee",
                "description": "Senior staff with task creation rights",
                "is_leadership": False,
                "scope_override": ScopeOverride.NONE,
                "permissions": [
                    "task_create", "task_assign", "task_view_all",
                    "review_conduct"
                ]
            },
            {
                "name": "Project Manager",
                "description": "Manages projects across departments",
                "is_leadership": False,
                "scope_override": ScopeOverride.GLOBAL,
                "permissions": [
                    "task_create", "task_assign", "task_review", "task_view_all",
                    "goal_create_departmental", "goal_view_all"
                ]
            }
        ]

        for role_data in roles_data:
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
                db.commit()
                print(f"[+] Created: {role_data['name']}")
            else:
                print(f"[=] Already exists: {role_data['name']}")

        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)

        total_orgs = db.query(Organization).count()
        total_roles = db.query(Role).count()

        by_level = {}
        for level in OrganizationLevel:
            count = db.query(Organization).filter(Organization.level == level).count()
            by_level[level.value] = count

        print(f"\nTotal Organizations: {total_orgs}")
        print(f"  - Global: {by_level.get('global', 0)}")
        print(f"  - Directorates: {by_level.get('directorate', 0)}")
        print(f"  - Departments: {by_level.get('department', 0)}")
        print(f"  - Units: {by_level.get('unit', 0)}")
        print(f"\nTotal Roles: {total_roles}")

        print("\n" + "="*60)
        print("ORGANIZATIONAL STRUCTURE COMPLETE!")
        print("="*60)
        print("\nYou can now:")
        print("1. Login with admin@nigcomsat.gov.ng / admin123")
        print("2. Create users and assign them to departments/units")
        print("3. Assign appropriate roles to users")
        print("="*60)

        db.close()

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        db.close()

if __name__ == "__main__":
    add_organizational_structure()

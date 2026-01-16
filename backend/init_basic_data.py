"""
Initialize basic data - Nigcomsat organization, roles, and super admin
"""
import sys
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Organization, Role, User, OrganizationLevel, ScopeOverride, UserStatus
from utils.auth import get_password_hash
import uuid

def init_basic_data():
    db = SessionLocal()
    try:
        print("="*60)
        print("INITIALIZING BASIC DATA")
        print("="*60)

        # 1. Create Nigcomsat Global Organization
        print("\n1. Creating Nigcomsat Global Organization...")
        global_org = db.query(Organization).filter(Organization.level == OrganizationLevel.GLOBAL).first()
        if not global_org:
            global_org = Organization(
                id=uuid.uuid4(),
                name="Nigcomsat",
                description="Nigerian Communications Satellite Limited",
                level=OrganizationLevel.GLOBAL,
                parent_id=None
            )
            db.add(global_org)
            db.commit()
            print(f"   Created: {global_org.name}")
        else:
            print(f"   Already exists: {global_org.name}")

        # 2. Create Super Admin Role
        print("\n2. Creating Super Admin Role...")
        super_admin_role = db.query(Role).filter(Role.name == "Super Admin").first()
        if not super_admin_role:
            super_admin_role = Role(
                id=uuid.uuid4(),
                name="Super Admin",
                description="Full system access and administration",
                is_leadership=True,
                scope_override=ScopeOverride.GLOBAL,
                permissions=[
                    "system_admin",
                    "organization_create",
                    "organization_edit",
                    "organization_delete",
                    "organization_view_all",
                    "role_create",
                    "role_edit",
                    "role_delete",
                    "role_assign",
                    "role_view_all",
                    "user_create",
                    "user_edit",
                    "user_suspend",
                    "user_activate",
                    "user_archive",
                    "user_view_all",
                    "user_history_view",
                    "goal_create_yearly",
                    "goal_create_quarterly",
                    "goal_create_departmental",
                    "goal_edit",
                    "goal_progress_update",
                    "goal_status_change",
                    "goal_view_all",
                    "task_create",
                    "task_assign",
                    "task_edit",
                    "task_review",
                    "task_view_all",
                    "task_extend_deadline",
                    "task_delete",
                    "review_create_cycle",
                    "review_edit_cycle",
                    "review_manage_cycle",
                    "review_trait_manage",
                    "review_view_all",
                    "review_conduct",
                    "performance_view_all",
                    "performance_edit",
                    "reports_generate",
                    "audit_access",
                    "notification_manage",
                    "backup_access"
                ]
            )
            db.add(super_admin_role)
            db.commit()
            print(f"   Created: {super_admin_role.name}")
        else:
            print(f"   Already exists: {super_admin_role.name}")

        # 3. Create Employee Role (basic role for all users)
        print("\n3. Creating Employee Role...")
        employee_role = db.query(Role).filter(Role.name == "Employee").first()
        if not employee_role:
            employee_role = Role(
                id=uuid.uuid4(),
                name="Employee",
                description="Standard employee with basic access",
                is_leadership=False,
                scope_override=ScopeOverride.NONE,
                permissions=[
                    "task_create",
                    "review_conduct"
                ]
            )
            db.add(employee_role)
            db.commit()
            print(f"   Created: {employee_role.name}")
        else:
            print(f"   Already exists: {employee_role.name}")

        # 4. Create Super Admin User
        print("\n4. Creating Super Admin User...")
        admin_user = db.query(User).filter(User.email == "admin@nigcomsat.gov.ng").first()
        if not admin_user:
            admin_user = User(
                id=uuid.uuid4(),
                email="admin@nigcomsat.gov.ng",
                name="System Administrator",
                first_name="System",
                last_name="Administrator",
                middle_name=None,
                phone="+234-800-000-0000",
                address="Nigcomsat HQ, Abuja",
                skillset="System Administration",
                level=17,  # Highest level
                level_rank=17,
                job_title="System Administrator",
                organization_id=global_org.id,
                role_id=super_admin_role.id,
                status=UserStatus.ACTIVE,
                password_hash=get_password_hash("admin123"),
                supervisor_id=None
            )
            db.add(admin_user)
            db.commit()
            print(f"   Created: {admin_user.email}")
            print(f"   Password: admin123")
        else:
            print(f"   Already exists: {admin_user.email}")

        print("\n" + "="*60)
        print("INITIALIZATION COMPLETE!")
        print("="*60)
        print("\nCredentials:")
        print("  Email: admin@nigcomsat.gov.ng")
        print("  Password: admin123")
        print("\nYou can now:")
        print("1. Start the backend server: python main.py")
        print("2. Login and create your organizational structure")
        print("3. Add more users as needed")
        print("="*60)

        db.close()

    except Exception as e:
        print(f"\nERROR: {e}")
        db.rollback()
        db.close()
        sys.exit(1)

if __name__ == "__main__":
    init_basic_data()

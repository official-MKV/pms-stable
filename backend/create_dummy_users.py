"""
Create dummy test users across different departments and roles
"""
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Organization, Role, User, UserStatus
from utils.auth import get_password_hash
import uuid

def create_dummy_users():
    db = SessionLocal()
    try:
        print("="*60)
        print("CREATING DUMMY TEST USERS")
        print("="*60)

        # Get organizations
        it_dept = db.query(Organization).filter(Organization.name == "Information Technology").first()
        hr_dept = db.query(Organization).filter(Organization.name == "Human Resources").first()
        finance_dept = db.query(Organization).filter(Organization.name == "Finance & Accounts").first()
        sales_dept = db.query(Organization).filter(Organization.name == "Sales & Marketing").first()
        satellite_ops = db.query(Organization).filter(Organization.name == "Satellite Operations").first()

        # Get roles
        employee_role = db.query(Role).filter(Role.name == "Employee").first()
        senior_role = db.query(Role).filter(Role.name == "Senior Employee").first()
        team_lead_role = db.query(Role).filter(Role.name == "Team Lead").first()
        dept_head_role = db.query(Role).filter(Role.name == "Department Head").first()
        hr_manager_role = db.query(Role).filter(Role.name == "HR Manager").first()

        if not all([it_dept, hr_dept, finance_dept, employee_role]):
            print("ERROR: Required organizations or roles not found!")
            print("Please run add_org_structure.py first")
            return

        # Test users data
        test_users = [
            # IT Department
            {
                "email": "john.doe@nigcomsat.gov.ng",
                "first_name": "John",
                "last_name": "Doe",
                "middle_name": "Michael",
                "phone": "+234-801-111-1111",
                "job_title": "Software Engineer",
                "organization": it_dept,
                "role": employee_role,
                "level": 8
            },
            {
                "email": "jane.smith@nigcomsat.gov.ng",
                "first_name": "Jane",
                "last_name": "Smith",
                "middle_name": "Ann",
                "phone": "+234-801-222-2222",
                "job_title": "Senior Developer",
                "organization": it_dept,
                "role": senior_role,
                "level": 10
            },
            {
                "email": "mike.johnson@nigcomsat.gov.ng",
                "first_name": "Mike",
                "last_name": "Johnson",
                "middle_name": None,
                "phone": "+234-801-333-3333",
                "job_title": "IT Team Lead",
                "organization": it_dept,
                "role": team_lead_role,
                "level": 12
            },

            # HR Department
            {
                "email": "sarah.williams@nigcomsat.gov.ng",
                "first_name": "Sarah",
                "last_name": "Williams",
                "middle_name": "Jane",
                "phone": "+234-802-111-1111",
                "job_title": "HR Manager",
                "organization": hr_dept,
                "role": hr_manager_role,
                "level": 13
            },
            {
                "email": "david.brown@nigcomsat.gov.ng",
                "first_name": "David",
                "last_name": "Brown",
                "middle_name": "Lee",
                "phone": "+234-802-222-2222",
                "job_title": "HR Officer",
                "organization": hr_dept,
                "role": employee_role,
                "level": 9
            },

            # Finance Department
            {
                "email": "emily.davis@nigcomsat.gov.ng",
                "first_name": "Emily",
                "last_name": "Davis",
                "middle_name": "Rose",
                "phone": "+234-803-111-1111",
                "job_title": "Finance Manager",
                "organization": finance_dept,
                "role": dept_head_role,
                "level": 14
            },
            {
                "email": "james.wilson@nigcomsat.gov.ng",
                "first_name": "James",
                "last_name": "Wilson",
                "middle_name": "Patrick",
                "phone": "+234-803-222-2222",
                "job_title": "Accountant",
                "organization": finance_dept,
                "role": employee_role,
                "level": 8
            },

            # Sales & Marketing
            {
                "email": "lisa.taylor@nigcomsat.gov.ng",
                "first_name": "Lisa",
                "last_name": "Taylor",
                "middle_name": "Marie",
                "phone": "+234-804-111-1111",
                "job_title": "Marketing Specialist",
                "organization": sales_dept if sales_dept else it_dept,
                "role": senior_role,
                "level": 10
            },
            {
                "email": "robert.anderson@nigcomsat.gov.ng",
                "first_name": "Robert",
                "last_name": "Anderson",
                "middle_name": "James",
                "phone": "+234-804-222-2222",
                "job_title": "Sales Officer",
                "organization": sales_dept if sales_dept else it_dept,
                "role": employee_role,
                "level": 7
            },

            # Satellite Operations
            {
                "email": "patricia.martin@nigcomsat.gov.ng",
                "first_name": "Patricia",
                "last_name": "Martin",
                "middle_name": "Ann",
                "phone": "+234-805-111-1111",
                "job_title": "Satellite Operations Engineer",
                "organization": satellite_ops if satellite_ops else it_dept,
                "role": senior_role,
                "level": 11
            },
        ]

        print("\nCreating test users...")
        created_count = 0

        for user_data in test_users:
            # Check if user already exists
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                print(f"[=] Already exists: {user_data['email']}")
                continue

            # Build full name
            name_parts = [user_data["first_name"]]
            if user_data["middle_name"]:
                name_parts.append(user_data["middle_name"])
            name_parts.append(user_data["last_name"])
            full_name = " ".join(name_parts)

            # Create user
            new_user = User(
                id=uuid.uuid4(),
                email=user_data["email"],
                name=full_name,
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                middle_name=user_data["middle_name"],
                phone=user_data["phone"],
                job_title=user_data["job_title"],
                organization_id=user_data["organization"].id,
                role_id=user_data["role"].id,
                level=user_data["level"],
                level_rank=user_data["level"],
                status=UserStatus.ACTIVE,
                password_hash=get_password_hash("password123"),
                address=f"{user_data['organization'].name}, Abuja",
                skillset=f"{user_data['job_title']} skills"
            )

            db.add(new_user)
            db.commit()

            print(f"[+] Created: {user_data['email']} - {user_data['job_title']} ({user_data['organization'].name})")
            created_count += 1

        print("\n" + "="*60)
        print("DUMMY USERS CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"\nTotal users created: {created_count}")
        print("\nAll test users have password: password123")
        print("\nTest Users by Department:")
        print("\nIT Department:")
        print("  - john.doe@nigcomsat.gov.ng (Software Engineer)")
        print("  - jane.smith@nigcomsat.gov.ng (Senior Developer)")
        print("  - mike.johnson@nigcomsat.gov.ng (IT Team Lead)")
        print("\nHR Department:")
        print("  - sarah.williams@nigcomsat.gov.ng (HR Manager)")
        print("  - david.brown@nigcomsat.gov.ng (HR Officer)")
        print("\nFinance Department:")
        print("  - emily.davis@nigcomsat.gov.ng (Finance Manager - Dept Head)")
        print("  - james.wilson@nigcomsat.gov.ng (Accountant)")
        print("\nSales & Marketing:")
        print("  - lisa.taylor@nigcomsat.gov.ng (Marketing Specialist)")
        print("  - robert.anderson@nigcomsat.gov.ng (Sales Officer)")
        print("\nSatellite Operations:")
        print("  - patricia.martin@nigcomsat.gov.ng (Satellite Operations Engineer)")
        print("\n" + "="*60)
        print("You can now login with any of these emails")
        print("Password for all users: password123")
        print("="*60)

        db.close()

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        db.close()

if __name__ == "__main__":
    create_dummy_users()

#!/usr/bin/env python3
"""
Debug script to test task creation workflow
"""
import sys
import traceback
from datetime import datetime, timezone
from database import get_db
from models import User
from utils.task_workflows import TaskWorkflowService
from utils.permissions import UserPermissions, SystemPermissions
import uuid

def debug_task_creation():
    """Debug Nancy's task creation"""
    db = next(get_db())

    try:
        # Get Nancy's user
        nancy = db.query(User).filter(User.email == "nancy.white@nigcomsat.gov.ng").first()
        if not nancy:
            print("[ERROR] Nancy not found")
            return

        print(f"[OK] Found Nancy: {nancy.name} ({nancy.email})")
        print(f"   Organization: {nancy.organization_id}")
        print(f"   Role: {nancy.role.name}")
        print(f"   Role permissions: {nancy.role.permissions}")

        # Test permission service
        permission_service = UserPermissions(db)
        has_create_permission = permission_service.user_has_permission(nancy, SystemPermissions.TASK_CREATE)
        print(f"   Has task_create permission: {has_create_permission}")

        # Get effective permissions
        effective_perms = permission_service.get_user_effective_permissions(nancy)
        print(f"   Effective scope: {effective_perms['effective_scope']}")

        # Get assignee
        robert = db.query(User).filter(User.id == uuid.UUID("9ead5206-5a7f-42b8-8362-37817e764668")).first()
        if not robert:
            print("[ERROR] Robert not found")
            return

        print(f"[OK] Found assignee: {robert.name} ({robert.email})")

        # Test scope validation
        can_access = permission_service.user_can_access_organization(nancy, robert.organization_id)
        print(f"   Can Nancy assign to Robert: {can_access}")

        # Test task service
        task_service = TaskWorkflowService(db)

        # Create task data
        task_data = {
            "title": "Debug Test Task",
            "description": "Testing task creation from debug script",
            "type": "individual",
            "urgency": "medium",
            "due_date": datetime(2025, 9, 26, 10, 0, 0, tzinfo=timezone.utc)
        }

        print("[PROGRESS] Attempting to create task...")

        # Try to create task
        task = task_service.create_task(
            creator=nancy,
            task_data=task_data,
            assignee_ids=[robert.id]
        )

        print(f"[SUCCESS] Task created successfully!")
        print(f"   Task ID: {task.id}")
        print(f"   Title: {task.title}")
        print(f"   Urgency: {task.urgency}")
        print(f"   Type: {task.type}")

    except Exception as e:
        print(f"[ERROR] Error during task creation:")
        print(f"   {type(e).__name__}: {str(e)}")
        print(f"   Traceback:")
        traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    debug_task_creation()
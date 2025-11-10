"""
Notification service for real-time notifications and emails
Implementation for notification triggers from CLAUDE.md
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models import User, Initiative, Goal, InitiativeExtension
from utils.email_service import EmailService
import uuid
from datetime import datetime

class NotificationService:
    """
    Handles all notification triggers as specified in CLAUDE.md
    Sends email notifications for important events
    """

    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()

    # Initiative-related notifications
    def notify_initiative_assigned(self, initiative: Initiative, assignees: List[User], created_by: User):
        """Notify users when task is assigned"""
        try:
            due_date = initiative.due_date.strftime("%B %d, %Y at %I:%M %p") if initiative.due_date else "Not specified"

            for assignee in assignees:
                if assignee.email and assignee.status == 'active':
                    try:
                        self.email_service.send_initiative_assignment_email(
                            user_email=assignee.email,
                            user_name=assignee.name or assignee.email,
                            initiative_title=initiative.title,
                            initiative_id=str(initiative.id),
                            due_date=due_date,
                            created_by_name=created_by.name or created_by.email
                        )
                        print(f"✓ Task assignment email sent to {assignee.email}")
                    except Exception as e:
                        print(f"✗ Failed to send task assignment email to {assignee.email}: {e}")
        except Exception as e:
            print(f"Error in notify_initiative_assigned: {e}")

    def notify_initiative_submitted(self, initiative: Initiative, submission, submitted_by: User):
        """Notify task creator when task is submitted"""
        try:
            creator = self.db.query(User).filter(User.id == initiative.created_by).first()
            if creator and creator.email and creator.status == 'active':
                try:
                    self.email_service.send_task_submitted_email(
                        creator_email=creator.email,
                        creator_name=creator.name or creator.email,
                        initiative_title=initiative.title,
                        submitted_by_name=submitted_by.name or submitted_by.email
                    )
                    print(f"✓ Task submission email sent to {creator.email}")
                except Exception as e:
                    print(f"✗ Failed to send task submission email: {e}")
        except Exception as e:
            print(f"Error in notify_initiative_submitted: {e}")

    def notify_task_reviewed(self, initiative: Initiative, assignees: List[User], score: int, feedback: str, approved: bool):
        """Notify assignees when task is reviewed"""
        try:
            for assignee in assignees:
                if assignee.email and assignee.status == 'active':
                    try:
                        self.email_service.send_task_reviewed_email(
                            assignee_email=assignee.email,
                            assignee_name=assignee.name or assignee.email,
                            initiative_title=initiative.title,
                            score=score,
                            feedback=feedback or "",
                            approved=approved
                        )
                        print(f"✓ Task review email sent to {assignee.email}")
                    except Exception as e:
                        print(f"✗ Failed to send task review email to {assignee.email}: {e}")
        except Exception as e:
            print(f"Error in notify_task_reviewed: {e}")

    def notify_initiative_approved(self, initiative: Initiative, assignees: List[User], score: int):
        """Notify assignees when initiative is approved"""
        self.notify_task_reviewed(initiative, assignees, score, initiative.feedback or "", True)

    def notify_initiative_redo_requested(self, initiative: Initiative, assignees: List[User], feedback: str):
        """Notify assignees when redo is requested"""
        self.notify_task_reviewed(initiative, assignees, initiative.score or 0, feedback, False)

    def notify_initiative_overdue(self, initiative: Initiative, stakeholders: List[User]):
        """Notify stakeholders when task becomes overdue"""
        # TODO: Implement overdue notification email
        print(f"Task {initiative.title} is overdue")

    def notify_extension_requested(self, initiative: Initiative, extension: InitiativeExtension):
        """Notify initiative creator when extension is requested"""
        # TODO: Implement extension request notification
        print(f"Extension requested for initiative {initiative.title}")

    def notify_extension_reviewed(self, extension: InitiativeExtension, approved: bool):
        """Notify requester when extension is reviewed"""
        # TODO: Implement extension review notification
        print(f"Extension {'approved' if approved else 'denied'}")

    # Goal-related notifications
    def notify_goal_stakeholders(self, goal: Goal, event_type: str):
        """Notify stakeholders about goal events"""
        # TODO: Implement goal notification emails
        print(f"Goal event: {event_type} for {goal.title}")

    def notify_goal_progress_updated(self, goal: Goal, report):
        """Notify when goal progress is updated"""
        # TODO: Implement goal progress notification
        print(f"Goal progress updated: {goal.title}")

    def notify_goal_discarded(self, goal: Goal, reason: str):
        """Notify when goal is discarded"""
        # TODO: Implement goal discard notification
        print(f"Goal discarded: {goal.title}")

    # User-related notifications
    def notify_user_created(self, user: User, onboarding_token: str):
        """Send onboarding email to new user"""
        try:
            if user.email:
                self.email_service.send_onboarding_email(
                    user_email=user.email,
                    user_name=user.name or user.email,
                    onboarding_token=onboarding_token
                )
                print(f"✓ Onboarding email sent to {user.email}")
        except Exception as e:
            print(f"✗ Failed to send onboarding email: {e}")

    def notify_password_reset(self, user: User, reset_token: str):
        """Send password reset email"""
        try:
            if user.email:
                self.email_service.send_password_reset_email(
                    user_email=user.email,
                    user_name=user.name or user.email,
                    reset_token=reset_token
                )
                print(f"✓ Password reset email sent to {user.email}")
        except Exception as e:
            print(f"✗ Failed to send password reset email: {e}")

    def notify_user_status_changed(self, user: User, old_status: str, new_status: str):
        """Notify relevant users when user status changes"""
        # TODO: Implement status change notification
        print(f"User {user.email} status changed: {old_status} -> {new_status}")

    def notify_user_role_changed(self, user: User, old_role: str, new_role: str):
        """Notify administrators when user role changes"""
        # TODO: Implement role change notification
        print(f"User {user.email} role changed: {old_role} -> {new_role}")
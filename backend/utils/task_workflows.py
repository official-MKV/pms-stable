"""
Task workflow implementation
Based on CLAUDE.md specification for task management workflows
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import uuid

from models import (
    Task, TaskStatus, TaskType, TaskUrgency, TaskAssignment, TaskSubmission,
    TaskDocument, TaskExtension, ExtensionStatus, User, UserStatus
)
from utils.notifications import NotificationService
from utils.permissions import UserPermissions

class TaskWorkflowService:
    """
    Implements task workflows including assignment, submission, review, and overdue management
    """

    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
        self.permission_service = UserPermissions(db)

    def create_task(self, creator: User, task_data: dict, assignee_ids: List[uuid.UUID],
                   team_head_id: Optional[uuid.UUID] = None, document_ids: Optional[List[uuid.UUID]] = None) -> Task:
        """
        Create new task with scope validation and assignment
        """
        # Validate assignment scope
        self.validate_task_assignment(creator, assignee_ids)

        # Validate document ownership if documents are provided
        if document_ids:
            self.validate_document_ownership(creator, document_ids)

        # Create task
        task = Task(
            title=task_data['title'],
            description=task_data.get('description'),
            type=task_data['type'],
            urgency=task_data.get('urgency', 'medium'),
            due_date=task_data['due_date'],
            created_by=creator.id,
            team_head_id=team_head_id
        )

        self.db.add(task)
        self.db.flush()  # Get task ID

        # Create assignments
        for assignee_id in assignee_ids:
            assignment = TaskAssignment(
                task_id=task.id,
                user_id=assignee_id
            )
            self.db.add(assignment)

        # Attach documents if provided
        if document_ids:
            self.attach_documents_to_task(task.id, document_ids)

        self.db.commit()

        # Send notifications
        assignees = self.db.query(User).filter(User.id.in_(assignee_ids)).all()
        self.notification_service.notify_task_assigned(task, assignees, creator)

        return task

    def validate_task_assignment(self, creator: User, assignee_ids: List[uuid.UUID]):
        """
        Validate that creator can assign tasks to specified users
        Based on organizational scope limitations
        """
        for assignee_id in assignee_ids:
            assignee = self.db.query(User).filter(User.id == assignee_id).first()
            if not assignee:
                raise ValueError(f"User {assignee_id} not found")

            if not self.permission_service.user_can_access_organization(creator, assignee.organization_id):
                raise ValueError(f"Cannot assign task to user outside your scope: {assignee.name}")

            if assignee.status != UserStatus.ACTIVE:
                raise ValueError(f"Cannot assign task to inactive user: {assignee.name}")

    def validate_document_ownership(self, creator: User, document_ids: List[uuid.UUID]):
        """
        Validate that creator owns all specified documents
        """
        for document_id in document_ids:
            document = self.db.query(TaskDocument).filter(TaskDocument.id == document_id).first()
            if not document:
                raise ValueError(f"Document {document_id} not found")
            if document.uploaded_by != creator.id:
                raise ValueError(f"Cannot attach document not owned by you: {document.file_name}")
            if document.task_id is not None:
                raise ValueError(f"Document {document.file_name} is already attached to another task")

    def attach_documents_to_task(self, task_id: uuid.UUID, document_ids: List[uuid.UUID]):
        """
        Attach pre-uploaded documents to a task
        """
        for document_id in document_ids:
            document = self.db.query(TaskDocument).filter(TaskDocument.id == document_id).first()
            if document:
                document.task_id = task_id

    def start_task(self, task_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Start a task (change status from PENDING to ONGOING)
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False

        if task.status != TaskStatus.PENDING:
            raise ValueError("Task can only be started from PENDING status")

        # Verify user is assigned to task
        assignment = self.db.query(TaskAssignment).filter(
            and_(TaskAssignment.task_id == task_id, TaskAssignment.user_id == user_id)
        ).first()

        if not assignment:
            raise ValueError("User is not assigned to this task")

        task.status = TaskStatus.ONGOING
        self.db.commit()

        return True

    def submit_task(self, task_id: uuid.UUID, user_id: uuid.UUID, report: str,
                   document_ids: Optional[List[uuid.UUID]] = None) -> bool:
        """
        Submit task completion report
        For group tasks, only team head can submit
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False

        if task.status == TaskStatus.OVERDUE:
            # Check if there's a pending extension
            pending_extension = self.db.query(TaskExtension).filter(
                and_(
                    TaskExtension.task_id == task_id,
                    TaskExtension.status == ExtensionStatus.PENDING
                )
            ).first()
            if pending_extension:
                raise ValueError("Cannot submit overdue task with pending extension request")

        if task.status not in [TaskStatus.ONGOING, TaskStatus.OVERDUE]:
            raise ValueError("Task must be started to submit")

        # For group tasks, verify submitter is team head
        if task.type == TaskType.GROUP:
            if task.team_head_id != user_id:
                raise ValueError("Only team head can submit group tasks")
        else:
            # For individual tasks, verify submitter is assigned
            assignment = self.db.query(TaskAssignment).filter(
                and_(TaskAssignment.task_id == task_id, TaskAssignment.user_id == user_id)
            ).first()
            if not assignment:
                raise ValueError("User is not assigned to this task")

        # Create submission
        submission = TaskSubmission(
            task_id=task_id,
            report=report,
            submitted_by=user_id
        )
        self.db.add(submission)

        # Link documents if provided
        if document_ids:
            for doc_id in document_ids:
                # Verify documents belong to this task
                doc = self.db.query(TaskDocument).filter(
                    and_(TaskDocument.id == doc_id, TaskDocument.task_id == task_id)
                ).first()
                if not doc:
                    raise ValueError(f"Document {doc_id} not found or not associated with this task")

        task.status = TaskStatus.PENDING_REVIEW
        self.db.commit()

        # Notify task creator
        submitted_by = self.db.query(User).filter(User.id == user_id).first()
        if submitted_by:
            self.notification_service.notify_task_submitted(task, submission, submitted_by)

        return True

    def review_task(self, task_id: uuid.UUID, reviewer_id: uuid.UUID, score: int,
                   feedback: Optional[str] = None, approved: bool = True) -> bool:
        """
        Review and score submitted task awaiting review
        Only task creator can review
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False

        if task.status != TaskStatus.PENDING_REVIEW:
            raise ValueError("Task must be submitted and pending review")

        if task.created_by != reviewer_id:
            raise ValueError("Only task creator can review submissions")

        if not (1 <= score <= 10):
            raise ValueError("Score must be between 1 and 10")

        task.score = score
        task.feedback = feedback
        task.reviewed_at = datetime.utcnow()

        if approved:
            task.status = TaskStatus.APPROVED
            # Notify assignees of approval
            assignees = [assignment.user for assignment in task.assignments]
            self.notification_service.notify_task_approved(task, assignees, score)
        else:
            task.status = TaskStatus.ONGOING  # Return to started for redo
            # Notify assignees of redo request
            assignees = [assignment.user for assignment in task.assignments]
            self.notification_service.notify_task_redo_requested(task, assignees, feedback)

        self.db.commit()
        return True

    def request_extension(self, task_id: uuid.UUID, user_id: uuid.UUID,
                         new_due_date: datetime, reason: str) -> TaskExtension:
        """
        Request deadline extension for task
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError("Task not found")

        # Verify user is assigned to task or is team head
        if task.type == TaskType.GROUP:
            if task.team_head_id != user_id:
                raise ValueError("Only team head can request extensions for group tasks")
        else:
            assignment = self.db.query(TaskAssignment).filter(
                and_(TaskAssignment.task_id == task_id, TaskAssignment.user_id == user_id)
            ).first()
            if not assignment:
                raise ValueError("User is not assigned to this task")

        # Check for existing pending extension
        existing_extension = self.db.query(TaskExtension).filter(
            and_(
                TaskExtension.task_id == task_id,
                TaskExtension.status == ExtensionStatus.PENDING
            )
        ).first()

        if existing_extension:
            raise ValueError("Extension request already pending for this task")

        extension = TaskExtension(
            task_id=task_id,
            requested_by=user_id,
            new_due_date=new_due_date,
            reason=reason
        )

        self.db.add(extension)
        self.db.commit()

        # Notify task creator
        self.notification_service.notify_extension_requested(task, extension)

        return extension

    def review_extension(self, extension_id: uuid.UUID, reviewer_id: uuid.UUID,
                        approved: bool, reason: Optional[str] = None) -> bool:
        """
        Approve or deny extension request
        Only task creator can review extensions
        """
        extension = self.db.query(TaskExtension).filter(TaskExtension.id == extension_id).first()
        if not extension:
            return False

        task = extension.task
        if task.created_by != reviewer_id:
            raise ValueError("Only task creator can review extension requests")

        if extension.status != ExtensionStatus.PENDING:
            raise ValueError("Extension request has already been reviewed")

        if approved:
            extension.status = ExtensionStatus.APPROVED
            task.due_date = extension.new_due_date
            # Remove overdue status if task was overdue
            if task.status == TaskStatus.OVERDUE:
                task.status = TaskStatus.ONGOING
        else:
            extension.status = ExtensionStatus.DENIED

        extension.reviewed_by = reviewer_id
        self.db.commit()

        # Notify requester
        self.notification_service.notify_extension_reviewed(extension, approved)

        return True

    def update_overdue_tasks(self):
        """
        Daily cron job to mark tasks as overdue
        Implementation of overdue task management from CLAUDE.md
        """
        now = datetime.utcnow()
        active_tasks = self.db.query(Task).filter(
            Task.status.in_([TaskStatus.PENDING, TaskStatus.ONGOING, TaskStatus.PENDING_REVIEW])
        ).all()

        for task in active_tasks:
            if task.due_date < now and task.status != TaskStatus.APPROVED:
                task.status = TaskStatus.OVERDUE
                self.db.add(task)

                # Notify stakeholders
                stakeholders = [assignment.user for assignment in task.assignments]
                stakeholders.append(task.creator)
                self.notification_service.notify_task_overdue(task, stakeholders)

        self.db.commit()

    def can_submit_task(self, task_id: uuid.UUID) -> bool:
        """
        Check if task can be submitted (handles overdue blocking)
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False

        if task.status == TaskStatus.OVERDUE:
            # Can only submit if no pending extensions
            pending_extensions = self.db.query(TaskExtension).filter(
                and_(
                    TaskExtension.task_id == task_id,
                    TaskExtension.status == ExtensionStatus.PENDING
                )
            ).count()
            return pending_extensions == 0

        return task.status == TaskStatus.ONGOING

    def get_task_visibility(self, user: User, task_id: uuid.UUID) -> bool:
        """
        Check if user can see task based on involvement and permissions
        Implementation of task visibility rules from CLAUDE.md
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False

        # Creator can always see their tasks
        if task.created_by == user.id:
            return True

        # Assigned users can see their tasks
        assignment = self.db.query(TaskAssignment).filter(
            and_(TaskAssignment.task_id == task_id, TaskAssignment.user_id == user.id)
        ).first()
        if assignment:
            return True

        # Team heads can see group tasks they lead
        if task.type == TaskType.GROUP and task.team_head_id == user.id:
            return True

        # Special permission holders within scope
        if self.permission_service.user_has_permission(user, "task_view_all"):
            # Check if user can access the task's organizational scope
            task_creator = self.db.query(User).filter(User.id == task.created_by).first()
            if task_creator:
                return self.permission_service.user_can_access_organization(user, task_creator.organization_id)

        return False

    def get_user_tasks(self, user: User, status_filter: Optional[List[TaskStatus]] = None) -> List[Task]:
        """Get tasks visible to user with optional status filtering"""
        base_query = self.db.query(Task)

        # Filter by status if provided
        if status_filter:
            base_query = base_query.filter(Task.status.in_(status_filter))

        # Get tasks where user is creator, assigned, or team head
        user_task_conditions = or_(
            Task.created_by == user.id,
            Task.assignments.any(TaskAssignment.user_id == user.id),
            and_(Task.type == TaskType.GROUP, Task.team_head_id == user.id)
        )

        tasks = base_query.filter(user_task_conditions).all()
        

        # If user has task_view_all permission, add tasks within scope
        if self.permission_service.user_has_permission(user, "task_view_all"):
            accessible_orgs = self.permission_service.get_accessible_organizations(user)
            additional_tasks = base_query.join(User, Task.created_by == User.id).filter(
                User.organization_id.in_(accessible_orgs)
            ).all()

            # Merge and deduplicate
            task_ids = {task.id for task in tasks}
            for task in additional_tasks:
                if task.id not in task_ids:
                    tasks.append(task)

        return tasks
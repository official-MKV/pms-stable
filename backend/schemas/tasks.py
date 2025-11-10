from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

class TaskType(str, Enum):
    INDIVIDUAL = "individual"
    GROUP = "group"

class TaskStatus(str, Enum):
    PENDING = "pending"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    OVERDUE = "overdue"

class TaskUrgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ExtensionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: TaskType
    urgency: Optional[TaskUrgency] = TaskUrgency.MEDIUM
    due_date: datetime
    goal_id: Optional[uuid.UUID] = None

class TaskCreate(TaskBase):
    assignee_ids: List[uuid.UUID] = Field(..., min_items=1)
    team_head_id: Optional[uuid.UUID] = None
    document_ids: Optional[List[uuid.UUID]] = Field(default_factory=list)

    @validator('due_date')
    def validate_due_date(cls, v):
        if v <= datetime.now():
            raise ValueError('Due date must be in the future')
        return v

    @validator('team_head_id', pre=True)
    def validate_team_head_id(cls, v):
        # Convert empty string to None
        if v == "":
            return None
        return v

    @validator('team_head_id')
    def validate_team_head(cls, v, values):
        if 'type' in values and 'assignee_ids' in values:
            if values['type'] == TaskType.GROUP:
                if v is None:
                    raise ValueError('Group tasks must have a team head')
                if v not in values['assignee_ids']:
                    raise ValueError('Team head must be selected from assigned group members')
            elif values['type'] == TaskType.INDIVIDUAL:
                if len(values['assignee_ids']) != 1:
                    raise ValueError('Individual tasks must have exactly one assignee')
                if v is not None:
                    raise ValueError('Individual tasks cannot have a team head')
        return v

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    urgency: Optional[TaskUrgency] = None
    due_date: Optional[datetime] = None

class TaskStatusUpdate(BaseModel):
    status: TaskStatus

class TaskSubmission(BaseModel):
    report: str = Field(..., min_length=1)
    document_ids: Optional[List[uuid.UUID]] = []

class TaskReview(BaseModel):
    score: int = Field(..., ge=1, le=10)
    feedback: Optional[str] = None
    approved: bool = True

class TaskExtensionRequest(BaseModel):
    new_due_date: datetime
    reason: str = Field(..., min_length=1)

    @validator('new_due_date')
    def validate_new_due_date(cls, v):
        if v <= datetime.now():
            raise ValueError('New due date must be in the future')
        return v

class TaskExtensionReview(BaseModel):
    status: ExtensionStatus
    reason: Optional[str] = None

class TaskInDB(TaskBase):
    id: uuid.UUID
    status: TaskStatus = TaskStatus.PENDING
    score: Optional[int] = None
    feedback: Optional[str] = None
    team_head_id: Optional[uuid.UUID] = None
    created_by: uuid.UUID
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Task(TaskInDB):
    creator_name: Optional[str] = None
    team_head_name: Optional[str] = None
    goal_title: Optional[str] = None
    assignee_count: Optional[int] = 0
    submission_count: Optional[int] = 0
    document_count: Optional[int] = 0
    extension_count: Optional[int] = 0

class TaskAssignee(BaseModel):
    """Task assignment information"""
    user_id: uuid.UUID
    user_name: str
    user_email: str
    assigned_at: datetime

    class Config:
        from_attributes = True

class TaskWithAssignees(Task):
    assignments: List[TaskAssignee] = []

class TaskSubmissionDetail(BaseModel):
    """Task submission with documents"""
    id: uuid.UUID
    report: str
    submitted_by: uuid.UUID
    submitter_name: Optional[str] = None
    submitted_at: datetime
    documents: List[dict] = []

    class Config:
        from_attributes = True

class TaskDocument(BaseModel):
    """Task document attachment"""
    id: uuid.UUID
    file_name: str
    file_path: str
    uploaded_by: uuid.UUID
    uploader_name: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True

class TaskExtension(BaseModel):
    """Task extension request details"""
    id: uuid.UUID
    new_due_date: datetime
    reason: str
    status: ExtensionStatus
    requested_by: uuid.UUID
    requester_name: Optional[str] = None
    reviewed_by: Optional[uuid.UUID] = None
    reviewer_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TaskList(BaseModel):
    """Paginated task list response"""
    tasks: List[TaskWithAssignees]
    total: int
    page: int
    per_page: int

class TaskStats(BaseModel):
    """Task statistics and analytics"""
    total_tasks: int
    by_status: dict[str, int]
    by_type: dict[str, int]
    by_urgency: dict[str, int]
    overdue_tasks: int
    average_score: Optional[float] = None
    completion_rate: float
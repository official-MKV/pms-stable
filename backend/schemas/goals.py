from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
import uuid

class GoalType(str, Enum):
    YEARLY = "YEARLY"
    QUARTERLY = "QUARTERLY"
    INDIVIDUAL = "INDIVIDUAL"

class GoalStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    ACHIEVED = "ACHIEVED"
    DISCARDED = "DISCARDED"
    REJECTED = "REJECTED"

class Quarter(str, Enum):
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"

class GoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: GoalType
    evaluation_method: Optional[str] = Field(None, max_length=255)
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    start_date: date
    end_date: date
    quarter: Optional[Quarter] = None  # Required for INDIVIDUAL goals
    year: Optional[int] = None  # Required for INDIVIDUAL goals

    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

    @validator('quarter')
    def validate_individual_quarter(cls, v, values):
        if 'type' in values and values['type'] == GoalType.INDIVIDUAL and not v:
            raise ValueError('Quarter is required for INDIVIDUAL goals')
        return v

    @validator('year')
    def validate_individual_year(cls, v, values):
        if 'type' in values and values['type'] == GoalType.INDIVIDUAL and not v:
            raise ValueError('Year is required for INDIVIDUAL goals')
        return v

class GoalCreate(GoalBase):
    parent_goal_id: Optional[uuid.UUID] = None
    owner_id: Optional[uuid.UUID] = None  # For INDIVIDUAL goals (if creating for someone else)

class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    evaluation_method: Optional[str] = Field(None, max_length=255)
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class GoalProgressUpdate(BaseModel):
    new_percentage: int = Field(..., ge=0, le=100)
    report: str = Field(..., min_length=1)

class GoalStatusUpdate(BaseModel):
    status: GoalStatus

class GoalInDB(GoalBase):
    id: uuid.UUID
    progress_percentage: int = 0
    status: GoalStatus = GoalStatus.ACTIVE
    parent_goal_id: Optional[uuid.UUID] = None
    created_by: uuid.UUID
    owner_id: Optional[uuid.UUID] = None
    frozen: bool = False
    frozen_at: Optional[datetime] = None
    frozen_by: Optional[uuid.UUID] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[uuid.UUID] = None
    rejection_reason: Optional[str] = None
    achieved_at: Optional[datetime] = None
    discarded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Goal(GoalInDB):
    creator_name: Optional[str] = None
    owner_name: Optional[str] = None
    approver_name: Optional[str] = None
    parent_goal_title: Optional[str] = None
    child_count: Optional[int] = 0

class GoalWithChildren(Goal):
    children: List['GoalWithChildren'] = []

class GoalProgressReport(BaseModel):
    """Progress report entry for manual goal updates"""
    id: uuid.UUID
    old_percentage: Optional[int] = None
    new_percentage: int
    report: str
    updater_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class GoalList(BaseModel):
    """Paginated goal list response"""
    goals: List[Goal]
    total: int
    page: int
    per_page: int

class GoalStats(BaseModel):
    """Goal statistics and analytics"""
    total_goals: int
    by_type: dict[str, int]
    by_status: dict[str, int]
    average_progress: float
    overdue_goals: int

class GoalApproval(BaseModel):
    """Approve or reject an individual goal"""
    approved: bool
    rejection_reason: Optional[str] = None

    @validator('rejection_reason')
    def validate_rejection_reason(cls, v, values):
        if 'approved' in values and not values['approved'] and not v:
            raise ValueError('Rejection reason is required when rejecting a goal')
        return v

class FreezeGoalsRequest(BaseModel):
    """Freeze all goals for a specific quarter"""
    quarter: Quarter
    year: int

class FreezeGoalsResponse(BaseModel):
    """Response after freezing goals"""
    frozen_count: int
    message: str

# Update forward references
GoalWithChildren.model_rebuild()
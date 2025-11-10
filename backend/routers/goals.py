"""
Goal Management API Router
Based on CLAUDE.md specification with hierarchical goal cascade
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from database import get_db
from models import Goal, GoalType, GoalStatus, User, Quarter
from schemas.goals import (
    GoalCreate, GoalUpdate, GoalProgressUpdate, GoalStatusUpdate,
    Goal as GoalSchema, GoalWithChildren, GoalProgressReport, GoalList, GoalStats,
    GoalApproval, FreezeGoalsRequest, FreezeGoalsResponse
)
from schemas.auth import UserSession
from utils.auth import get_current_user
from utils.permissions import UserPermissions, SystemPermissions
from utils.goal_cascade import GoalCascadeService

router = APIRouter(tags=["goals"])

def get_permission_service(db: Session = Depends(get_db)) -> UserPermissions:
    return UserPermissions(db)

def get_goal_service(db: Session = Depends(get_db)) -> GoalCascadeService:
    return GoalCascadeService(db)

@router.get("/", response_model=GoalList)
async def get_goals(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    goal_type: Optional[GoalType] = None,
    status: Optional[GoalStatus] = None,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db),
    permission_service: UserPermissions = Depends(get_permission_service)
):
    """
    List goals filtered by scope and permissions
    Users see goals based on their organizational access and permissions
    """
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get accessible organizations
    # Build base query - all goals are company-wide (yearly/quarterly)
    query = db.query(Goal)

    # Apply scope filtering
    if permission_service.user_has_permission(user, SystemPermissions.GOAL_VIEW_ALL):
        # Can see all goals
        pass  # No filtering needed
    else:
        # Get user's supervisees (users who report to this user)
        supervisee_ids_subquery = db.query(User.id).filter(User.supervisor_id == user.id).subquery()

        # Users can see:
        # 1. All organizational goals (yearly/quarterly) - everyone can view
        # 2. Individual goals they own
        # 3. Individual goals owned by their supervisees (for approval/review)
        # 4. Goals they created
        from sqlalchemy import or_
        visibility_filter = or_(
            Goal.type.in_(['yearly', 'quarterly']),  # All organizational goals
            Goal.owner_id == user.id,  # Individual goals owned by user
            Goal.owner_id.in_(supervisee_ids_subquery),  # Individual goals owned by supervisees
            Goal.created_by == user.id  # Goals created by user
        )
        query = query.filter(visibility_filter)

    # Apply filters
    if goal_type:
        query = query.filter(Goal.type == goal_type)

    if status:
        query = query.filter(Goal.status == status)

    # organization_id filter is no longer applicable since goals are company-wide

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * per_page
    goals = query.offset(offset).limit(per_page).all()

    return GoalList(
        goals=[GoalSchema.from_orm(goal) for goal in goals],
        total=total,
        page=page,
        per_page=per_page
    )

@router.post("/", response_model=GoalSchema)
async def create_goal(
    goal_data: GoalCreate,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db),
    permission_service: UserPermissions = Depends(get_permission_service),
    goal_service: GoalCascadeService = Depends(get_goal_service)
):
    """
    Create new goal with permission gating by type
    - YEARLY/QUARTERLY: Company-wide organizational goals (requires goal_create_yearly/quarterly permission)
    - INDIVIDUAL: Personal employee goals (no special permission required, starts as PENDING_APPROVAL)
    """
    
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Determine initial status based on goal type
    initial_status = GoalStatus.PENDING_APPROVAL if goal_data.type == GoalType.INDIVIDUAL else GoalStatus.ACTIVE

    # Check permission based on goal type (individual goals don't need special permission)
    if goal_data.type != GoalType.INDIVIDUAL:
        required_permission = f"goal_create_{goal_data.type.value.lower()}"
        if not permission_service.user_has_permission(user, required_permission):
            raise HTTPException(status_code=403, detail=f"Missing permission: {required_permission}")

    # Validate parent goal relationship if specified
    if goal_data.parent_goal_id:
        parent_goal = db.query(Goal).filter(Goal.id == goal_data.parent_goal_id).first()
        if not parent_goal:
            raise HTTPException(status_code=404, detail="Parent goal not found")

        # Validate relationship using cascade service
        temp_goal = Goal(**goal_data.dict(exclude={'parent_goal_id'}))
        if not goal_service.validate_goal_relationship(goal_data.parent_goal_id, temp_goal):
            raise HTTPException(status_code=400, detail="Invalid parent-child goal relationship")

    # Validate individual goal requirements
    if goal_data.type == GoalType.INDIVIDUAL:
        if not goal_data.quarter:
            raise HTTPException(status_code=400, detail="Quarter is required for individual goals")
        if not goal_data.year:
            raise HTTPException(status_code=400, detail="Year is required for individual goals")

    # Create goal
    goal = Goal(
        title=goal_data.title,
        description=goal_data.description,
        type=goal_data.type,
        evaluation_method=goal_data.evaluation_method,
        difficulty_level=goal_data.difficulty_level,
        start_date=goal_data.start_date,
        end_date=goal_data.end_date,
        quarter=goal_data.quarter,
        year=goal_data.year,
        parent_goal_id=goal_data.parent_goal_id,
        created_by=user.id,
        owner_id=goal_data.owner_id if goal_data.owner_id else user.id,  # Default to creator as owner
        status=initial_status 
    )

    db.add(goal)
    db.commit()
    db.refresh(goal)

    return GoalSchema.from_orm(goal)

@router.get("/{goal_id}", response_model=GoalSchema)
async def get_goal(
    goal_id: uuid.UUID,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db),
    permission_service: UserPermissions = Depends(get_permission_service)
):
    """
    Get goal details
    """
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    # Check access permissions
    # Check access permissions - all goals are company-wide
    if not permission_service.user_has_permission(user, SystemPermissions.GOAL_VIEW_ALL):
        if goal.created_by != user.id:
            raise HTTPException(status_code=403, detail="Cannot access this goal")

    return GoalSchema.from_orm(goal)

@router.put("/{goal_id}", response_model=GoalSchema)
async def update_goal(
    goal_id: uuid.UUID,
    goal_data: GoalUpdate,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db),
    permission_service: UserPermissions = Depends(get_permission_service)
):
    """
    Edit goal details
    Requires GOAL_EDIT permission
    """
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not permission_service.user_has_permission(user, SystemPermissions.GOAL_EDIT):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    # Check if goal is frozen
    if goal.frozen:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot edit frozen goal. This goal was frozen on {goal.frozen_at.strftime('%Y-%m-%d') if goal.frozen_at else 'unknown date'}."
        )

    # Check access permissions
    if not permission_service.user_has_permission(user, SystemPermissions.GOAL_EDIT):
        if goal.created_by != user.id:
            raise HTTPException(status_code=403, detail="Cannot modify this goal")

    # Update fields
    update_data = goal_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)

    return GoalSchema.from_orm(goal)

@router.put("/{goal_id}/progress", response_model=GoalSchema)
async def update_goal_progress(
    goal_id: uuid.UUID,
    progress_data: GoalProgressUpdate,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db),
    permission_service: UserPermissions = Depends(get_permission_service),
    goal_service: GoalCascadeService = Depends(get_goal_service)
):
    """
    Update progress percentage with required report
    Only allowed for goals without children (leaf goals)
    """
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Allow super-admin or users with goal progress update permission
    is_super_admin = permission_service.user_has_permission(user, SystemPermissions.SYSTEM_ADMIN)
    has_progress_permission = permission_service.user_has_permission(user, SystemPermissions.GOAL_PROGRESS_UPDATE)

    if not (is_super_admin or has_progress_permission):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    # Super-admin can access any goal, others need organizational access
    if not is_super_admin:
        if goal.created_by != user.id:
            raise HTTPException(status_code=403, detail="Cannot update progress for this goal")

    try:
        # Use cascade service to update progress
        success = goal_service.update_goal_progress(
            goal_id, progress_data.new_percentage, progress_data.report, user.id
        )

        if not success:
            raise HTTPException(status_code=400, detail="Failed to update goal progress")

        db.refresh(goal)
        return GoalSchema.from_orm(goal)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{goal_id}/status", response_model=GoalSchema)
async def update_goal_status(
    goal_id: uuid.UUID,
    status_data: GoalStatusUpdate,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db),
    permission_service: UserPermissions = Depends(get_permission_service),
    goal_service: GoalCascadeService = Depends(get_goal_service)
):
    """
    Mark goal as achieved or discard
    Status changes trigger parent goal achievement check
    """
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not permission_service.user_has_permission(user, SystemPermissions.GOAL_STATUS_CHANGE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    # Check access permissions
    if not permission_service.user_has_permission(user, SystemPermissions.GOAL_STATUS_CHANGE):
        if goal.created_by != user.id:
            raise HTTPException(status_code=403, detail="Cannot update status for this goal")

    if status_data.status == GoalStatus.DISCARDED:
        success = goal_service.discard_goal(goal_id, "Manual discard", user.id)
    else:
        goal.status = status_data.status
        if status_data.status == GoalStatus.ACHIEVED:
            goal.achieved_at = db.func.now()
            goal.progress_percentage = 100

        db.commit()

        # Check parent goal cascade if achieving this goal
        if status_data.status == GoalStatus.ACHIEVED and goal.parent_goal_id:
            goal_service.check_goal_auto_achievement(goal.parent_goal_id)

        success = True

    if not success:
        raise HTTPException(status_code=400, detail="Failed to update goal status")

    db.refresh(goal)
    return GoalSchema.from_orm(goal)

@router.get("/{goal_id}/children", response_model=List[GoalSchema])
async def get_goal_children(
    goal_id: uuid.UUID,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db),
    goal_service: GoalCascadeService = Depends(get_goal_service)
):
    """
    Get child goals
    """
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    children = goal_service.get_child_goals(goal_id)
    return [GoalSchema.from_orm(child) for child in children]

@router.get("/{goal_id}/hierarchy")
async def get_goal_hierarchy(
    goal_id: uuid.UUID,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db),
    goal_service: GoalCascadeService = Depends(get_goal_service)
):
    """
    Get complete goal hierarchy starting from specified goal
    Returns nested structure showing parent-child relationships
    """
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    hierarchy = goal_service.get_goal_hierarchy(goal_id)
    return hierarchy

@router.post("/{goal_id}/progress-report", response_model=GoalProgressReport)
async def add_progress_report(
    goal_id: uuid.UUID,
    progress_data: GoalProgressUpdate,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db),
    permission_service: UserPermissions = Depends(get_permission_service),
    goal_service: GoalCascadeService = Depends(get_goal_service)
):
    """
    Add progress report (same as update progress but returns the report)
    """
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not permission_service.user_has_permission(user, SystemPermissions.GOAL_PROGRESS_UPDATE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        success = goal_service.update_goal_progress(
            goal_id, progress_data.new_percentage, progress_data.report, user.id
        )

        if not success:
            raise HTTPException(status_code=400, detail="Failed to add progress report")

        # Get the latest progress report
        from models import GoalProgressReport as ProgressReportModel
        latest_report = db.query(ProgressReportModel).filter(
            ProgressReportModel.goal_id == goal_id
        ).order_by(ProgressReportModel.created_at.desc()).first()

        return GoalProgressReport.from_orm(latest_report)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats", response_model=GoalStats)
async def get_goal_stats(
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db),
    permission_service: UserPermissions = Depends(get_permission_service)
):
    """
    Get goal statistics and analytics
    Returns stats based on user's access scope
    """
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get accessible organizations
    accessible_org_ids = permission_service.get_accessible_organizations(user)

    # Get all goals (company-wide)
    if permission_service.user_has_permission(user, SystemPermissions.GOAL_VIEW_ALL):
        goals = db.query(Goal).all()
    else:
        # Can only see goals they created
        goals = db.query(Goal).filter(Goal.created_by == user.id).all()

    # Calculate statistics
    total_goals = len(goals)

    by_type = {}
    for goal_type in GoalType:
        by_type[goal_type.value] = sum(1 for goal in goals if goal.type == goal_type)

    by_status = {}
    for goal_status in GoalStatus:
        by_status[goal_status.value] = sum(1 for goal in goals if goal.status == goal_status)

    # Calculate average progress
    total_progress = sum(goal.progress_percentage for goal in goals if goal.progress_percentage)
    average_progress = total_progress / len(goals) if goals else 0

    # Count overdue goals
    from datetime import date
    today = date.today()
    overdue_goals = sum(1 for goal in goals
                       if goal.end_date < today and goal.status == GoalStatus.ACTIVE)

    return GoalStats(
        total_goals=total_goals,
        by_type=by_type,
        by_status=by_status,
        average_progress=average_progress,
        overdue_goals=overdue_goals
    )

@router.put("/{goal_id}/approve", response_model=GoalSchema)
async def approve_goal(
    goal_id: uuid.UUID,
    approval: GoalApproval,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db),
    permission_service: UserPermissions = Depends(get_permission_service)
):
    """
    Approve or reject an individual goal
    Only supervisors or HOD can approve goals
    """
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    # Validate goal type
    if goal.type != GoalType.INDIVIDUAL:
        raise HTTPException(
            status_code=400,
            detail="Only INDIVIDUAL goals require approval"
        )

    # Check if goal is pending approval
    if goal.status != GoalStatus.PENDING_APPROVAL:
        raise HTTPException(
            status_code=400,
            detail=f"Goal is not pending approval (current status: {goal.status})"
        )

    # Permission check: must be supervisor or have goal_approve permission
    goal_owner = db.query(User).filter(User.id == goal.owner_id).first()
    can_approve = (
        (goal_owner and goal_owner.supervisor_id == user.id) or  # Is supervisor
        permission_service.user_has_permission(user, 'goal_approve')  # Has permission
    )

    if not can_approve:
        raise HTTPException(
            status_code=403,
            detail="Only supervisors or authorized users can approve goals"
        )

    # Check if goal is frozen
    if goal.frozen:
        raise HTTPException(status_code=400, detail="Cannot approve frozen goal")

    # Apply approval
    if approval.approved:
        goal.status = GoalStatus.ACTIVE
        goal.approved_at = datetime.now()
        goal.approved_by = user.id
        goal.rejection_reason = None
    else:
        goal.status = GoalStatus.REJECTED
        goal.rejection_reason = approval.rejection_reason
        goal.approved_by = user.id
        goal.approved_at = datetime.now()

    db.commit()
    db.refresh(goal)

    return GoalSchema.from_orm(goal)


@router.post("/freeze-quarter", response_model=FreezeGoalsResponse)
async def freeze_goals_for_quarter(
    freeze_request: FreezeGoalsRequest,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db),
    permission_service: UserPermissions = Depends(get_permission_service)
):
    """
    Freeze all goals for a specific quarter
    Frozen goals cannot be edited
    Only users with goal_freeze permission can freeze goals
    """
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Permission check
    # if not permission_service.user_has_permission(user, 'goal_freeze'):
    #     raise HTTPException(
    #         status_code=403,
    #         detail="You do not have permission to freeze goals"
    #     )

    # Get all individual goals for the specified quarter and year
    goals = db.query(Goal).filter(
        Goal.type == GoalType.INDIVIDUAL,
        Goal.quarter == freeze_request.quarter,
        Goal.year == freeze_request.year,
        Goal.frozen == False  # Only freeze goals that aren't already frozen
    ).all()

    if not goals:
        return FreezeGoalsResponse(
            frozen_count=0,
            message=f"No unfrozen individual goals found for {freeze_request.quarter.value} {freeze_request.year}"
        )

    # Freeze all goals
    frozen_count = 0
    for goal in goals:
        goal.frozen = True
        goal.frozen_at = datetime.now()
        goal.frozen_by = user.id
        frozen_count += 1

    db.commit()

    return FreezeGoalsResponse(
        frozen_count=frozen_count,
        message=f"Successfully frozen {frozen_count} goal(s) for {freeze_request.quarter.value} {freeze_request.year}"
    )


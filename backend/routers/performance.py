"""
Performance Management API Router
Handles performance records, development plans, and competency assessments
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from database import get_db
from models import (
    User, PerformanceRecord, DevelopmentPlan, CompetencyAssessment,
    Initiative, InitiativeAssignment, Goal, ReviewCycle, PerformanceRating, DevelopmentPlanStatus
)
from routers.auth import get_current_user
from utils.permissions import UserPermissions, SystemPermissions
from schemas.performance import (
    PerformanceRecordCreate, PerformanceRecordResponse, PerformanceAnalytics,
    DevelopmentPlanCreate, DevelopmentPlanResponse, UserPerformanceSummary,
    CompetencyAssessmentCreate, CompetencyAssessmentResponse
)
from datetime import datetime, timedelta, date
import json

router = APIRouter(prefix="/performance", tags=["performance"])

# Performance Records endpoints
@router.get("/records", response_model=List[PerformanceRecordResponse])
async def get_performance_records(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    period: Optional[str] = Query(None, description="Filter by period"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance records with filtering"""
    user_permissions = UserPermissions(db)

    query = db.query(PerformanceRecord)

    # Apply user filter
    if user_id:
        # Check if user can access this user's data
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        if user_id != str(current_user.id):
            if not user_permissions.user_has_permission(current_user, SystemPermissions.PERFORMANCE_VIEW_ALL):
                if not user_permissions.user_can_access_organization(current_user, target_user.organization_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Cannot access this user's performance data"
                    )

        query = query.filter(PerformanceRecord.user_id == user_id)
    else:
        # If no user specified, show only current user's records unless they have view all permission
        if not user_permissions.user_has_permission(current_user, SystemPermissions.PERFORMANCE_VIEW_ALL):
            query = query.filter(PerformanceRecord.user_id == current_user.id)

    # Apply period filter
    if period:
        query = query.filter(PerformanceRecord.period == period)

    return query.order_by(desc(PerformanceRecord.period_end)).all()

@router.post("/records", response_model=PerformanceRecordResponse)
async def create_performance_record(
    record_data: PerformanceRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new performance record"""
    user_permissions = UserPermissions(db)

    # Check if user can create performance records
    if not user_permissions.user_has_permission(current_user, SystemPermissions.PERFORMANCE_EDIT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create performance records"
        )

    # Verify target user exists and is accessible
    target_user = db.query(User).filter(User.id == record_data.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user_permissions.user_can_access_organization(current_user, target_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create performance record for user outside your scope"
        )

    # Create performance record
    record = PerformanceRecord(
        user_id=record_data.user_id,
        period=record_data.period,
        period_start=record_data.period_start,
        period_end=record_data.period_end,
        overall_rating=record_data.overall_rating,
        goal_achievement_rate=record_data.goal_achievement_rate,
        task_completion_rate=record_data.task_completion_rate,
        average_task_score=record_data.average_task_score,
        technical_competency=record_data.technical_competency,
        leadership_skills=record_data.leadership_skills,
        communication_skills=record_data.communication_skills,
        teamwork_collaboration=record_data.teamwork_collaboration,
        innovation_creativity=record_data.innovation_creativity,
        strengths=record_data.strengths,
        development_areas=record_data.development_areas,
        achievements=record_data.achievements,
        feedback_summary=record_data.feedback_summary
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record

@router.get("/records/{record_id}", response_model=PerformanceRecordResponse)
async def get_performance_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific performance record"""
    user_permissions = UserPermissions(db)

    record = db.query(PerformanceRecord).filter(PerformanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Performance record not found")

    # Check access permissions
    if str(record.user_id) != str(current_user.id):
        if not user_permissions.user_has_permission(current_user, SystemPermissions.PERFORMANCE_VIEW_ALL):
            target_user = db.query(User).filter(User.id == record.user_id).first()
            if not user_permissions.user_can_access_organization(current_user, target_user.organization_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot access this performance record"
                )

    return record

# Development Plans endpoints
@router.get("/development-plans", response_model=List[DevelopmentPlanResponse])
async def get_development_plans(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get development plans with filtering"""
    user_permissions = UserPermissions(db)

    query = db.query(DevelopmentPlan)

    # Apply user filter
    if user_id:
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        if user_id != str(current_user.id):
            if not user_permissions.user_has_permission(current_user, SystemPermissions.PERFORMANCE_VIEW_ALL):
                if not user_permissions.user_can_access_organization(current_user, target_user.organization_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Cannot access this user's development plans"
                    )

        query = query.filter(DevelopmentPlan.user_id == user_id)
    else:
        # If no user specified, show only current user's plans unless they have view all permission
        if not user_permissions.user_has_permission(current_user, SystemPermissions.PERFORMANCE_VIEW_ALL):
            query = query.filter(DevelopmentPlan.user_id == current_user.id)

    # Apply status filter
    if status:
        query = query.filter(DevelopmentPlan.status == status)

    return query.order_by(desc(DevelopmentPlan.start_date)).all()

@router.post("/development-plans", response_model=DevelopmentPlanResponse)
async def create_development_plan(
    plan_data: DevelopmentPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new development plan"""
    user_permissions = UserPermissions(db)

    # Verify target user exists and is accessible
    target_user = db.query(User).filter(User.id == plan_data.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Users can create their own plans, or those with permission can create for others
    if plan_data.user_id != str(current_user.id):
        if not user_permissions.user_has_permission(current_user, SystemPermissions.PERFORMANCE_EDIT):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create development plans for others"
            )

        if not user_permissions.user_can_access_organization(current_user, target_user.organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create development plan for user outside your scope"
            )

    # Create development plan
    plan = DevelopmentPlan(
        user_id=plan_data.user_id,
        title=plan_data.title,
        description=plan_data.description,
        period=plan_data.period,
        start_date=plan_data.start_date,
        end_date=plan_data.end_date,
        objectives=plan_data.objectives,
        activities=plan_data.activities,
        resources=plan_data.resources,
        success_metrics=plan_data.success_metrics,
        created_by=current_user.id
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    return plan

# Analytics endpoints
@router.get("/analytics/summary")
async def get_performance_analytics(
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    period: Optional[str] = Query(None, description="Filter by period"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance analytics and summary data"""
    user_permissions = UserPermissions(db)

    if not user_permissions.user_has_permission(current_user, SystemPermissions.PERFORMANCE_VIEW_ALL):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view performance analytics"
        )

    # Base query for performance records
    query = db.query(PerformanceRecord)

    # Apply organization filter
    if organization_id:
        if not user_permissions.user_can_access_organization(current_user, organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access performance data for this organization"
            )
        # Join with users to filter by organization
        query = query.join(User).filter(User.organization_id == organization_id)

    # Apply period filter
    if period:
        query = query.filter(PerformanceRecord.period == period)

    records = query.all()

    if not records:
        return {
            "total_records": 0,
            "average_ratings": {},
            "competency_averages": {},
            "goal_achievement_rate": 0,
            "task_completion_rate": 0
        }

    # Calculate analytics
    total_records = len(records)

    # Rating distribution
    rating_counts = {}
    for record in records:
        if record.overall_rating:
            rating = record.overall_rating.value
            rating_counts[rating] = rating_counts.get(rating, 0) + 1

    # Average competency scores
    competency_totals = {
        "technical_competency": 0,
        "leadership_skills": 0,
        "communication_skills": 0,
        "teamwork_collaboration": 0,
        "innovation_creativity": 0
    }
    competency_counts = {key: 0 for key in competency_totals.keys()}

    goal_achievement_total = 0
    goal_achievement_count = 0
    task_completion_total = 0
    task_completion_count = 0

    for record in records:
        for competency in competency_totals.keys():
            value = getattr(record, competency)
            if value is not None:
                competency_totals[competency] += value
                competency_counts[competency] += 1

        if record.goal_achievement_rate is not None:
            goal_achievement_total += record.goal_achievement_rate
            goal_achievement_count += 1

        if record.task_completion_rate is not None:
            task_completion_total += record.task_completion_rate
            task_completion_count += 1

    # Calculate averages
    competency_averages = {}
    for competency, total in competency_totals.items():
        count = competency_counts[competency]
        competency_averages[competency] = total / count if count > 0 else 0

    return {
        "total_records": total_records,
        "rating_distribution": rating_counts,
        "competency_averages": competency_averages,
        "goal_achievement_rate": goal_achievement_total / goal_achievement_count if goal_achievement_count > 0 else 0,
        "task_completion_rate": task_completion_total / task_completion_count if task_completion_count > 0 else 0,
        "period": period,
        "organization_id": organization_id
    }

@router.get("/user/{user_id}/summary")
async def get_user_performance_summary(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive performance summary for a specific user"""
    user_permissions = UserPermissions(db)

    # Verify target user exists
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check access permissions
    if user_id != str(current_user.id):
        if not user_permissions.user_has_permission(current_user, SystemPermissions.PERFORMANCE_VIEW_ALL):
            if not user_permissions.user_can_access_organization(current_user, target_user.organization_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot access this user's performance summary"
                )

    # Get performance records
    performance_records = db.query(PerformanceRecord).filter(
        PerformanceRecord.user_id == user_id
    ).order_by(desc(PerformanceRecord.period_end)).all()

    # Get development plans
    development_plans = db.query(DevelopmentPlan).filter(
        DevelopmentPlan.user_id == user_id
    ).order_by(desc(DevelopmentPlan.start_date)).all()

    # Get task statistics
    completed_tasks = db.query(Initiative).join(InitiativeAssignment).filter(
        InitiativeAssignment.user_id == user_id,
        Initiative.status == "approved"
    ).all()

    # Calculate task performance
    task_scores = [task.score for task in completed_tasks if task.score is not None]
    average_task_score = sum(task_scores) / len(task_scores) if task_scores else 0

    # Get goal participation
    user_goals = db.query(Goal).filter(
        Goal.created_by == user_id
    ).all()

    achieved_goals = [goal for goal in user_goals if goal.status.value == "achieved"]
    goal_achievement_rate = len(achieved_goals) / len(user_goals) if user_goals else 0

    return {
        "user": {
            "id": target_user.id,
            "name": target_user.name,
            "job_title": target_user.job_title,
            "organization": target_user.organization.name if target_user.organization else None
        },
        "performance_records": performance_records,
        "development_plans": development_plans,
        "task_performance": {
            "completed_tasks": len(completed_tasks),
            "average_score": average_task_score,
            "scores_distribution": task_scores
        },
        "goal_performance": {
            "total_goals": len(user_goals),
            "achieved_goals": len(achieved_goals),
            "achievement_rate": goal_achievement_rate
        },
        "latest_record": performance_records[0] if performance_records else None
    }
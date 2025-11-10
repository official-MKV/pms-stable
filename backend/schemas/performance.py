"""
Pydantic schemas for Performance Management System
Handles performance records, development plans, and competency assessments
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from models import PerformanceRating, DevelopmentPlanStatus

# Performance Record Schemas
class PerformanceRecordBase(BaseModel):
    user_id: str
    period: str = Field(..., description="Q1-2024, FY-2024, etc.")
    period_start: date
    period_end: date

class PerformanceRecordCreate(PerformanceRecordBase):
    overall_rating: Optional[PerformanceRating] = None
    goal_achievement_rate: Optional[float] = Field(None, ge=0, le=100)
    task_completion_rate: Optional[float] = Field(None, ge=0, le=100)
    average_task_score: Optional[float] = Field(None, ge=0, le=10)
    peer_feedback_score: Optional[float] = Field(None, ge=0, le=10)

    # Competency scores
    technical_competency: Optional[float] = Field(None, ge=0, le=10)
    leadership_skills: Optional[float] = Field(None, ge=0, le=10)
    communication_skills: Optional[float] = Field(None, ge=0, le=10)
    teamwork_collaboration: Optional[float] = Field(None, ge=0, le=10)
    innovation_creativity: Optional[float] = Field(None, ge=0, le=10)

    # Qualitative assessments
    strengths: Optional[List[str]] = Field(default_factory=list)
    development_areas: Optional[List[str]] = Field(default_factory=list)
    achievements: Optional[List[str]] = Field(default_factory=list)
    feedback_summary: Optional[str] = None

class PerformanceRecordUpdate(BaseModel):
    overall_rating: Optional[PerformanceRating] = None
    goal_achievement_rate: Optional[float] = Field(None, ge=0, le=100)
    task_completion_rate: Optional[float] = Field(None, ge=0, le=100)
    average_task_score: Optional[float] = Field(None, ge=0, le=10)
    peer_feedback_score: Optional[float] = Field(None, ge=0, le=10)
    technical_competency: Optional[float] = Field(None, ge=0, le=10)
    leadership_skills: Optional[float] = Field(None, ge=0, le=10)
    communication_skills: Optional[float] = Field(None, ge=0, le=10)
    teamwork_collaboration: Optional[float] = Field(None, ge=0, le=10)
    innovation_creativity: Optional[float] = Field(None, ge=0, le=10)
    strengths: Optional[List[str]] = None
    development_areas: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    feedback_summary: Optional[str] = None

class PerformanceRecordResponse(PerformanceRecordBase):
    id: str
    overall_rating: Optional[PerformanceRating]
    goal_achievement_rate: Optional[float]
    task_completion_rate: Optional[float]
    average_task_score: Optional[float]
    peer_feedback_score: Optional[float]
    technical_competency: Optional[float]
    leadership_skills: Optional[float]
    communication_skills: Optional[float]
    teamwork_collaboration: Optional[float]
    innovation_creativity: Optional[float]
    strengths: Optional[List[str]]
    development_areas: Optional[List[str]]
    achievements: Optional[List[str]]
    feedback_summary: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Development Plan Schemas
class DevelopmentPlanBase(BaseModel):
    user_id: str
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    period: Optional[str] = None
    start_date: date
    end_date: date

class DevelopmentPlanCreate(DevelopmentPlanBase):
    objectives: List[Dict[str, Any]] = Field(..., min_items=1)
    activities: List[Dict[str, Any]] = Field(..., min_items=1)
    resources: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    success_metrics: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class DevelopmentPlanUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    period: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    objectives: Optional[List[Dict[str, Any]]] = None
    activities: Optional[List[Dict[str, Any]]] = None
    resources: Optional[List[Dict[str, Any]]] = None
    success_metrics: Optional[List[Dict[str, Any]]] = None
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[DevelopmentPlanStatus] = None

class DevelopmentPlanResponse(DevelopmentPlanBase):
    id: str
    objectives: List[Dict[str, Any]]
    activities: List[Dict[str, Any]]
    resources: Optional[List[Dict[str, Any]]]
    success_metrics: Optional[List[Dict[str, Any]]]
    progress_percentage: float
    status: DevelopmentPlanStatus
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Competency Assessment Schemas
class CompetencyAssessmentBase(BaseModel):
    user_id: str
    competency_framework: str = Field(..., description="Technical, Leadership, Core, etc.")
    assessment_date: date

class CompetencyAssessmentCreate(CompetencyAssessmentBase):
    competency_scores: Dict[str, float] = Field(..., description="Competency name -> score mapping")
    evidence: Optional[Dict[str, Any]] = Field(default_factory=dict)
    assessor_notes: Optional[str] = None
    development_recommendations: Optional[List[str]] = Field(default_factory=list)

class CompetencyAssessmentUpdate(BaseModel):
    competency_framework: Optional[str] = None
    assessment_date: Optional[date] = None
    competency_scores: Optional[Dict[str, float]] = None
    evidence: Optional[Dict[str, Any]] = None
    assessor_notes: Optional[str] = None
    development_recommendations: Optional[List[str]] = None

class CompetencyAssessmentResponse(CompetencyAssessmentBase):
    id: str
    competency_scores: Dict[str, float]
    evidence: Optional[Dict[str, Any]]
    assessor_notes: Optional[str]
    development_recommendations: Optional[List[str]]
    assessor_id: str
    performance_record_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Analytics and Summary Schemas
class PerformanceAnalytics(BaseModel):
    total_records: int
    rating_distribution: Dict[str, int]
    competency_averages: Dict[str, float]
    goal_achievement_rate: float
    task_completion_rate: float
    period: Optional[str]
    organization_id: Optional[str]

class UserPerformanceSummary(BaseModel):
    user: Dict[str, Any]
    performance_records: List[PerformanceRecordResponse]
    development_plans: List[DevelopmentPlanResponse]
    task_performance: Dict[str, Any]
    goal_performance: Dict[str, Any]
    latest_record: Optional[PerformanceRecordResponse]

class CompetencyFrameworkDefinition(BaseModel):
    framework_name: str
    description: str
    competencies: Dict[str, Dict[str, Any]]  # competency_name -> {description, scale, examples}
    applicable_roles: List[str]
    assessment_frequency: str

class PerformanceTrend(BaseModel):
    user_id: str
    period_start: date
    period_end: date
    trend_data: List[Dict[str, Any]]
    overall_direction: str  # improving, declining, stable
    key_insights: List[str]
    recommendations: List[str]

# Bulk Operations
class BulkPerformanceRecordCreate(BaseModel):
    records: List[PerformanceRecordCreate] = Field(..., min_items=1, max_items=100)
    validate_users: bool = Field(default=True)
    skip_duplicates: bool = Field(default=True)

class BulkOperationResult(BaseModel):
    total_submitted: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]]
    created_ids: List[str]
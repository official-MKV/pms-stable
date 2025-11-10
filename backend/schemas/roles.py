from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

class ScopeOverride(str, Enum):
    NONE = "none"
    GLOBAL = "global"
    CROSS_DIRECTORATE = "cross_directorate"

class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_leadership: bool = False
    scope_override: ScopeOverride = ScopeOverride.NONE
    permissions: List[str] = Field(default_factory=list)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_leadership: Optional[bool] = None
    scope_override: Optional[ScopeOverride] = None
    permissions: Optional[List[str]] = None

class RoleInDB(RoleBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Role(RoleInDB):
    user_count: Optional[int] = 0

class PermissionGroup(BaseModel):
    """Grouped permissions for easier role management"""
    group_name: str
    description: str
    permissions: List[str]

class PermissionList(BaseModel):
    """Complete list of all system permissions grouped by category"""
    organization: PermissionGroup
    role_management: PermissionGroup
    user_management: PermissionGroup
    goal_management: PermissionGroup
    task_management: PermissionGroup
    system_administration: PermissionGroup
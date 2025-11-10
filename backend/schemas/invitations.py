from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from models import InvitationStatus

class InvitationCreate(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    department_id: Optional[int] = None
    employee_id: Optional[str] = None
    role_ids: List[int] = []
    invitation_message: Optional[str] = None
    expires_in_days: int = 7

class BulkInvitationCreate(BaseModel):
    invitations: List[InvitationCreate]

class InvitationResponse(BaseModel):
    id: int
    email: str
    token: str
    status: InvitationStatus
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    employee_id: Optional[str] = None
    invitation_message: Optional[str] = None
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    inviter_name: Optional[str] = None
    department_name: Optional[str] = None
    role_names: List[str] = []

    class Config:
        from_attributes = True

class InvitationAccept(BaseModel):
    token: str
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class InvitationStats(BaseModel):
    total_invitations: int
    pending_invitations: int
    accepted_invitations: int
    expired_invitations: int
    cancelled_invitations: int
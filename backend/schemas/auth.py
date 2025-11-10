from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
import uuid

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[uuid.UUID] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict
    permissions: List[str]
    scope: str

class OnboardingRequest(BaseModel):
    token: str
    password: str = Field(..., min_length=8)

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class UserSession(BaseModel):
    """Current user session information"""
    user_id: uuid.UUID
    email: str
    name: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    skillset: Optional[str] = None
    level: Optional[int] = None
    job_title: Optional[str] = None
    organization_id: uuid.UUID
    organization_name: str
    role_id: uuid.UUID
    role_name: str
    permissions: List[str]
    scope_override: str
    effective_scope: str
    is_leadership: bool
    status: str
    profile_image_path: Optional[str] = None
    profile_image_url: Optional[str] = None
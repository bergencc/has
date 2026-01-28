from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    nickname: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    email: EmailStr


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, min_length=3, max_length=50)


class UserResponse(UserBase):
    id: int
    email: EmailStr
    institution: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    """Public user info (nickname only, no email)"""
    id: int
    nickname: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class GoogleAuthUrl(BaseModel):
    auth_url: str

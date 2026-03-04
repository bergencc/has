from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    dog_tag: str = Field(..., min_length=3, max_length=50)
    decoding: int = Field(..., ge=0, le=100)
    perception: int = Field(..., ge=0, le=100)
    logic: int = Field(..., ge=0, le=100)
    resilience: int = Field(..., ge=0, le=100)
    arcane: int = Field(..., ge=0, le=100)
    insight: int = Field(..., ge=0, le=100)
    treat: int = Field(..., ge=0)


class UserCreate(UserBase):
    email: EmailStr


class UserUpdate(BaseModel):
    decoding: Optional[int] = Field(None, ge=0, le=100)
    perception: Optional[int] = Field(None, ge=0, le=100)
    logic: Optional[int] = Field(None, ge=0, le=100)
    resilience: Optional[int] = Field(None, ge=0, le=100)
    arcane: Optional[int] = Field(None, ge=0, le=100)
    insight: Optional[int] = Field(None, ge=0, le=100)
    treat: Optional[int] = Field(None, ge=0)


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
    """Public user info (dog_tag only, no email)"""
    id: int
    dog_tag: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

from app.schemas.team import TeamListResponse


class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    code: str = Field(..., min_length=3, max_length=50)
    starts_at: datetime
    ends_at: datetime
    registration_opens_at: Optional[datetime] = None
    registration_closes_at: Optional[datetime] = None
    min_team_size: int = Field(1, ge=1, le=10)
    max_team_size: int = Field(4, ge=1, le=10)
    ranking_point: int = Field(0, ge=0, le=10000)
    treat_point: int = Field(0, ge=0, le=10000)
    decoding_point: int = Field(0, ge=0, le=100)
    perception_point: int = Field(0, ge=0, le=100)
    logic_point: int = Field(0, ge=0, le=100)
    resilience_point: int = Field(0, ge=0, le=100)
    arcane_point: int = Field(0, ge=0, le=100)
    insight_point: int = Field(0, ge=0, le=100)
    team_lock_mode: str = Field("open", pattern="^(open|locked)$")
    rules: Optional[dict] = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    registration_opens_at: Optional[datetime] = None
    registration_closes_at: Optional[datetime] = None
    min_team_size: Optional[int] = Field(None, ge=1, le=10)
    max_team_size: Optional[int] = Field(None, ge=1, le=10)
    ranking_point: Optional[int] = Field(None, ge=0, le=10000)
    treat_point: Optional[int] = Field(None, ge=0, le=10000)
    decoding_point: Optional[int] = Field(None, ge=0, le=100)
    perception_point: Optional[int] = Field(None, ge=0, le=100)
    logic_point: Optional[int] = Field(None, ge=0, le=100)
    resilience_point: Optional[int] = Field(None, ge=0, le=100)
    arcane_point: Optional[int] = Field(None, ge=0, le=100)
    insight_point: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[str] = Field(None, pattern="^(draft|registration|active|completed|cancelled)$")
    team_lock_mode: Optional[str] = Field(None, pattern="^(open|locked)$")
    rules: Optional[dict] = None


class EventResponse(EventBase):
    id: int
    status: str
    is_registration_open: bool
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime
    registered_teams_count: int = 0
    challenges_count: int = 0

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    id: int
    title: str
    code: str
    status: str
    starts_at: datetime
    ends_at: datetime
    is_registration_open: bool
    is_active: bool
    registered_teams_count: int = 0

    class Config:
        from_attributes = True


class EventRegistrationCreate(BaseModel):
    event_id: int
    team_id: int


class EventRegistrationResponse(BaseModel):
    id: int
    event_id: int
    team: TeamListResponse
    registered_at: datetime
    status: str

    class Config:
        from_attributes = True


class LeaderboardEntryResponse(BaseModel):
    rank: int
    team_id: int
    team_name: str
    total_points: int
    completed_challenges: int
    total_time_seconds: Optional[int] = None
    hints_used: int
    wrong_attempts: int

    class Config:
        from_attributes = True


class EventLeaderboardResponse(BaseModel):
    event_id: int
    event_title: str
    entries: List[LeaderboardEntryResponse]
    updated_at: datetime

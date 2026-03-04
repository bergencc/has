from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.schemas.user import UserPublic


class TeamBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class TeamMemberResponse(BaseModel):
    id: int
    user: UserPublic
    role: str
    joined_at: datetime
    lock_expires_at: datetime
    is_locked: bool
    can_leave: bool

    class Config:
        from_attributes = True


class TeamResponse(TeamBase):
    id: int
    created_at: datetime
    disbanded_at: Optional[datetime] = None
    members: List[TeamMemberResponse] = []
    member_count: int

    class Config:
        from_attributes = True


class TeamListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    member_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class TeamRankingResponse(BaseModel):
    rank: int
    team_id: int
    team_name: str
    member_count: int
    events_registered: int
    total_points: int
    completed_challenges: int
    hints_used: int
    hint_usage_score: Optional[float] = None


class UserTreatRankingResponse(BaseModel):
    rank: int
    user_id: int
    dog_tag: str
    treat: int
    total_attributes: int


# Join Request schemas
class JoinRequestCreate(BaseModel):
    team_id: int


class JoinRequestVoteCreate(BaseModel):
    vote: str = Field(..., pattern="^(accept|reject)$")


class JoinRequestVoteResponse(BaseModel):
    id: int
    voter: UserPublic
    vote: str
    voted_at: datetime

    class Config:
        from_attributes = True


class JoinRequestResponse(BaseModel):
    id: int
    team_id: int
    team_name: str
    user: UserPublic
    requested_at: datetime
    expires_at: datetime
    status: str
    resolved_at: Optional[datetime] = None
    votes: List[JoinRequestVoteResponse] = []
    votes_needed: int
    votes_received: int

    class Config:
        from_attributes = True


class TeamMembershipStatus(BaseModel):
    has_team: bool
    team: Optional[TeamResponse] = None
    membership: Optional[TeamMemberResponse] = None
    pending_requests: List[JoinRequestResponse] = []

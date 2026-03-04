from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class ChallengeBase(BaseModel):
    type: str = Field(..., pattern="^(riddle|scavenger_code)$")
    title: str = Field(..., min_length=3, max_length=200)
    prompt: str = Field(..., min_length=10)
    ranking_point: int = Field(100, ge=1, le=10000)
    treat_point: int = Field(0, ge=0, le=10000)
    decoding_point: int = Field(0, ge=0, le=100)
    perception_point: int = Field(0, ge=0, le=100)
    logic_point: int = Field(0, ge=0, le=100)
    resilience_point: int = Field(0, ge=0, le=100)
    arcane_point: int = Field(0, ge=0, le=100)
    insight_point: int = Field(0, ge=0, le=100)
    hint_cost: int = Field(10, ge=0, le=1000)
    max_attempts: Optional[int] = Field(None, ge=1, le=100)
    point_decay_per_attempt: int = Field(0, ge=0, le=100)
    hints: Optional[List[str]] = None
    unlock_rule: Optional[dict] = None
    accepted_answers: List[str] = Field(..., min_length=1)
    sort_order: int = Field(0, ge=0)


class ChallengeCreate(ChallengeBase):
    event_id: int


class ChallengeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    prompt: Optional[str] = Field(None, min_length=10)
    ranking_point: Optional[int] = Field(None, ge=1, le=10000)
    treat_point: Optional[int] = Field(None, ge=0, le=10000)
    decoding_point: Optional[int] = Field(None, ge=0, le=100)
    perception_point: Optional[int] = Field(None, ge=0, le=100)
    logic_point: Optional[int] = Field(None, ge=0, le=100)
    resilience_point: Optional[int] = Field(None, ge=0, le=100)
    arcane_point: Optional[int] = Field(None, ge=0, le=100)
    insight_point: Optional[int] = Field(None, ge=0, le=100)
    hint_cost: Optional[int] = Field(None, ge=0, le=1000)
    max_attempts: Optional[int] = Field(None, ge=1, le=100)
    point_decay_per_attempt: Optional[int] = Field(None, ge=0, le=100)
    hints: Optional[List[str]] = None
    unlock_rule: Optional[dict] = None
    accepted_answers: Optional[List[str]] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ChallengeResponse(BaseModel):
    """Challenge response for players (no answers)"""
    id: int
    event_id: int
    type: str
    title: str
    prompt: str
    ranking_point: int
    treat_point: int
    decoding_point: int
    perception_point: int
    logic_point: int
    resilience_point: int
    arcane_point: int
    insight_point: int
    hint_cost: int
    max_attempts: Optional[int] = None
    point_decay_per_attempt: int
    hints_available: int  # Number of hints available
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True


class ChallengeAdminResponse(ChallengeBase):
    """Challenge response for admins (includes answers)"""
    id: int
    event_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChallengeStatusResponse(BaseModel):
    """Challenge status for a team"""
    challenge: ChallengeResponse
    is_unlocked: bool
    is_solved: bool
    attempts_made: int
    hints_used: int
    hints_revealed: List[str] = []  # Hints that have been used
    points_possible: int  # After penalties
    solved_at: Optional[datetime] = None
    points_awarded: Optional[int] = None


# Attempt schemas
class AttemptCreate(BaseModel):
    challenge_id: int
    answer: str = Field(..., min_length=1, max_length=500)


class AttemptResponse(BaseModel):
    id: int
    challenge_id: int
    is_correct: bool
    points_awarded: int
    submitted_at: datetime
    message: str  # Feedback message
    attempts_remaining: Optional[int] = None

    class Config:
        from_attributes = True


# Hint schemas
class HintRequest(BaseModel):
    challenge_id: int


class HintResponse(BaseModel):
    hint_index: int
    hint_text: str
    penalty_applied: int
    hints_remaining: int

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING, Any

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.team import Team
    from app.models.challenge import Challenge


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)  # e.g., "BCC-SAB-FALL26"

    # Timing
    registration_opens_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    registration_closes_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Team constraints
    min_team_size: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_team_size: Mapped[int] = mapped_column(Integer, default=4, nullable=False)

    # Reward/Penalty profile
    ranking_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    treat_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    decoding_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    perception_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    logic_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    resilience_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    arcane_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    insight_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Rules
    rules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Custom rules JSON
    team_lock_mode: Mapped[str] = mapped_column(String(20), default="open", nullable=False)  # open, locked

    # Status
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)  # draft, registration, active, completed, cancelled

    # Metadata
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    registrations: Mapped[List["EventRegistration"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    challenges: Mapped[List["Challenge"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    leaderboard_entries: Mapped[List["EventLeaderboard"]] = relationship(back_populates="event", cascade="all, delete-orphan")

    @property
    def is_registration_open(self) -> bool:
        now = datetime.now(timezone.utc)

        if self.registration_opens_at and now < self.registration_opens_at:
            return False

        if self.registration_closes_at and now > self.registration_closes_at:
            return False

        return self.status in ["draft", "registration"]

    @property
    def is_active(self) -> bool:
        now = datetime.now(timezone.utc)

        return self.status == "active" and self.starts_at <= now <= self.ends_at

    def __repr__(self) -> str:
        return f"<Event {self.title} ({self.code})>"


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)
    registered_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="registered", nullable=False)  # registered, withdrawn, disqualified
    outcome_applied: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    event: Mapped["Event"] = relationship(back_populates="registrations")
    team: Mapped["Team"] = relationship(back_populates="event_registrations")

    def __repr__(self) -> str:
        return f"<EventRegistration event={self.event_id} team={self.team_id}>"


class EventLeaderboard(Base):
    __tablename__ = "event_leaderboards"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)

    # Scoring
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_challenges: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_time_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Time to last solve
    hints_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wrong_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Rank (computed)
    rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    event: Mapped["Event"] = relationship(back_populates="leaderboard_entries")
    team: Mapped["Team"] = relationship()

    def __repr__(self) -> str:
        return f"<EventLeaderboard event={self.event_id} team={self.team_id} rank={self.rank}>"

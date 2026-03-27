"""Event management models.

This module defines the core entities for organizing and tracking competitive events
in the Hide and Seek application. Events are time-bound competitions with challenges,
team registrations, and leaderboards. The models support flexible configuration for
rules, rewards, and status tracking.

Key concepts:
- Events have phases: draft -> registration -> active -> completed/cancelled.
- Teams register during open periods and compete on associated challenges.
- Leaderboards track progress and compute rankings based on points and performance.
"""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING, Any

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.team import Team
    from app.models.challenge import Challenge


class Event(Base):
    """Represents a competitive event with challenges, registrations, and leaderboards.

    An event is the top-level entity for a competition, defining its schedule,
    rules, team constraints, and reward structure. Events progress through
    lifecycle states and manage related registrations and leaderboard entries.

    Attributes:
        id: Unique primary key.
        title: Human-readable event name.
        description: Optional detailed description.
        code: Unique short code (e.g., "BCC-SAB-FALL26") for URLs/identifiers.

        registration_opens_at: Optional start of registration window (UTC).
        registration_closes_at: Optional end of registration window (UTC).
        starts_at: Event start time (required, UTC).
        ends_at: Event end time (required, UTC).

        min_team_size: Minimum team members allowed (default 1).
        max_team_size: Maximum team members allowed (default 4).

        ranking_point: Base points for participation.
        treat_point: Treat currency reward.
        decoding_point, perception_point, logic_point, resilience_point,
        arcane_point, insight_point: Stat point rewards for completion.

        rules: Optional JSON object with custom event rules.
        team_lock_mode: "open" or "locked" - whether teams can change during event.
        status: Lifecycle state ("draft", "registration", "active", "completed", "cancelled").

        created_by: User ID who created the event.
        created_at: Creation timestamp (UTC).
        updated_at: Last update timestamp (UTC).

    Relationships:
        registrations: List of EventRegistration entries.
        challenges: List of associated Challenge entities.
        leaderboard_entries: List of EventLeaderboard entries.

    Properties:
        is_registration_open: True if registration is currently allowed.
        is_active: True if event is running (between start/end times and status=active).
    """

    __tablename__ = "events"

    # Primary identifier
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Basic event info
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)  # e.g., "BCC-SAB-FALL26"

    # Timing fields (all UTC)
    registration_opens_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    registration_closes_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Team size constraints
    min_team_size: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_team_size: Mapped[int] = mapped_column(Integer, default=4, nullable=False)

    # Reward points (awarded on completion)
    ranking_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    treat_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    decoding_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    perception_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    logic_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    resilience_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    arcane_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    insight_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Rules and configuration
    rules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Custom rules JSON
    team_lock_mode: Mapped[str] = mapped_column(String(20), default="open", nullable=False)  # open, locked

    # Status and lifecycle
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)  # draft, registration, active, completed, cancelled

    # Audit fields
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
        """Check if team registration is currently allowed.

        Considers current time, registration window, and event status.
        Returns True if within window and status allows registration.
        """
        now = datetime.now(timezone.utc)

        if self.registration_opens_at and now < self.registration_opens_at:
            return False

        if self.registration_closes_at and now > self.registration_closes_at:
            return False

        return self.status in ["draft", "registration"]

    @property
    def is_active(self) -> bool:
        """Check if the event is currently running.

        Returns True if status is 'active' and current time is between start/end.
        """
        now = datetime.now(timezone.utc)

        return self.status == "active" and self.starts_at <= now <= self.ends_at

    def __repr__(self) -> str:
        """Return a string representation of the event."""
        return f"<Event {self.title} ({self.code})>"


class EventRegistration(Base):
    """Tracks team registrations for events.

    Represents a team's participation in an event, including registration time,
    status, and outcome processing state. Used to manage who can compete and
    track participation history.

    Attributes:
        id: Unique primary key.
        event_id: Foreign key to the event.
        team_id: Foreign key to the registered team.
        registered_by: User ID who performed the registration.
        registered_at: Registration timestamp (UTC).
        status: Registration state ("registered", "withdrawn", "disqualified").
        outcome_applied: Whether rewards/penalties have been processed.

    Relationships:
        event: The associated Event.
        team: The registered Team.
    """

    __tablename__ = "event_registrations"

    # Primary identifier
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign keys
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)
    registered_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Registration details
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
        """Return a string representation of the registration."""
        return f"<EventRegistration event={self.event_id} team={self.team_id}>"


class EventLeaderboard(Base):
    """Tracks team performance and rankings in events.

    Maintains real-time scoring for registered teams, including points earned,
    challenges completed, and performance metrics. Rankings are computed based
    on total points and tie-breakers.

    Attributes:
        id: Unique primary key.
        event_id: Foreign key to the event.
        team_id: Foreign key to the competing team.

        total_points: Accumulated points from challenges.
        completed_challenges: Number of solved challenges.
        total_time_seconds: Optional total time to completion (for speed rankings).
        hints_used: Penalty count for hints requested.
        wrong_attempts: Count of incorrect submissions.

        rank: Computed ranking position (1-based, null if not ranked).
        updated_at: Last score update timestamp (UTC).

    Relationships:
        event: The associated Event.
        team: The competing Team.
    """

    __tablename__ = "event_leaderboards"

    # Primary identifier
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign keys
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)

    # Scoring metrics
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_challenges: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_time_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Time to last solve
    hints_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wrong_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Computed rank
    rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Audit
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
        """Return a string representation of the leaderboard entry."""
        return f"<EventLeaderboard event={self.event_id} team={self.team_id} rank={self.rank}>"

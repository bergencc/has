from datetime import datetime, timezone, timedelta
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING

from app.core.database import Base
from app.core.config import settings

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.event import EventRegistration
    from app.models.challenge import Attempt, HintUse


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    disbanded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    members: Mapped[List["TeamMember"]] = relationship(back_populates="team", cascade="all, delete-orphan")
    join_requests: Mapped[List["JoinRequest"]] = relationship(back_populates="team", cascade="all, delete-orphan")
    event_registrations: Mapped[List["EventRegistration"]] = relationship(back_populates="team", cascade="all, delete-orphan")
    attempts: Mapped[List["Attempt"]] = relationship(back_populates="team", cascade="all, delete-orphan")
    hint_uses: Mapped[List["HintUse"]] = relationship(back_populates="team", cascade="all, delete-orphan")

    @property
    def active_members(self) -> List["TeamMember"]:
        return [m for m in self.members if m.left_at is None]

    @property
    def member_count(self) -> int:
        return len(self.active_members)

    def __repr__(self) -> str:
        return f"<Team {self.name}>"


class TeamMember(Base):
    __tablename__ = "team_members"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)  # member, captain
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    lock_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(days=settings.team_lock_days),
        nullable=False
    )
    left_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    team: Mapped["Team"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="team_memberships")

    @property
    def is_locked(self) -> bool:
        if self.left_at is not None:
            return False

        return datetime.now(timezone.utc) < self.lock_expires_at

    @property
    def can_leave(self) -> bool:
        return not self.is_locked

    def __repr__(self) -> str:
        return f"<TeamMember user={self.user_id} team={self.team_id}>"


class JoinRequest(Base):
    __tablename__ = "join_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=settings.join_request_expiry_hours),
        nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending, accepted, rejected, expired, cancelled
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    team: Mapped["Team"] = relationship(back_populates="join_requests")
    user: Mapped["User"] = relationship(back_populates="join_requests")
    votes: Mapped[List["JoinRequestVote"]] = relationship(back_populates="join_request", cascade="all, delete-orphan")

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at and self.status == "pending"

    def __repr__(self) -> str:
        return f"<JoinRequest user={self.user_id} team={self.team_id} status={self.status}>"


class JoinRequestVote(Base):
    __tablename__ = "join_request_votes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    join_request_id: Mapped[int] = mapped_column(ForeignKey("join_requests.id"), nullable=False, index=True)
    voter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    vote: Mapped[str] = mapped_column(String(10), nullable=False)  # accept, reject
    voted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    join_request: Mapped["JoinRequest"] = relationship(back_populates="votes")
    voter: Mapped["User"] = relationship(back_populates="join_request_votes")

    def __repr__(self) -> str:
        return f"<JoinRequestVote request={self.join_request_id} voter={self.voter_id} vote={self.vote}>"

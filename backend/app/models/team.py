"""Team management models.

This module defines the database schema for teams, memberships, join requests, and voting.
It supports collaborative gameplay with team formation, membership locking, and democratic
join approval processes. Teams can participate in events and track collective progress.
"""

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
    """Represents a user-created team for collaborative gameplay.

    Teams allow users to group together for events, share rewards, and compete as a unit.
    Each team has a unique name, optional description, and tracks creation/disbandment.
    Membership is managed through TeamMember records with role-based permissions.

    Attributes:
        id: Unique primary key.
        name: Unique team name (up to 100 chars, indexed).
        description: Optional team description/bio.
        created_at: UTC timestamp of team creation.
        disbanded_at: UTC timestamp if team was disbanded (null if active).

    Relationships:
        members: List of TeamMember associations (active and historical).
        join_requests: Pending/accepted join requests from users.
        event_registrations: Team's participation in events.
        attempts: Team's challenge attempts.
        hint_uses: Team's hint usage records.

    Properties:
        active_members: List of current (non-left) team members.
        member_count: Count of active members.

    Notes:
        - Teams can be disbanded but records are retained for history.
        - Cascade delete removes all related records on team deletion.
    """

    __tablename__ = "teams"

    # Primary key: auto-incrementing unique identifier.
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Name: unique team identifier, used in UI and URLs.
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    # Description: optional team bio or mission statement.
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Created At: when the team was formed (UTC).
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Disbanded At: null if active, set when team is dissolved.
    disbanded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships: linked entities for team activities.
    members: Mapped[List["TeamMember"]] = relationship(back_populates="team", cascade="all, delete-orphan")
    join_requests: Mapped[List["JoinRequest"]] = relationship(back_populates="team", cascade="all, delete-orphan")
    event_registrations: Mapped[List["EventRegistration"]] = relationship(back_populates="team", cascade="all, delete-orphan")
    attempts: Mapped[List["Attempt"]] = relationship(back_populates="team", cascade="all, delete-orphan")
    hint_uses: Mapped[List["HintUse"]] = relationship(back_populates="team", cascade="all, delete-orphan")

    @property
    def active_members(self) -> List["TeamMember"]:
        """Return list of current team members (not left)."""
        return [m for m in self.members if m.left_at is None]

    @property
    def member_count(self) -> int:
        """Return count of active team members."""
        return len(self.active_members)

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"<Team {self.name}>"


class TeamMember(Base):
    """Association between a user and a team with membership details.

    Tracks user participation in teams, including roles, join/leave dates, and lock periods
    to prevent rapid team-hopping. Members can be 'member' or 'captain' with different perms.

    Attributes:
        id: Unique primary key.
        team_id: Foreign key to Team.
        user_id: Foreign key to User.
        role: 'member' or 'captain' (default 'member').
        joined_at: UTC timestamp when user joined.
        lock_expires_at: UTC timestamp until user is locked from leaving (from config).
        left_at: UTC timestamp if user left (null if active).

    Relationships:
        team: The associated Team.
        user: The associated User.

    Properties:
        is_locked: True if user cannot leave yet (based on lock_expires_at).
        can_leave: True if user is not locked and can leave.

    Notes:
        - Lock prevents leaving for team_lock_days after joining.
        - Captains may have elevated permissions in team management.
    """

    __tablename__ = "team_members"

    # Primary key: auto-incrementing unique identifier.
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Team ID: references the team this membership belongs to.
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)

    # User ID: references the user who is a member.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Role: 'member' (default) or 'captain' for permissions.
    role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)

    # Joined At: when the user became a member (UTC).
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Lock Expires At: user cannot leave until this time (prevents team-hopping).
    lock_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(days=settings.team_lock_days),
        nullable=False
    )

    # Left At: null if active, set when user leaves.
    left_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships: bidirectional links to team and user.
    team: Mapped["Team"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="team_memberships")

    @property
    def is_locked(self) -> bool:
        """Check if the member is currently locked from leaving the team."""
        if self.left_at is not None:
            return False

        return datetime.now(timezone.utc) < self.lock_expires_at

    @property
    def can_leave(self) -> bool:
        """Check if the member can voluntarily leave the team."""
        return not self.is_locked

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"<TeamMember user={self.user_id} team={self.team_id}>"


class JoinRequest(Base):
    """Request from a user to join a team, subject to voting and expiration.

    Users can request to join teams, and existing members vote to accept/reject.
    Requests expire after a configured time and can be cancelled or resolved.

    Attributes:
        id: Unique primary key.
        team_id: Foreign key to Team.
        user_id: Foreign key to User.
        requested_at: UTC timestamp of request creation.
        expires_at: UTC timestamp when request expires (from config).
        status: 'pending', 'accepted', 'rejected', 'expired', 'cancelled'.
        resolved_at: UTC timestamp when status changed from pending.

    Relationships:
        team: The team being requested to join.
        user: The user making the request.
        votes: List of votes on this request.

    Properties:
        is_expired: True if past expiry and still pending.

    Notes:
        - Voting is democratic; majority may decide acceptance.
        - Expired requests are not automatically cleaned but marked.
    """

    __tablename__ = "join_requests"

    # Primary key: auto-incrementing unique identifier.
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Team ID: the team the user wants to join.
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)

    # User ID: the user requesting to join.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Requested At: when the request was made (UTC).
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Expires At: request becomes invalid after this time.
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=settings.join_request_expiry_hours),
        nullable=False
    )

    # Status: lifecycle state of the request.
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)

    # Resolved At: when status was set to non-pending.
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships: links to team, user, and votes.
    team: Mapped["Team"] = relationship(back_populates="join_requests")
    user: Mapped["User"] = relationship(back_populates="join_requests")
    votes: Mapped[List["JoinRequestVote"]] = relationship(back_populates="join_request", cascade="all, delete-orphan")

    @property
    def is_expired(self) -> bool:
        """Check if the request has expired and is still pending."""
        return datetime.now(timezone.utc) > self.expires_at and self.status == "pending"

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"<JoinRequest user={self.user_id} team={self.team_id} status={self.status}>"


class JoinRequestVote(Base):
    """Vote by a team member on a join request.

    Team members can vote 'accept' or 'reject' on pending join requests.
    Votes are recorded with timestamps for audit and decision-making.

    Attributes:
        id: Unique primary key.
        join_request_id: Foreign key to JoinRequest.
        voter_id: Foreign key to User (the voter).
        vote: 'accept' or 'reject'.
        voted_at: UTC timestamp of the vote.

    Relationships:
        join_request: The request being voted on.
        voter: The user who cast the vote.

    Notes:
        - Each member can vote once per request (enforced by app logic).
        - Votes help determine if request is accepted (e.g., majority rule).
    """

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

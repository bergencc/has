from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.team import TeamMember, JoinRequest, JoinRequestVote
    from app.models.event import EventRegistration
    from app.models.challenge import Attempt, HintUse


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("decoding >= 0 AND decoding <= 100", name="ck_users_decoding_range"),
        CheckConstraint("perception >= 0 AND perception <= 100", name="ck_users_perception_range"),
        CheckConstraint("logic >= 0 AND logic <= 100", name="ck_users_logic_range"),
        CheckConstraint("resilience >= 0 AND resilience <= 100", name="ck_users_resilience_range"),
        CheckConstraint("arcane >= 0 AND arcane <= 100", name="ck_users_arcane_range"),
        CheckConstraint("insight >= 0 AND insight <= 100", name="ck_users_insight_range"),
        CheckConstraint("treat >= 0", name="ck_users_treat_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    dog_tag: Mapped[str] = mapped_column(String(50), default="witness", index=True, nullable=False)
    decoding: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    perception: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    logic: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    resilience: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    arcane: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    insight: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    treat: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    institution: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="student", nullable=False)  # student, admin
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    team_memberships: Mapped[List["TeamMember"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    join_requests: Mapped[List["JoinRequest"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    join_request_votes: Mapped[List["JoinRequestVote"]] = relationship(back_populates="voter", cascade="all, delete-orphan")
    attempts: Mapped[List["Attempt"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    hint_uses: Mapped[List["HintUse"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.dog_tag} ({self.email})>"

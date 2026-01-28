from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
import re
import unicodedata

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.team import Team
    from app.models.user import User


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False, index=True)

    # Basic info
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # riddle, scavenger_code
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)

    # Scoring
    points: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    hint_cost: Mapped[int] = mapped_column(Integer, default=10, nullable=False)  # Points deducted per hint
    max_attempts: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # None = unlimited
    point_decay_per_attempt: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Points lost per wrong attempt

    # Hints (stored as JSON array of strings)
    hints: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Unlock rules
    unlock_rule: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Examples:
    # null = always unlocked
    # {"type": "after", "challenge_id": 5}
    # {"type": "points", "minimum": 200}

    # Answer matching
    accepted_answers: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # Normalized accepted strings

    # Ordering
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    event: Mapped["Event"] = relationship(back_populates="challenges")
    attempts: Mapped[List["Attempt"]] = relationship(back_populates="challenge", cascade="all, delete-orphan")
    hint_uses: Mapped[List["HintUse"]] = relationship(back_populates="challenge", cascade="all, delete-orphan")

    @staticmethod
    def normalize_answer(answer: str) -> str:
        """Normalize an answer for comparison."""
        if not answer:
            return ""

        # Lowercase
        normalized = answer.lower()

        # Normalize unicode characters
        normalized = unicodedata.normalize('NFKD', normalized)

        # Remove punctuation except spaces
        normalized = re.sub(r'[^\w\s]', '', normalized)

        # Collapse multiple spaces to single space
        normalized = re.sub(r'\s+', ' ', normalized)

        # Strip leading/trailing whitespace
        normalized = normalized.strip()

        # Optionally remove common articles
        articles = ['the', 'a', 'an']
        words = normalized.split()

        if words and words[0] in articles:
            normalized = ' '.join(words[1:])

        return normalized

    def check_answer(self, submitted: str) -> bool:
        """Check if a submitted answer matches any accepted answer."""
        normalized_submitted = self.normalize_answer(submitted)

        for accepted in self.accepted_answers:
            if self.normalize_answer(accepted) == normalized_submitted:
                return True

        return False

    def __repr__(self) -> str:
        return f"<Challenge {self.title} ({self.type})>"


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    submitted_answer: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_answer: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    points_awarded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    challenge: Mapped["Challenge"] = relationship(back_populates="attempts")
    team: Mapped["Team"] = relationship(back_populates="attempts")
    user: Mapped["User"] = relationship(back_populates="attempts")

    def __repr__(self) -> str:
        return f"<Attempt challenge={self.challenge_id} team={self.team_id} correct={self.is_correct}>"


class HintUse(Base):
    __tablename__ = "hint_uses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    hint_index: Mapped[int] = mapped_column(Integer, nullable=False)  # 0, 1, 2, ...
    used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    penalty_applied: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Points deducted

    # Relationships
    challenge: Mapped["Challenge"] = relationship(back_populates="hint_uses")
    team: Mapped["Team"] = relationship(back_populates="hint_uses")
    user: Mapped["User"] = relationship(back_populates="hint_uses")

    def __repr__(self) -> str:
        return f"<HintUse challenge={self.challenge_id} team={self.team_id} hint={self.hint_index}>"

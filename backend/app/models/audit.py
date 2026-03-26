"""Audit logging models.

This module defines the database schema for tracking user actions and system events.
Audit logs are immutable records used for compliance, debugging, and security monitoring.
They capture who did what, when, and contextual details without storing sensitive data.
"""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, Any

from app.core.database import Base


class AuditLog(Base):
    """Immutable audit log entry for tracking user and system actions.

    This model stores structured records of significant events in the application,
    such as user logins, challenge completions, team changes, or admin actions.
    Each log entry is timestamped and includes optional metadata for context.

    The table is designed for high-volume inserts with minimal updates/deletes.
    Indexes are placed on frequently queried fields (id, actor_id, action, occurred_at).

    Attributes:
        id: Unique primary key for the audit entry.
        actor_id: ID of the user who performed the action (nullable for system events).
        action: Short string describing the action (e.g., 'login', 'challenge_complete').
        target_type: Type of entity affected (e.g., 'user', 'team', 'challenge').
        target_id: ID of the specific entity affected.
        metadata: JSON object with additional context (e.g., {'old_value': 'x', 'new_value': 'y'}).
        ip_address: Client IP address at the time of action (for security tracking).
        occurred_at: UTC timestamp when the action occurred (auto-set on insert).

    Notes:
        - All fields except id and occurred_at are nullable to support various event types.
        - Metadata should avoid storing PII or secrets; use for operational context only.
        - The __repr__ provides a concise summary for debugging/logging.
    """

    __tablename__ = "audit_logs"

    # Primary key: auto-incrementing unique identifier.
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Actor: the user who initiated the action (null for anonymous/system events).
    actor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)

    # Action: descriptive string of what happened (e.g., 'user_login', 'team_join').
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Target: the entity type and ID affected by the action.
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Metadata: flexible JSON for extra details (e.g., changed fields, error codes).
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # IP Address: captured for security/audit purposes (supports IPv4/IPv6).
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # Timestamp: when the event occurred (UTC, indexed for time-range queries).
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    def __repr__(self) -> str:
        """Return a string representation of the audit log entry.

        Useful for logging and debugging; shows key identifiers and timestamp.
        """
        return f"<AuditLog {self.action} by={self.actor_id} at={self.occurred_at}>"

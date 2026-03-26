"""Reward utilities and batching helpers.

This module provides functions for updating user reward stats, keeping all
stat attributes in range, recalculating the derived dog-tag tier, and applying
bulk deltas to active team members.

The module intentionally mutates User model objects in memory (SQLAlchemy ORM
instances). Commit/flush is expected from the caller context/session manager.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.team import TeamMember


def clamp_stat(value: int) -> int:
    """Clamp a user stat to the allowed [0, 100] range.

    Args:
        value: Proposed updated stat value.

    Returns:
        int: clamped stat value between 0 and 100.
    """
    return max(0, min(100, value))


def get_total_attributes(user: User) -> int:
    """Compute a user's combined skill total.

    Args:
        user: user ORM instance with six stat attributes.

    Returns:
        int: sum of decoding, perception, logic, resilience, arcane, insight.
    """
    return (
        user.decoding
        + user.perception
        + user.logic
        + user.resilience
        + user.arcane
        + user.insight
    )


def get_dog_tag_for_total(total_attributes: int) -> str:
    """Map a total stat score to a dog-tag zone.

    Args:
        total_attributes: aggregated user attribute points.

    Returns:
        str: one of {'enigma','oracle','codebreaker','scout','witness'}.
    """
    if total_attributes >= 550:
        return "enigma"
    if total_attributes >= 451:
        return "oracle"
    if total_attributes >= 401:
        return "codebreaker"
    if total_attributes >= 301:
        return "scout"
    return "witness"


def sync_dog_tag(user: User) -> None:
    """Update a user's dog_tag field to match current total stats.

    Args:
        user: user ORM instance.
    """
    user.dog_tag = get_dog_tag_for_total(get_total_attributes(user))


def apply_user_reward_delta(
    user: User,
    *,
    treat: int = 0,
    decoding: int = 0,
    perception: int = 0,
    logic: int = 0,
    resilience: int = 0,
    arcane: int = 0,
    insight: int = 0,
) -> None:
    """Apply reward deltas to a single user model in place.

    This updates numeric reward fields and maintains invariants:
    - treat is never negative.
    - each stat is clamped to [0,100].
    - dog_tag is kept in sync with total stats.

    Args:
        user: user ORM instance to modify.
        treat: treat delta (non-negative floor at 0).
        decoding, perception, logic, resilience, arcane, insight: per-stat deltas.
    """
    user.treat = max(0, user.treat + treat)
    user.decoding = clamp_stat(user.decoding + decoding)
    user.perception = clamp_stat(user.perception + perception)
    user.logic = clamp_stat(user.logic + logic)
    user.resilience = clamp_stat(user.resilience + resilience)
    user.arcane = clamp_stat(user.arcane + arcane)
    user.insight = clamp_stat(user.insight + insight)
    sync_dog_tag(user)


async def apply_team_member_reward_delta(
    db: AsyncSession,
    *,
    team_id: int,
    treat: int = 0,
    decoding: int = 0,
    perception: int = 0,
    logic: int = 0,
    resilience: int = 0,
    arcane: int = 0,
    insight: int = 0,
) -> None:
    """Bulk apply reward deltas to active members of a team.

    Selects all users still on the team (`left_at is None`) and applies the same
    delta to each member via `apply_user_reward_delta`.

    Args:
        db: AsyncSession used for query and model instances.
        team_id: target team identifier.
        treat: treat delta for each member.
        decoding, perception, logic, resilience, arcane, insight: stat deltas.
    """
    result = await db.execute(
        select(User)
        .join(TeamMember, TeamMember.user_id == User.id)
        .where(
            TeamMember.team_id == team_id,
            TeamMember.left_at.is_(None)
        )
    )
    members = result.scalars().all()

    for member in members:
        apply_user_reward_delta(
            member,
            treat=treat,
            decoding=decoding,
            perception=perception,
            logic=logic,
            resilience=resilience,
            arcane=arcane,
            insight=insight,
        )

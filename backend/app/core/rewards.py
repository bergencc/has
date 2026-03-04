from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.team import TeamMember


def clamp_stat(value: int) -> int:
    return max(0, min(100, value))


def get_total_attributes(user: User) -> int:
    return (
        user.decoding
        + user.perception
        + user.logic
        + user.resilience
        + user.arcane
        + user.insight
    )


def get_dog_tag_for_total(total_attributes: int) -> str:
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

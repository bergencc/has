from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.api.routes.challenges import settle_event_outcomes
from app.models.user import User
from app.models.team import Team, TeamMember
from app.models.event import Event, EventRegistration, EventLeaderboard
from app.models.challenge import Challenge, Attempt, HintUse
from app.schemas.event import (
    EventCreate, EventUpdate, EventResponse, EventListResponse,
    EventRegistrationResponse, EventLeaderboardResponse, LeaderboardEntryResponse
)
from app.schemas.team import TeamListResponse

router = APIRouter(prefix="/events", tags=["Events"])


def build_event_response(event: Event, teams_count: int = 0, challenges_count: int = 0) -> EventResponse:
    return EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        code=event.code,
        starts_at=event.starts_at,
        ends_at=event.ends_at,
        registration_opens_at=event.registration_opens_at,
        registration_closes_at=event.registration_closes_at,
        min_team_size=event.min_team_size,
        max_team_size=event.max_team_size,
        ranking_point=event.ranking_point,
        treat_point=event.treat_point,
        decoding_point=event.decoding_point,
        perception_point=event.perception_point,
        logic_point=event.logic_point,
        resilience_point=event.resilience_point,
        arcane_point=event.arcane_point,
        insight_point=event.insight_point,
        team_lock_mode=event.team_lock_mode,
        rules=event.rules,
        status=event.status,
        is_registration_open=event.is_registration_open,
        is_active=event.is_active,
        created_by=event.created_by,
        created_at=event.created_at,
        updated_at=event.updated_at,
        registered_teams_count=teams_count,
        challenges_count=challenges_count
    )


@router.get("", response_model=List[EventListResponse])
async def list_events(
        status_filter: str = None,
        include_past: bool = False,
        limit: int = 20,
        offset: int = 0,
        db: AsyncSession = Depends(get_db)
):
    """List events."""
    query = select(Event)

    if status_filter:
        query = query.where(Event.status == status_filter)

    if not include_past:
        query = query.where(Event.ends_at >= datetime.now(timezone.utc))

    query = query.order_by(Event.starts_at.asc()).limit(limit).offset(offset)

    result = await db.execute(query.options(selectinload(Event.registrations)))
    events = result.scalars().all()

    return [
        EventListResponse(
            id=e.id,
            title=e.title,
            code=e.code,
            status=e.status,
            starts_at=e.starts_at,
            ends_at=e.ends_at,
            is_registration_open=e.is_registration_open,
            is_active=e.is_active,
            registered_teams_count=len([r for r in e.registrations if r.status == "registered"])
        )

        for e in events
    ]


@router.get("/code/{code}", response_model=EventResponse)
async def get_event_by_code(
        code: str,
        db: AsyncSession = Depends(get_db)
):
    """Get event by code."""
    result = await db.execute(
        select(Event)
        .options(selectinload(Event.registrations), selectinload(Event.challenges))
        .where(Event.code == code)
    )

    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    teams_count = len([r for r in event.registrations if r.status == "registered"])
    challenges_count = len([c for c in event.challenges if c.is_active])

    return build_event_response(event, teams_count, challenges_count)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
        event_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Get event details."""
    result = await db.execute(
        select(Event)
        .options(selectinload(Event.registrations), selectinload(Event.challenges))
        .where(Event.id == event_id)
    )

    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    teams_count = len([r for r in event.registrations if r.status == "registered"])
    challenges_count = len([c for c in event.challenges if c.is_active])

    return build_event_response(event, teams_count, challenges_count)


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
        event_data: EventCreate,
        current_user: User = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    """Create a new event (admin only)."""
    # Check code uniqueness
    existing = await db.execute(select(Event).where(Event.code == event_data.code))

    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event code already exists"
        )

    event = Event(
        **event_data.model_dump(),
        created_by=current_user.id
    )

    db.add(event)

    await db.commit()
    await db.refresh(event)

    return build_event_response(event)


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
        event_id: int,
        event_data: EventUpdate,
        current_user: User = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    """Update an event (admin only)."""
    result = await db.execute(
        select(Event)
        .options(selectinload(Event.registrations), selectinload(Event.challenges))
        .where(Event.id == event_id)
    )

    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    update_data = event_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(event, key, value)

    await db.commit()
    await db.refresh(event)

    teams_count = len([r for r in event.registrations if r.status == "registered"])
    challenges_count = len([c for c in event.challenges if c.is_active])

    return build_event_response(event, teams_count, challenges_count)


@router.post("/{event_id}/register", response_model=EventRegistrationResponse)
async def register_for_event(
        event_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Register your team for an event."""
    # Get event
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )

    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    if not event.is_registration_open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration is not open for this event"
        )

    # Get user's team
    result = await db.execute(
        select(TeamMember)
        .options(selectinload(TeamMember.team).selectinload(Team.members))
        .where(
            TeamMember.user_id == current_user.id,
            TeamMember.left_at.is_(None)
        )
    )

    membership = result.scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must be on a team to register"
        )

    team = membership.team
    active_members = [m for m in team.members if m.left_at is None]

    # Check team size requirements
    if len(active_members) < event.min_team_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team needs at least {event.min_team_size} members"
        )

    if len(active_members) > event.max_team_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team exceeds maximum of {event.max_team_size} members"
        )

    # Check if already registered
    existing = await db.execute(
        select(EventRegistration).where(
            EventRegistration.event_id == event_id,
            EventRegistration.team_id == team.id,
            EventRegistration.status == "registered"
        )
    )

    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team is already registered for this event"
        )

    # Create registration
    registration = EventRegistration(
        event_id=event_id,
        team_id=team.id,
        registered_by=current_user.id
    )

    db.add(registration)

    # Create leaderboard entry
    leaderboard = EventLeaderboard(
        event_id=event_id,
        team_id=team.id
    )

    db.add(leaderboard)

    await db.commit()
    await db.refresh(registration)

    return EventRegistrationResponse(
        id=registration.id,
        event_id=event_id,
        team=TeamListResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            member_count=len(active_members),
            created_at=team.created_at
        ),
        registered_at=registration.registered_at,
        status=registration.status
    )


@router.get("/{event_id}/registrations", response_model=List[EventRegistrationResponse])
async def get_event_registrations(
        event_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Get all registrations for an event."""
    result = await db.execute(
        select(EventRegistration)
        .options(selectinload(EventRegistration.team).selectinload(Team.members))
        .where(
            EventRegistration.event_id == event_id,
            EventRegistration.status == "registered"
        )
    )

    registrations = result.scalars().all()

    return [
        EventRegistrationResponse(
            id=r.id,
            event_id=r.event_id,
            team=TeamListResponse(
                id=r.team.id,
                name=r.team.name,
                description=r.team.description,
                member_count=len([m for m in r.team.members if m.left_at is None]),
                created_at=r.team.created_at
            ),
            registered_at=r.registered_at,
            status=r.status
        )

        for r in registrations
    ]


@router.get("/{event_id}/leaderboard", response_model=EventLeaderboardResponse)
async def get_event_leaderboard(
        event_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Get event leaderboard."""
    # Get event
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    await settle_event_outcomes(db, event)

    # Get leaderboard entries
    result = await db.execute(
        select(EventLeaderboard)
        .options(selectinload(EventLeaderboard.team))
        .where(EventLeaderboard.event_id == event_id)
        .order_by(
            EventLeaderboard.total_points.desc(),
            EventLeaderboard.total_time_seconds.asc().nullsfirst(),
            EventLeaderboard.hints_used.asc(),
            EventLeaderboard.wrong_attempts.asc()
        )
    )

    entries = result.scalars().all()

    # Compute ranks
    ranked_entries = []

    for i, entry in enumerate(entries, 1):
        ranked_entries.append(LeaderboardEntryResponse(
            rank=i,
            team_id=entry.team_id,
            team_name=entry.team.name,
            total_points=entry.total_points,
            completed_challenges=entry.completed_challenges,
            total_time_seconds=entry.total_time_seconds,
            hints_used=entry.hints_used,
            wrong_attempts=entry.wrong_attempts
        ))

    return EventLeaderboardResponse(
        event_id=event_id,
        event_title=event.title,
        entries=ranked_entries,
        updated_at=datetime.now(timezone.utc)
    )


@router.post("/{event_id}/withdraw")
async def withdraw_from_event(
        event_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Withdraw your team from an event."""
    # Get user's team
    result = await db.execute(
        select(TeamMember)
        .where(
            TeamMember.user_id == current_user.id,
            TeamMember.left_at.is_(None)
        )
    )

    membership = result.scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not on a team"
        )

    # Get registration
    result = await db.execute(
        select(EventRegistration)
        .join(Event)
        .where(
            EventRegistration.event_id == event_id,
            EventRegistration.team_id == membership.team_id,
            EventRegistration.status == "registered"
        )
    )
    registration = result.scalar_one_or_none()

    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    # Check if event is active
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one()

    if event.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot withdraw from an active event"
        )

    registration.status = "withdrawn"

    await db.commit()

    return {"message": "Successfully withdrawn from event"}

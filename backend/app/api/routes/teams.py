from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone, timedelta
from typing import List

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.api.routes.challenges import settle_event_outcomes
from app.models.user import User
from app.models.team import Team, TeamMember, JoinRequest, JoinRequestVote
from app.models.event import EventRegistration, Event, EventLeaderboard
from app.models.challenge import HintUse
from app.schemas.team import (
    TeamCreate, TeamUpdate, TeamResponse, TeamListResponse,
    TeamMemberResponse, JoinRequestCreate, JoinRequestVoteCreate,
    JoinRequestResponse, JoinRequestVoteResponse, TeamMembershipStatus,
    TeamRankingResponse, UserTreatRankingResponse
)
from app.schemas.user import UserPublic

router = APIRouter(prefix="/teams", tags=["Teams"])


async def get_active_membership(db: AsyncSession, user_id: int) -> TeamMember | None:
    """Get user's active team membership."""
    result = await db.execute(
        select(TeamMember)
        .options(selectinload(TeamMember.team).selectinload(Team.members).selectinload(TeamMember.user))
        .where(
            TeamMember.user_id == user_id,
            TeamMember.left_at.is_(None)
        )
    )

    return result.scalar_one_or_none()


async def check_team_in_active_event(db: AsyncSession, team_id: int) -> bool:
    """Check if team is in an active event."""
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(EventRegistration)
        .join(Event)
        .where(
            EventRegistration.team_id == team_id,
            EventRegistration.status == "registered",
            Event.status == "active",
            Event.starts_at <= now,
            Event.ends_at >= now
        )
    )

    return result.scalar_one_or_none() is not None


def build_team_member_response(member: TeamMember) -> TeamMemberResponse:
    return TeamMemberResponse(
        id=member.id,
        user=UserPublic(id=member.user.id, dog_tag=member.user.dog_tag),
        role=member.role,
        joined_at=member.joined_at,
        lock_expires_at=member.lock_expires_at,
        is_locked=member.is_locked,
        can_leave=member.can_leave
    )


def build_team_response(team: Team) -> TeamResponse:
    active_members = [m for m in team.members if m.left_at is None]

    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        created_at=team.created_at,
        disbanded_at=team.disbanded_at,
        members=[build_team_member_response(m) for m in active_members],
        member_count=len(active_members)
    )


@router.get("/my-status", response_model=TeamMembershipStatus)
async def get_my_team_status(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get current user's team membership status."""
    membership = await get_active_membership(db, current_user.id)

    # Get pending join requests
    result = await db.execute(
        select(JoinRequest)
        .options(
            selectinload(JoinRequest.team),
            selectinload(JoinRequest.user),
            selectinload(JoinRequest.votes).selectinload(JoinRequestVote.voter)
        )
        .where(
            JoinRequest.user_id == current_user.id,
            JoinRequest.status == "pending"
        )
    )

    pending_requests = result.scalars().all()

    # Build pending request responses
    pending_responses = []

    for req in pending_requests:
        active_members = [m for m in req.team.members if m.left_at is None]
        pending_responses.append(JoinRequestResponse(
            id=req.id,
            team_id=req.team_id,
            team_name=req.team.name,
            user=UserPublic(id=req.user.id, dog_tag=req.user.dog_tag),
            requested_at=req.requested_at,
            expires_at=req.expires_at,
            status=req.status,
            resolved_at=req.resolved_at,
            votes=[JoinRequestVoteResponse(
                id=v.id,
                voter=UserPublic(id=v.voter.id, dog_tag=v.voter.dog_tag),
                vote=v.vote,
                voted_at=v.voted_at
            ) for v in req.votes],
            votes_needed=len(active_members),
            votes_received=len(req.votes)
        ))

    if membership:
        team_response = build_team_response(membership.team)
        member_response = build_team_member_response(membership)

        return TeamMembershipStatus(
            has_team=True,
            team=team_response,
            membership=member_response,
            pending_requests=pending_responses
        )

    return TeamMembershipStatus(
        has_team=False,
        team=None,
        membership=None,
        pending_requests=pending_responses
    )


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
        team_data: TeamCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Create a new team (user becomes sole member, locked for 60 days)."""
    # Check if user already has a team
    existing = await get_active_membership(db, current_user.id)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already on a team. Leave your current team first."
        )

    # Check team name uniqueness
    result = await db.execute(select(Team).where(Team.name == team_data.name))

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team name already taken"
        )

    # Create team
    team = Team(
        name=team_data.name,
        description=team_data.description
    )

    db.add(team)

    await db.flush()

    # Add creator as member
    membership = TeamMember(
        team_id=team.id,
        user_id=current_user.id,
        role="captain"
    )

    db.add(membership)

    await db.commit()

    # Reload with relationships
    result = await db.execute(
        select(Team)
        .options(selectinload(Team.members).selectinload(TeamMember.user))
        .where(Team.id == team.id)
    )

    team = result.scalar_one()

    return build_team_response(team)


@router.get("", response_model=List[TeamListResponse])
async def list_teams(
        search: str = None,
        limit: int = 20,
        offset: int = 0,
        db: AsyncSession = Depends(get_db)
):
    """List teams (for discovery)."""
    query = select(Team).where(Team.disbanded_at.is_(None))

    if search:
        query = query.where(Team.name.ilike(f"%{search}%"))

    query = query.order_by(Team.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(
        query.options(selectinload(Team.members))
    )

    teams = result.scalars().all()

    return [
        TeamListResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            member_count=len([m for m in t.members if m.left_at is None]),
            created_at=t.created_at
        )

        for t in teams
    ]


@router.get("/rankings", response_model=List[TeamRankingResponse])
async def get_team_rankings(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Global team rankings across all events."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Event).where(Event.ends_at < now)
    )
    ended_events = result.scalars().all()
    for event in ended_events:
        await settle_event_outcomes(db, event)

    member_subquery = (
        select(
            TeamMember.team_id.label("team_id"),
            func.count(TeamMember.id).label("member_count")
        )
        .where(TeamMember.left_at.is_(None))
        .group_by(TeamMember.team_id)
        .subquery()
    )

    registration_subquery = (
        select(
            EventRegistration.team_id.label("team_id"),
            func.count(EventRegistration.id).label("events_registered")
        )
        .where(EventRegistration.status == "registered")
        .group_by(EventRegistration.team_id)
        .subquery()
    )

    scores_subquery = (
        select(
            EventLeaderboard.team_id.label("team_id"),
            func.coalesce(func.sum(EventLeaderboard.total_points), 0).label("total_points"),
            func.coalesce(func.sum(EventLeaderboard.completed_challenges), 0).label("completed_challenges")
        )
        .group_by(EventLeaderboard.team_id)
        .subquery()
    )

    hints_subquery = (
        select(
            HintUse.team_id.label("team_id"),
            func.count(HintUse.id).label("hints_used")
        )
        .group_by(HintUse.team_id)
        .subquery()
    )

    query = (
        select(
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            func.coalesce(member_subquery.c.member_count, 0).label("member_count"),
            func.coalesce(registration_subquery.c.events_registered, 0).label("events_registered"),
            func.coalesce(scores_subquery.c.total_points, 0).label("total_points"),
            func.coalesce(scores_subquery.c.completed_challenges, 0).label("completed_challenges"),
            func.coalesce(hints_subquery.c.hints_used, 0).label("hints_used")
        )
        .where(Team.disbanded_at.is_(None))
        .outerjoin(member_subquery, member_subquery.c.team_id == Team.id)
        .outerjoin(registration_subquery, registration_subquery.c.team_id == Team.id)
        .outerjoin(scores_subquery, scores_subquery.c.team_id == Team.id)
        .outerjoin(hints_subquery, hints_subquery.c.team_id == Team.id)
        .order_by(
            func.coalesce(scores_subquery.c.total_points, 0).desc(),
            func.coalesce(scores_subquery.c.completed_challenges, 0).desc(),
            func.coalesce(hints_subquery.c.hints_used, 0).asc(),
            Team.name.asc()
        )
    )

    result = await db.execute(query)
    rows = result.all()

    rankings: List[TeamRankingResponse] = []

    for index, row in enumerate(rows, start=1):
        completed = row.completed_challenges or 0
        hints_used = row.hints_used or 0
        hint_usage_score = None

        if completed > 0:
            hint_usage_score = hints_used / completed

        rankings.append(TeamRankingResponse(
            rank=index,
            team_id=row.team_id,
            team_name=row.team_name,
            member_count=row.member_count or 0,
            events_registered=row.events_registered or 0,
            total_points=row.total_points or 0,
            completed_challenges=completed,
            hints_used=hints_used,
            hint_usage_score=hint_usage_score
        ))

    return rankings


@router.get("/rankings/users", response_model=List[UserTreatRankingResponse])
async def get_user_treat_rankings(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Global user rankings by treat."""
    query = (
        select(User)
        .where(User.is_active == True)
        .order_by(User.treat.desc(), User.created_at.asc())
    )

    result = await db.execute(query)
    users = result.scalars().all()

    rankings: List[UserTreatRankingResponse] = []
    for index, user in enumerate(users, start=1):
        total_attributes = (
            user.decoding
            + user.perception
            + user.logic
            + user.resilience
            + user.arcane
            + user.insight
        )
        rankings.append(UserTreatRankingResponse(
            rank=index,
            user_id=user.id,
            dog_tag=user.dog_tag,
            treat=user.treat,
            total_attributes=total_attributes
        ))

    return rankings


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
        team_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Get team details."""
    result = await db.execute(
        select(Team)
        .options(selectinload(Team.members).selectinload(TeamMember.user))
        .where(Team.id == team_id)
    )

    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    return build_team_response(team)


@router.post("/{team_id}/join-request", response_model=JoinRequestResponse, status_code=status.HTTP_201_CREATED)
async def request_to_join_team(
        team_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Request to join a team."""
    # Check if user already has a team
    existing = await get_active_membership(db, current_user.id)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already on a team. Leave your current team first."
        )

    # Get team
    result = await db.execute(
        select(Team)
        .options(selectinload(Team.members).selectinload(TeamMember.user))
        .where(Team.id == team_id, Team.disbanded_at.is_(None))
    )

    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    active_members = [m for m in team.members if m.left_at is None]

    # Check team size
    if len(active_members) >= settings.max_team_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team is full"
        )

    # Check for existing pending request
    existing_request = await db.execute(
        select(JoinRequest).where(
            JoinRequest.team_id == team_id,
            JoinRequest.user_id == current_user.id,
            JoinRequest.status == "pending"
        )
    )

    if existing_request.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending request to this team"
        )

    # Create join request
    join_request = JoinRequest(
        team_id=team_id,
        user_id=current_user.id
    )

    db.add(join_request)

    await db.commit()
    await db.refresh(join_request)

    return JoinRequestResponse(
        id=join_request.id,
        team_id=team_id,
        team_name=team.name,
        user=UserPublic(id=current_user.id, dog_tag=current_user.dog_tag),
        requested_at=join_request.requested_at,
        expires_at=join_request.expires_at,
        status=join_request.status,
        resolved_at=None,
        votes=[],
        votes_needed=len(active_members),
        votes_received=0
    )


@router.get("/{team_id}/join-requests", response_model=List[JoinRequestResponse])
async def get_team_join_requests(
        team_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get pending join requests for a team (team members only)."""
    # Verify user is on this team
    membership = await get_active_membership(db, current_user.id)

    if not membership or membership.team_id != team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a team member to view join requests"
        )

    result = await db.execute(
        select(JoinRequest)
        .options(
            selectinload(JoinRequest.team).selectinload(Team.members),
            selectinload(JoinRequest.user),
            selectinload(JoinRequest.votes).selectinload(JoinRequestVote.voter)
        )
        .where(
            JoinRequest.team_id == team_id,
            JoinRequest.status == "pending"
        )
        .order_by(JoinRequest.requested_at.desc())
    )

    requests = result.scalars().all()

    responses = []

    for req in requests:
        # Check if expired
        if req.is_expired:
            req.status = "expired"
            req.resolved_at = datetime.now(timezone.utc)
            continue

        active_members = [m for m in req.team.members if m.left_at is None]

        responses.append(JoinRequestResponse(
            id=req.id,
            team_id=req.team_id,
            team_name=req.team.name,
            user=UserPublic(id=req.user.id, dog_tag=req.user.dog_tag),
            requested_at=req.requested_at,
            expires_at=req.expires_at,
            status=req.status,
            resolved_at=req.resolved_at,
            votes=[JoinRequestVoteResponse(
                id=v.id,
                voter=UserPublic(id=v.voter.id, dog_tag=v.voter.dog_tag),
                vote=v.vote,
                voted_at=v.voted_at
            ) for v in req.votes],
            votes_needed=len(active_members),
            votes_received=len(req.votes)
        ))

    await db.commit()

    return responses


@router.post("/join-requests/{request_id}/vote", response_model=JoinRequestResponse)
async def vote_on_join_request(
        request_id: int,
        vote_data: JoinRequestVoteCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Vote on a join request (all team members must accept)."""
    # Get join request
    result = await db.execute(
        select(JoinRequest)
        .options(
            selectinload(JoinRequest.team).selectinload(Team.members).selectinload(TeamMember.user),
            selectinload(JoinRequest.user),
            selectinload(JoinRequest.votes).selectinload(JoinRequestVote.voter)
        )
        .where(JoinRequest.id == request_id)
    )

    join_request = result.scalar_one_or_none()

    if not join_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Join request not found"
        )

    if join_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This request is no longer pending"
        )

    if join_request.is_expired:
        join_request.status = "expired"
        join_request.resolved_at = datetime.now(timezone.utc)

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This request has expired"
        )

    # Verify voter is on the team
    active_members = [m for m in join_request.team.members if m.left_at is None]
    member_user_ids = [m.user_id for m in active_members]

    if current_user.id not in member_user_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a team member to vote"
        )

    # Check if already voted
    existing_vote = next((v for v in join_request.votes if v.voter_id == current_user.id), None)

    if existing_vote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already voted on this request"
        )

    # Create vote
    vote = JoinRequestVote(
        join_request_id=request_id,
        voter_id=current_user.id,
        vote=vote_data.vote
    )

    db.add(vote)

    await db.flush()

    # If rejected, immediately reject the request
    if vote_data.vote == "reject":
        join_request.status = "rejected"
        join_request.resolved_at = datetime.now(timezone.utc)
    else:
        # Check if all members have accepted
        all_votes = list(join_request.votes) + [vote]
        accept_votes = [v for v in all_votes if v.vote == "accept"]

        if len(accept_votes) >= len(active_members):
            # All accepted! Add the user to the team
            join_request.status = "accepted"
            join_request.resolved_at = datetime.now(timezone.utc)

            new_member = TeamMember(
                team_id=join_request.team_id,
                user_id=join_request.user_id,
                role="member"
            )

            db.add(new_member)

    await db.commit()

    # Reload for response
    result = await db.execute(
        select(JoinRequest)
        .options(
            selectinload(JoinRequest.team).selectinload(Team.members),
            selectinload(JoinRequest.user),
            selectinload(JoinRequest.votes).selectinload(JoinRequestVote.voter)
        )
        .where(JoinRequest.id == request_id)
    )

    join_request = result.scalar_one()
    active_members = [m for m in join_request.team.members if m.left_at is None]

    return JoinRequestResponse(
        id=join_request.id,
        team_id=join_request.team_id,
        team_name=join_request.team.name,
        user=UserPublic(id=join_request.user.id, dog_tag=join_request.user.dog_tag),
        requested_at=join_request.requested_at,
        expires_at=join_request.expires_at,
        status=join_request.status,
        resolved_at=join_request.resolved_at,
        votes=[JoinRequestVoteResponse(
            id=v.id,
            voter=UserPublic(id=v.voter.id, dog_tag=v.voter.dog_tag),
            vote=v.vote,
            voted_at=v.voted_at
        ) for v in join_request.votes],
        votes_needed=len(active_members),
        votes_received=len(join_request.votes)
    )


@router.post("/join-requests/{request_id}/cancel")
async def cancel_join_request(
        request_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Cancel your own join request."""
    result = await db.execute(
        select(JoinRequest).where(
            JoinRequest.id == request_id,
            JoinRequest.user_id == current_user.id,
            JoinRequest.status == "pending"
        )
    )

    join_request = result.scalar_one_or_none()

    if not join_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending join request not found"
        )

    join_request.status = "cancelled"
    join_request.resolved_at = datetime.now(timezone.utc)

    await db.commit()

    return {"message": "Join request cancelled"}


@router.post("/{team_id}/leave")
async def leave_team(
        team_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Leave your current team (only after 60-day lock expires and not in active event)."""
    membership = await get_active_membership(db, current_user.id)

    if not membership or membership.team_id != team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not on this team"
        )

    if membership.is_locked:
        days_left = (membership.lock_expires_at - datetime.now(timezone.utc)).days

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You cannot leave yet. Lock expires in {days_left} days."
        )

    # Check if team is in active event
    if await check_team_in_active_event(db, team_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot leave team while participating in an active event"
        )

    membership.left_at = datetime.now(timezone.utc)

    await db.commit()

    return {"message": "You have left the team"}

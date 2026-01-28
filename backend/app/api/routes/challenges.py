from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.models.user import User
from app.models.team import Team, TeamMember
from app.models.event import Event, EventRegistration, EventLeaderboard
from app.models.challenge import Challenge, Attempt, HintUse
from app.schemas.challenge import (
    ChallengeCreate, ChallengeUpdate, ChallengeResponse, ChallengeAdminResponse,
    ChallengeStatusResponse, AttemptCreate, AttemptResponse, HintRequest, HintResponse
)

router = APIRouter(prefix="/challenges", tags=["Challenges"])


async def get_user_team_for_event(db: AsyncSession, user_id: int, event_id: int) -> tuple[TeamMember, EventRegistration] | None:
    """Get user's team registration for an event."""
    result = await db.execute(
        select(TeamMember)
        .where(
            TeamMember.user_id == user_id,
            TeamMember.left_at.is_(None)
        )
    )

    membership = result.scalar_one_or_none()

    if not membership:
        return None

    result = await db.execute(
        select(EventRegistration)
        .where(
            EventRegistration.team_id == membership.team_id,
            EventRegistration.event_id == event_id,
            EventRegistration.status == "registered"
        )
    )

    registration = result.scalar_one_or_none()

    if not registration:
        return None

    return membership, registration


async def check_challenge_unlocked(db: AsyncSession, challenge: Challenge, team_id: int, event: Event) -> bool:
    """Check if a challenge is unlocked for a team."""
    if not challenge.unlock_rule:
        return True

    rule_type = challenge.unlock_rule.get("type")

    if rule_type == "after":
        required_challenge_id = challenge.unlock_rule.get("challenge_id")
        result = await db.execute(
            select(Attempt).where(
                Attempt.challenge_id == required_challenge_id,
                Attempt.team_id == team_id,
                Attempt.is_correct == True
            )
        )

        return result.scalar_one_or_none() is not None

    elif rule_type == "points":
        minimum = challenge.unlock_rule.get("minimum", 0)
        result = await db.execute(
            select(EventLeaderboard).where(
                EventLeaderboard.event_id == event.id,
                EventLeaderboard.team_id == team_id
            )
        )

        leaderboard = result.scalar_one_or_none()

        return leaderboard and leaderboard.total_points >= minimum

    return True


async def update_leaderboard(db: AsyncSession, event_id: int, team_id: int, event_start: datetime):
    """Update leaderboard for a team."""
    # Get all correct attempts for this team in this event
    result = await db.execute(
        select(Attempt)
        .join(Challenge)
        .where(
            Challenge.event_id == event_id,
            Attempt.team_id == team_id,
            Attempt.is_correct == True
        )
    )

    correct_attempts = result.scalars().all()

    # Get all attempts (for wrong count)
    result = await db.execute(
        select(Attempt)
        .join(Challenge)
        .where(
            Challenge.event_id == event_id,
            Attempt.team_id == team_id,
            Attempt.is_correct == False
        )
    )

    wrong_attempts = result.scalars().all()

    # Get hint uses
    result = await db.execute(
        select(HintUse)
        .join(Challenge)
        .where(
            Challenge.event_id == event_id,
            HintUse.team_id == team_id
        )
    )

    hints = result.scalars().all()

    # Calculate stats
    total_points = sum(a.points_awarded for a in correct_attempts)
    completed = len(correct_attempts)
    hints_used = len(hints)
    wrong_count = len(wrong_attempts)

    # Calculate time to last solve
    if correct_attempts:
        last_solve = max(a.submitted_at for a in correct_attempts)
        total_time = int((last_solve - event_start).total_seconds())
    else:
        total_time = None

    # Update leaderboard
    result = await db.execute(
        select(EventLeaderboard).where(
            EventLeaderboard.event_id == event_id,
            EventLeaderboard.team_id == team_id
        )
    )

    leaderboard = result.scalar_one_or_none()

    if leaderboard:
        leaderboard.total_points = total_points
        leaderboard.completed_challenges = completed
        leaderboard.total_time_seconds = total_time
        leaderboard.hints_used = hints_used
        leaderboard.wrong_attempts = wrong_count


# Admin routes
@router.post("", response_model=ChallengeAdminResponse, status_code=status.HTTP_201_CREATED)
async def create_challenge(
        challenge_data: ChallengeCreate,
        current_user: User = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    """Create a new challenge (admin only)."""
    # Verify event exists
    result = await db.execute(select(Event).where(Event.id == challenge_data.event_id))

    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    challenge = Challenge(**challenge_data.model_dump())
    db.add(challenge)

    await db.commit()
    await db.refresh(challenge)

    return ChallengeAdminResponse.model_validate(challenge)


@router.get("/admin/event/{event_id}", response_model=List[ChallengeAdminResponse])
async def list_challenges_admin(
        event_id: int,
        current_user: User = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    """List all challenges for an event with answers (admin only)."""
    result = await db.execute(
        select(Challenge)
        .where(Challenge.event_id == event_id)
        .order_by(Challenge.sort_order.asc())
    )

    challenges = result.scalars().all()

    return [ChallengeAdminResponse.model_validate(c) for c in challenges]


@router.patch("/{challenge_id}", response_model=ChallengeAdminResponse)
async def update_challenge(
        challenge_id: int,
        challenge_data: ChallengeUpdate,
        current_user: User = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    """Update a challenge (admin only)."""
    result = await db.execute(select(Challenge).where(Challenge.id == challenge_id))
    challenge = result.scalar_one_or_none()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    update_data = challenge_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(challenge, key, value)

    await db.commit()
    await db.refresh(challenge)

    return ChallengeAdminResponse.model_validate(challenge)


@router.delete("/{challenge_id}")
async def delete_challenge(
        challenge_id: int,
        current_user: User = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    """Delete a challenge (admin only)."""
    result = await db.execute(select(Challenge).where(Challenge.id == challenge_id))
    challenge = result.scalar_one_or_none()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    await db.delete(challenge)
    await db.commit()

    return {"message": "Challenge deleted"}


# Player routes
@router.get("/event/{event_id}", response_model=List[ChallengeStatusResponse])
async def list_challenges_for_event(
        event_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """List challenges for an event with team status."""
    # Get event
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    # Get user's registration
    team_data = await get_user_team_for_event(db, current_user.id, event_id)

    if not team_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your team is not registered for this event"
        )

    membership, registration = team_data
    team_id = membership.team_id

    # Get challenges
    result = await db.execute(
        select(Challenge)
        .where(Challenge.event_id == event_id, Challenge.is_active == True)
        .order_by(Challenge.sort_order.asc())
    )

    challenges = result.scalars().all()

    responses = []

    for challenge in challenges:
        # Check if unlocked
        is_unlocked = await check_challenge_unlocked(db, challenge, team_id, event)

        # Get attempts
        result = await db.execute(
            select(Attempt).where(
                Attempt.challenge_id == challenge.id,
                Attempt.team_id == team_id
            ).order_by(Attempt.submitted_at.desc())
        )

        attempts = result.scalars().all()

        # Check if solved
        correct_attempt = next((a for a in attempts if a.is_correct), None)
        is_solved = correct_attempt is not None

        # Get hints used
        result = await db.execute(
            select(HintUse).where(
                HintUse.challenge_id == challenge.id,
                HintUse.team_id == team_id
            ).order_by(HintUse.hint_index.asc())
        )

        hint_uses = result.scalars().all()
        hints_revealed = []

        if challenge.hints:
            for hu in hint_uses:
                if hu.hint_index < len(challenge.hints):
                    hints_revealed.append(challenge.hints[hu.hint_index])

        # Calculate points possible
        wrong_attempts = len([a for a in attempts if not a.is_correct])
        hint_penalty = sum(hu.penalty_applied for hu in hint_uses)
        attempt_penalty = wrong_attempts * challenge.point_decay_per_attempt
        points_possible = max(0, challenge.points - hint_penalty - attempt_penalty)

        responses.append(ChallengeStatusResponse(
            challenge=ChallengeResponse(
                id=challenge.id,
                event_id=challenge.event_id,
                type=challenge.type,
                title=challenge.title,
                prompt=challenge.prompt if is_unlocked else "🔒 Complete previous challenges to unlock",
                points=challenge.points,
                hint_cost=challenge.hint_cost,
                max_attempts=challenge.max_attempts,
                point_decay_per_attempt=challenge.point_decay_per_attempt,
                hints_available=len(challenge.hints) if challenge.hints else 0,
                sort_order=challenge.sort_order,
                is_active=challenge.is_active
            ),
            is_unlocked=is_unlocked,
            is_solved=is_solved,
            attempts_made=len(attempts),
            hints_used=len(hint_uses),
            hints_revealed=hints_revealed,
            points_possible=points_possible if not is_solved else (
                correct_attempt.points_awarded if correct_attempt else 0),
            solved_at=correct_attempt.submitted_at if correct_attempt else None,
            points_awarded=correct_attempt.points_awarded if correct_attempt else None
        ))

    return responses


@router.post("/submit", response_model=AttemptResponse)
async def submit_answer(
        attempt_data: AttemptCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Submit an answer for a challenge."""
    # Get challenge
    result = await db.execute(
        select(Challenge)
        .options(selectinload(Challenge.event))
        .where(Challenge.id == attempt_data.challenge_id)
    )

    challenge = result.scalar_one_or_none()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    event = challenge.event

    # Check event is active
    if not event.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is not currently active"
        )

    # Get team registration
    team_data = await get_user_team_for_event(db, current_user.id, event.id)

    if not team_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your team is not registered for this event"
        )

    membership, registration = team_data
    team_id = membership.team_id

    # Check if unlocked
    if not await check_challenge_unlocked(db, challenge, team_id, event):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This challenge is locked"
        )

    # Check if already solved
    result = await db.execute(
        select(Attempt).where(
            Attempt.challenge_id == challenge.id,
            Attempt.team_id == team_id,
            Attempt.is_correct == True
        )
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your team has already solved this challenge"
        )

    # Check attempt limit
    result = await db.execute(
        select(Attempt).where(
            Attempt.challenge_id == challenge.id,
            Attempt.team_id == team_id
        )
    )

    previous_attempts = result.scalars().all()

    if challenge.max_attempts and len(previous_attempts) >= challenge.max_attempts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum attempts reached for this challenge"
        )

    # Normalize and check answer
    normalized = Challenge.normalize_answer(attempt_data.answer)
    is_correct = challenge.check_answer(attempt_data.answer)

    # Calculate points
    points_awarded = 0

    if is_correct:
        # Get hint penalty
        result = await db.execute(
            select(HintUse).where(
                HintUse.challenge_id == challenge.id,
                HintUse.team_id == team_id
            )
        )

        hint_uses = result.scalars().all()
        hint_penalty = sum(hu.penalty_applied for hu in hint_uses)

        # Get attempt penalty
        wrong_attempts = len([a for a in previous_attempts if not a.is_correct])
        attempt_penalty = wrong_attempts * challenge.point_decay_per_attempt

        points_awarded = max(0, challenge.points - hint_penalty - attempt_penalty)

    # Create attempt
    attempt = Attempt(
        challenge_id=challenge.id,
        team_id=team_id,
        user_id=current_user.id,
        submitted_answer=attempt_data.answer,
        normalized_answer=normalized,
        is_correct=is_correct,
        points_awarded=points_awarded
    )

    db.add(attempt)

    # Update leaderboard if correct
    if is_correct:
        await update_leaderboard(db, event.id, team_id, event.starts_at)

    await db.commit()
    await db.refresh(attempt)

    # Calculate remaining attempts
    attempts_remaining = None
    if challenge.max_attempts:
        attempts_remaining = challenge.max_attempts - len(previous_attempts) - 1

    # Build message
    if is_correct:
        message = f"Correct! You earned {points_awarded} points."
    else:
        message = "Incorrect. Try again!"
        if attempts_remaining is not None and attempts_remaining > 0:
            message += f" ({attempts_remaining} attempts remaining)"
        elif attempts_remaining == 0:
            message += " (No more attempts remaining)"

    return AttemptResponse(
        id=attempt.id,
        challenge_id=attempt.challenge_id,
        is_correct=attempt.is_correct,
        points_awarded=attempt.points_awarded,
        submitted_at=attempt.submitted_at,
        message=message,
        attempts_remaining=attempts_remaining
    )


@router.post("/hint", response_model=HintResponse)
async def request_hint(
        hint_data: HintRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Request a hint for a challenge."""
    # Get challenge
    result = await db.execute(
        select(Challenge)
        .options(selectinload(Challenge.event))
        .where(Challenge.id == hint_data.challenge_id)
    )

    challenge = result.scalar_one_or_none()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    event = challenge.event

    # Check event is active
    if not event.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is not currently active"
        )

    if not challenge.hints or len(challenge.hints) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hints available for this challenge"
        )

    # Get team registration
    team_data = await get_user_team_for_event(db, current_user.id, event.id)

    if not team_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your team is not registered for this event"
        )

    membership, registration = team_data
    team_id = membership.team_id

    # Check if unlocked
    if not await check_challenge_unlocked(db, challenge, team_id, event):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This challenge is locked"
        )

    # Check if already solved
    result = await db.execute(
        select(Attempt).where(
            Attempt.challenge_id == challenge.id,
            Attempt.team_id == team_id,
            Attempt.is_correct == True
        )
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your team has already solved this challenge"
        )

    # Get previous hints
    result = await db.execute(
        select(HintUse).where(
            HintUse.challenge_id == challenge.id,
            HintUse.team_id == team_id
        ).order_by(HintUse.hint_index.asc())
    )
    previous_hints = result.scalars().all()

    next_hint_index = len(previous_hints)

    if next_hint_index >= len(challenge.hints):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All hints have been used"
        )

    # Create hint use
    hint_use = HintUse(
        challenge_id=challenge.id,
        team_id=team_id,
        user_id=current_user.id,
        hint_index=next_hint_index,
        penalty_applied=challenge.hint_cost
    )

    db.add(hint_use)
    await db.commit()

    return HintResponse(
        hint_index=next_hint_index,
        hint_text=challenge.hints[next_hint_index],
        penalty_applied=challenge.hint_cost,
        hints_remaining=len(challenge.hints) - next_hint_index - 1
    )

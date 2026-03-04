from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from authlib.integrations.starlette_client import OAuth
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.models.user import User
from app.schemas.user import TokenResponse, UserResponse, UserUpdate

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth setup
oauth = OAuth()
if settings.google_client_id and settings.google_client_secret:
    oauth.register(
        name='google',
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
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


def get_total_attributes(user: User) -> int:
    return (
        user.decoding
        + user.perception
        + user.logic
        + user.resilience
        + user.arcane
        + user.insight
    )


def sync_dog_tag(user: User) -> None:
    user.dog_tag = get_dog_tag_for_total(get_total_attributes(user))


def extract_institution(email: str) -> str | None:
    """Extract institution from email domain."""
    domain = email.split('@')[1] if '@' in email else None

    if domain and domain.endswith('.edu'):
        return domain

    return domain


@router.get("/google")
async def google_auth(request: Request):
    """Start Google OAuth flow."""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )

    redirect_uri = settings.google_redirect_uri
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback."""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )

    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {str(e)}"
        )

    user_info = token.get('userinfo')

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not get user info from Google"
        )

    email = user_info.get('email')
    google_id = user_info.get('sub')

    if not email or not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and Google ID required"
        )

    # Find or create user
    result = await db.execute(
        select(User).where((User.google_id == google_id) | (User.email == email))
    )

    user = result.scalar_one_or_none()

    if user:
        # Update Google ID if not set
        if not user.google_id:
            user.google_id = google_id

        if not user.email_verified_at:
            user.email_verified_at = datetime.now(timezone.utc)
        sync_dog_tag(user)
    else:
        # Create new user with baseline stats
        user = User(
            email=email,
            dog_tag="witness",
            decoding=0,
            perception=0,
            logic=0,
            resilience=0,
            arcane=0,
            insight=0,
            treat=0,
            google_id=google_id,
            institution=extract_institution(email),
            email_verified_at=datetime.now(timezone.utc),
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)

    # Create JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Redirect to frontend with token
    frontend_url = f"{settings.frontend_url}/auth/callback?token={access_token}"

    return RedirectResponse(url=frontend_url)


@router.post("/dev-login", response_model=TokenResponse)
async def dev_login(
        email: str,
        db: AsyncSession = Depends(get_db)
):
    """Development-only login endpoint."""
    if not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dev login only available in debug mode"
        )

    # Find or create user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            dog_tag="witness",
            decoding=0,
            perception=0,
            logic=0,
            resilience=0,
            arcane=0,
            insight=0,
            treat=0,
            institution=extract_institution(email),
            email_verified_at=datetime.now(timezone.utc),
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
        update: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Update current user profile."""
    update_data = update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(current_user, key, value)

    sync_dog_tag(current_user)

    await db.commit()
    await db.refresh(current_user)

    return UserResponse.model_validate(current_user)

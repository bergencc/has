from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from authlib.integrations.starlette_client import OAuth
from datetime import datetime, timezone
import secrets

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.models.user import User
from app.schemas.user import TokenResponse, UserResponse, GoogleAuthUrl, UserUpdate

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


def generate_nickname(email: str) -> str:
    """Generate a unique nickname from email."""
    base = email.split('@')[0]

    # Clean up the base
    base = ''.join(c for c in base if c.isalnum())[:15]

    # Add random suffix
    suffix = secrets.token_hex(3)

    return f"{base}_{suffix}"


def extract_institution(email: str) -> str | None:
    """Extract institution from email domain."""
    domain = email.split('@')[1] if '@' in email else None

    if domain and domain.endswith('.edu'):
        return domain

    return domain


@router.get("/google", response_model=GoogleAuthUrl)
async def google_auth_url(request: Request):
    """Get Google OAuth URL."""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )

    redirect_uri = settings.google_redirect_uri
    url = await oauth.google.create_authorization_url(redirect_uri)

    # Store state in session
    request.session['oauth_state'] = url['state']

    return GoogleAuthUrl(auth_url=url['url'])


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
    else:
        # Create new user
        nickname = generate_nickname(email)

        # Ensure nickname is unique
        while True:
            existing = await db.execute(select(User).where(User.nickname == nickname))

            if not existing.scalar_one_or_none():
                break

            nickname = generate_nickname(email)

        user = User(
            email=email,
            nickname=nickname,
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
        nickname: str,
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
        # Check nickname uniqueness
        nick_check = await db.execute(select(User).where(User.nickname == nickname))

        if nick_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nickname already taken"
            )

        user = User(
            email=email,
            nickname=nickname,
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
    if update.nickname:
        # Check nickname uniqueness
        result = await db.execute(
            select(User).where(
                User.nickname == update.nickname,
                User.id != current_user.id
            )
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nickname already taken"
            )

        current_user.nickname = update.nickname

    await db.commit()
    await db.refresh(current_user)

    return UserResponse.model_validate(current_user)

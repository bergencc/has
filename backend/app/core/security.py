"""
Authentication utilities for JWT token management and user verification.

Provides password hashing, token creation/verification, and FastAPI
dependency functions for protecting routes.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

# Handles password hashing and verification using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Extracts the Bearer token from the Authorization header
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token.

    Args:
        data: Claims to encode in the token (should include "sub" for user ID).
        expires_delta: How long until the token expires. Defaults to the
                       value set in settings (jwt_expiration_hours).

    Returns:
        A signed JWT string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiration_hours)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.

    Args:
        token: The raw JWT string.

    Returns:
        The decoded payload as a dict, or None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    FastAPI dependency that returns the authenticated user for a request.

    Extracts the Bearer token from the Authorization header, validates it,
    and looks up the corresponding user in the database.

    Args:
        credentials: Bearer token injected by FastAPI from the request header.
        db: Database session injected by FastAPI.

    Returns:
        The authenticated User object.

    Raises:
        HTTPException 401: If the token is missing, invalid, expired, or the
                           user no longer exists in the database.
    """
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await db.execute(select(User).where(User.id == user_id_int))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    FastAPI dependency that requires the current user to be an admin.

    Builds on get_current_user — the request must pass authentication first,
    then this checks the user's role.

    Args:
        current_user: Authenticated user injected by get_current_user.

    Returns:
        The authenticated User object, guaranteed to have role == "admin".

    Raises:
        HTTPException 403: If the user is authenticated but not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
):
    """
    FastAPI dependency that returns the current user if authenticated, or None.

    Use this on routes that behave differently for logged-in vs. anonymous
    users, but don't require authentication.

    Args:
        credentials: Bearer token from the Authorization header, or None if
                     the header is absent (auto_error=False prevents a 403).

    Returns:
        An inner async dependency function that resolves to the User or None.
    """
    async def _get_optional_user(db: AsyncSession = Depends(get_db)) -> Optional[User]:
        if credentials is None:
            return None
        try:
            return await get_current_user(credentials, db)
        except HTTPException:
            return None
    return _get_optional_user

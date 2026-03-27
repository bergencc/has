"""
Database configuration and session management.

This module initializes the SQLAlchemy async engine and session factory,
and provides a dependency for FastAPI to manage database sessions.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


"""
Initialize the async engine using the database URL from settings.
echo=True will log all SQL queries which is useful for debugging
"""
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)


"""
Factory for creating new AsyncSession instances
"""
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """
    Base class for all declarative SQLAlchemy models.
    """
    pass


async def get_db() -> AsyncSession:
    """
    FastAPI dependency that provides an asynchronous database session.

    This generator ensures that:
    1. A new session is created for each request.
    2. The transaction is committed if the request is successful.
    3. The transaction is rolled back if an exception occurs.
    4. The session is always closed after the request.

    Yields:
        AsyncSession: The active database session.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
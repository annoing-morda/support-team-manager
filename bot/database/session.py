"""Database session management."""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot.config import settings

# AICODE-NOTE: Engine is created lazily to allow for testing with different URLs
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get or create the async engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url_str,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True,  # Verify connections before using
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    """
    Dependency for getting async database session.
    
    Usage:
        async with get_session() as session:
            # Use session here
            pass
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def close_engine() -> None:
    """Close the database engine (call on shutdown)."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None

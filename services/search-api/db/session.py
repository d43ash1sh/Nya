"""
Database session and connection engine for ঞ (Nya) Search.
Supports both SQLite (for zero-dependency local Windows dev & testing)
and PostgreSQL (for production container deployments).
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import settings
from db.models import Base

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining database session."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

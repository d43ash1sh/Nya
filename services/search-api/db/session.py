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
    """Initialize database tables and ensure column schema compatibility."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        def migrate_sqlite_columns(sync_conn):
            from sqlalchemy import inspect, text
            inspector = inspect(sync_conn)
            if "indexed_documents" in inspector.get_table_names():
                cols = {c["name"] for c in inspector.get_columns("indexed_documents")}
                if "published_at" not in cols:
                    sync_conn.execute(text("ALTER TABLE indexed_documents ADD COLUMN published_at DATETIME"))
                if "updated_at" not in cols:
                    sync_conn.execute(text("ALTER TABLE indexed_documents ADD COLUMN updated_at DATETIME"))
                if "crawled_at" not in cols:
                    sync_conn.execute(text("ALTER TABLE indexed_documents ADD COLUMN crawled_at DATETIME"))
                if "is_news" not in cols:
                    sync_conn.execute(text("ALTER TABLE indexed_documents ADD COLUMN is_news BOOLEAN DEFAULT 0"))
                # Backfill published_at from published_date where available
                sync_conn.execute(text("UPDATE indexed_documents SET published_at = published_date WHERE published_at IS NULL AND published_date IS NOT NULL"))

        await conn.run_sync(migrate_sqlite_columns)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining database session."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

""" With help from Pilot, Claude and
    ChatGPT, this file handles the database connection 
    and session management for the FastAPI application. 
    It uses SQLAlchemy's async capabilities to create an 
    asynchronous engine and session maker. 
    The `get_db` function is a FastAPI dependency that yields a 
    database session for each request, ensuring proper commit, 
    rollback, and cleanup of the session.
    Meant to be DB agnostic, but currently configured for None, SQLLite or 
    PostgreSQL with asyncpg.
    The database URL is loaded from environment variables or a .env file.
     """

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# Pilot came up with the idea of using a static pool for SQLite to avoid 
# issues with multiple threads.

# Pilot came up with this test for using SQLite in-memory database for testing.
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
engine_kwargs = {"echo": False}
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine_kwargs["poolclass"] = StaticPool
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields a DB session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

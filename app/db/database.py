""" With help from Claude and
    ChatGPT, this file handles the database connection 
    and session management for the FastAPI application. 
    It uses SQLAlchemy's async capabilities to create an 
    asynchronous engine and session maker. 
    The `get_db` function is a FastAPI dependency that yields a 
    database session for each request, ensuring proper commit, 
    rollback, and cleanup of the session.
     """

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
)

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

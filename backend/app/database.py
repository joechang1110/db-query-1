"""SQLite database setup and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from app.config import settings

# Import all models to register them with SQLModel
from app.models.database import DatabaseConnection
from app.models.metadata import DatabaseMetadata
from app.models.query import QueryHistory

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
)


# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get database session dependency for FastAPI."""
    async with async_session_maker() as session:
        yield session


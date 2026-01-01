"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from app.database import get_session
from app.models.database import DatabaseConnection
from app.models.metadata import DatabaseMetadata
from app.models.query import QueryHistory


@pytest.fixture
async def test_db_url() -> str:
    """Get test database URL."""
    return "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_engine(test_db_url: str):
    """Create test database engine."""
    engine = create_async_engine(test_db_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Create test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_maker() as session:
        yield session


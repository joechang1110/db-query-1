"""Database connection management service."""

from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import text
from typing import Any
from app.models.database import DatabaseType
from app.config import settings


class ConnectionError(Exception):
    """Database connection error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """Initialize connection error."""
        super().__init__(message)
        self.message = message
        self.details = details or {}


def parse_database_url(url: str) -> tuple[DatabaseType, str]:
    """Parse database URL and infer database type.
    
    Args:
        url: Database connection URL
        
    Returns:
        Tuple of (database_type, normalized_url)
        
    Raises:
        ConnectionError: If URL format is invalid
    """
    try:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        
        if scheme == "postgresql" or scheme == "postgres":
            return (DatabaseType.POSTGRESQL, url)
        elif scheme == "mysql":
            return (DatabaseType.MYSQL, url)
        elif scheme == "sqlite":
            # SQLite URLs: sqlite:///path/to/db or sqlite+aiosqlite:///path/to/db
            return (DatabaseType.SQLITE, url)
        else:
            raise ConnectionError(
                f"Unsupported database type: {scheme}",
                {"scheme": scheme, "supported": ["postgresql", "mysql", "sqlite"]}
            )
    except Exception as e:
        raise ConnectionError(
            f"Invalid database URL format: {str(e)}",
            {"error": str(e)}
        )


async def test_connection(url: str, database_type: DatabaseType) -> None:
    """Test database connection.
    
    Args:
        url: Database connection URL
        database_type: Database type
        
    Raises:
        ConnectionError: If connection fails
    """
    import traceback
    
    try:
        # Convert URL to async format before testing
        test_url = url
        if database_type == DatabaseType.POSTGRESQL:
            if not test_url.startswith("postgresql+asyncpg://"):
                test_url = test_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif database_type == DatabaseType.MYSQL:
            if not test_url.startswith("mysql+aiomysql://"):
                test_url = test_url.replace("mysql://", "mysql+aiomysql://", 1)
        elif database_type == DatabaseType.SQLITE:
            if not test_url.startswith("sqlite+aiosqlite://"):
                test_url = test_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        
        # Create engine with short timeout
        connect_args = {}
        if database_type == DatabaseType.SQLITE:
            connect_args["timeout"] = 10
        elif database_type == DatabaseType.MYSQL:
            # MySQL connection arguments
            connect_args["connect_timeout"] = 10
        
        engine = create_async_engine(
            test_url,
            pool_pre_ping=True,
            connect_args=connect_args,
            echo=False,  # Set to True for SQL query logging
        )
        
        async with engine.connect() as conn:
            # Test connection with a simple query
            await conn.execute(text("SELECT 1"))
        
        await engine.dispose()
    except Exception as e:
        error_details = {
            "error": str(e),
            "error_type": type(e).__name__,
            "url": url,
            "database_type": database_type.value,
        }
        
        # Add traceback in debug mode
        if settings.debug:
            error_details["traceback"] = traceback.format_exc().split("\n")
        
        raise ConnectionError(
            f"Failed to connect to database: {str(e)}",
            error_details
        )


def create_engine_for_database(url: str, database_type: DatabaseType) -> AsyncEngine:
    """Create SQLAlchemy engine for database.
    
    Args:
        url: Database connection URL
        database_type: Database type
        
    Returns:
        AsyncEngine instance
    """
    # Ensure async driver is used
    if database_type == DatabaseType.POSTGRESQL:
        if not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif database_type == DatabaseType.MYSQL:
        if not url.startswith("mysql+aiomysql://"):
            url = url.replace("mysql://", "mysql+aiomysql://", 1)
    elif database_type == DatabaseType.SQLITE:
        if not url.startswith("sqlite+aiosqlite://"):
            url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    
    return create_async_engine(
        url,
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=10,
    )


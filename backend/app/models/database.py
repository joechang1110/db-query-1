"""Database connection model."""

from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum


class DatabaseType(str, Enum):
    """Database type enumeration."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class ConnectionStatus(str, Enum):
    """Connection status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class DatabaseConnection(SQLModel, table=True):
    """Database connection entity."""

    __tablename__ = "database_connections"

    name: str = Field(primary_key=True, max_length=50)
    url: str = Field(index=True, max_length=500)
    database_type: DatabaseType = Field(default=DatabaseType.POSTGRESQL)
    description: str | None = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_connected_at: datetime | None = None
    status: ConnectionStatus = Field(default=ConnectionStatus.ACTIVE)


"""Query history model."""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text
from datetime import datetime
from enum import Enum


class QuerySource(str, Enum):
    """Query source enumeration."""

    MANUAL = "manual"
    NATURAL_LANGUAGE = "natural_language"


class QueryHistory(SQLModel, table=True):
    """Query history entity."""

    __tablename__ = "query_history"

    id: int | None = Field(default=None, primary_key=True)
    database_name: str = Field(foreign_key="database_connections.name", max_length=50)
    sql_text: str = Field(sa_column=Column(Text))
    executed_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    execution_time_ms: int | None = None
    row_count: int | None = None
    success: bool
    error_message: str | None = Field(default=None, sa_column=Column(Text))
    query_source: QuerySource = Field(default=QuerySource.MANUAL)


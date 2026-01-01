"""API request/response schemas."""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Literal, Any
from app.models.database import DatabaseType, ConnectionStatus
from app.models.query import QuerySource


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return components[0] + "".join(x.capitalize() for x in components[1:])


# Configure global Pydantic settings for camelCase
class BaseSchema(BaseModel):
    """Base schema with camelCase alias generator."""
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


# Database Connection Schemas
class DatabaseConnectionInput(BaseSchema):
    """Input schema for creating/updating database connection."""

    url: str = Field(max_length=500)
    description: str | None = Field(default=None, max_length=200)


class DatabaseConnectionResponse(BaseSchema):
    """Response schema for database connection."""

    name: str
    url: str
    database_type: DatabaseType
    description: str | None
    created_at: datetime
    updated_at: datetime
    last_connected_at: datetime | None
    status: ConnectionStatus


# Metadata Schemas
class ColumnMetadata(BaseSchema):
    """Column metadata schema."""

    name: str = Field(max_length=63)
    data_type: str
    nullable: bool
    primary_key: bool
    unique: bool = False
    default_value: str | None = None
    comment: str | None = None


class TableMetadata(BaseSchema):
    """Table metadata schema."""

    name: str = Field(max_length=63)
    type: Literal["table", "view"]
    schema_name: str = Field(default="public")
    columns: list[ColumnMetadata]
    row_count: int | None = None


class DatabaseMetadataResponse(BaseSchema):
    """Response schema for database metadata."""

    database_name: str
    database_type: DatabaseType
    tables: list[TableMetadata]
    views: list[TableMetadata]
    fetched_at: datetime
    is_stale: bool


# Query Schemas
class QueryInput(BaseSchema):
    """Input schema for query execution."""

    sql: str


class QueryColumn(BaseSchema):
    """Query result column schema."""

    name: str
    data_type: str


class QueryResult(BaseSchema):
    """Query result schema."""

    columns: list[QueryColumn]
    rows: list[dict[str, Any]]
    row_count: int
    execution_time_ms: int
    sql: str


class QueryHistoryEntry(BaseSchema):
    """Query history entry schema."""

    id: int
    database_name: str
    sql_text: str
    executed_at: datetime
    execution_time_ms: int | None
    row_count: int | None
    success: bool
    error_message: str | None
    query_source: QuerySource


# Error Schema
class ErrorDetail(BaseSchema):
    """Error detail schema."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseSchema):
    """Error response schema."""

    error: ErrorDetail


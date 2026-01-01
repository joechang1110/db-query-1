"""Query execution API endpoints."""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pydantic import BaseModel

from app.models.schemas import QueryInput, QueryResult, QueryHistoryEntry, ErrorResponse
from app.models.database import DatabaseConnection
from app.models.query import QuerySource
from app.services.query import (
    execute_query,
    get_query_history,
    QueryExecutionError
)
from app.services.sql_validator import SQLValidationError
from app.services.nl2sql import generate_sql_from_natural_language, NL2SQLError
from app.services.metadata import get_database_metadata
from app.services.export import export_service, ExportFormat
from app.database import get_session

router = APIRouter()


@router.post(
    "/dbs/{name}/query",
    response_model=QueryResult,
    responses={
        400: {"model": ErrorResponse, "description": "SQL validation error"},
        404: {"model": ErrorResponse, "description": "Database not found"},
        500: {"model": ErrorResponse, "description": "Query execution error"}
    },
    summary="Execute SQL query",
    description="Execute a SELECT query against the specified database. "
                "Query will be validated and LIMIT 1000 will be added if missing."
)
async def execute_sql_query(name: str, query_input: QueryInput, session: AsyncSession = Depends(get_session)):
    """Execute SQL query against target database.

    Args:
        name: Database connection name
        query_input: Query input with SQL text
        session: Database session

    Returns:
        Query result with columns and rows

    Raises:
        HTTPException: If database not found or query execution fails
    """
    # Get database connection
    statement = select(DatabaseConnection).where(DatabaseConnection.name == name)
    result = await session.execute(statement)
    db_connection = result.scalar_one_or_none()

    if not db_connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DATABASE_NOT_FOUND",
                    "message": f"Database '{name}' not found",
                    "details": {"databaseName": name}
                }
            }
        )

    # Execute query
    try:
        result = await execute_query(
            db_connection=db_connection,
            sql=query_input.sql,
            query_source=QuerySource.MANUAL
        )

        return QueryResult(**result)

    except SQLValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": e.message,
                    "details": e.details
                }
            }
        )

    except QueryExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "EXECUTION_ERROR",
                    "message": e.message,
                    "details": e.details
                }
            }
        )


@router.get(
    "/dbs/{name}/history",
    response_model=list[QueryHistoryEntry],
    responses={
        404: {"model": ErrorResponse, "description": "Database not found"}
    },
    summary="Get query history",
    description="Get the query execution history for the specified database. "
                "Returns the last 50 queries in reverse chronological order."
)
async def get_database_query_history(name: str, limit: int = 50, session: AsyncSession = Depends(get_session)):
    """Get query history for a database.

    Args:
        name: Database connection name
        limit: Maximum number of history entries to return (default 50)
        session: Database session

    Returns:
        List of query history entries

    Raises:
        HTTPException: If database not found
    """
    # Verify database exists
    statement = select(DatabaseConnection).where(DatabaseConnection.name == name)
    result = await session.execute(statement)
    db_connection = result.scalar_one_or_none()

    if not db_connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DATABASE_NOT_FOUND",
                    "message": f"Database '{name}' not found",
                    "details": {"databaseName": name}
                }
            }
        )

    # Get history
    history = await get_query_history(name, limit=limit)

    return [QueryHistoryEntry(**entry) for entry in history]


# Schemas for natural language endpoint
class NaturalLanguageInput(BaseModel):
    """Input schema for natural language query."""
    prompt: str


class NaturalLanguageResult(BaseModel):
    """Result schema for natural language query."""
    sql: str
    explanation: str


@router.post(
    "/dbs/{name}/query/natural",
    response_model=NaturalLanguageResult,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input or generated SQL"},
        404: {"model": ErrorResponse, "description": "Database not found"},
        500: {"model": ErrorResponse, "description": "Natural language processing error"}
    },
    summary="Generate SQL from natural language",
    description="Generate a SQL query from natural language input using AI. "
                "The generated SQL will be validated and can be executed directly."
)
async def generate_sql_from_natural_language_endpoint(name: str, nl_input: NaturalLanguageInput, session: AsyncSession = Depends(get_session)):
    """Generate SQL query from natural language input.

    Args:
        name: Database connection name
        nl_input: Natural language input with prompt
        session: Database session

    Returns:
        Generated SQL and explanation

    Raises:
        HTTPException: If database not found or generation fails
    """
    # Get database connection
    statement = select(DatabaseConnection).where(DatabaseConnection.name == name)
    result = await session.execute(statement)
    db_connection = result.scalar_one_or_none()

    if not db_connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DATABASE_NOT_FOUND",
                    "message": f"Database '{name}' not found",
                    "details": {"databaseName": name}
                }
            }
        )

    # Get database metadata
    try:
        metadata = await get_database_metadata(db_connection)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "METADATA_ERROR",
                    "message": f"Failed to fetch database metadata: {str(e)}",
                    "details": {"error": str(e)}
                }
            }
        )

    # Generate SQL from natural language
    try:
        result = await generate_sql_from_natural_language(
            db_connection=db_connection,
            prompt=nl_input.prompt,
            metadata_json=metadata,
        )

        return NaturalLanguageResult(**result)

    except SQLValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "GENERATED_SQL_INVALID",
                    "message": f"Generated SQL failed validation: {e.message}",
                    "details": e.details
                }
            }
        )

    except NL2SQLError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "NL2SQL_ERROR",
                    "message": e.message,
                    "details": e.details
                }
            }
        )


# Schemas for export endpoint
class ExportInput(BaseModel):
    """Input schema for data export."""
    columns: list[dict]
    rows: list[dict]
    format: ExportFormat
    filename: str | None = None


class ExportResult(BaseModel):
    """Result schema for data export."""
    data: str
    format: str
    filename: str


@router.post(
    "/dbs/{name}/export",
    response_model=ExportResult,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid export format"},
        500: {"model": ErrorResponse, "description": "Export processing error"}
    },
    summary="Export query results",
    description="Export query results to CSV or JSON format. "
                "Returns the exported data as a string that can be downloaded."
)
async def export_query_results(name: str, export_input: ExportInput):
    """Export query results to specified format.

    Args:
        name: Database connection name (for context)
        export_input: Export input with columns, rows, and format

    Returns:
        Exported data and metadata

    Raises:
        HTTPException: If export fails
    """
    try:
        # Generate filename if not provided
        if not export_input.filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_input.filename = f"query_result_{timestamp}.{export_input.format.value}"

        # Export data
        exported_data = export_service.export_data(
            columns=export_input.columns,
            rows=export_input.rows,
            format=export_input.format
        )

        return ExportResult(
            data=exported_data,
            format=export_input.format,
            filename=export_input.filename
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_FORMAT",
                    "message": str(e),
                    "details": {"format": export_input.format}
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "EXPORT_ERROR",
                    "message": f"Failed to export data: {str(e)}",
                    "details": {"error": str(e)}
                }
            }
        )

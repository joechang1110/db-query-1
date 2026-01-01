"""Query execution service."""

import time
from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from datetime import datetime

from app.services.sql_validator import validate_and_transform_sql, SQLValidationError
from app.services.db_connection import create_engine_for_database, ConnectionError
from app.models.database import DatabaseConnection, DatabaseType
from app.models.query import QueryHistory, QuerySource
from app.database import async_session_maker


class QueryExecutionError(Exception):
    """Query execution error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """Initialize query execution error."""
        super().__init__(message)
        self.message = message
        self.details = details or {}


async def execute_query(
    db_connection: DatabaseConnection,
    sql: str,
    query_source: QuerySource = QuerySource.MANUAL,
    timeout: int = 30
) -> dict[str, Any]:
    """Execute SQL query against target database.

    Args:
        db_connection: Database connection object
        sql: SQL query to execute
        query_source: Source of the query (manual or natural_language)
        timeout: Query timeout in seconds (default 30)

    Returns:
        Query result dictionary with columns, rows, metadata

    Raises:
        SQLValidationError: If SQL validation fails
        QueryExecutionError: If query execution fails
    """
    # Validate and transform SQL
    try:
        validated_sql = validate_and_transform_sql(sql)
    except SQLValidationError as e:
        # Save failed query to history
        await _save_query_history(
            db_name=db_connection.name,
            sql_text=sql,
            execution_time_ms=0,
            row_count=0,
            success=False,
            error_message=e.message,
            query_source=query_source
        )
        raise

    # Create engine for target database
    try:
        engine = create_engine_for_database(db_connection.url, db_connection.database_type)
    except Exception as e:
        raise QueryExecutionError(
            f"Failed to create database engine: {str(e)}",
            {"error": str(e)}
        )

    # Execute query
    start_time = time.time()
    try:
        async with engine.connect() as conn:
            # Set statement timeout (database-specific)
            if db_connection.database_type == DatabaseType.POSTGRESQL:
                await conn.execute(text(f"SET statement_timeout = {timeout * 1000}"))
            elif db_connection.database_type == DatabaseType.MYSQL:
                await conn.execute(text(f"SET SESSION max_execution_time = {timeout * 1000}"))

            # Execute query
            result = await conn.execute(text(validated_sql))
            rows = result.fetchall()
            columns = result.keys()

        execution_time_ms = int((time.time() - start_time) * 1000)

        # Transform result to JSON format
        column_defs = [
            {"name": col, "dataType": _infer_column_type(col, rows)}
            for col in columns
        ]
        row_data = [dict(row._mapping) for row in rows]

        # Save successful query to history
        await _save_query_history(
            db_name=db_connection.name,
            sql_text=validated_sql,
            execution_time_ms=execution_time_ms,
            row_count=len(row_data),
            success=True,
            error_message=None,
            query_source=query_source
        )

        # Cleanup query history (keep last 50)
        await _cleanup_query_history(db_connection.name)

        return {
            "columns": column_defs,
            "rows": row_data,
            "rowCount": len(row_data),
            "executionTimeMs": execution_time_ms,
            "sql": validated_sql
        }

    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Save failed query to history
        await _save_query_history(
            db_name=db_connection.name,
            sql_text=validated_sql,
            execution_time_ms=execution_time_ms,
            row_count=0,
            success=False,
            error_message=str(e),
            query_source=query_source
        )

        raise QueryExecutionError(
            f"Query execution failed: {str(e)}",
            {
                "error": str(e),
                "error_type": type(e).__name__,
                "executionTimeMs": execution_time_ms
            }
        )
    finally:
        await engine.dispose()


async def get_query_history(db_name: str, limit: int = 50) -> list[dict[str, Any]]:
    """Get query history for a database.

    Args:
        db_name: Database name
        limit: Maximum number of history entries to return (default 50)

    Returns:
        List of query history entries
    """
    async with async_session_maker() as session:
        from sqlmodel import select

        # Get recent history
        statement = (
            select(QueryHistory)
            .where(QueryHistory.database_name == db_name)
            .order_by(QueryHistory.executed_at.desc())
            .limit(limit)
        )

        results = await session.execute(statement)
        history_entries = results.scalars().all()

        # Convert to dict with camelCase
        return [
            {
                "id": entry.id,
                "databaseName": entry.database_name,
                "sqlText": entry.sql_text,
                "executedAt": entry.executed_at.isoformat() if entry.executed_at else None,
                "executionTimeMs": entry.execution_time_ms,
                "rowCount": entry.row_count,
                "success": entry.success,
                "errorMessage": entry.error_message,
                "querySource": entry.query_source.value
            }
            for entry in history_entries
        ]


async def _save_query_history(
    db_name: str,
    sql_text: str,
    execution_time_ms: int,
    row_count: int,
    success: bool,
    error_message: str | None,
    query_source: QuerySource
) -> None:
    """Save query to history.

    Args:
        db_name: Database name
        sql_text: SQL query text
        execution_time_ms: Execution time in milliseconds
        row_count: Number of rows returned
        success: Whether query succeeded
        error_message: Error message if failed
        query_source: Source of the query
    """
    async with async_session_maker() as session:
        history_entry = QueryHistory(
            database_name=db_name,
            sql_text=sql_text,
            executed_at=datetime.utcnow(),
            execution_time_ms=execution_time_ms,
            row_count=row_count,
            success=success,
            error_message=error_message,
            query_source=query_source
        )

        session.add(history_entry)
        await session.commit()


async def _cleanup_query_history(db_name: str, keep_last: int = 50) -> None:
    """Cleanup old query history entries.

    Args:
        db_name: Database name
        keep_last: Number of recent entries to keep (default 50)
    """
    async with async_session_maker() as session:
        from sqlmodel import select, delete

        # Get IDs of entries to delete
        statement = (
            select(QueryHistory.id)
            .where(QueryHistory.database_name == db_name)
            .order_by(QueryHistory.executed_at.desc())
            .offset(keep_last)
        )

        results = await session.execute(statement)
        ids_to_delete = [row[0] for row in results.fetchall()]

        if ids_to_delete:
            delete_stmt = delete(QueryHistory).where(QueryHistory.id.in_(ids_to_delete))
            await session.execute(delete_stmt)
            await session.commit()


def _infer_column_type(column_name: str, rows: list) -> str:
    """Infer column data type from column name and sample data.

    Args:
        column_name: Column name
        rows: Sample rows

    Returns:
        Data type string
    """
    # Try to infer from first non-null value
    for row in rows:
        row_dict = dict(row._mapping)
        value = row_dict.get(column_name)

        if value is not None:
            value_type = type(value).__name__

            # Map Python types to SQL types
            type_mapping = {
                "int": "integer",
                "float": "real",
                "str": "text",
                "bool": "boolean",
                "date": "date",
                "datetime": "timestamp",
                "bytes": "blob"
            }

            return type_mapping.get(value_type, "text")

    return "text"  # Default to text if can't infer

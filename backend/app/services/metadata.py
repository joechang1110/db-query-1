"""Metadata extraction service for multiple database types."""

import json
from datetime import datetime
from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from app.models.database import DatabaseType
from app.models.metadata import DatabaseMetadata
from app.models.schemas import TableMetadata, ColumnMetadata
from app.services.db_connection import create_engine_for_database, ConnectionError


async def extract_metadata_postgresql(engine: AsyncEngine) -> dict[str, Any]:
    """Extract metadata from PostgreSQL database.
    
    Args:
        engine: SQLAlchemy async engine
        
    Returns:
        Dictionary with tables and views metadata
    """
    tables_metadata = []
    views_metadata = []
    
    async with engine.connect() as conn:
        # Get all tables
        tables_query = text("""
            SELECT schemaname, tablename
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schemaname, tablename
        """)
        tables_result = await conn.execute(tables_query)
        
        for row in tables_result:
            schema_name = row[0]
            table_name = row[1]
            columns = await _get_postgresql_columns(conn, schema_name, table_name)
            row_count = await _get_postgresql_row_count(conn, schema_name, table_name)
            
            tables_metadata.append({
                "name": table_name,
                "type": "table",
                "schemaName": schema_name,
                "columns": columns,
                "rowCount": row_count,
            })
        
        # Get all views
        views_query = text("""
            SELECT schemaname, viewname
            FROM pg_views
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schemaname, viewname
        """)
        views_result = await conn.execute(views_query)
        
        for row in views_result:
            schema_name = row[0]
            view_name = row[1]
            columns = await _get_postgresql_columns(conn, schema_name, view_name)
            
            views_metadata.append({
                "name": view_name,
                "type": "view",
                "schemaName": schema_name,
                "columns": columns,
            })
    
    return {
        "tables": tables_metadata,
        "views": views_metadata,
    }


async def extract_metadata_mysql(engine: AsyncEngine) -> dict[str, Any]:
    """Extract metadata from MySQL database.
    
    Args:
        engine: SQLAlchemy async engine
        
    Returns:
        Dictionary with tables and views metadata
    """
    tables_metadata = []
    views_metadata = []
    
    async with engine.connect() as conn:
        # Get database name from connection
        db_query = text("SELECT DATABASE()")
        db_result = await conn.execute(db_query)
        db_name = db_result.scalar()
        
        # Get all tables and views
        tables_query = text("""
            SELECT table_schema, table_name, table_type
            FROM information_schema.tables
            WHERE table_schema NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
            AND table_schema = :db_name
            ORDER BY table_name
        """)
        tables_result = await conn.execute(tables_query, {"db_name": db_name})
        
        for row in tables_result:
            schema_name = row[0]
            table_name = row[1]
            table_type = row[2]
            
            columns = await _get_mysql_columns(conn, schema_name, table_name)
            
            metadata = {
                "name": table_name,
                "type": "table" if table_type == "BASE TABLE" else "view",
                "schemaName": schema_name,
                "columns": columns,
            }
            
            if table_type == "BASE TABLE":
                row_count = await _get_mysql_row_count(conn, schema_name, table_name)
                metadata["rowCount"] = row_count
                tables_metadata.append(metadata)
            else:
                views_metadata.append(metadata)
    
    return {
        "tables": tables_metadata,
        "views": views_metadata,
    }


async def extract_metadata_sqlite(engine: AsyncEngine) -> dict[str, Any]:
    """Extract metadata from SQLite database.
    
    Args:
        engine: SQLAlchemy async engine
        
    Returns:
        Dictionary with tables and views metadata
    """
    tables_metadata = []
    views_metadata = []
    
    async with engine.connect() as conn:
        # Get all tables
        tables_query = text("""
            SELECT name, type
            FROM sqlite_master
            WHERE type IN ('table', 'view')
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables_result = await conn.execute(tables_query)
        
        for row in tables_result:
            table_name = row[0]
            table_type = row[1]
            
            columns = await _get_sqlite_columns(conn, table_name)
            
            metadata = {
                "name": table_name,
                "type": table_type,
                "schemaName": "main",
                "columns": columns,
            }
            
            if table_type == "table":
                row_count = await _get_sqlite_row_count(conn, table_name)
                metadata["rowCount"] = row_count
                tables_metadata.append(metadata)
            else:
                views_metadata.append(metadata)
    
    return {
        "tables": tables_metadata,
        "views": views_metadata,
    }


async def extract_metadata(engine: AsyncEngine, database_type: DatabaseType) -> dict[str, Any]:
    """Extract metadata from database based on type.
    
    Args:
        engine: SQLAlchemy async engine
        database_type: Database type
        
    Returns:
        Dictionary with tables and views metadata
    """
    if database_type == DatabaseType.POSTGRESQL:
        return await extract_metadata_postgresql(engine)
    elif database_type == DatabaseType.MYSQL:
        return await extract_metadata_mysql(engine)
    elif database_type == DatabaseType.SQLITE:
        return await extract_metadata_sqlite(engine)
    else:
        raise ValueError(f"Unsupported database type: {database_type}")


async def _get_postgresql_columns(conn: AsyncSession, schema: str, table: str) -> list[dict[str, Any]]:
    """Get PostgreSQL table columns."""
    query = text("""
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = :schema AND table_name = :table
        ORDER BY ordinal_position
    """)
    result = await conn.execute(query, {"schema": schema, "table": table})
    
    # Get primary keys
    pk_query = text("""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_schema = :schema
            AND tc.table_name = :table
            AND tc.constraint_type = 'PRIMARY KEY'
    """)
    pk_result = await conn.execute(pk_query, {"schema": schema, "table": table})
    primary_keys = {row[0] for row in pk_result}
    
    columns = []
    for row in result:
        columns.append({
            "name": row[0],
            "dataType": row[1],
            "nullable": row[2] == "YES",
            "primaryKey": row[0] in primary_keys,
            "defaultValue": row[3],
        })
    
    return columns


async def _get_postgresql_row_count(conn: AsyncSession, schema: str, table: str) -> int:
    """Get PostgreSQL table row count."""
    query = text(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
    result = await conn.execute(query)
    return result.scalar() or 0


async def _get_mysql_columns(conn: AsyncSession, schema: str, table: str) -> list[dict[str, Any]]:
    """Get MySQL table columns."""
    query = text("""
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default,
            column_key
        FROM information_schema.columns
        WHERE table_schema = :schema AND table_name = :table
        ORDER BY ordinal_position
    """)
    result = await conn.execute(query, {"schema": schema, "table": table})
    
    columns = []
    for row in result:
        columns.append({
            "name": row[0],
            "dataType": row[1],
            "nullable": row[2] == "YES",
            "primaryKey": "PRI" in (row[4] or ""),
            "defaultValue": row[3],
        })
    
    return columns


async def _get_mysql_row_count(conn: AsyncSession, schema: str, table: str) -> int:
    """Get MySQL table row count."""
    query = text(f"SELECT COUNT(*) FROM `{schema}`.`{table}`")
    result = await conn.execute(query)
    return result.scalar() or 0


async def _get_sqlite_columns(conn: AsyncSession, table: str) -> list[dict[str, Any]]:
    """Get SQLite table columns."""
    query = text(f"PRAGMA table_info({table})")
    result = await conn.execute(query)
    
    columns = []
    for row in result:
        columns.append({
            "name": row[1],
            "dataType": row[2],
            "nullable": not row[3],
            "primaryKey": bool(row[5]),
            "defaultValue": row[4],
        })
    
    return columns


async def _get_sqlite_row_count(conn: AsyncSession, table: str) -> int:
    """Get SQLite table row count."""
    query = text(f"SELECT COUNT(*) FROM {table}")
    result = await conn.execute(query)
    return result.scalar() or 0


async def get_cached_metadata(session: AsyncSession, database_name: str) -> DatabaseMetadata | None:
    """Get cached metadata from database.
    
    Args:
        session: Database session
        database_name: Database connection name
        
    Returns:
        DatabaseMetadata if found and not stale, None otherwise
    """
    from sqlalchemy import select
    
    stmt = select(DatabaseMetadata).where(DatabaseMetadata.database_name == database_name)
    result = await session.execute(stmt)
    metadata = result.scalar_one_or_none()
    
    if metadata and not metadata.is_stale:
        return metadata
    
    return None


async def save_metadata(
    session: AsyncSession,
    database_name: str,
    metadata_dict: dict[str, Any],
) -> DatabaseMetadata:
    """Save metadata to database.
    
    Args:
        session: Database session
        database_name: Database connection name
        metadata_dict: Metadata dictionary
        
    Returns:
        Saved DatabaseMetadata instance
    """
    from sqlalchemy import select
    
    metadata_json = json.dumps(metadata_dict)
    table_count = len(metadata_dict.get("tables", [])) + len(metadata_dict.get("views", []))
    
    # Check if metadata exists
    stmt = select(DatabaseMetadata).where(DatabaseMetadata.database_name == database_name)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        existing.metadata_json = metadata_json
        existing.fetched_at = datetime.utcnow()
        existing.table_count = table_count
        await session.commit()
        await session.refresh(existing)
        return existing
    else:
        new_metadata = DatabaseMetadata(
            database_name=database_name,
            metadata_json=metadata_json,
            fetched_at=datetime.utcnow(),
            table_count=table_count,
        )
        session.add(new_metadata)
        await session.commit()
        await session.refresh(new_metadata)
        return new_metadata


async def get_database_metadata(db_connection) -> dict[str, Any]:
    """Get database metadata for a connection (from cache or fresh extraction).

    This is a convenience function for getting metadata to pass to NL2SQL service.

    Args:
        db_connection: DatabaseConnection instance

    Returns:
        Metadata dictionary with tables and views
    """
    from app.services.db_connection import create_engine_for_database

    # Create engine for target database
    engine = create_engine_for_database(db_connection.url, db_connection.database_type)

    try:
        # Extract metadata
        metadata_dict = await extract_metadata(engine, db_connection.database_type)
        return metadata_dict
    finally:
        await engine.dispose()

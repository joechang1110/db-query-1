"""Database connection management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any
from app.database import get_session
from app.models.database import DatabaseConnection, DatabaseType, ConnectionStatus
from app.models.schemas import (
    DatabaseConnectionInput,
    DatabaseConnectionResponse,
    DatabaseMetadataResponse,
    ErrorResponse,
    ErrorDetail,
)
from app.services.db_connection import (
    parse_database_url,
    test_connection,
    create_engine_for_database,
    ConnectionError,
)
from app.services.metadata import (
    extract_metadata,
    get_cached_metadata,
    save_metadata,
)
import json
from datetime import datetime

router = APIRouter()


@router.get("/dbs", response_model=dict[str, list[DatabaseConnectionResponse]])
async def list_databases(
    session: AsyncSession = Depends(get_session),
) -> dict[str, list[DatabaseConnectionResponse]]:
    """List all database connections."""
    stmt = select(DatabaseConnection).order_by(DatabaseConnection.created_at.desc())
    result = await session.execute(stmt)
    connections = result.scalars().all()
    
    return {
        "databases": [
            DatabaseConnectionResponse.model_validate(conn) for conn in connections
        ]
    }


@router.put(
    "/dbs/{name}",
    response_model=DatabaseConnectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_or_update_database(
    name: str,
    input_data: DatabaseConnectionInput,
    session: AsyncSession = Depends(get_session),
) -> DatabaseConnectionResponse:
    """Create or update database connection."""
    # Validate name format
    import re
    if not re.match(r"^[a-zA-Z0-9-_]+$", name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid database name format",
                    "details": {"name": name},
                }
            },
        )
    
    # Parse URL and infer database type
    try:
        database_type, normalized_url = parse_database_url(input_data.url)
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": e.message,
                    "details": e.details,
                }
            },
        )
    
    # Test connection
    try:
        await test_connection(normalized_url, database_type)
    except ConnectionError as e:
        # Log detailed error in debug mode
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Connection test failed: {e.message}", extra={"details": e.details})
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "CONNECTION_ERROR",
                    "message": e.message,
                    "details": e.details,
                }
            },
        )
    
    # Check if connection exists
    stmt = select(DatabaseConnection).where(DatabaseConnection.name == name)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing
        existing.url = normalized_url
        existing.database_type = database_type
        existing.description = input_data.description
        existing.updated_at = datetime.utcnow()
        existing.last_connected_at = datetime.utcnow()
        existing.status = ConnectionStatus.ACTIVE
        await session.commit()
        await session.refresh(existing)
        return DatabaseConnectionResponse.model_validate(existing)
    else:
        # Create new
        new_connection = DatabaseConnection(
            name=name,
            url=normalized_url,
            database_type=database_type,
            description=input_data.description,
            last_connected_at=datetime.utcnow(),
            status=ConnectionStatus.ACTIVE,
        )
        session.add(new_connection)
        await session.commit()
        await session.refresh(new_connection)
        return DatabaseConnectionResponse.model_validate(new_connection)


@router.get("/dbs/{name}", response_model=DatabaseMetadataResponse)
async def get_database_metadata(
    name: str,
    session: AsyncSession = Depends(get_session),
) -> DatabaseMetadataResponse:
    """Get database metadata."""
    # Check if connection exists
    stmt = select(DatabaseConnection).where(DatabaseConnection.name == name)
    result = await session.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DATABASE_NOT_FOUND",
                    "message": f"Database connection '{name}' not found",
                }
            },
        )
    
    # Check cached metadata
    cached = await get_cached_metadata(session, name)
    
    if cached and not cached.is_stale:
        # Return cached metadata
        metadata_dict = json.loads(cached.metadata_json)
        return DatabaseMetadataResponse(
            database_name=name,
            database_type=connection.database_type,
            tables=metadata_dict.get("tables", []),
            views=metadata_dict.get("views", []),
            fetched_at=cached.fetched_at,
            is_stale=False,
        )
    
    # Fetch fresh metadata
    try:
        engine = create_engine_for_database(connection.url, connection.database_type)
        metadata_dict = await extract_metadata(engine, connection.database_type)
        await engine.dispose()
        
        # Save to cache
        saved_metadata = await save_metadata(session, name, metadata_dict)
        
        return DatabaseMetadataResponse(
            database_name=name,
            database_type=connection.database_type,
            tables=metadata_dict.get("tables", []),
            views=metadata_dict.get("views", []),
            fetched_at=saved_metadata.fetched_at,
            is_stale=False,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "CONNECTION_ERROR",
                    "message": f"Failed to fetch metadata: {str(e)}",
                    "details": {"error": str(e)},
                }
            },
        )


@router.delete("/dbs/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_database(
    name: str,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete database connection."""
    stmt = select(DatabaseConnection).where(DatabaseConnection.name == name)
    result = await session.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DATABASE_NOT_FOUND",
                    "message": f"Database connection '{name}' not found",
                }
            },
        )
    
    # Delete metadata
    from app.models.metadata import DatabaseMetadata
    metadata_stmt = select(DatabaseMetadata).where(DatabaseMetadata.database_name == name)
    metadata_result = await session.execute(metadata_stmt)
    metadata = metadata_result.scalar_one_or_none()
    if metadata:
        await session.delete(metadata)
    
    # Delete connection
    await session.delete(connection)
    await session.commit()


@router.post("/dbs/{name}/refresh", response_model=DatabaseMetadataResponse)
async def refresh_metadata(
    name: str,
    session: AsyncSession = Depends(get_session),
) -> DatabaseMetadataResponse:
    """Refresh database metadata."""
    # Check if connection exists
    stmt = select(DatabaseConnection).where(DatabaseConnection.name == name)
    result = await session.execute(stmt)
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DATABASE_NOT_FOUND",
                    "message": f"Database connection '{name}' not found",
                }
            },
        )
    
    # Fetch fresh metadata
    try:
        engine = create_engine_for_database(connection.url, connection.database_type)
        metadata_dict = await extract_metadata(engine, connection.database_type)
        await engine.dispose()
        
        # Save to cache
        saved_metadata = await save_metadata(session, name, metadata_dict)
        
        return DatabaseMetadataResponse(
            database_name=name,
            database_type=connection.database_type,
            tables=metadata_dict.get("tables", []),
            views=metadata_dict.get("views", []),
            fetched_at=saved_metadata.fetched_at,
            is_stale=False,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "CONNECTION_ERROR",
                    "message": f"Failed to refresh metadata: {str(e)}",
                    "details": {"error": str(e)},
                }
            },
        )


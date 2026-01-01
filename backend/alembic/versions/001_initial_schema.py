"""Initial database schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial tables."""
    # Database connections table
    op.create_table(
        "database_connections",
        sa.Column("name", sa.String(50), primary_key=True),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("database_type", sa.String(20), nullable=False),
        sa.Column("description", sa.String(200)),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.Column("last_connected_at", sa.DateTime),
        sa.Column("status", sa.String(20), nullable=False),
    )
    op.create_index("ix_database_connections_url", "database_connections", ["url"])

    # Database metadata table
    op.create_table(
        "database_metadata",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("database_name", sa.String(50), sa.ForeignKey("database_connections.name"), nullable=False),
        sa.Column("metadata_json", sa.Text, nullable=False),
        sa.Column("fetched_at", sa.DateTime, nullable=False),
        sa.Column("table_count", sa.Integer, nullable=False),
    )
    op.create_index("ix_database_metadata_database_name", "database_metadata", ["database_name"])

    # Query history table
    op.create_table(
        "query_history",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("database_name", sa.String(50), sa.ForeignKey("database_connections.name"), nullable=False),
        sa.Column("sql_text", sa.Text, nullable=False),
        sa.Column("executed_at", sa.DateTime, nullable=False),
        sa.Column("execution_time_ms", sa.Integer),
        sa.Column("row_count", sa.Integer),
        sa.Column("success", sa.Boolean, nullable=False),
        sa.Column("error_message", sa.Text),
        sa.Column("query_source", sa.String(20), nullable=False),
    )
    op.create_index("ix_query_history_executed_at", "query_history", ["executed_at"])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index("ix_query_history_executed_at", table_name="query_history")
    op.drop_table("query_history")
    op.drop_index("ix_database_metadata_database_name", table_name="database_metadata")
    op.drop_table("database_metadata")
    op.drop_index("ix_database_connections_url", table_name="database_connections")
    op.drop_table("database_connections")


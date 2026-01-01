"""SQL validation service using sqlparse."""

import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DML
from typing import Any


class SQLValidationError(Exception):
    """SQL validation error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """Initialize validation error."""
        super().__init__(message)
        self.message = message
        self.details = details or {}


def validate_and_transform_sql(sql: str) -> str:
    """Validate SQL and transform if needed.
    
    Args:
        sql: SQL query string
        
    Returns:
        Validated and transformed SQL query
        
    Raises:
        SQLValidationError: If SQL is invalid or contains non-SELECT statements
    """
    # Parse SQL
    try:
        parsed = sqlparse.parse(sql)
    except Exception as e:
        raise SQLValidationError(
            f"Failed to parse SQL: {str(e)}",
            {"error": str(e), "line": 1, "column": 0}
        )
    
    if not parsed:
        raise SQLValidationError("Empty SQL query")
    
    # Check for multiple statements
    if len(parsed) > 1:
        raise SQLValidationError(
            "Multiple statements are not allowed",
            {"statementCount": len(parsed)}
        )
    
    statement = parsed[0]
    
    # Check statement type
    statement_type = _get_statement_type(statement)
    if statement_type != "SELECT":
        raise SQLValidationError(
            f"Only SELECT statements are allowed, found: {statement_type}",
            {"statementType": statement_type, "line": 1, "column": 0}
        )
    
    # Check for LIMIT clause
    has_limit = _has_limit_clause(statement)
    
    # Transform SQL: add LIMIT if missing
    if not has_limit:
        transformed_sql = _add_limit_clause(sql)
    else:
        transformed_sql = sql
    
    return transformed_sql


def _get_statement_type(statement: Statement) -> str:
    """Get SQL statement type."""
    for token in statement.tokens:
        if token.ttype is DML:
            return token.value.upper()
        if token.ttype is Keyword and token.value.upper() in ("SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"):
            return token.value.upper()
    return "UNKNOWN"


def _has_limit_clause(statement: Statement) -> bool:
    """Check if statement has LIMIT clause."""
    sql_upper = str(statement).upper()
    return "LIMIT" in sql_upper


def _add_limit_clause(sql: str) -> str:
    """Add LIMIT 1000 clause to SQL query."""
    # Simple approach: append LIMIT 1000
    # More sophisticated parsing could be done, but this works for most cases
    sql_trimmed = sql.strip().rstrip(";")
    return f"{sql_trimmed} LIMIT 1000"


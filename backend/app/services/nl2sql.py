"""Natural language to SQL service using OpenAI SDK."""

import json
from typing import Any
from openai import AsyncOpenAI
from app.config import settings
from app.models.database import DatabaseConnection
from app.services.sql_validator import validate_and_transform_sql, SQLValidationError


class NL2SQLError(Exception):
    """Natural language to SQL error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """Initialize NL2SQL error."""
        super().__init__(message)
        self.message = message
        self.details = details or {}


async def generate_sql_from_natural_language(
    db_connection: DatabaseConnection,
    prompt: str,
    metadata_json: dict[str, Any],
) -> dict[str, str]:
    """Generate SQL query from natural language input.

    Args:
        db_connection: Database connection object
        prompt: Natural language query from user
        metadata_json: Database metadata (tables, columns, etc.)

    Returns:
        Dictionary with 'sql' and 'explanation' keys

    Raises:
        NL2SQLError: If SQL generation fails
        SQLValidationError: If generated SQL is invalid
    """
    if not settings.openai_api_key:
        raise NL2SQLError(
            "OpenAI API key not configured",
            {"hint": "Set OPENAI_API_KEY environment variable"}
        )

    # Initialize OpenAI client
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    # Build system prompt with database schema context
    system_prompt = _build_system_prompt(db_connection.database_type.value, metadata_json)

    # Call OpenAI API
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Use gpt-4o-mini for cost efficiency
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,  # Low temperature for consistent SQL generation
            max_tokens=500,
        )

        # Extract response
        content = response.choices[0].message.content
        if not content:
            raise NL2SQLError("Empty response from OpenAI API")

        # Parse response (expected format: JSON with sql and explanation)
        try:
            result = json.loads(content)
            sql = result.get("sql", "")
            explanation = result.get("explanation", "")
        except json.JSONDecodeError:
            # Fallback: treat entire response as SQL
            sql = content.strip()
            explanation = "Generated SQL query from natural language input"

        if not sql:
            raise NL2SQLError("No SQL query generated")

        # Validate generated SQL
        try:
            validated_sql = validate_and_transform_sql(sql)
        except SQLValidationError as e:
            raise NL2SQLError(
                f"Generated SQL failed validation: {e.message}",
                {"generated_sql": sql, "validation_error": e.details}
            )

        return {
            "sql": validated_sql,
            "explanation": explanation,
        }

    except Exception as e:
        if isinstance(e, (NL2SQLError, SQLValidationError)):
            raise

        raise NL2SQLError(
            f"Failed to generate SQL: {str(e)}",
            {
                "error": str(e),
                "error_type": type(e).__name__,
            }
        )


def _build_system_prompt(database_type: str, metadata_json: dict[str, Any]) -> str:
    """Build system prompt with database schema context.

    Args:
        database_type: Type of database (postgresql, mysql, sqlite)
        metadata_json: Database metadata

    Returns:
        System prompt string
    """
    # Extract tables and views from metadata
    tables = metadata_json.get("tables", [])
    views = metadata_json.get("views", [])

    # Build schema description
    schema_lines = []
    for item in tables + views:
        table_name = item.get("name", "")
        table_type = item.get("type", "table")
        columns = item.get("columns", [])

        column_list = []
        for col in columns:
            col_name = col.get("name", "")
            col_type = col.get("dataType", "")
            col_nullable = col.get("nullable", True)
            col_pk = col.get("primaryKey", False)

            col_desc = f"{col_name} {col_type}"
            if col_pk:
                col_desc += " PRIMARY KEY"
            if not col_nullable:
                col_desc += " NOT NULL"

            column_list.append(col_desc)

        schema_lines.append(f"{table_type.upper()} {table_name} (")
        schema_lines.append("  " + ",\n  ".join(column_list))
        schema_lines.append(")")

    schema_description = "\n".join(schema_lines)

    # Build system prompt
    prompt = f"""You are a SQL expert for {database_type} databases. Generate SQL SELECT queries based on natural language input.

Database Schema:
{schema_description}

Rules:
1. ONLY generate SELECT statements (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Use explicit column names (avoid SELECT *)
3. Include appropriate WHERE, JOIN, ORDER BY, GROUP BY clauses as needed
4. Use {database_type}-specific SQL syntax
5. Return response as JSON with two fields:
   - "sql": the SQL query (string)
   - "explanation": brief explanation of what the query does (string)

Example response format:
{{
  "sql": "SELECT name, email FROM users WHERE status = 'active' LIMIT 100",
  "explanation": "This query retrieves the name and email of all active users, limited to 100 rows."
}}

User input may be in English or Chinese. Always respond with valid JSON containing SQL and explanation in English."""

    return prompt

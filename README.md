# Database Query Tool

A multi-database query tool that allows users to connect to databases, view metadata, execute SQL queries, and generate SQL from natural language.

## Project Structure

```
w2/db_query_1/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
└── README.md         # This file
```

## Quick Start

### Backend

```bash
cd w2/db_query_1/backend

# Install dependencies
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Set OpenAI API key (required for NL2SQL feature)
# Windows PowerShell:
$env:OPENAI_API_KEY="your-api-key-here"
# Linux/macOS:
export OPENAI_API_KEY="your-api-key-here"

# Initialize database (creates ./db/db_query.db automatically)
alembic upgrade head

# Run server
uvicorn app.main:app --reload --port 8000
```

**Note**: The SQLite database for storing connections and metadata will be created at `./db/db_query.db` automatically.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

## Features

- ✅ Add database connections (PostgreSQL, MySQL, SQLite)
- ✅ View database metadata (tables, views, columns)
- ✅ Execute SQL queries (SELECT only)
- ✅ Natural language to SQL generation (coming in Phase 5)

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Status

**Phase 1-3 Complete**: Database connection and metadata viewing
**Phase 4**: SQL query execution (in progress)
**Phase 5**: Natural language to SQL (planned)


# Database Query Tool - Backend

Backend API for the Database Query Tool built with FastAPI.

## Setup

### Prerequisites

- Python 3.12+
- uv (Python package manager)

### Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"
```

### Configuration

The application reads configuration from environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required for NL2SQL feature)
- `LOG_LEVEL`: Logging level (default: INFO)
- `CORS_ORIGINS`: CORS allowed origins (default: *)

**Database**: The SQLite database is automatically created at `./db/db_query.db` (relative to the backend directory). No configuration needed.

**Note**: You can also create a `.env` file in the backend directory if you prefer, but environment variables take precedence.

### Database Setup

```bash
# Initialize database
alembic upgrade head
```

### Running

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- OpenAPI: http://localhost:8000/openapi.json

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Project Structure

```
backend/
├── app/
│   ├── api/          # FastAPI routers
│   ├── models/       # SQLModel entities and Pydantic schemas
│   ├── services/     # Business logic
│   ├── config.py    # Settings
│   ├── database.py  # Database setup
│   └── main.py      # FastAPI app
├── alembic/         # Database migrations
├── tests/           # Test suite
└── pyproject.toml   # Project configuration
```


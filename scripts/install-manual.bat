@echo off
REM Manual installation script for backend dependencies
REM Use this if the automatic installation fails

echo ==========================================
echo Manual Backend Installation
echo ==========================================
echo.

REM Navigate to project root
cd /d "%~dp0.."
echo Project root: %CD%
echo.

REM Check if pyproject.toml exists
if not exist "pyproject.toml" (
    echo ERROR: pyproject.toml not found!
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Step 1: Create virtual environment...
cd backend
if not exist ".venv" (
    uv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
)
cd ..
echo ✓ Virtual environment ready
echo.

echo Step 2: Installing core packages individually...
echo.

echo Installing uvicorn...
uv pip install --python backend/.venv/Scripts/python.exe "uvicorn[standard]>=0.24.0"
echo.

echo Installing fastapi...
uv pip install --python backend/.venv/Scripts/python.exe "fastapi>=0.104.0"
echo.

echo Installing pydantic...
uv pip install --python backend/.venv/Scripts/python.exe "pydantic>=2.0.0" "pydantic-settings>=2.0.0"
echo.

echo Installing SQLAlchemy and SQLModel...
uv pip install --python backend/.venv/Scripts/python.exe "sqlalchemy>=2.0.0" "sqlmodel>=0.0.14"
echo.

echo Installing database drivers...
uv pip install --python backend/.venv/Scripts/python.exe "aiosqlite>=0.19.0" "asyncpg>=0.29.0" "aiomysql>=0.2.0"
echo.

echo Installing alembic...
uv pip install --python backend/.venv/Scripts/python.exe "alembic>=1.13.0"
echo.

echo Installing other dependencies...
uv pip install --python backend/.venv/Scripts/python.exe "sqlparse>=0.5.0" "openai>=1.0.0" "python-multipart>=0.0.6"
echo.

echo Step 3: Installing dev dependencies...
echo.
uv pip install --python backend/.venv/Scripts/python.exe "pytest>=7.4.0" "pytest-asyncio>=0.21.0" "httpx>=0.25.0"
uv pip install --python backend/.venv/Scripts/python.exe "mypy>=1.7.0" "ruff>=0.1.0" "black>=23.12.0"
echo.

echo Step 4: Verifying installation...
echo.
cd backend

.venv\Scripts\python.exe -c "import uvicorn; print('✓ uvicorn:', uvicorn.__version__)"
.venv\Scripts\python.exe -c "import fastapi; print('✓ fastapi:', fastapi.__version__)"
.venv\Scripts\python.exe -c "import alembic; print('✓ alembic:', alembic.__version__)"
.venv\Scripts\python.exe -c "import sqlmodel; print('✓ sqlmodel:', sqlmodel.__version__)"

cd ..
echo.
echo ==========================================
echo Manual installation complete!
echo ==========================================
pause


@echo off
REM Fix broken virtual environment and install dependencies
REM This script fixes the "No module named pip" issue

echo ==========================================
echo Fixing Virtual Environment and Installing Dependencies
echo ==========================================
echo.

cd /d "%~dp0.."
set PROJECT_ROOT=%CD%
echo Project root: %PROJECT_ROOT%
echo.

echo Step 1: Removing broken virtual environment...
if exist "backend\.venv" (
    rmdir /s /q backend\.venv
    echo ✓ Old virtual environment removed
) else (
    echo No existing virtual environment found
)
echo.

echo Step 2: Creating new virtual environment with uv...
cd backend
uv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment!
    echo.
    echo Please check:
    echo   1. Is uv installed? Run: uv --version
    echo   2. Try: pip install uv
    pause
    exit /b 1
)
echo ✓ Virtual environment created
echo.

cd ..
echo Step 3: Installing dependencies using uv pip...
echo.
echo Installing from: %PROJECT_ROOT%\pyproject.toml
echo.

REM Use uv pip to install (it handles the venv internally)
uv pip install --python backend/.venv/Scripts/python.exe -e ".[dev]"
if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    echo.
    echo Trying alternative method...
    echo.
    
    REM Alternative: install packages directly
    uv pip install --python backend/.venv/Scripts/python.exe uvicorn[standard] fastapi pydantic pydantic-settings sqlparse openai sqlalchemy sqlmodel asyncpg aiomysql aiosqlite alembic python-multipart
    uv pip install --python backend/.venv/Scripts/python.exe pytest pytest-asyncio httpx mypy ruff black
)

echo.
echo Step 4: Verifying installation...
echo.

cd backend
.venv\Scripts\python.exe -c "import sys; print('Python:', sys.version)"
echo.

echo Checking packages...
.venv\Scripts\python.exe -c "import uvicorn; print('✓ uvicorn:', uvicorn.__version__)" 2>nul
if errorlevel 1 (
    echo ✗ uvicorn not installed
) else (
    echo ✓ uvicorn installed
)

.venv\Scripts\python.exe -c "import fastapi; print('✓ fastapi:', fastapi.__version__)" 2>nul
if errorlevel 1 (
    echo ✗ fastapi not installed
) else (
    echo ✓ fastapi installed
)

.venv\Scripts\python.exe -c "import alembic; print('✓ alembic:', alembic.__version__)" 2>nul
if errorlevel 1 (
    echo ✗ alembic not installed
) else (
    echo ✓ alembic installed
)

cd ..
echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo Next steps:
echo   1. Run migrations: cd backend ^&^& .venv\Scripts\python.exe run_migrations.py
echo   2. Start backend: scripts\start-backend.bat
echo.
pause


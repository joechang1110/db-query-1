@echo off
REM Database Query Tool - Backend Startup Script
REM Starts the FastAPI backend server

echo ==========================================
echo Starting Backend Server...
echo ==========================================
echo.

cd /d "%~dp0.."
cd backend

REM Check if virtual environment exists
if not exist ".venv" (
    echo Error: Virtual environment not found!
    echo Please run: make install-backend
    echo Or manually: cd backend ^&^& uv venv ^&^& uv pip install -e ".[dev]"
    pause
    exit /b 1
)

REM Check if dependencies are installed
.venv\Scripts\python.exe -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
    echo Warning: Dependencies not installed!
    echo Installing dependencies...
    echo.
    REM Go to project root (where pyproject.toml is)
    cd /d "%~dp0.."
    echo Current directory: %CD%
    echo Installing from: %CD%\pyproject.toml
    uv pip install -e ".[dev]"
    if errorlevel 1 (
        echo.
        echo Error: Failed to install dependencies!
        echo Please run manually:
        echo   cd w2\db_query_1
        echo   uv pip install -e ".[dev]"
        pause
        exit /b 1
    )
    cd backend
    echo.
    echo Dependencies installed successfully!
    echo.
)

REM Check if database exists, if not run migrations
if not exist "db\db_query.db" (
    echo Database not found. Running migrations...
    echo.
    set PYTHONUNBUFFERED=1
    .venv\Scripts\python.exe run_migrations.py
    if errorlevel 1 (
        echo.
        echo ==========================================
        echo ERROR: Migration failed!
        echo ==========================================
        echo Please check the error message above.
        echo You can try running manually:
        echo   cd backend
        echo   .venv\Scripts\python.exe run_migrations.py
        echo.
        pause
        exit /b 1
    )
    echo.
)

REM Activate virtual environment and start server
echo Starting uvicorn server on http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Debug Mode: ENABLED
echo.
echo Press Ctrl+C to stop the server
echo.

REM Enable Python error traceback and start server with debug options
set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

pause


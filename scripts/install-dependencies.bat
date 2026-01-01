@echo off
REM Database Query Tool - Install Dependencies Script
REM Installs all required dependencies for backend and frontend

echo ==========================================
echo Installing Dependencies...
echo ==========================================
echo.

REM Get the script directory and navigate to project root
cd /d "%~dp0.."
echo Project root: %CD%
echo.

REM Install backend dependencies
echo [1/2] Installing backend dependencies...
echo.

cd backend
if not exist ".venv" (
    echo Creating virtual environment...
    uv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment!
        echo Please ensure uv is installed: https://github.com/astral-sh/uv
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
    echo.
)

REM Install packages from project root
echo Installing Python packages from pyproject.toml...
echo Current directory: %CD%
cd ..
set PROJECT_ROOT=%CD%
echo Project root: %PROJECT_ROOT%
echo Installing from: %PROJECT_ROOT%\pyproject.toml
echo.

REM Check if pyproject.toml exists
if not exist "pyproject.toml" (
    echo ERROR: pyproject.toml not found!
    echo Current directory: %CD%
    echo Expected file: %CD%\pyproject.toml
    echo.
    echo Please ensure you are in the correct directory.
    pause
    exit /b 1
)

echo Running: uv pip install --python backend/.venv/Scripts/python.exe -e ".[dev]"
echo.
uv pip install --python backend/.venv/Scripts/python.exe -e ".[dev]"
if errorlevel 1 (
    echo.
    echo Installation with -e flag failed. Trying alternative method...
    echo Installing packages directly...
    echo.
    uv pip install --python backend/.venv/Scripts/python.exe uvicorn[standard] fastapi pydantic pydantic-settings sqlparse openai sqlalchemy sqlmodel asyncpg aiomysql aiosqlite alembic python-multipart
    uv pip install --python backend/.venv/Scripts/python.exe pytest pytest-asyncio httpx mypy ruff black
    if errorlevel 1 (
        echo.
        echo ==========================================
        echo ERROR: Failed to install backend dependencies!
        echo ==========================================
        echo.
        echo Troubleshooting:
        echo   1. Check if uv is installed: uv --version
        echo   2. Try updating uv: pip install --upgrade uv
        echo   3. Try manual install script: scripts\install-manual.bat
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Installation command completed.
echo.

REM Verify installation
cd backend
echo.
echo ==========================================
echo Verifying Installation...
echo ==========================================
echo.
echo Checking installed packages...
echo.

REM Check uvicorn
echo [1/3] Checking uvicorn...
.venv\Scripts\python.exe -c "import uvicorn; print('  Version: ' + uvicorn.__version__)" 2>nul
if errorlevel 1 (
    echo   ✗ uvicorn NOT found
    echo.
    echo   This is critical! Backend server requires uvicorn.
    echo.
    set VERIFY_FAILED=1
) else (
    echo   ✓ uvicorn installed
)

REM Check alembic
echo.
echo [2/3] Checking alembic...
.venv\Scripts\python.exe -c "import alembic; print('  Version: ' + alembic.__version__)" 2>nul
if errorlevel 1 (
    echo   ✗ alembic NOT found
    echo.
    echo   This is critical! Database migrations require alembic.
    echo.
    set VERIFY_FAILED=1
) else (
    echo   ✓ alembic installed
)

REM Check fastapi
echo.
echo [3/3] Checking fastapi...
.venv\Scripts\python.exe -c "import fastapi; print('  Version: ' + fastapi.__version__)" 2>nul
if errorlevel 1 (
    echo   ✗ fastapi NOT found
    echo.
    echo   This is critical! Backend framework requires fastapi.
    echo.
    set VERIFY_FAILED=1
) else (
    echo   ✓ fastapi installed
)

echo.
if defined VERIFY_FAILED (
    echo ==========================================
    echo ERROR: Some packages failed to install!
    echo ==========================================
    echo.
    echo The installation completed but some packages are missing.
    echo.
    echo Manual fix:
    echo   1. Check Python version: python --version
    echo      ^(Should be Python 3.12 or higher^)
    echo.
    echo   2. Try installing packages individually:
    echo      cd %PROJECT_ROOT%
    echo      uv pip install uvicorn[standard]
    echo      uv pip install fastapi
    echo      uv pip install alembic
    echo      uv pip install sqlmodel
    echo.
    echo   3. Check virtual environment:
    echo      cd %PROJECT_ROOT%\backend
    echo      .venv\Scripts\python.exe --version
    echo.
    cd ..
    pause
    exit /b 1
) else (
    echo ==========================================
    echo ✓ All backend dependencies verified!
    echo ==========================================
)
cd ..

REM Install frontend dependencies
echo.
echo [2/2] Installing frontend dependencies...
echo.

cd frontend
if not exist "node_modules" (
    echo Installing npm packages...
    npm install
    if errorlevel 1 (
        echo Warning: Failed to install frontend dependencies!
        echo Please check npm is installed and try again.
    ) else (
        echo Frontend dependencies installed successfully!
    )
) else (
    echo Frontend dependencies already installed.
)
cd ..

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo Dependencies installed successfully:
echo   ✓ Backend: Python packages in backend/.venv
echo   ✓ Frontend: Node packages in frontend/node_modules
echo.
echo Next steps:
echo   1. Run database migrations: 
echo      cd backend
echo      .venv\Scripts\python.exe run_migrations.py
echo.
echo   2. Start backend: scripts\start-backend.bat
echo   3. Start frontend: scripts\start-frontend.bat
echo.
pause


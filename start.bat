@echo off
REM Database Query Tool - Quick Start Script
REM This script provides a menu to start/stop services

:MENU
cls
echo ==========================================
echo   Database Query Tool - Quick Start
echo ==========================================
echo.
echo   1. Start Backend Only
echo   2. Start Frontend Only
echo   3. Start All (Backend + Frontend)
echo   4. Stop All Services
echo   5. Install Dependencies
echo   6. Run Database Migrations
echo   7. Exit
echo.
set /p choice="Please select an option (1-7): "

if "%choice%"=="1" goto START_BACKEND
if "%choice%"=="2" goto START_FRONTEND
if "%choice%"=="3" goto START_ALL
if "%choice%"=="4" goto STOP_ALL
if "%choice%"=="5" goto INSTALL
if "%choice%"=="6" goto MIGRATE
if "%choice%"=="7" goto EXIT

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto MENU

:START_BACKEND
call scripts\start-backend.bat
goto MENU

:START_FRONTEND
call scripts\start-frontend.bat
goto MENU

:START_ALL
call scripts\start-all.bat
goto MENU

:STOP_ALL
call scripts\stop-all.bat
goto MENU

:INSTALL
echo Installing dependencies...
echo.

REM Install backend dependencies
echo Installing backend dependencies...
cd backend
if not exist ".venv" (
    echo Creating virtual environment...
    uv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment!
        echo Please ensure uv is installed: https://github.com/astral-sh/uv
        cd ..
        pause
        goto MENU
    )
)

REM Install backend packages (from project root)
cd ..
echo Installing Python packages...
uv pip install -e ".[dev]"
if errorlevel 1 (
    echo Error: Failed to install backend dependencies!
    cd backend
    pause
    cd ..
    goto MENU
)
cd backend

REM Install frontend dependencies
cd ..\frontend
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
    if errorlevel 1 (
        echo Warning: Failed to install frontend dependencies!
    )
)
cd ..

echo.
echo Dependencies installed successfully!
pause
goto MENU

:MIGRATE
echo Running database migrations...
cd backend
if not exist ".venv" (
    echo Error: Virtual environment not found. Please install dependencies first.
    pause
    goto MENU
)
echo Running alembic migrations...
.venv\Scripts\python.exe run_migrations.py
if errorlevel 1 (
    echo Error: Migration failed. Please check the error message above.
) else (
    echo Migrations completed successfully!
)
cd ..
pause
goto MENU

:EXIT
echo Goodbye!
exit /b 0


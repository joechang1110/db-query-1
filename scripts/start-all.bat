@echo off
REM Database Query Tool - Start All Services
REM Starts both backend and frontend servers in separate windows

echo ==========================================
echo Starting All Services...
echo ==========================================
echo.

REM Get the script directory
set SCRIPT_DIR=%~dp0

REM Start backend in a new window
echo Starting Backend Server...
start "Database Query Tool - Backend" cmd /k "%SCRIPT_DIR%start-backend.bat"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
echo Starting Frontend Server...
start "Database Query Tool - Frontend" cmd /k "%SCRIPT_DIR%start-frontend.bat"

echo.
echo ==========================================
echo Both servers are starting...
echo ==========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Two new windows have been opened for the servers.
echo Close those windows or press Ctrl+C in them to stop.
echo.
echo Press any key to exit this window (servers will continue running)...
pause >nul


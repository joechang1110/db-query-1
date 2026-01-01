@echo off
REM Database Query Tool - Frontend Startup Script
REM Starts the React frontend development server

echo ==========================================
echo Starting Frontend Server...
echo ==========================================
echo.

cd /d "%~dp0.."
cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Error: Dependencies not installed!
    echo Please run: make install-frontend
    echo Or manually: cd frontend ^&^& npm install
    pause
    exit /b 1
)

REM Start development server
echo Starting Vite development server on http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev

pause


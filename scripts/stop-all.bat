@echo off
REM Database Query Tool - Stop All Services
REM Stops all running backend and frontend servers

echo ==========================================
echo Stopping All Services...
echo ==========================================
echo.

REM Stop processes on port 8000 (backend)
echo Stopping Backend (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process %%a on port 8000...
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo Process %%a not found or already stopped
    ) else (
        echo Backend stopped (PID: %%a)
    )
)

REM Stop processes on port 5173 (frontend)
echo Stopping Frontend (port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    echo Killing process %%a on port 5173...
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo Process %%a not found or already stopped
    ) else (
        echo Frontend stopped (PID: %%a)
    )
)

REM Also kill uvicorn processes
echo Stopping any remaining uvicorn processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Database Query Tool - Backend*" >nul 2>&1

REM Also kill node processes (be careful - this might kill other node processes)
REM Uncomment the line below if you want to kill all node processes
REM taskkill /F /IM node.exe >nul 2>&1

echo.
echo ==========================================
echo All services stopped
echo ==========================================
echo.
pause


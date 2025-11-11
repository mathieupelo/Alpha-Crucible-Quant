@echo off
REM Start both frontend and backend in development mode
REM Opens separate windows for each service
REM Supports both uvicorn and python main.py backend modes

setlocal ENABLEDELAYEDEXPANSION

echo ==============================================
echo   Starting Full Stack Development
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0..\.."

REM Check if user wants simple mode (python main.py) or uvicorn mode
REM Default to simple mode (easier, matches user's preference)
set USE_SIMPLE=1
if "%1"=="uvicorn" (
    set USE_SIMPLE=0
    echo Using uvicorn mode (with hot reload)
) else (
    echo Using simple mode (python main.py)
    echo To use uvicorn mode, run: scripts\dev\dev_all.bat uvicorn
)

echo.
echo Starting Backend...
if !USE_SIMPLE!==1 (
    start "Alpha Crucible - Backend" cmd /k "scripts\dev\dev_backend_simple.bat"
) else (
    start "Alpha Crucible - Backend" cmd /k "scripts\dev\dev_backend.bat"
)

echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo Starting Frontend...
start "Alpha Crucible - Frontend" cmd /k "scripts\dev\dev_frontend.bat"

echo.
echo ==============================================
echo   Development servers starting...
echo ==============================================
echo.
echo Backend:    http://localhost:8000
echo API Docs:   http://localhost:8000/api/docs
echo Frontend:   http://localhost:3000
echo.
echo Both servers are running in separate windows.
echo Close the windows or press Ctrl+C in each to stop.
echo.
echo TIP: For final testing with ngrok, run:
echo   scripts\ngrok\start_ngrok_dev.bat
echo.
echo Waiting 3 seconds before closing this window...
timeout /t 3 /nobreak >nul

endlocal


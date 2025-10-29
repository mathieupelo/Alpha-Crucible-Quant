@echo off
REM Start both frontend and backend in development mode
REM Opens separate windows for each service

echo ==============================================
echo   Starting Full Stack Development
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

echo Starting Backend...
start "Alpha Crucible - Backend" cmd /k "%~dp0dev_backend.bat"

echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo Starting Frontend...
start "Alpha Crucible - Frontend" cmd /k "%~dp0dev_frontend.bat"

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
echo Waiting 3 seconds before closing this window...
timeout /t 3 /nobreak >nul


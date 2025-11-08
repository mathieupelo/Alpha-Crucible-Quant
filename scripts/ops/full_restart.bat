@echo off
setlocal enabledelayedexpansion
REM Full Restart - Clears all caches and restarts everything
echo ==============================================
echo   Full Restart - Clearing All Caches
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

echo [1/6] Clearing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f" 2>nul
echo Python cache cleared!
echo.

echo [2/6] Clearing Vite cache directories...
if exist "frontend\node_modules\.vite" (
    rd /s /q "frontend\node_modules\.vite" 2>nul
)
for /d /r frontend %%d in (.vite) do @if exist "%%d" rd /s /q "%%d" 2>nul
if exist "frontend\dist" rd /s /q "frontend\dist" 2>nul
echo Vite cache cleared!
echo.

echo [3/6] Killing existing backend processes...
taskkill /FI "WINDOWTITLE eq Alpha Crucible - Backend*" /T /F >nul 2>&1
taskkill /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *uvicorn*" /T /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo Backend processes killed!
echo.

echo [4/6] Killing existing frontend processes...
REM Kill by window title first
taskkill /FI "WINDOWTITLE eq Alpha Crucible - Frontend*" /T /F >nul 2>&1
REM Kill any node processes with vite in command line
taskkill /FI "IMAGENAME eq node.exe" /FI "COMMANDLINE eq *vite*" /T /F >nul 2>&1

REM Kill any process listening on port 3000 (most reliable method)
echo   Killing processes using port 3000...
REM Use netstat to find processes (simpler and more reliable in batch)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
    set "PIDVAL=%%a"
    if not "!PIDVAL!"=="" (
        if not "!PIDVAL!"=="0" (
            echo     Killing PID !PIDVAL!...
            taskkill /F /PID !PIDVAL! >nul 2>&1
        )
    )
)

timeout /t 3 /nobreak >nul
echo Frontend processes killed!
echo.

echo [5/6] Stopping Docker containers (if running)...
docker --version >nul 2>&1
if not errorlevel 1 (
    echo   Checking for Docker containers...
    REM Try to stop containers using docker-compose (graceful shutdown)
    docker-compose down >nul 2>&1
    docker-compose -f docker-compose.dev.yml down >nul 2>&1
    
    REM Also try stopping known container names individually (in case compose fails)
    docker stop alpha-crucible-frontend alpha-crucible-frontend-dev alpha-crucible-backend alpha-crucible-backend-dev alpha-crucible-nginx alpha-crucible-nginx-dev >nul 2>&1
    
    echo   Docker containers stopped (if any were running)
) else (
    echo   Docker not available - skipping container check.
)
echo.

echo [5.5/6] Final verification - ensuring port 3000 is free...
REM Verify port 3000 is free using netstat (simple and reliable)
netstat -ano | findstr ":3000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo   Port 3000 is free - ready for Vite dev server.
) else (
    echo   WARNING: Port 3000 is still in use! Force-killing processes...
    REM Try one more time with netstat
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
        set "PIDVAL=%%a"
        if not "!PIDVAL!"=="" (
            if not "!PIDVAL!"=="0" (
                echo     Killing PID !PIDVAL!...
                taskkill /F /PID !PIDVAL! >nul 2>&1
            )
        )
    )
    
    timeout /t 3 /nobreak >nul
    
    REM Final verification
    netstat -ano | findstr ":3000" | findstr "LISTENING" >nul 2>&1
    if errorlevel 1 (
        echo   Port 3000 is now free - ready for Vite dev server.
    ) else (
        echo   ERROR: Port 3000 is STILL in use after multiple cleanup attempts!
        echo   Try running: scripts\troubleshoot\kill_port_3000.bat
        echo   Or manually: docker-compose down
        pause
    )
)
echo.

echo [6/6] Starting fresh servers...
call "%~dp0dev_all.bat"


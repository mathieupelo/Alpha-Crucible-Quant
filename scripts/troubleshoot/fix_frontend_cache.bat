@echo off
REM Quick Fix for Frontend Cache Issues
REM This is the nuclear option - stops everything, clears all caches, rebuilds

echo ==============================================
echo   Fixing Frontend Cache Issues
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

echo [1/5] Stopping all containers...
docker-compose down 2>nul
echo Done!
echo.

echo [2/5] Clearing all local caches...
REM Python cache
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f" 2>nul

REM Vite cache
if exist "frontend\node_modules\.vite" rd /s /q "frontend\node_modules\.vite" 2>nul
for /d /r frontend %%d in (.vite) do @if exist "%%d" rd /s /q "%%d" 2>nul
if exist "frontend\dist" rd /s /q "frontend\dist" 2>nul

echo Done!
echo.

echo [3/5] Clearing Docker build cache...
docker builder prune -f
echo Done!
echo.

echo [4/5] Rebuilding containers (no cache)...
docker-compose build --no-cache frontend
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo Done!
echo.

echo [5/5] Starting containers...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start!
    pause
    exit /b 1
)
echo Done!
echo.

echo ==============================================
echo   ✅ Containers rebuilt and restarted!
echo.
echo   🔴 IMPORTANT - Clear Browser Cache:
echo      - Press Ctrl+Shift+Delete
echo      - Or Ctrl+Shift+R (hard refresh)
echo      - Or F12 → Right-click refresh → Empty Cache
echo ==============================================
echo.
echo Waiting 5 seconds for containers to start...
timeout /t 5 /nobreak >nul
docker-compose ps
echo.
pause


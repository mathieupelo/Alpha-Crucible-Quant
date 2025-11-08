@echo off
REM Full Restart with Docker - Clears all caches, rebuilds Docker, and restarts
echo ==============================================
echo   Full Restart - Docker Mode
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

echo [3/6] Stopping Docker containers...
docker-compose down
echo Containers stopped!
echo.

echo [4/6] Clearing Docker build cache...
docker builder prune -f
echo Docker cache cleared!
echo.

echo [5/6] Rebuilding Docker containers (no cache)...
docker-compose build --no-cache
if errorlevel 1 (
    echo ERROR: Docker build failed!
    pause
    exit /b 1
)
echo Containers rebuilt!
echo.

echo [6/6] Starting Docker containers...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start containers!
    pause
    exit /b 1
)
echo Containers started!
echo.

echo ==============================================
echo   Full restart complete!
echo.
echo   IMPORTANT: Clear your browser cache!
echo   - Chrome/Edge: Ctrl+Shift+Delete
echo   - Or do a hard refresh: Ctrl+Shift+R or Ctrl+F5
echo   - Or open DevTools (F12) -> Right-click refresh -> Empty Cache and Hard Reload
echo ==============================================
echo.
pause


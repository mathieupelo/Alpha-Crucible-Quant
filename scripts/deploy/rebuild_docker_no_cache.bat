@echo off
REM Rebuild Docker containers without using cache
REM This ensures you get the latest code changes

echo ==============================================
echo   Rebuilding Docker Containers (No Cache)
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

echo Stopping containers...
docker-compose down

echo.
echo Clearing Docker build cache...
docker builder prune -f

echo.
echo Clearing local caches...
call "%~dp0clear_all_cache.bat"

echo.
echo Rebuilding containers without cache...
docker-compose build --no-cache

echo.
echo Starting containers...
docker-compose up -d

echo.
echo ==============================================
echo   Docker containers rebuilt and started!
echo   Clear browser cache (Ctrl+Shift+Delete)
echo   or hard refresh (Ctrl+Shift+R)
echo ==============================================
echo.
pause


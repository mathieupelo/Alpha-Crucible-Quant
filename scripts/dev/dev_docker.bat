@echo off
REM Docker Development Mode with Hot Reload
REM This starts Docker services with source code mounted for hot reload
REM Much faster than full Docker rebuilds

echo ==============================================
echo   Docker Development Mode (Hot Reload)
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

REM Check if Docker is running
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Starting Docker services in development mode...
echo Code changes will be reflected immediately (hot reload enabled).
echo.
echo This uses docker-compose.dev.yml which mounts your source code.
echo.
echo Backend:    http://localhost:8000
echo Frontend:   http://localhost:3000
echo API Docs:   http://localhost:8000/api/docs
echo.

REM Start services with development compose file
REM Note: This will rebuild images if Dockerfile changed, but code changes are hot-reloaded
docker-compose -f docker-compose.dev.yml up --build

pause


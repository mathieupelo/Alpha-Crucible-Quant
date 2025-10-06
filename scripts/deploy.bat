@echo off
REM Alpha Crucible Quant - Docker Deployment Script for Windows
REM This script deploys the application using Docker containers

echo Alpha Crucible Quant - Docker Deployment
echo ======================================
echo.

REM Change to project root directory
cd /d "%~dp0.."

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not running or not installed!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo Error: .env file not found in project root!
    echo Please copy .env_template to .env and configure your settings.
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Building and starting Docker containers...
echo.

REM Stop any existing containers
echo Stopping existing containers...
docker-compose down

REM Build and start containers
echo Building and starting new containers...
docker-compose up --build -d

REM Check if containers started successfully
timeout /t 10 /nobreak >nul

echo.
echo Checking container status...
docker-compose ps

echo.
echo Deployment completed!
echo.
echo Your application is now running at:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo - Nginx Proxy: http://localhost:80
echo.
echo To view logs: docker-compose logs -f
echo To stop: docker-compose down
echo.

pause

@echo off
REM Alpha Crucible Quant - Quick Start Script for Windows
REM This script sets up and deploys the application in one go

echo Alpha Crucible Quant - Quick Start
echo =================================
echo.

REM Change to project root directory
cd /d "%~dp0.."

REM Check if .env file exists, if not copy from template
if not exist .env (
    echo Setting up environment configuration...
    copy .env_template .env
    echo.
    echo IMPORTANT: Please review and update the .env file with your settings!
    echo The template contains your Supabase credentials but you may need to adjust them.
    echo.
    pause
)

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not running or not installed!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Starting deployment...
echo.

REM Deploy the application
call scripts\deploy\deploy.bat

echo.
echo Deployment completed!
echo.
echo Next steps:
echo 1. For external access, run: scripts\ngrok\prepare_and_start_ngrok_final.bat
echo 2. Your app will be available at the Ngrok URL shown
echo 3. To view logs: docker-compose logs -f
echo.

pause

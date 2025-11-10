@echo off
REM FastAPI Backend Development Server (Local)
REM Runs the backend locally without Docker for fast development

echo ==============================================
echo   FastAPI Backend - Development Mode
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

REM Check if virtual environment exists
if exist venv (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found.
    echo You may want to run: python -m venv venv
    echo Then install dependencies: pip install -r requirements.txt -r backend/requirements.txt
    echo.
)

REM Set PYTHONPATH to include root directory for src imports
REM This allows 'from src.database import ...' to work correctly
REM Save the repo root path before changing directories
set REPO_ROOT=%CD%
set PYTHONPATH=%REPO_ROOT%;%REPO_ROOT%\backend;%PYTHONPATH%

REM Check if .env file exists in repo root
if not exist .env (
    echo WARNING: .env file not found in repo root!
    echo Please create .env file with your database credentials.
    echo The .env file should be in the repository root directory.
    echo.
) else (
    echo Found .env file - database connection should work.
    echo.
)

REM Check if backend requirements are installed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo ERROR: FastAPI not found. Installing dependencies...
    pip install -r backend/requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies. Exiting.
        pause
        exit /b 1
    )
)

echo Starting FastAPI backend...
echo Backend will be available at: http://localhost:8000
echo API docs will be available at: http://localhost:8000/api/docs
echo.
echo Press Ctrl+C to stop the server.
echo.

REM Start the backend with hot reload
REM Change to backend directory - main.py uses relative imports
cd backend
REM Run uvicorn from backend directory where main.py is located
REM PYTHONPATH is already set to include repo root for src imports
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --reload-dir .. --reload-dir ../src


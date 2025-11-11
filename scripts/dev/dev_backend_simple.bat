@echo off
REM Simple Backend Development Script
REM Runs backend with 'python main.py' from the backend folder
REM This is the simplest way to run the backend locally

echo ==============================================
echo   FastAPI Backend - Simple Local Mode
echo   (Using: python main.py)
echo ==============================================
echo.

REM Move to backend directory
cd /d "%~dp0..\..\backend"

REM Check if virtual environment exists in repo root
if exist ..\venv (
    echo Activating virtual environment...
    call ..\venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found at ..\venv
    echo You may want to run: python -m venv venv (from repo root)
    echo.
)

REM Set PYTHONPATH to include repo root for src imports
REM This allows 'from src.database import ...' to work correctly
REM Get absolute path to repo root
pushd "%~dp0..\.."
set REPO_ROOT=%CD%
popd
set PYTHONPATH=%REPO_ROOT%;%REPO_ROOT%\backend;%PYTHONPATH%

REM Check if .env file exists in repo root
if not exist ..\.env (
    echo WARNING: .env file not found in repo root!
    echo Please create .env file with your database credentials.
    echo.
) else (
    echo Found .env file - database connection should work.
    echo.
)

REM Check if FastAPI is installed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo ERROR: FastAPI not found. Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies. Exiting.
        pause
        exit /b 1
    )
)

echo Starting FastAPI backend with 'python main.py'...
echo Backend will be available at: http://localhost:8000
echo API docs will be available at: http://localhost:8000/api/docs
echo.
echo Press Ctrl+C to stop the server.
echo.

REM Run main.py directly (it uses uvicorn internally)
python main.py


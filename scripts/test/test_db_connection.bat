@echo off
REM Test Database Connection
REM Quick script to verify .env file is being loaded and database is accessible

echo ==============================================
echo   Testing Database Connection
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
    echo.
)

REM Set PYTHONPATH
set PYTHONPATH=%CD%;%CD%\backend;%PYTHONPATH%

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found in repo root!
    echo Please create .env file with your database credentials.
    pause
    exit /b 1
)

echo Checking .env file exists... OK
echo.

REM Run Python script to test connection
echo Testing database connection...
python -c "from src.database import DatabaseManager; db = DatabaseManager(); result = db.connect(); print('Connection successful!' if result else 'Connection failed!'); db.disconnect() if db.is_connected() else None"

if errorlevel 1 (
    echo.
    echo Connection test failed. Check:
    echo 1. .env file exists and has correct credentials
    echo 2. Supabase database is accessible
    echo 3. Network connection is working
    pause
    exit /b 1
)

echo.
echo ==============================================
echo   Database connection test completed!
echo ==============================================
echo.
pause


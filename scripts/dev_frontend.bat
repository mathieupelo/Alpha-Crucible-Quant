@echo off
REM Vite Frontend Development Server (Local)
REM Runs the frontend locally without Docker for fast development

echo ==============================================
echo   Vite Frontend - Development Mode
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0..\frontend"

REM Check if node_modules exists
if not exist node_modules (
    echo node_modules not found. Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo Failed to install dependencies. Exiting.
        pause
        exit /b 1
    )
)

REM Check for .env.local or create one for development
if not exist .env.local (
    echo Creating .env.local for development...
    (
        echo VITE_API_URL=http://localhost:8000/api
        echo VITE_API_KEY=my-awesome-key-123
    ) > .env.local
    echo Created .env.local with development settings.
    echo.
)

echo Starting Vite development server...
echo Frontend will be available at: http://localhost:3000
echo Backend API should be running at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server.
echo.

REM Start the frontend dev server
call npm run dev


@echo off
REM Ngrok startup script for Windows (Background version)
REM This script starts Ngrok tunnel for Alpha Crucible Quant in the background

echo Starting Ngrok tunnel for Alpha Crucible Quant in background...
echo.

REM Change to project root directory (where .env should be)
cd /d "%~dp0.."

REM Check if .env file exists
if not exist .env (
    echo Error: .env file not found in project root!
    echo Please copy .env_template to .env and configure your settings.
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Load environment variables from .env file
for /f "usebackq tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="NGROK_AUTHTOKEN" (
        set NGROK_AUTHTOKEN=%%b
        goto :found_token
    )
)

:found_token
REM Check if auth token is set
if "%NGROK_AUTHTOKEN%"=="" (
    echo Error: NGROK_AUTHTOKEN not found in .env file!
    echo Please check that the .env file contains: NGROK_AUTHTOKEN=your_token_here
    echo.
    echo Current .env file contents:
    type .env
    pause
    exit /b 1
)

REM Configure Ngrok auth token
ngrok config add-authtoken %NGROK_AUTHTOKEN%

REM Stop any existing Ngrok tunnels
echo Stopping any existing Ngrok tunnels...
call "%~dp0kill_ngrok.bat" >nul 2>&1

REM Wait a moment for processes to stop
timeout /t 2 /nobreak >nul

REM Start Ngrok tunnel in background
echo Starting Ngrok tunnel on port 80...
echo Your app will be accessible via the public URL shown below.
echo.
echo Ngrok is running in the background.
echo To check status: curl http://localhost:4040/api/tunnels
echo To stop ngrok: scripts\kill_ngrok.bat
echo.

start /B ngrok http 80 --log=stdout > ngrok.log 2>&1

REM Wait a moment for ngrok to start
timeout /t 3 /nobreak >nul

REM Get the public URL
echo Getting public URL...
for /f "tokens=*" %%i in ('curl -s http://localhost:4040/api/tunnels ^| findstr "public_url"') do (
    echo %%i
)

echo.
echo Ngrok tunnel started successfully!
echo Check ngrok.log for detailed logs.
echo.


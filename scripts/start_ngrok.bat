@echo off
REM Ngrok startup script for Windows
REM This script starts Ngrok tunnel for Alpha Crucible Quant

echo Starting Ngrok tunnel for Alpha Crucible Quant...
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
ping 127.0.0.1 -n 3 >nul

REM Start Ngrok tunnel
echo Starting Ngrok tunnel on port 8080...
echo Your app will be accessible via the public URL shown below.
echo.
echo Ngrok is running in the background. Check the URL above.
echo To stop ngrok, run: scripts\kill_ngrok.bat
echo.
ngrok http 8080 --log=stdout

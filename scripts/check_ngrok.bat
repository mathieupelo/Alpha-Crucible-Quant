@echo off
REM Check Ngrok tunnel status

echo Checking Ngrok tunnel status...
echo.

REM Check if Ngrok is running
tasklist /fi "imagename eq ngrok.exe" 2>nul | find /i "ngrok.exe" >nul
if %errorlevel% equ 0 (
    echo Ngrok is running!
    echo.
    echo Getting tunnel information...
    curl -s http://localhost:4040/api/tunnels | findstr "public_url"
    if %errorlevel% neq 0 (
        echo Could not get tunnel URL. Check http://localhost:4040 for details.
    )
) else (
    echo Ngrok is not running.
    echo Run scripts\start_ngrok.bat to start the tunnel.
)

echo.
pause

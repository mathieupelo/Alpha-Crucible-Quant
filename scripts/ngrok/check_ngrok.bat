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
    echo.
    echo To start ngrok:
    echo   - Full deployment: scripts\ngrok\prepare_and_start_ngrok_final.bat
    echo   - Dev/local: scripts\ngrok\start_ngrok_dev.bat
    echo   - Manual (if services running): scripts\ngrok\start_ngrok.bat
)

echo.
pause

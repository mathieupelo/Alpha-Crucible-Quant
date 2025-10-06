@echo off
REM Kill all Ngrok processes

echo Killing all Ngrok processes...
echo.

REM Stop all Ngrok processes
taskkill /f /im ngrok.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo Ngrok processes killed successfully.
) else (
    echo No Ngrok processes were running.
)

echo.
echo All Ngrok tunnels have been stopped.
echo You can now run scripts\start_ngrok.bat to start a fresh tunnel.
echo.
pause

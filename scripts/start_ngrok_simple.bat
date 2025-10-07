@echo off
REM Simple ngrok startup script
echo Starting ngrok tunnel...

REM Kill any existing ngrok processes
taskkill /F /IM ngrok.exe 2>nul

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start ngrok
ngrok http 80










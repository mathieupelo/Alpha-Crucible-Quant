@echo off
REM Restart Backend Script - Clears cache and restarts server
echo ==============================================
echo   Restarting Backend with Cache Clear
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

echo Clearing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f" 2>nul
echo Cache cleared!
echo.

echo Finding and closing existing backend processes...
taskkill /FI "WINDOWTITLE eq Alpha Crucible - Backend*" /T /F >nul 2>&1
taskkill /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *uvicorn*" /T /F >nul 2>&1
REM Also kill any process using port 8000
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :8000') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 3 /nobreak >nul
echo.

echo Starting backend...
call "%~dp0dev_backend.bat"


@echo off
REM Full Restart - Clears all caches and restarts everything
echo ==============================================
echo   Full Restart - Clearing All Caches
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

echo [1/4] Clearing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f" 2>nul
echo Python cache cleared!
echo.

echo [2/4] Killing existing backend processes...
taskkill /FI "WINDOWTITLE eq Alpha Crucible - Backend*" /T /F >nul 2>&1
taskkill /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *uvicorn*" /T /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo Backend processes killed!
echo.

echo [3/4] Killing existing frontend processes...
taskkill /FI "WINDOWTITLE eq Alpha Crucible - Frontend*" /T /F >nul 2>&1
taskkill /FI "IMAGENAME eq node.exe" /FI "COMMANDLINE eq *vite*" /T /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo Frontend processes killed!
echo.

echo [4/4] Starting fresh servers...
call "%~dp0dev_all.bat"


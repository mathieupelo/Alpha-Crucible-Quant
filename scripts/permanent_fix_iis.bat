@echo off
REM Permanently disable IIS to prevent port 80 conflicts

echo ==============================================
echo   Permanently Disable IIS (Run as Admin)
echo ==============================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if errorlevel 1 (
  echo ERROR: This script must be run as Administrator!
  echo Right-click on this file and select "Run as administrator"
  echo.
  echo Press any key to close this window...
  pause >nul
  exit /b 1
)

echo [1/4] Stopping IIS services...
net stop "World Wide Web Publishing Service" >nul 2>&1
net stop "IIS Admin Service" >nul 2>&1
net stop "HTTP SSL" >nul 2>&1

echo [2/4] Disabling IIS services...
sc config "W3SVC" start= disabled >nul 2>&1
sc config "IISADMIN" start= disabled >nul 2>&1
sc config "HTTPFilter" start= disabled >nul 2>&1

echo [3/4] Disabling IIS Windows Feature...
dism /online /disable-feature /featurename:IIS-WebServer /norestart >nul 2>&1
dism /online /disable-feature /featurename:IIS-CommonHttpFeatures /norestart >nul 2>&1
dism /online /disable-feature /featurename:IIS-HttpErrors /norestart >nul 2>&1
dism /online /disable-feature /featurename:IIS-HttpLogging /norestart >nul 2>&1
dism /online /disable-feature /featurename:IIS-RequestFiltering /norestart >nul 2>&1
dism /online /disable-feature /featurename:IIS-StaticContent /norestart >nul 2>&1
dism /online /disable-feature /featurename:IIS-DefaultDocument /norestart >nul 2>&1
dism /online /disable-feature /featurename:IIS-DirectoryBrowsing /norestart >nul 2>&1
dism /online /disable-feature /featurename:IIS-ASPNET45 /norestart >nul 2>&1

echo [4/4] Removing IIS from startup...
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "IIS" /t REG_SZ /d "" /f >nul 2>&1

echo.
echo ==============================================
echo   IIS Permanently Disabled
echo ==============================================
echo.
echo IIS has been permanently disabled and will not start automatically.
echo Port 80 is now free for your Docker application.
echo.
echo You may need to restart your computer for all changes to take effect.
echo After restart, you can run: scripts\start_docker_and_deploy.bat
echo.
echo Press any key to close this window...
pause >nul


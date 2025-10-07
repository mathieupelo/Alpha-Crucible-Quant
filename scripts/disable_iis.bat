@echo off
REM Disable IIS to free up port 80 for Docker

echo ==============================================
echo   Disable IIS to Free Port 80
echo ==============================================
echo.

echo [1/3] Stopping IIS services...
net stop "World Wide Web Publishing Service" >nul 2>&1
net stop "IIS Admin Service" >nul 2>&1
net stop "HTTP SSL" >nul 2>&1

echo [2/3] Disabling IIS services...
sc config "W3SVC" start= disabled >nul 2>&1
sc config "IISADMIN" start= disabled >nul 2>&1
sc config "HTTPFilter" start= disabled >nul 2>&1

echo [3/3] Disabling IIS Windows Feature...
dism /online /disable-feature /featurename:IIS-WebServer /norestart >nul 2>&1

echo.
echo ==============================================
echo   IIS Disabled Successfully
echo ==============================================
echo.
echo Port 80 is now free for Docker.
echo You may need to restart your computer for changes to take effect.
echo.
echo Press any key to close this window...
pause >nul


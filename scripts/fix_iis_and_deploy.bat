@echo off
REM Fix IIS port conflict and deploy Alpha Crucible Quant

setlocal ENABLEDELAYEDEXPANSION

echo ==============================================
echo   Fix IIS Conflict and Deploy App
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

REM Check if port 80 is in use
echo [1/6] Checking port 80 availability...
netstat -ano | findstr ":80 " | findstr "LISTENING" >nul
if errorlevel 1 (
  echo   Port 80 is free
  goto :start_docker
)

echo   Port 80 is in use by another service
echo [2/6] Stopping IIS services to free port 80...
net stop "World Wide Web Publishing Service" >nul 2>&1
net stop "IIS Admin Service" >nul 2>&1
net stop "HTTP SSL" >nul 2>&1

REM Wait a moment for services to stop
ping 127.0.0.1 -n 3 >nul

REM Check if port 80 is now free
echo [3/6] Verifying port 80 is free...
netstat -ano | findstr ":80 " | findstr "LISTENING" >nul
if not errorlevel 1 (
  echo   WARNING: Port 80 is still in use. Trying to kill the process...
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":80 " ^| findstr "LISTENING"') do (
    if not "%%a"=="0" (
      echo     Killing process %%a
      taskkill /F /PID %%a >nul 2>&1
    )
  )
  ping 127.0.0.1 -n 2 >nul
)

:start_docker
echo [4/6] Starting Docker Desktop and deployment...
call scripts\start_docker_and_deploy.bat
if errorlevel 1 (
  echo   Deployment failed
  echo.
  echo Press any key to close this window...
  pause >nul
  exit /b 1
)

echo [5/6] Deployment completed successfully!
echo [6/6] Your app is now accessible via ngrok
echo.
echo Check http://localhost:4040/api/tunnels for the ngrok URL
echo.
echo Press any key to close this window...
pause >nul

endlocal
exit /b 0


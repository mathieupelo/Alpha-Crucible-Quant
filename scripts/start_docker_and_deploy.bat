@echo off
REM Start Docker Desktop and deploy Alpha Crucible Quant with ngrok

setlocal ENABLEDELAYEDEXPANSION

echo ==============================================
echo   Start Docker Desktop and Deploy App
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

REM Check if Docker Desktop is already running
echo [1/5] Checking if Docker Desktop is running...
docker ps >nul 2>&1
if not errorlevel 1 (
  echo   Docker Desktop is already running
  goto :deploy_app
)

REM Start Docker Desktop
echo [2/5] Starting Docker Desktop...
echo   This may take 1-2 minutes...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

REM Wait for Docker Desktop to start
echo [3/5] Waiting for Docker Desktop to start...
set /a _COUNT=0
:wait_docker_start
set /a _COUNT+=1
docker ps >nul 2>&1
if not errorlevel 1 goto :docker_ready
if %_COUNT% GEQ 120 goto :docker_timeout
echo     Waiting for Docker Desktop... (%_COUNT%/120)
ping 127.0.0.1 -n 3 >nul
goto :wait_docker_start

:docker_ready
echo   Docker Desktop is ready!
goto :deploy_app

:docker_timeout
echo   WARNING: Docker Desktop is taking longer than expected
echo   Please wait for Docker Desktop to fully start, then run:
echo   scripts\prepare_and_start_ngrok.bat
echo.
echo Press any key to close this window...
pause >nul
exit /b 1

:deploy_app
REM Run the deployment script
echo [4/5] Starting deployment...
call scripts\prepare_and_start_ngrok.bat
if errorlevel 1 (
  echo   Deployment failed
  echo.
  echo Press any key to close this window...
  pause >nul
  exit /b 1
)

echo [5/5] Deployment completed successfully!
echo.
echo Your app should now be accessible via ngrok.
echo Check http://localhost:4040/api/tunnels for the ngrok URL.
echo.
echo Press any key to close this window...
pause >nul

endlocal
exit /b 0


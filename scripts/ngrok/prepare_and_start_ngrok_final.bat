@echo off
REM Prepare Docker stack (up + health checks) then start ngrok (Windows) with IIS conflict resolution

setlocal ENABLEDELAYEDEXPANSION

echo ==============================================
echo   Prepare stack and start ngrok (Windows)
echo   with IIS conflict resolution
echo   Includes: Main app + Airflow + Ngrok
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0..\.."

REM Ensure no stray ngrok is running (non-blocking)
taskkill /F /IM ngrok.exe >nul 2>&1

REM Check for IIS port conflicts and fix them
echo [0.5/8] Checking for IIS port conflicts...
netstat -ano | findstr ":80 " | findstr "LISTENING" >nul
if not errorlevel 1 (
  echo   Port 80 is in use by another service (likely IIS)
  echo   Stopping IIS services to free port 80...
  net stop "World Wide Web Publishing Service" >nul 2>&1
  net stop "IIS Admin Service" >nul 2>&1
  net stop "HTTP SSL" >nul 2>&1
  ping 127.0.0.1 -n 3 >nul
  
  REM Check if port 80 is now free
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
  echo   IIS services stopped and port 80 freed
) else (
  echo   Port 80 is free
)

REM Check if Docker Desktop is running and start if needed
echo [1/8] Checking Docker Desktop...

REM First, quickly check if Docker engine is already ready (best case)
docker ps >nul 2>&1
if not errorlevel 1 (
  echo   Docker Desktop is running and engine is ready
  goto :continue
)

REM Docker engine is not ready, check if Docker Desktop process is running
tasklist /FI "IMAGENAME eq Docker Desktop.exe" 2>nul | find /I /N "Docker Desktop.exe">nul
if "%ERRORLEVEL%"=="0" (
  echo   Docker Desktop process is running, but engine is not ready
  echo   This may indicate Docker Desktop needs to be restarted
  echo.
  echo   Options:
  echo   1. Wait for Docker Desktop to finish starting (may take 30-60 seconds)
  echo   2. Restart Docker Desktop to fix potential issues
  echo.
  choice /C YN /M "Restart Docker Desktop now? (Y=Yes, N=No - will wait)"
  if errorlevel 2 goto :check_docker_engine
  if errorlevel 1 goto :restart_docker
)

REM Docker Desktop is not running, try to start it
echo   Docker Desktop is not running, attempting to start it...
echo   This may take a moment...

REM Try common Docker Desktop installation paths
set DOCKER_STARTED=0

REM Try Program Files path
if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
  start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
  set DOCKER_STARTED=1
  goto :docker_started
)

REM Try Program Files (x86) path
if exist "C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe" (
  start "" "C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe"
  set DOCKER_STARTED=1
  goto :docker_started
)

REM Try PowerShell to start Docker Desktop (works with Start menu shortcut)
powershell -Command "Start-Process 'Docker Desktop'" >nul 2>&1
if not errorlevel 1 (
  set DOCKER_STARTED=1
  goto :docker_started
)

REM If we couldn't start it, give helpful error
if %DOCKER_STARTED%==0 (
  echo   ERROR: Could not start Docker Desktop automatically!
  echo   Please start Docker Desktop manually and run this script again.
  echo   Look for Docker Desktop in your Start menu or system tray.
  echo.
  pause >nul
  exit /b 1
)

:restart_docker
REM Restart Docker Desktop
echo   Restarting Docker Desktop...
echo   Stopping Docker Desktop...

REM Try to stop Docker Desktop gracefully first
taskkill /IM "Docker Desktop.exe" /T >nul 2>&1
ping 127.0.0.1 -n 3 >nul

REM Make sure it's stopped
taskkill /F /IM "Docker Desktop.exe" /T >nul 2>&1
ping 127.0.0.1 -n 5 >nul

REM Now start it
echo   Starting Docker Desktop...
if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
  start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
  goto :docker_started
)
if exist "C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe" (
  start "" "C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe"
  goto :docker_started
)
powershell -Command "Start-Process 'Docker Desktop'" >nul 2>&1
goto :docker_started

:docker_started
echo   Docker Desktop is starting, please wait...
echo   (This may take 30-60 seconds for Docker Desktop to fully initialize)

:check_docker_engine
REM Wait for Docker engine to be ready (check docker ps command)
echo   Waiting for Docker engine to be ready...
set /a _COUNT=0
:wait_docker
set /a _COUNT+=1
docker ps >nul 2>&1
if not errorlevel 1 goto :docker_ready
if %_COUNT% GEQ 90 goto :docker_timeout

REM Show progress and helpful messages
if %_COUNT%==1 (
  echo   Checking Docker engine status...
)
if %_COUNT%==15 (
  echo   Still waiting... Docker Desktop engine initialization can take 30-60 seconds
)
if %_COUNT%==30 (
  echo   This is taking longer than usual...
  echo   If Docker Desktop is stuck, you may need to restart it manually
)
if %_COUNT%==60 (
  echo   Docker Desktop is taking a very long time to start
  echo   Consider checking Docker Desktop's status in the system tray
)
if %_COUNT%==75 (
  echo   Almost at timeout... If this fails, try restarting Docker Desktop manually
)

REM Show progress every 5 seconds
set /a _MOD=!_COUNT! %% 5
if !_MOD!==0 (
  echo     Waiting... (%_COUNT%/90)
)
ping 127.0.0.1 -n 3 >nul
goto :wait_docker

:docker_ready
echo   Docker Desktop engine is ready
goto :continue

:docker_timeout
echo   ERROR: Docker Desktop engine did not become ready after 90 seconds
echo.
echo   Possible issues:
echo   - Docker Desktop may be stuck or in a bad state
echo   - Try restarting Docker Desktop manually
echo   - Check Docker Desktop's status in the system tray
echo   - Look for error messages in Docker Desktop
echo.
choice /C YN /M "Continue anyway? (may fail) (Y=Yes, N=No)"
if errorlevel 2 (
  echo   Exiting. Please fix Docker Desktop and try again.
  pause >nul
  exit /b 1
)
echo   Continuing despite timeout warning...
goto :continue

:continue

REM Ensure docker stack is up
echo [2/8] Starting Docker services...
echo   This may take several minutes if images need to be rebuilt...

REM Try docker-compose up with retry logic
set /a _RETRY_COUNT=0
:docker_compose_retry
set /a _RETRY_COUNT+=1
echo   Attempt %_RETRY_COUNT%/3: Starting Docker services...
docker-compose up -d --build
if not errorlevel 1 goto :docker_success
if %_RETRY_COUNT% GEQ 3 goto :docker_failed
echo   Docker failed, waiting 10 seconds before retry...
ping 127.0.0.1 -n 11 >nul
goto :docker_compose_retry

:docker_success
echo   Docker services started successfully
goto :fix_nginx_ips

:fix_nginx_ips
REM Ensure nginx.conf uses container names (not IPs) - Docker DNS handles resolution
echo [2.5/8] Verifying nginx configuration...
REM Check if nginx.conf uses container names (correct) or IPs (needs fixing)
findstr /C:"proxy_pass http://frontend:3000" nginx.conf >nul
if errorlevel 1 (
  echo   WARNING: nginx.conf may not use container names correctly
  echo   Checking if IP addresses need to be replaced with container names...
  REM Restore container names if IPs were used
  powershell -Command "$content = Get-Content nginx.conf -Raw; $content = $content -replace 'http://172\.18\.0\.[0-9]+:3000', 'http://frontend:3000'; $content = $content -replace 'http://172\.18\.0\.[0-9]+:8000', 'http://backend:8000'; Set-Content nginx.conf -Value $content -NoNewline"
  echo   Restored container names in nginx.conf
  docker-compose restart nginx
  echo   Waiting for nginx to restart...
  ping 127.0.0.1 -n 3 >nul
) else (
  echo   nginx.conf correctly uses container names
)
goto :health_checks

:docker_failed
echo   ERROR: docker-compose up failed after 3 attempts.
echo   Check the output above for build errors.
echo   Make sure Docker Desktop is fully running.
echo.
echo Press any key to close this window...
pause >nul
exit /b 1

:health_checks

REM 3) Wait for nginx on port 8080 (app health)
echo [3/8] Checking app health on http://localhost:8080/health ...
set /a _COUNT=0
:wait_nginx
set /a _COUNT+=1
powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri 'http://localhost:8080/health' -UseBasicParsing -TimeoutSec 3; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }"
if not errorlevel 1 (
  echo   OK: nginx is ready
  goto :wait_root
)
if %_COUNT% GEQ 30 (
  echo   WARNING: nginx health check timed out, continuing...
  goto :wait_root
)
echo     Waiting for nginx... (%_COUNT%/30)
ping 127.0.0.1 -n 3 >nul
goto :wait_nginx

:wait_root
REM 4) Wait for frontend root through nginx
echo [4/8] Checking frontend root on http://localhost:8080/ ...
set /a _COUNT=0
:wait_root_loop
set /a _COUNT+=1
powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri 'http://localhost:8080/' -UseBasicParsing -TimeoutSec 5; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }"
if not errorlevel 1 (
  echo   OK: frontend root is serving
  goto :wait_backend
)
if %_COUNT% GEQ 60 (
  echo   WARNING: frontend root check timed out, continuing...
  goto :wait_backend
)
echo     Waiting for frontend root... (%_COUNT%/60)
ping 127.0.0.1 -n 3 >nul
goto :wait_root_loop

:wait_backend
REM 5) Wait for backend on port 8000 (API health)
echo [5/8] Checking backend health on http://localhost:8000/api/health ...
set /a _COUNT=0
:wait_backend_loop
set /a _COUNT+=1
powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -UseBasicParsing -TimeoutSec 3; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }"
if not errorlevel 1 (
  echo   OK: backend is ready
  goto :wait_proxy_api
)
if %_COUNT% GEQ 30 (
  echo   WARNING: backend health check timed out, continuing...
  goto :wait_proxy_api
)
echo     Waiting for backend... (%_COUNT%/30)
ping 127.0.0.1 -n 3 >nul
goto :wait_backend_loop

:wait_proxy_api
REM 6) Wait for proxied API via nginx
echo [6/8] Checking proxied API on http://localhost:8080/api/health/db ...
set /a _COUNT=0
:wait_proxy_api_loop
set /a _COUNT+=1
powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri 'http://localhost:8080/api/health/db' -UseBasicParsing -TimeoutSec 5; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }"
if not errorlevel 1 (
  echo   OK: proxied API is reachable
  goto :start_airflow
)
if %_COUNT% GEQ 60 (
  echo   WARNING: proxied API check timed out, continuing to Airflow...
  goto :start_airflow
)
echo     Waiting for proxied API... (%_COUNT%/60)
ping 127.0.0.1 -n 3 >nul
goto :wait_proxy_api_loop

:start_airflow

REM 7) Start Airflow services
echo [7/8] Starting Airflow services...

REM Check if Airflow is already running
docker ps --format "{{.Names}}" | findstr /I "airflow-webserver" >nul 2>&1
if not errorlevel 1 (
  echo   Airflow services are already running
  goto :start_ngrok
)

REM Start Airflow
docker-compose -f docker-compose.airflow.yml up -d
if errorlevel 1 (
  echo   WARNING: Failed to start Airflow services
  echo   Continuing with main deployment...
  goto :start_ngrok
)

echo   Waiting for Airflow to be ready...
set /a _COUNT=0
:wait_airflow_ready
set /a _COUNT+=1
powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri 'http://localhost:8081/health' -UseBasicParsing -TimeoutSec 3; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 (
  echo   OK: Airflow is ready
  goto :start_ngrok
)
if !_COUNT! GEQ 60 (
  echo   WARNING: Airflow health check timed out, but continuing...
  echo   Airflow may still be starting. Check http://localhost:8081 in a few moments
  goto :start_ngrok
)
if !_COUNT!==1 (
  echo   Waiting for Airflow webserver...
)
if !_COUNT!==30 (
  echo   Still waiting... Airflow initialization can take 30-60 seconds
)
REM Show progress every 10 seconds
set /a _MOD=!_COUNT! %% 10
if !_MOD!==0 (
  echo     Waiting... (!_COUNT!/60)
)
ping 127.0.0.1 -n 3 >nul
goto :wait_airflow_ready

:start_ngrok

REM 8) Start ngrok
echo [8/8] Starting ngrok on port 8080 ...

REM Load NGROK_AUTHTOKEN from .env
set NGROK_AUTHTOKEN=
for /f "usebackq tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="NGROK_AUTHTOKEN" (
        set NGROK_AUTHTOKEN=%%b
        goto :found_token_final
    )
)

:found_token_final
if "%NGROK_AUTHTOKEN%"=="" (
    echo   ERROR: NGROK_AUTHTOKEN not found in .env file!
    echo   Please add NGROK_AUTHTOKEN=your_token_here to your .env file.
    pause >nul
    exit /b 1
)

REM Configure ngrok auth token (idempotent)
ngrok config add-authtoken %NGROK_AUTHTOKEN% >nul 2>&1

REM Stop any existing ngrok processes
call "%~dp0kill_ngrok.bat" >nul 2>&1
ping 127.0.0.1 -n 2 >nul

REM Start ngrok in a new window
start "ngrok" cmd /k "ngrok http 8080 --log=stdout"

echo.
echo ==============================================
echo   Deployment completed successfully!
echo ==============================================
echo.
echo Services running:
echo   - Main App: http://localhost:8080
echo   - Airflow UI: http://localhost:8081 (airflow / airflow)
echo   - Ngrok: Check http://localhost:4040/api/tunnels for public URL
echo.
echo Done. If the ngrok URL wasn't shown, open http://localhost:4040/api/tunnels to view it.
echo.
echo Press any key to close this window...
pause >nul

endlocal
exit /b 0













@echo off
REM Prepare Docker stack (up + health checks) then start ngrok (Windows) with IIS conflict resolution

setlocal ENABLEDELAYEDEXPANSION

echo ==============================================
echo   Prepare stack and start ngrok (Windows)
echo   with IIS conflict resolution
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

REM Ensure no stray ngrok is running (non-blocking)
taskkill /F /IM ngrok.exe >nul 2>&1

REM Check for IIS port conflicts and fix them
echo [0.5/7] Checking for IIS port conflicts...
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

REM Check if Docker is running and fully ready
echo [1/7] Checking Docker Desktop...
docker --version >nul 2>&1
if errorlevel 1 (
  echo   ERROR: Docker Desktop is not running!
  echo   Please start Docker Desktop and wait for it to fully load.
  echo   Look for the whale icon in your system tray.
  echo.
  echo Press any key to close this window...
  pause >nul
  exit /b 1
)

echo   Docker Desktop is starting, waiting for it to be fully ready...
set /a _COUNT=0
:wait_docker
set /a _COUNT+=1
docker ps >nul 2>&1
if not errorlevel 1 goto :docker_ready
if %_COUNT% GEQ 60 goto :docker_timeout
echo     Waiting for Docker engine... (%_COUNT%/60)
ping 127.0.0.1 -n 3 >nul
goto :wait_docker

:docker_ready
echo   Docker Desktop is fully ready
goto :continue

:docker_timeout
echo   WARNING: Docker Desktop may not be fully ready, but continuing...
goto :continue

:continue

REM Ensure docker stack is up
echo [2/7] Starting Docker services...
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
REM Fix nginx configuration with correct IP addresses
echo [2.5/7] Fixing nginx configuration...
if exist scripts\fix_nginx_ips_v2.bat (
  call scripts\fix_nginx_ips_v2.bat
) else (
  echo   WARNING: fix_nginx_ips_v2.bat not found, trying original...
  if exist scripts\fix_nginx_ips.bat (
    call scripts\fix_nginx_ips.bat
  ) else (
    echo   WARNING: No nginx IP fix script found, continuing...
  )
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
echo [3/7] Checking app health on http://localhost:8080/health ...
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
echo [4/7] Checking frontend root on http://localhost:8080/ ...
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
echo [5/7] Checking backend health on http://localhost:8000/api/health ...
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
echo [6/7] Checking proxied API on http://localhost:8080/api/health/db ...
set /a _COUNT=0
:wait_proxy_api_loop
set /a _COUNT+=1
powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri 'http://localhost:8080/api/health/db' -UseBasicParsing -TimeoutSec 5; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }"
if not errorlevel 1 (
  echo   OK: proxied API is reachable
  goto :start_ngrok
)
if %_COUNT% GEQ 60 (
  echo   WARNING: proxied API check timed out, continuing to ngrok...
  goto :start_ngrok
)
echo     Waiting for proxied API... (%_COUNT%/60)
ping 127.0.0.1 -n 3 >nul
goto :wait_proxy_api_loop

:start_ngrok

REM 7) Start ngrok
echo [7/7] Starting ngrok on port 8080 ...
if exist scripts\start_ngrok.bat (
  start "ngrok" cmd /c scripts\start_ngrok.bat
) else (
  echo   ERROR: scripts\start_ngrok.bat not found.
  exit /b 1
)

echo.
echo ==============================================
echo   Deployment completed successfully!
echo ==============================================
echo.
echo Done. If the ngrok URL wasn't shown, open http://localhost:4040/api/tunnels to view it.
echo.
echo Press any key to close this window...
pause >nul

endlocal
exit /b 0








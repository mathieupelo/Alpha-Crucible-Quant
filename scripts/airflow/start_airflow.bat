@echo off
REM Start Airflow services

setlocal ENABLEDELAYEDEXPANSION

REM Change to repository root directory
cd /d "%~dp0\..\.."

REM Verify we're in the right directory
if not exist "docker-compose.airflow.yml" (
  echo ERROR: docker-compose.airflow.yml not found!
  echo Current directory: %CD%
  echo Please run this script from the scripts\airflow directory.
  pause
  exit /b 1
)

echo ==============================================
echo   Starting Airflow Services
echo ==============================================
echo.

REM Check if Docker Desktop is running and start if needed
echo [1/3] Checking Docker Desktop...

REM First, quickly check if Docker engine is already ready (best case)
docker ps >nul 2>&1
if not errorlevel 1 (
  echo   Docker Desktop is running and engine is ready
  goto :start_airflow
)

REM Docker engine is not ready, check if Docker Desktop process is running
tasklist /FI "IMAGENAME eq Docker Desktop.exe" 2>nul | find /I /N "Docker Desktop.exe">nul
if not errorlevel 1 (
  echo   Docker Desktop process is running, but engine is not ready
  echo   Waiting for Docker engine to become ready...
  echo   (This is normal if Docker Desktop is still starting up)
  goto :check_docker_engine_airflow
)

REM Docker Desktop is not running, try to start it
echo   Docker Desktop is not running, attempting to start it...

REM Try common Docker Desktop installation paths
set DOCKER_STARTED=0

if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
  start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
  set DOCKER_STARTED=1
  goto :docker_started_airflow
)

if exist "C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe" (
  start "" "C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe"
  set DOCKER_STARTED=1
  goto :docker_started_airflow
)

powershell -Command "Start-Process 'Docker Desktop'" >nul 2>&1
if not errorlevel 1 (
  set DOCKER_STARTED=1
  goto :docker_started_airflow
)

if %DOCKER_STARTED%==0 (
  echo   ERROR: Could not start Docker Desktop automatically!
  echo   Please start Docker Desktop manually and run this script again.
  pause
  exit /b 1
)

:check_docker_engine_airflow
REM Wait for Docker engine to be ready (without restarting)
set /a _COUNT=0
:wait_docker_airflow
set /a _COUNT+=1
docker ps >nul 2>&1
if not errorlevel 1 goto :start_airflow
if !_COUNT! GEQ 90 (
  echo   ERROR: Docker Desktop engine did not become ready after 90 seconds
  echo   Docker Desktop may be stuck. Consider restarting it manually.
  echo   Note: Your other containers will continue running.
  pause
  exit /b 1
)
if !_COUNT!==1 (
  echo   Waiting for Docker engine to become ready...
)
if !_COUNT!==30 (
  echo   Still waiting... Docker Desktop engine initialization can take 30-60 seconds
)
if !_COUNT!==60 (
  echo   Docker Desktop is taking longer than usual...
  echo   If this continues, Docker Desktop may need attention
)
REM Show progress every 5 seconds
set /a _MOD=!_COUNT! %% 5
if !_MOD!==0 (
  echo     Waiting... (!_COUNT!/90)
)
ping 127.0.0.1 -n 3 >nul
goto :wait_docker_airflow

:docker_started_airflow
echo   Docker Desktop is starting, please wait...
echo   (This may take 30-60 seconds for Docker Desktop to fully initialize)
goto :check_docker_engine_airflow

:start_airflow
echo [2/3] Starting Airflow services...
echo   This may take a few minutes if images need to be built...

docker-compose -f docker-compose.airflow.yml up -d
if errorlevel 1 (
  echo   ERROR: Failed to start Airflow services
  echo   Check the error messages above for details.
  pause
  exit /b 1
)

echo [3/3] Waiting for Airflow to be ready...
echo   This may take 30-60 seconds...

REM Wait for Airflow webserver to be ready
set /a _COUNT=0
:wait_airflow
set /a _COUNT+=1
REM Check root endpoint (more reliable than /health which may require auth)
powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri 'http://localhost:8081/' -UseBasicParsing -TimeoutSec 3; if($r.StatusCode -eq 200 -or $r.StatusCode -eq 302){ exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 (
  echo   Airflow is ready!
  goto :airflow_ready
)
if !_COUNT! GEQ 60 (
  echo   WARNING: Airflow health check timed out, but services may still be starting
  echo   Check http://localhost:8081 in a few moments
  goto :airflow_ready
)
if !_COUNT!==1 (
  echo   Waiting for Airflow webserver...
)
if !_COUNT!==30 (
  echo   Still waiting... Airflow initialization can take 30-60 seconds
)
echo     Waiting... (!_COUNT!/60)
ping 127.0.0.1 -n 3 >nul
goto :wait_airflow

:airflow_ready
echo.
echo ==============================================
echo   Airflow Services Started Successfully!
echo ==============================================
echo.
echo Access Airflow UI at: http://localhost:8081
echo Default credentials: airflow / airflow
echo.
echo To view logs:
echo   docker-compose -f docker-compose.airflow.yml logs -f
echo.
echo To stop Airflow:
echo   docker-compose -f docker-compose.airflow.yml down
echo.

pause


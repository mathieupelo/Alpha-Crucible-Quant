@echo off
REM Prepare and Start Ngrok - Works with both Local and Docker setups
REM This script detects whether services are running locally or in Docker
REM and starts ngrok on the appropriate port

setlocal ENABLEDELAYEDEXPANSION

echo ==============================================
echo   Prepare and Start Ngrok
echo   (Works with Local and Docker setups)
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0..\.."

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found in project root!
    echo Please ensure .env file exists with your configuration.
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Load NGROK_AUTHTOKEN from .env
set NGROK_AUTHTOKEN=
for /f "usebackq tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="NGROK_AUTHTOKEN" (
        set NGROK_AUTHTOKEN=%%b
        goto :found_token
    )
)

:found_token
if "%NGROK_AUTHTOKEN%"=="" (
    echo ERROR: NGROK_AUTHTOKEN not found in .env file!
    echo Please add NGROK_AUTHTOKEN=your_token_here to your .env file.
    pause
    exit /b 1
)

REM Configure ngrok auth token (idempotent)
echo [1/5] Configuring ngrok auth token...
ngrok config add-authtoken %NGROK_AUTHTOKEN% >nul 2>&1

REM Stop any existing ngrok processes
echo [2/5] Stopping any existing ngrok tunnels...
call "%~dp0kill_ngrok.bat" >nul 2>&1
ping 127.0.0.1 -n 2 >nul

REM Detect which setup is running
echo [3/5] Detecting running services...

REM Check if Docker services are running (port 8080 = nginx proxy)
set USE_DOCKER=0
netstat -ano | findstr ":8080 " | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo   Found Docker setup: nginx proxy on port 8080
    set USE_DOCKER=1
    set NGROK_PORT=8080
    goto :check_health
)

REM Check if local services are running
set LOCAL_BACKEND=0
set LOCAL_FRONTEND=0

netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul
if not errorlevel 1 (
    set LOCAL_BACKEND=1
    echo   Found local backend on port 8000
)

netstat -ano | findstr ":3000 " | findstr "LISTENING" >nul
if not errorlevel 1 (
    set LOCAL_FRONTEND=1
    echo   Found local frontend on port 3000
)

REM Determine which port to use for ngrok
if !LOCAL_BACKEND!==1 (
    if !LOCAL_FRONTEND!==1 (
        echo   Found local development setup (frontend + backend)
        echo   Using frontend port 3000 for ngrok (frontend proxies to backend)
        set NGROK_PORT=3000
        set USE_DOCKER=0
        goto :check_health
    ) else (
        echo   Found only local backend on port 8000
        echo   Using backend port 8000 for ngrok
        set NGROK_PORT=8000
        set USE_DOCKER=0
        goto :check_health
    )
) else (
    echo   WARNING: No services detected on ports 3000, 8000, or 8080
    echo   Assuming Docker setup and using port 8080
    set NGROK_PORT=8080
    set USE_DOCKER=1
)

:check_health
echo [4/5] Checking service health...

if !USE_DOCKER!==1 (
    REM Check Docker nginx health
    powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri 'http://localhost:8080/health' -UseBasicParsing -TimeoutSec 5; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
    if errorlevel 1 (
        echo   WARNING: Docker services may not be fully ready
        echo   Attempting to start Docker services...
        docker-compose up -d
        echo   Waiting for services to start...
        set /a _COUNT=0
        :wait_docker_health
        set /a _COUNT+=1
        powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri 'http://localhost:8080/health' -UseBasicParsing -TimeoutSec 3; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
        if not errorlevel 1 (
            echo   Docker services are ready
            goto :start_ngrok
        )
        if !_COUNT! GEQ 30 (
            echo   WARNING: Docker services health check timed out, continuing anyway...
            goto :start_ngrok
        )
        echo     Waiting for Docker services... (!_COUNT!/30)
        ping 127.0.0.1 -n 3 >nul
        goto :wait_docker_health
    ) else (
        echo   Docker services are healthy
    )
) else (
    REM Check local service health
    if !NGROK_PORT!==3000 (
        REM Check frontend
        powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing -TimeoutSec 3; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
        if errorlevel 1 (
            echo   WARNING: Frontend on port 3000 may not be ready
        ) else (
            echo   Frontend is ready
        )
    ) else if !NGROK_PORT!==8000 (
        REM Check backend
        powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -UseBasicParsing -TimeoutSec 3; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
        if errorlevel 1 (
            echo   WARNING: Backend on port 8000 may not be ready
        ) else (
            echo   Backend is ready
        )
    )
)

:start_ngrok
echo [5/5] Starting ngrok on port !NGROK_PORT!...
echo.
echo ==============================================
if !USE_DOCKER!==1 (
    echo   Ngrok will tunnel Docker setup (port 8080)
    echo   Access via: http://localhost:8080
) else (
    echo   Ngrok will tunnel local setup (port !NGROK_PORT!)
    if !NGROK_PORT!==3000 (
        echo   Frontend: http://localhost:3000
        echo   Backend API: http://localhost:8000
    ) else (
        echo   Backend API: http://localhost:8000
    )
)
echo ==============================================
echo.
echo Starting ngrok tunnel...
echo Your public URL will be shown below.
echo.
echo To view the ngrok URL later, visit: http://localhost:4040/api/tunnels
echo To stop ngrok, run: scripts\ngrok\kill_ngrok.bat
echo.
echo Press Ctrl+C to stop ngrok.
echo.

REM Start ngrok
ngrok http !NGROK_PORT! --log=stdout

endlocal
exit /b 0


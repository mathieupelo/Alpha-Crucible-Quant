@echo off
REM Prepare Docker stack (up + health checks) then start ngrok (Windows)

setlocal ENABLEDELAYEDEXPANSION

echo ==============================================
echo   Prepare stack and start ngrok (Windows)
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

REM Ensure no stray ngrok is running (non-blocking)
taskkill /F /IM ngrok.exe >nul 2>&1

REM Ensure docker stack is up
echo [1/4] Starting Docker services...
docker-compose up -d
if errorlevel 1 (
  echo   ERROR: docker-compose up failed.
  exit /b 1
)

REM Function-like label to probe an HTTP endpoint and wait until 200 or timeout
REM Usage: call :wait_http "http://localhost/health" 60
:wait_http
set "_URL=%~1"
set /a _RETRIES=%~2
if "%_RETRIES%"=="" set /a _RETRIES=60
set /a _COUNT=0
echo     Waiting for %_URL% to return 200 ...
:wait_loop
set /a _COUNT+=1
powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri '%_URL%' -UseBasicParsing -TimeoutSec 3; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }"
if not errorlevel 1 goto :wait_ok
if %_COUNT% GEQ %_RETRIES% goto :wait_timeout
timeout /t 2 >nul
goto :wait_loop

:wait_ok
echo       OK: %_URL%
exit /b 0

:wait_timeout
echo       WARNING: Timed out waiting for %_URL%
exit /b 0

REM 2) Wait for nginx on port 80 (app health)
echo [2/4] Checking app health on http://localhost/health ...
call :wait_http "http://localhost/health" 60

REM 3) Wait for backend on port 8000 (API health)
echo [3/4] Checking backend health on http://localhost:8000/health ...
call :wait_http "http://localhost:8000/health" 60

REM 4) Start ngrok
echo [4/4] Starting ngrok on port 80 ...
if exist scripts\start_ngrok.bat (
  start "ngrok" cmd /c scripts\start_ngrok.bat
) else (
  echo   ERROR: scripts\start_ngrok.bat not found.
  exit /b 1
)

echo.
echo Done. If the ngrok URL wasn't shown, open http://localhost:4040/api/tunnels to view it.
endlocal
exit /b 0

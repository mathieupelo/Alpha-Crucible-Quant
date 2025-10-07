@echo off
REM Verify container connectivity after restart
setlocal ENABLEDELAYEDEXPANSION

echo ==============================================
echo   Verifying Container Connectivity
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

echo [1/3] Checking container status...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo [2/3] Testing nginx connectivity...
set /a _COUNT=0
:test_nginx
set /a _COUNT+=1
powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri 'http://localhost:8080/health' -UseBasicParsing -TimeoutSec 3; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }"
if not errorlevel 1 (
  echo   OK: nginx health endpoint responding
  goto :test_frontend
)
if %_COUNT% GEQ 10 (
  echo   WARNING: nginx health check failed after 10 attempts
  goto :test_frontend
)
echo     Waiting for nginx... (%_COUNT%/10)
ping 127.0.0.1 -n 2 >nul
goto :test_nginx

:test_frontend
echo [3/3] Testing frontend and API...
set /a _COUNT=0
:test_endpoints
set /a _COUNT+=1

REM Test frontend
powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri 'http://localhost:8080/' -UseBasicParsing -TimeoutSec 5; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }"
if errorlevel 1 (
  echo   Frontend test failed, attempt %_COUNT%/10
  if %_COUNT% GEQ 10 (
    echo   ERROR: Frontend not responding after 10 attempts
    goto :end
  )
  ping 127.0.0.1 -n 3 >nul
  goto :test_endpoints
)

REM Test API
powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -Uri 'http://localhost:8080/api/health/db' -UseBasicParsing -TimeoutSec 5; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }"
if errorlevel 1 (
  echo   API test failed, attempt %_COUNT%/10
  if %_COUNT% GEQ 10 (
    echo   ERROR: API not responding after 10 attempts
    goto :end
  )
  ping 127.0.0.1 -n 3 >nul
  goto :test_endpoints
)

echo   OK: Both frontend and API are responding correctly
echo.
echo ==============================================
echo   All connectivity tests passed!
echo ==============================================

:end
echo.
echo Press any key to close this window...
pause >nul

endlocal
exit /b 0






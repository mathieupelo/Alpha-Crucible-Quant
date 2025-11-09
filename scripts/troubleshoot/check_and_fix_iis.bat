@echo off
REM Check for IIS conflicts and fix them automatically

echo ==============================================
echo   IIS Conflict Checker and Fixer
echo ==============================================
echo.

echo [1/4] Checking port 80 usage...
netstat -ano | findstr ":80 " | findstr "LISTENING" >nul
if errorlevel 1 (
  echo   Port 80 is free - no conflicts detected
  goto :check_8080
)

echo   Port 80 is in use by another service
echo [2/4] Identifying the service using port 80...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":80 " ^| findstr "LISTENING"') do (
  if not "%%a"=="0" (
    echo   Process ID %%a is using port 80
    for /f "tokens=1" %%b in ('tasklist /FI "PID eq %%a" /FO CSV /NH') do (
      set "PROCESS_NAME=%%b"
      set "PROCESS_NAME=!PROCESS_NAME:"=!"
      echo   Process name: !PROCESS_NAME!
    )
  )
)

echo [3/4] Stopping IIS services to free port 80...
net stop "World Wide Web Publishing Service" >nul 2>&1
if not errorlevel 1 echo   Stopped World Wide Web Publishing Service
net stop "IIS Admin Service" >nul 2>&1
if not errorlevel 1 echo   Stopped IIS Admin Service
net stop "HTTP SSL" >nul 2>&1
if not errorlevel 1 echo   Stopped HTTP SSL

REM Wait for services to stop
ping 127.0.0.1 -n 3 >nul

echo [4/4] Verifying port 80 is now free...
netstat -ano | findstr ":80 " | findstr "LISTENING" >nul
if errorlevel 1 (
  echo   SUCCESS: Port 80 is now free
) else (
  echo   WARNING: Port 80 is still in use. Trying to kill the process...
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":80 " ^| findstr "LISTENING"') do (
    if not "%%a"=="0" (
      echo     Killing process %%a
      taskkill /F /PID %%a >nul 2>&1
    )
  )
  ping 127.0.0.1 -n 2 >nul
  echo   Process killed
)

:check_8080
echo.
echo Checking port 8080 usage...
netstat -ano | findstr ":8080 " | findstr "LISTENING" >nul
if errorlevel 1 (
  echo   Port 8080 is free
) else (
  echo   Port 8080 is in use
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080 " ^| findstr "LISTENING"') do (
    if not "%%a"=="0" (
      echo   Process ID %%a is using port 8080
    )
  )
)

echo.
echo ==============================================
echo   IIS Conflict Check Complete
echo ==============================================
echo.
echo You can now run your Docker containers without port conflicts.
echo.
echo Press any key to close this window...
pause >nul

endlocal
exit /b 0













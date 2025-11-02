@echo off
REM Quick script to kill processes using port 3000
REM Useful when you need to free the port manually
REM This is the MOST AGGRESSIVE method - kills everything on port 3000

echo ==============================================
echo   Killing ALL processes on port 3000
echo ==============================================
echo.

echo [1/3] Checking port 3000...
powershell -Command "$conns = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue; if ($conns) { Write-Host \"Found processes using port 3000:\"; $conns | ForEach-Object { Write-Host \"  PID: $($_.OwningProcess)\" }; exit 1 } else { Write-Host \"Port 3000 appears to be free.\"; exit 0 }"
set PORT_IN_USE=%ERRORLEVEL%

if %PORT_IN_USE% == 0 (
    echo Port 3000 is not in use (or only has time-wait connections).
    echo.
) else (
    echo.
    echo [2/3] Killing processes using port 3000...
    REM Use PowerShell for reliable process killing
    REM Note: Using $procId instead of $pid because $pid is read-only in PowerShell
    powershell -Command "$conns = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue; if ($conns) { $conns | ForEach-Object { $procId = $_.OwningProcess; Write-Host \"  Killing PID $procId...\"; Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue } }"
    
    REM Also kill via netstat (fallback)
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
        if not "%%a"=="0" (
            echo   Killing PID %%a (via netstat fallback)...
            taskkill /F /PID %%a >nul 2>&1
        )
    )
    
    REM Kill ALL node.exe processes as extra safety
    echo   Killing all Node.js processes (extra safety)...
    for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq node.exe" /FO LIST 2^>nul ^| findstr "PID:"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    
    timeout /t 2 /nobreak >nul
    echo.
)

echo [3/3] Stopping Docker containers...
docker-compose down >nul 2>&1
docker-compose -f docker-compose.dev.yml down >nul 2>&1
echo   Docker containers stopped.
echo.

echo Final verification...
REM Note: Using $procId instead of $pid because $pid is read-only in PowerShell
powershell -Command "$conn = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue; if ($conn) { $procId = $conn.OwningProcess; Write-Host \"WARNING: Port 3000 is still in use! PID: $procId\"; exit 1 } else { Write-Host \"SUCCESS: Port 3000 is now free!\"; exit 0 }"

if errorlevel 1 (
    echo.
    echo Port 3000 is STILL in use. You may need to:
    echo   1. Restart your computer
    echo   2. Check Windows Firewall
    echo   3. Check if another application is binding to the port
) else (
    echo.
    echo Done! Port 3000 is free and ready to use.
)
echo.
pause


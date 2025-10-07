@echo off
REM Complete cleanup script - removes everything and kills all processes

setlocal ENABLEDELAYEDEXPANSION

echo ==============================================
echo   Complete Cleanup - Alpha Crucible Quant
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

REM 1) Kill all ngrok processes
echo [1/6] Killing all ngrok processes...
taskkill /F /IM ngrok.exe >nul 2>&1
if errorlevel 1 (
  echo   No ngrok processes found
) else (
  echo   Killed ngrok processes
)

REM 2) Kill processes using ports 80, 8000, 4040
echo [2/6] Killing processes using ports 80, 8000, 4040...
for %%p in (80 8000 4040) do (
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%p') do (
    if not "%%a"=="0" (
      taskkill /F /PID %%a >nul 2>&1
    )
  )
)
echo   Port cleanup completed

REM 3) Stop and remove all Docker containers, networks, volumes, images
echo [3/6] Stopping and removing all Docker resources...
docker-compose down --rmi all -v --remove-orphans >nul 2>&1
if errorlevel 1 (
  echo   No Docker Compose services to stop
) else (
  echo   Docker Compose services stopped and removed
)

REM 4) Remove all unused Docker resources
echo [4/6] Cleaning up unused Docker resources...
docker system prune -af >nul 2>&1
if errorlevel 1 (
  echo   Docker system prune failed
) else (
  echo   Docker system cleaned
)

REM 5) Remove Docker volumes (if any remain)
echo [5/6] Removing Docker volumes...
docker volume prune -f >nul 2>&1
if errorlevel 1 (
  echo   No Docker volumes to remove
) else (
  echo   Docker volumes removed
)

REM 6) Remove Docker networks (if any remain)
echo [6/6] Removing Docker networks...
docker network prune -f >nul 2>&1
if errorlevel 1 (
  echo   No Docker networks to remove
) else (
  echo   Docker networks removed
)

echo.
echo ==============================================
echo   Cleanup completed successfully
echo ==============================================
echo.
echo You can now run: scripts\prepare_and_start_ngrok.bat
echo.

endlocal
exit /b 0

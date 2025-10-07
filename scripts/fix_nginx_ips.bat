@echo off
REM Fix nginx configuration with correct IP addresses
setlocal ENABLEDELAYEDEXPANSION

echo ==============================================
echo   Fixing nginx configuration with correct IPs
echo ==============================================
echo.

REM Move to repo root
cd /d "%~dp0.."

echo [1/3] Getting container IP addresses...

REM Get backend IP
for /f "tokens=*" %%i in ('docker network inspect alpha-crucible-quant_alpha-crucible-network --format "{{range .Containers}}{{if eq .Name \"alpha-crucible-backend\"}}{{.IPv4Address}}{{end}}{{end}}"') do set BACKEND_IP=%%i
set BACKEND_IP=!BACKEND_IP:/16=!

REM Get frontend IP  
for /f "tokens=*" %%i in ('docker network inspect alpha-crucible-quant_alpha-crucible-network --format "{{range .Containers}}{{if eq .Name \"alpha-crucible-frontend\"}}{{.IPv4Address}}{{end}}{{end}}"') do set FRONTEND_IP=%%i
set FRONTEND_IP=!FRONTEND_IP:/16=!

echo   Backend IP: !BACKEND_IP!
echo   Frontend IP: !FRONTEND_IP!

echo [2/3] Updating nginx.conf...

REM Update nginx.conf with correct IPs
powershell -Command "(Get-Content nginx.conf) -replace 'http://alpha-crucible-backend:8000/', 'http://!BACKEND_IP!:8000/' | Set-Content nginx.conf"
powershell -Command "(Get-Content nginx.conf) -replace 'http://alpha-crucible-frontend:3000', 'http://!FRONTEND_IP!:3000' | Set-Content nginx.conf"

echo [3/3] Restarting nginx...
docker-compose restart nginx

echo.
echo ==============================================
echo   nginx configuration updated successfully!
echo ==============================================
echo.

endlocal
exit /b 0






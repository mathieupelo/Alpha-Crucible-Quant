@echo off
REM Kill all Ngrok processes and stop active tunnels

REM Stop all Ngrok processes
taskkill /f /im ngrok.exe >nul 2>&1

REM Also try to stop tunnels via ngrok API if ngrok web interface is running
REM Wait a moment for process to fully stop
ping 127.0.0.1 -n 2 >nul

REM Try to stop tunnels via API (if ngrok web interface is accessible)
powershell -NoProfile -Command "try { $tunnels = Invoke-RestMethod -Uri 'http://localhost:4040/api/tunnels' -ErrorAction SilentlyContinue; foreach ($tunnel in $tunnels.tunnels) { Invoke-RestMethod -Uri \"http://localhost:4040/api/tunnels/$($tunnel.name)/stop\" -Method Post -ErrorAction SilentlyContinue } } catch { }" >nul 2>&1

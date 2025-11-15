@echo off
REM Stop active ngrok tunnel via API

echo Stopping active ngrok tunnel...
echo.

REM Kill ngrok processes
taskkill /f /im ngrok.exe >nul 2>&1
ping 127.0.0.1 -n 2 >nul

REM Try to stop tunnels via API
echo Checking for active tunnels via ngrok API...
powershell -NoProfile -Command "try { $tunnels = Invoke-RestMethod -Uri 'http://localhost:4040/api/tunnels' -ErrorAction SilentlyContinue; if ($tunnels.tunnels.Count -gt 0) { Write-Host \"Found $($tunnels.tunnels.Count) active tunnel(s):\"; foreach ($tunnel in $tunnels.tunnels) { Write-Host \"  - $($tunnel.name): $($tunnel.public_url)\"; try { Invoke-RestMethod -Uri \"http://localhost:4040/api/tunnels/$($tunnel.name)/stop\" -Method Post -ErrorAction SilentlyContinue | Out-Null; Write-Host \"    Stopped successfully\" } catch { Write-Host \"    Failed to stop: $_\" } } } else { Write-Host 'No active tunnels found via API' } } catch { Write-Host 'Could not connect to ngrok API (ngrok may not be running)' }"

echo.
echo Done. You can now start ngrok again.
pause


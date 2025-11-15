@echo off
REM Check ngrok status and display tunnel information

echo Checking ngrok status...
echo.

REM Check if ngrok process is running
tasklist | findstr /I "ngrok.exe" >nul
if errorlevel 1 (
    echo ERROR: ngrok.exe is not running!
    echo.
    echo Please start ngrok using:
    echo   scripts\ngrok\start_ngrok.bat
    echo   or
    echo   scripts\ngrok\prepare_and_start_ngrok_final.bat
    pause
    exit /b 1
)

echo ngrok.exe process is running
echo.

REM Check ngrok API for tunnel information
powershell -NoProfile -Command "$ErrorActionPreference = 'SilentlyContinue'; try { $response = Invoke-RestMethod -Uri 'http://localhost:4040/api/tunnels'; if ($response.tunnels.Count -gt 0) { Write-Host 'Active tunnels:'; Write-Host ''; foreach ($tunnel in $response.tunnels) { Write-Host \"  Name: $($tunnel.name)\"; Write-Host \"  Public URL: $($tunnel.public_url)\"; Write-Host \"  Config: $($tunnel.config.addr)\"; Write-Host \"  Status: $($tunnel.status)\"; Write-Host '' } } else { Write-Host 'No active tunnels found' } } catch { Write-Host \"Could not connect to ngrok API: $($_.Exception.Message)\"; Write-Host 'This might mean ngrok is still starting up...' }"

echo.
echo Ngrok web interface: http://localhost:4040
echo.
pause


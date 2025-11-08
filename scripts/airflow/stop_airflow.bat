@echo off
REM Stop Airflow services

REM Change to repository root directory
cd /d "%~dp0\..\.."

echo Stopping Airflow services...
docker-compose -f docker-compose.airflow.yml down

echo.
echo Airflow services stopped!

pause


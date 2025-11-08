@echo off
REM Start Airflow services

REM Change to repository root directory
cd /d "%~dp0\..\.."

echo Starting Airflow services...
docker-compose -f docker-compose.airflow.yml up -d

echo.
echo Airflow services started!
echo.
echo Access Airflow UI at: http://localhost:8081
echo Default credentials: airflow / airflow
echo.
echo To view logs:
echo   docker-compose -f docker-compose.airflow.yml logs -f
echo.
echo To stop Airflow:
echo   docker-compose -f docker-compose.airflow.yml down

pause


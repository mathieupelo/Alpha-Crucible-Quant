@echo off
REM Setup script for Airflow

REM Change to repository root directory
cd /d "%~dp0\..\.."

echo Setting up Airflow...

REM Create necessary directories
if not exist "airflow\logs" mkdir airflow\logs
if not exist "airflow\plugins" mkdir airflow\plugins
if not exist "airflow\repos" mkdir airflow\repos
if not exist "airflow\config" mkdir airflow\config

REM Set Airflow UID (for Linux/Mac compatibility)
set AIRFLOW_UID=50000

REM Initialize Airflow database
echo Initializing Airflow database...
docker-compose -f docker-compose.airflow.yml up airflow-init
if errorlevel 1 (
    echo Error initializing Airflow. Please check the logs.
    pause
    exit /b 1
)

echo.
echo Airflow setup complete!
echo.
echo To start Airflow:
echo   docker-compose -f docker-compose.airflow.yml up -d
echo.
echo Access Airflow UI at: http://localhost:8081
echo Default credentials: airflow / airflow

pause


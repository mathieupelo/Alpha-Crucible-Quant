@echo off
REM Script to push skeleton repos to GitHub
REM This script clones the empty repos, adds skeleton files, and pushes them

echo ========================================
echo Pushing Skeleton Repos to GitHub
echo ========================================
echo.

REM Create temp directory
if exist "temp_repos" (
    echo Cleaning up existing temp_repos directory...
    rmdir /s /q temp_repos
)
mkdir temp_repos

echo.
echo [1/2] Setting up alpha-crucible-data-news...
echo ----------------------------------------
cd temp_repos
git clone https://github.com/mathieupelo/alpha-crucible-data-news.git
if errorlevel 1 (
    echo ERROR: Failed to clone alpha-crucible-data-news
    echo Make sure the repository exists and you have access.
    cd ..
    pause
    exit /b 1
)

cd alpha-crucible-data-news
xcopy /E /I /Y ..\..\repos_skeleton\alpha-crucible-data-news\* .
if errorlevel 1 (
    echo ERROR: Failed to copy skeleton files
    cd ..\..
    pause
    exit /b 1
)

git add .
git commit -m "Initial commit: Add skeleton structure with Dockerfile, requirements.txt, main.py, and README"
git push origin main
if errorlevel 1 (
    echo ERROR: Failed to push alpha-crucible-data-news
    echo Make sure you're authenticated with GitHub.
    cd ..\..
    pause
    exit /b 1
)
echo [OK] alpha-crucible-data-news pushed successfully!
cd ..

echo.
echo [2/2] Setting up alpha-crucible-signals-news...
echo ----------------------------------------
git clone https://github.com/mathieupelo/alpha-crucible-signals-news.git
if errorlevel 1 (
    echo ERROR: Failed to clone alpha-crucible-signals-news
    echo Make sure the repository exists and you have access.
    cd ..
    pause
    exit /b 1
)

cd alpha-crucible-signals-news
xcopy /E /I /Y ..\..\repos_skeleton\alpha-crucible-signals-news\* .
if errorlevel 1 (
    echo ERROR: Failed to copy skeleton files
    cd ..\..
    pause
    exit /b 1
)

git add .
git commit -m "Initial commit: Add skeleton structure with Dockerfile, requirements.txt, main.py, and README"
git push origin main
if errorlevel 1 (
    echo ERROR: Failed to push alpha-crucible-signals-news
    echo Make sure you're authenticated with GitHub.
    cd ..\..
    pause
    exit /b 1
)
echo [OK] alpha-crucible-signals-news pushed successfully!
cd ..

cd ..
echo.
echo ========================================
echo SUCCESS! Both repos have been pushed.
echo ========================================
echo.
echo You can now:
echo 1. Update the DAG configuration in airflow/dags/repo_executor_dag.py
echo 2. Implement your logic in each repository's main.py
echo 3. Test locally or wait for Airflow to execute them
echo.
echo To clean up temp files, delete the temp_repos folder.
echo.

pause


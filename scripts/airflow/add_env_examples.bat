@echo off
REM Add .env.example files to the repos

echo Adding .env.example files to repos...

REM Create .env.example for data-news
(
echo # ORE Database Configuration
echo ORE_DATABASE_URL=postgresql://user:password@host:port/database
echo ORE_DB_HOST=your-ore-db-host
echo ORE_DB_PORT=5432
echo ORE_DB_USER=postgres
echo ORE_DB_PASSWORD=your-password
echo ORE_DB_NAME=ore_database
echo.
echo # News API Configuration (if needed)
echo # NEWS_API_KEY=your-api-key
) > temp_repos\alpha-crucible-data-news\.env.example

cd temp_repos\alpha-crucible-data-news
git add .env.example
git commit -m "Add .env.example template"
git push origin main
cd ..\..

REM Create .env.example for signals-news
(
echo # ORE Database Configuration (for reading data)
echo ORE_DATABASE_URL=postgresql://user:password@host:port/database
echo ORE_DB_HOST=your-ore-db-host
echo ORE_DB_PORT=5432
echo ORE_DB_USER=postgres
echo ORE_DB_PASSWORD=your-password
echo ORE_DB_NAME=ore_database
echo.
echo # Main Database Configuration (for writing signals)
echo DATABASE_URL=postgresql://user:password@host:port/database
echo DB_HOST=your-main-db-host
echo DB_PORT=5432
echo DB_USER=postgres
echo DB_PASSWORD=your-password
echo DB_NAME=postgres
) > temp_repos\alpha-crucible-signals-news\.env.example

cd temp_repos\alpha-crucible-signals-news
git add .env.example
git commit -m "Add .env.example template"
git push origin main
cd ..\..

echo.
echo Done! .env.example files have been added to both repos.

pause


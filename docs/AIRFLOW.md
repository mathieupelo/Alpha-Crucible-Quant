# Airflow Setup and Usage

This guide explains how to set up and use Apache Airflow for scheduling external repository executions and automated backtests.

## Overview

Airflow is used to schedule and execute:
1. **Data Repositories**: Fetch data from APIs (Reddit, YouTube, etc.) and store in ORE database
2. **Signal Repositories**: Calculate signals from ORE data and store in main database
3. **Weekly Backtests**: Automatically run backtests on a schedule

## Prerequisites

- Docker and Docker Compose installed
- Git installed
- `.env` file configured with database credentials (both main and ORE databases)

## Quick Start

### 1. Setup Airflow (One-Time)

```bash
# Windows
scripts\airflow\setup_airflow.bat

# Linux/Mac
mkdir -p airflow/{logs,plugins,repos,config}
export AIRFLOW_UID=50000
docker-compose -f docker-compose.airflow.yml up airflow-init
```

### 2. Start Airflow

```bash
# Windows
scripts\airflow\start_airflow.bat

# Linux/Mac
docker-compose -f docker-compose.airflow.yml up -d
```

### 3. Access Airflow UI

- URL: http://localhost:8080
- Username: `airflow`
- Password: `airflow`

**Note:** Change the default password in production!

## Configuration

### Environment Variables

Ensure your `.env` file includes:

```bash
# Main Database (for signal storage)
DATABASE_URL=postgresql://...
DB_HOST=...
DB_PORT=5432
DB_USER=...
DB_PASSWORD=...
DB_NAME=...

# ORE Database (for alternative data storage)
ORE_DATABASE_URL=postgresql://...
ORE_DB_HOST=...
ORE_DB_PORT=5432
ORE_DB_USER=...
ORE_DB_PASSWORD=...
ORE_DB_NAME=...
```

### Repository Configuration

Edit `airflow/dags/repo_executor_dag.py` to add/modify repositories:

```python
REPOS_CONFIG = [
    {
        'name': 'alpha-crucible-data-reddit',
        'url': 'https://github.com/mathieupelo/alpha-crucible-data-reddit.git',
        'type': 'data',
    },
    {
        'name': 'alpha-crucible-signals-news',
        'url': 'https://github.com/mathieupelo/alpha-crucible-signals-news.git',
        'type': 'signals',
    },
    # Add more repos here
]
```

## How It Works

### DAG Execution Flow

1. **Clone/Update Repos**: Each repository is cloned or updated from GitHub
2. **Build Docker Image**: Docker image is built for each repository
3. **Run Container**: Container runs with environment variables injected
4. **Monitor Execution**: Airflow tracks success/failure via exit codes

### Schedule

- **Repository Execution**: Daily at 2 AM EST (7 AM UTC)
- **Weekly Backtest**: Every Monday at 2 AM EST (configurable)
- **Parallel Execution**: All repos run in parallel (no dependencies)

### Exit Codes

- `0`: Success
- Non-zero: Failure (will be retried once)

## Weekly Backtest Setup

### Configuration

Edit `airflow/dags/weekly_backtest_dag.py`:

```python
BACKTEST_CONFIG = {
    'universe_id': 1,  # Your universe ID
    'signals': ['SENTIMENT'],  # Your signals
    'lookback_days': 252,  # 1 year
    'initial_capital': 10000.0,
    'rebalancing_frequency': 'monthly',
    'max_weight': 0.1,
    'risk_aversion': 0.5,
    'benchmark_ticker': 'SPY',
}
```

### Find Your Universe ID

```bash
# Option 1: Use CLI
python scripts/cli/create_universe.py --interactive

# Option 2: Check API
curl http://localhost:8000/api/universes
```

### Schedule Configuration

Edit `schedule_interval` in `weekly_backtest_dag.py`:

```python
schedule_interval='0 2 * * 1',  # Every Monday at 2 AM EST
```

Common schedules:
- `'0 2 * * 1'` - Every Monday at 2 AM EST
- `'0 2 * * 0'` - Every Sunday at 2 AM EST
- `'0 0 * * 1'` - Every Monday at midnight EST
- `'0 2 1 * *'` - First day of every month at 2 AM EST

### Rebuild Airflow (First Time Only)

Since the Dockerfile includes backtest dependencies, rebuild:

```bash
# Windows
scripts\airflow\stop_airflow.bat
docker-compose -f docker-compose.airflow.yml build
scripts\airflow\start_airflow.bat
```

## Monitoring

### View DAG Runs

1. Open Airflow UI: http://localhost:8080
2. Navigate to "DAGs" tab
3. Find your DAG (`repo_executor` or `weekly-backtest`)
4. Click on the DAG to view runs

### View Logs

1. Click on a task instance
2. Click "Log" button
3. View detailed execution logs

### Check Repository Status

Each repository task shows:
- ✅ Green: Success
- ❌ Red: Failure
- ⏸️ Yellow: Running/Retrying

### View Backtest Results

Backtest results are saved to the database and can be viewed:

**Via API:**
```bash
curl http://localhost:8000/api/backtests
```

**In Frontend:**
Go to the Backtests page in your web application.

## Troubleshooting

### Airflow Won't Start

1. Check Docker is running: `docker ps`
2. Check ports are available: `netstat -an | findstr 8080`
3. View logs: `docker-compose -f docker-compose.airflow.yml logs`

### Repository Execution Fails

1. Check repository exists and is accessible
2. Verify Docker can build the image
3. Check environment variables are set correctly
4. View task logs in Airflow UI

### Database Connection Issues

1. Verify database credentials in `.env`
2. Check network connectivity from Airflow container
3. Ensure databases are accessible (not blocked by firewall)

### DAG Not Appearing

1. Check file is in `airflow/dags/` directory
2. Restart Airflow scheduler: `scripts\airflow\restart_airflow.bat`
3. Check for syntax errors in Airflow logs
4. Verify file name ends with `.py`

### Import Errors

1. Verify `backend/` and `src/` are mounted in docker-compose.airflow.yml
2. Rebuild Airflow image: `docker-compose -f docker-compose.airflow.yml build`
3. Check that all dependencies are in `airflow/Dockerfile`
4. Check Airflow task logs for specific import errors

### Backtest Fails

1. Check Airflow task logs for error details
2. Verify universe has at least 5 tickers
3. Ensure signals exist in database for the date range
4. Check that price data is available for all tickers
5. Verify date range is valid (not in future, start < end)

## Adding New Repositories

1. Create the repository on GitHub
2. Add repository config to `airflow/dags/repo_executor_dag.py`
3. Restart Airflow scheduler: `docker-compose -f docker-compose.airflow.yml restart scheduler`

## Repository Structure

Each repository should have:

- `Dockerfile`: Container definition
- `requirements.txt`: Python dependencies
- `main.py`: Main execution script (must exit with 0 on success)
- `.env.example`: Environment variable template
- `README.md`: Documentation

## Architecture

```
┌─────────────────────────────────────────┐
│         Airflow Scheduler               │
│  (Daily at 2 AM EST)                    │
└───────────────┬─────────────────────────┘
                │
                ├─── Clone/Update Repos
                ├─── Build Docker Images
                └─── Run Containers (Parallel)
                     │
        ┌────────────┴────────────┐
        │                         │
   ┌────▼─────┐            ┌──────▼──────┐
   │ Data     │            │ Signal      │
   │ Repos    │            │ Repos       │
   └────┬─────┘            └──────┬──────┘
        │                         │
        │                         │
   ┌────▼──────────┐      ┌───────▼────────┐
   │ ORE Database │      │ Main Database  │
   │ (Raw Data)    │      │ (Signals)      │
   └───────────────┘      └─────────────────┘
```

## Production Considerations

### Security

- Change default Airflow password
- Use secrets management for database credentials
- Restrict Airflow UI access
- Use private repositories

### Scaling

- Consider using CeleryExecutor for distributed execution
- Use Kubernetes for production deployments
- Monitor resource usage

### Monitoring

- Set up alerts for failed DAG runs
- Monitor database connections
- Track execution times

## Next Steps

1. Create your repositories using the skeleton templates in `repos_skeleton/`
2. Push repositories to GitHub
3. Update `REPOS_CONFIG` in the DAG
4. Test execution manually in Airflow UI
5. Monitor first scheduled run

For more details, see:
- [Deployment Guide](DEPLOYMENT.md) - General deployment
- [Architecture](ARCHITECTURE.md) - System design


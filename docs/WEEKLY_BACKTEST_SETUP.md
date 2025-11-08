# Weekly Backtest Setup Guide

This guide explains how to set up and use the weekly scheduled backtest feature in Airflow.

## Overview

The weekly backtest DAG automatically runs backtests on a specified universe on a schedule (default: every Monday at 2 AM EST). This allows you to:

- Automatically track performance over time
- Generate regular backtest reports
- Monitor strategy performance without manual intervention

## What Was Set Up

### 1. Docker Configuration Updates

**File: `docker-compose.airflow.yml`**
- Added volume mounts for `backend/` and `src/` directories
- Allows Airflow to access the backtest engine and database service

**File: `airflow/Dockerfile`**
- Added required Python dependencies:
  - `mysql-connector-python` (database)
  - `pandas`, `numpy` (data processing)
  - `yfinance` (price data)
  - `cvxopt` (portfolio optimization)
  - `fastapi`, `pydantic` (API dependencies)

### 2. Backtest Utility Function

**File: `airflow/dags/backtest_utils.py`**
- Provides `run_backtest_task()` function for running backtests from Airflow
- Handles:
  - Database connection
  - Universe validation
  - Date range calculation
  - Backtest execution
  - Result logging

### 3. Weekly Backtest DAG

**File: `airflow/dags/weekly_backtest_dag.py`**
- Airflow DAG that runs weekly (configurable)
- Configurable via `BACKTEST_CONFIG` dictionary
- Default schedule: Every Monday at 2 AM EST

## Quick Start

### Step 1: Configure Your Backtest

Edit `airflow/dags/weekly_backtest_dag.py`:

```python
BACKTEST_CONFIG = {
    'universe_id': 1,  # Your universe ID
    'signals': ['SENTIMENT'],  # Your signals
    'lookback_days': 252,  # 1 year
    'initial_capital': 10000.0,
    'rebalancing_frequency': 'monthly',
}
```

### Step 2: Find Your Universe ID

```bash
# Option 1: Use CLI
python scripts/cli/create_universe.py --interactive

# Option 2: Check API
curl http://localhost:8000/api/universes
```

### Step 3: Rebuild Airflow (First Time Only)

Since we updated the Dockerfile, rebuild the Airflow image:

```bash
# Windows
scripts\airflow\stop_airflow.bat
docker-compose -f docker-compose.airflow.yml build
scripts\airflow\start_airflow.bat
```

### Step 4: Verify DAG Appears

1. Go to http://localhost:8081
2. Login (username: `airflow`, password: `airflow`)
3. Look for `weekly-backtest` DAG
4. Unpause it if needed (toggle switch)

### Step 5: Test Run (Optional)

You can trigger a manual run:
1. Click on the DAG
2. Click "Trigger DAG" button
3. Watch the logs to see it run

## Configuration Options

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

### Backtest Parameters

All parameters in `BACKTEST_CONFIG`:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `universe_id` | int | Required | ID of universe to backtest |
| `signals` | List[str] | Required | List of signal names |
| `lookback_days` | int | 252 | Days to look back (if start_date not set) |
| `start_date` | str | None | Start date (YYYY-MM-DD), overrides lookback_days |
| `end_date` | str | None | End date (YYYY-MM-DD), defaults to yesterday |
| `name` | str | None | Custom backtest name (auto-generated if not provided) |
| `initial_capital` | float | 10000.0 | Starting capital |
| `rebalancing_frequency` | str | 'monthly' | 'daily', 'weekly', 'monthly', 'quarterly' |
| `max_weight` | float | 0.1 | Maximum weight per stock (10%) |
| `risk_aversion` | float | 0.5 | Risk aversion parameter |
| `benchmark_ticker` | str | 'SPY' | Benchmark ticker |
| `transaction_costs` | float | 0.001 | Transaction costs (0.1%) |

## Viewing Results

### In Airflow UI

1. Go to http://localhost:8081
2. Click on `weekly-backtest` DAG
3. Click on a run (green = success, red = failed)
4. Click on the task → "Log" to see detailed output

### In Database

Backtest results are saved to `backtest_results` table:

```sql
SELECT * FROM backtest_results 
WHERE name LIKE 'Weekly Backtest%' 
ORDER BY created_at DESC;
```

### Via API

```bash
# Get all backtests
curl http://localhost:8000/api/backtests

# Get specific backtest
curl http://localhost:8000/api/backtests/{backtest_id}
```

### In Frontend

Go to the Backtests page in your web application to see all backtests, including scheduled ones.

## Troubleshooting

### DAG Not Appearing

**Problem**: DAG doesn't show up in Airflow UI

**Solutions**:
- Check file is in `airflow/dags/` directory
- Restart Airflow scheduler: `scripts\airflow\restart_airflow.bat`
- Check for syntax errors in Airflow logs
- Verify file name ends with `.py`

### Import Errors

**Problem**: `ModuleNotFoundError` or import errors

**Solutions**:
- Verify `backend/` and `src/` are mounted in docker-compose.airflow.yml
- Rebuild Airflow image: `docker-compose -f docker-compose.airflow.yml build`
- Check that all dependencies are in `airflow/Dockerfile`
- Check Airflow task logs for specific import errors

### Database Connection Errors

**Problem**: Cannot connect to database

**Solutions**:
- Verify `.env` file has correct database credentials
- Check database is running and accessible
- Verify environment variables are passed to Airflow containers
- Test connection from Airflow container: `docker exec -it airflow-scheduler python -c "from services.database_service import DatabaseService; db = DatabaseService(); print(db.ensure_connection())"`

### Backtest Fails

**Problem**: Backtest task fails

**Solutions**:
- Check Airflow task logs for error details
- Verify universe has at least 5 tickers
- Ensure signals exist in database for the date range
- Check that price data is available for all tickers
- Verify date range is valid (not in future, start < end)

### Date Range Issues

**Problem**: No data found for date range

**Solutions**:
- Check signal data exists: `SELECT MIN(date), MAX(date) FROM signal_scores WHERE signal_id = 'SENTIMENT'`
- Adjust `lookback_days` to match available data
- Use explicit `start_date` and `end_date` if needed

## Example Configurations

### Weekly Backtest with 2-Year Lookback

```python
BACKTEST_CONFIG = {
    'universe_id': 1,
    'signals': ['SENTIMENT'],
    'lookback_days': 504,  # 2 years
    'rebalancing_frequency': 'monthly',
}
```

### Daily Backtest with Custom Date Range

```python
BACKTEST_CONFIG = {
    'universe_id': 1,
    'signals': ['SENTIMENT', 'SENTIMENT_YT'],
    'start_date': '2024-01-01',
    'end_date': '2024-12-31',
    'rebalancing_frequency': 'weekly',
    'max_weight': 0.15,  # 15% max per stock
}
```

### Monthly Backtest with Higher Capital

```python
BACKTEST_CONFIG = {
    'universe_id': 1,
    'signals': ['SENTIMENT'],
    'lookback_days': 252,
    'initial_capital': 100000.0,
    'rebalancing_frequency': 'monthly',
    'risk_aversion': 0.7,
    'benchmark_ticker': 'QQQ',
}
```

## Advanced Usage

### Multiple Weekly Backtests

Create multiple DAG files for different universes:

- `weekly_backtest_universe1_dag.py`
- `weekly_backtest_universe2_dag.py`
- etc.

Each with different `BACKTEST_CONFIG` and DAG IDs.

### Conditional Execution

You can add conditions to skip backtest if certain conditions aren't met:

```python
def should_run_backtest(**context):
    # Check if signals are available
    # Check if universe has enough tickers
    # etc.
    return True

backtest_task = PythonOperator(
    task_id='run_weekly_backtest',
    python_callable=run_backtest_task,
    op_kwargs=BACKTEST_CONFIG,
    dag=dag,
)
```

### Email Notifications

Add email on failure:

```python
default_args = {
    'email_on_failure': True,
    'email': ['your-email@example.com'],
}
```

## Next Steps

1. Configure your universe and signals
2. Set your preferred schedule
3. Test with a manual run
4. Monitor results in Airflow UI
5. View backtests in your web application

For more details, see `airflow/dags/WEEKLY_BACKTEST_README.md`.


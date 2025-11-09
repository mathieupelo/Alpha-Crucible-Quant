# Weekly Backtest DAG

This DAG runs a scheduled backtest on a universe every week.

## Setup

### 1. Configure the Backtest

Edit `weekly_backtest_dag.py` and update the `BACKTEST_CONFIG` dictionary:

```python
BACKTEST_CONFIG = {
    'universe_id': 1,  # Your universe ID
    'signals': ['SENTIMENT'],  # List of signals to use
    'lookback_days': 252,  # 1 year lookback (252 trading days)
    'initial_capital': 10000.0,
    'rebalancing_frequency': 'monthly',
    # Add more configuration as needed
}
```

### 2. Find Your Universe ID

You can find your universe ID by:
- Using the CLI: `python scripts/cli/create_universe.py --interactive` (lists universes)
- Checking the database directly
- Using the API: `GET /api/universes`

### 3. Configure Schedule

The default schedule is every Monday at 2 AM EST. To change it, modify the `schedule_interval` in the DAG:

```python
schedule_interval='0 2 * * 1',  # Every Monday at 2 AM EST
```

Common schedule examples:
- `'0 2 * * 1'` - Every Monday at 2 AM EST
- `'0 2 * * 0'` - Every Sunday at 2 AM EST  
- `'0 0 * * 1'` - Every Monday at midnight EST
- `'0 2 1 * *'` - First day of every month at 2 AM EST
- `'0 2 * * 1,3,5'` - Monday, Wednesday, Friday at 2 AM EST

### 4. Restart Airflow

After making changes, restart Airflow:

```bash
# Windows
scripts\airflow\stop_airflow.bat
scripts\airflow\start_airflow.bat
```

## How It Works

1. **Every week** (or as scheduled), Airflow triggers the DAG
2. The DAG runs `run_backtest_task` which:
   - Connects to the database
   - Fetches the universe and its tickers
   - Calculates the date range (defaults to last `lookback_days` days)
   - Runs the backtest using the BacktestEngine
   - Saves results to the database
   - Logs the results

## Configuration Options

### Required Parameters

- `universe_id`: ID of the universe to backtest
- `signals`: List of signal names (e.g., `['SENTIMENT', 'SENTIMENT_YT']`)

### Optional Parameters

- `lookback_days`: Number of days to look back (default: 252 = 1 year)
- `start_date`: Override start date in 'YYYY-MM-DD' format
- `end_date`: Override end date in 'YYYY-MM-DD' format (defaults to yesterday)
- `name`: Custom name for the backtest (auto-generated if not provided)
- `initial_capital`: Starting capital (default: 10000.0)
- `rebalancing_frequency`: 'daily', 'weekly', 'monthly', or 'quarterly' (default: 'monthly')
- `max_weight`: Maximum weight per stock (default: 0.1 = 10%)
- `risk_aversion`: Risk aversion parameter (default: 0.5)
- `benchmark_ticker`: Benchmark ticker (default: 'SPY')
- `transaction_costs`: Transaction costs as decimal (default: 0.001 = 0.1%)

## Viewing Results

### In Airflow UI

1. Go to http://localhost:8081
2. Find the `weekly-backtest` DAG
3. Click on a run to see logs and results

### In Database

Backtest results are saved to the `backtest_results` table with:
- `backtest_id`: Unique ID for the backtest
- `universe_id`: The universe that was backtested
- `name`: Name of the backtest
- Performance metrics: total_return, sharpe_ratio, max_drawdown, etc.

### Via API

```bash
# Get all backtests
curl http://localhost:8000/api/backtests

# Get specific backtest
curl http://localhost:8000/api/backtests/{backtest_id}
```

## Troubleshooting

### DAG Not Appearing

- Check that the file is in `airflow/dags/` directory
- Restart Airflow scheduler
- Check Airflow logs for import errors

### Import Errors

- Ensure `backend/` and `src/` directories are mounted in docker-compose.airflow.yml
- Check that all dependencies are installed in the Airflow Dockerfile
- Verify Python paths in `backtest_utils.py`

### Database Connection Errors

- Verify database credentials in `.env` file
- Check that database is accessible from Airflow container
- Ensure database service is running

### Backtest Fails

- Check Airflow task logs for detailed error messages
- Verify universe has at least 5 tickers
- Ensure signals exist in the database for the date range
- Check that price data is available for all tickers

## Example Configuration

```python
BACKTEST_CONFIG = {
    'universe_id': 1,
    'signals': ['SENTIMENT', 'SENTIMENT_YT'],
    'lookback_days': 504,  # 2 years
    'initial_capital': 50000.0,
    'rebalancing_frequency': 'weekly',
    'max_weight': 0.15,  # 15% max per stock
    'risk_aversion': 0.7,
    'benchmark_ticker': 'QQQ',
}
```


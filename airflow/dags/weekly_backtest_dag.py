"""
Airflow DAG for weekly scheduled backtests.

Runs a backtest on a specified universe every week.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from backtest_utils import run_backtest_task

# Backtest configuration
BACKTEST_CONFIG = {
    'universe_id': 1,  # Change this to your universe ID
    'signals': ['SENTIMENT'],  # List of signals to use (e.g., ['SENTIMENT', 'SENTIMENT_YT'])
    'lookback_days': 252,  # 1 year lookback (252 trading days)
    'initial_capital': 10000.0,
    'rebalancing_frequency': 'monthly',  # 'daily', 'weekly', 'monthly', 'quarterly'
    # Optional parameters:
    # 'start_date': '2024-01-01',  # Override start date (YYYY-MM-DD)
    # 'end_date': '2024-12-31',    # Override end date (YYYY-MM-DD)
    # 'max_weight': 0.1,           # Maximum weight per stock (10%)
    # 'risk_aversion': 0.5,         # Risk aversion parameter
    # 'benchmark_ticker': 'SPY',    # Benchmark ticker
}

# Default arguments for the DAG
default_args = {
    'owner': 'alpha-crucible',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

# Create DAG
dag = DAG(
    'weekly-backtest',
    default_args=default_args,
    description='Weekly scheduled backtest on universe',
    schedule_interval='0 2 * * 1',  # Every Monday at 2 AM EST (7 AM UTC)
    # Schedule examples:
    # '0 2 * * 1' - Every Monday at 2 AM EST
    # '0 2 * * 0' - Every Sunday at 2 AM EST
    # '0 0 * * 1' - Every Monday at midnight EST
    # '0 2 1 * *' - First day of every month at 2 AM EST
    start_date=days_ago(1),
    catchup=False,
    tags=['backtest', 'weekly', 'scheduled'],
)

# Create the task
backtest_task = PythonOperator(
    task_id='run_weekly_backtest',
    python_callable=run_backtest_task,
    op_kwargs=BACKTEST_CONFIG,
    dag=dag,
)


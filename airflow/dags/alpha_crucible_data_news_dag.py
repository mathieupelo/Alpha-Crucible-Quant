"""
Airflow DAG for alpha-crucible-data-news repository.

Fetches news data and stores it in ORE database.
Runs daily at 2 AM EST to process yesterday's news.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from repo_utils import execute_repo_task
import os

# Repository configuration
REPO_CONFIG = {
    'name': 'alpha-crucible-data-news',
    'url': 'https://github.com/mathieupelo/alpha-crucible-data-news.git',
    'type': 'data',  # data fetcher -> ORE
}

# Default arguments for the DAG
default_args = {
    'owner': 'alpha-crucible',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'alpha-crucible-data-news',
    default_args=default_args,
    description='Fetch news data and store in ORE database',
    schedule_interval='0 2 * * *',  # Daily at 2 AM EST (7 AM UTC)
    start_date=days_ago(1),
    catchup=False,
    tags=['repos', 'data', 'news'],
)


def execute_news_fetch_task(**context):
    """
    Wrapper function to set date range environment variables before executing the repo.
    Processes yesterday's date (the execution date) for daily runs.
    """
    # Get the data interval start from Airflow context (Airflow 2.x)
    # For daily runs, this represents the date we want to process
    data_interval_start = context.get('data_interval_start')
    execution_date = context.get('execution_date')
    
    target_date = None
    
    if data_interval_start:
        # Airflow 2.x: use data_interval_start
        if isinstance(data_interval_start, datetime):
            target_date = data_interval_start.date()
        elif isinstance(data_interval_start, str):
            # Parse string datetime
            try:
                dt = datetime.fromisoformat(data_interval_start.replace('Z', '+00:00'))
                target_date = dt.date()
            except (ValueError, AttributeError):
                pass
    elif execution_date:
        # Fallback to execution_date (Airflow 1.x compatibility)
        if isinstance(execution_date, datetime):
            target_date = execution_date.date()
        elif isinstance(execution_date, str):
            try:
                dt = datetime.fromisoformat(execution_date.replace('Z', '+00:00'))
                target_date = dt.date()
            except (ValueError, AttributeError):
                pass
    
    if not target_date:
        # Final fallback: use yesterday's date
        target_date = (datetime.now() - timedelta(days=1)).date()
    
    # Set environment variables for date range
    # Process only the target date (yesterday for daily runs)
    date_str = target_date.strftime('%Y-%m-%d')
    os.environ['START_DATE'] = date_str
    os.environ['END_DATE'] = date_str
    
    # Execute the repo task
    return execute_repo_task(repo_config=REPO_CONFIG, **context)


# Create the task
execute_task = PythonOperator(
    task_id='execute_repo',
    python_callable=execute_news_fetch_task,
    dag=dag,
)


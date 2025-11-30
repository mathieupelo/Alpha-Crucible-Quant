"""
Airflow DAG for sentiment-reddit repository.

Fetches Reddit posts for QUEST Core Gaming (QUEST) universe companies (id 491) 
and stores them in ORE database.
Processes the previous 2 days (yesterday and day before yesterday).
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from repo_utils import execute_repo_task
import logging

# Repository configuration
REPO_CONFIG = {
    'name': 'sentiment-reddit',
    'url': 'https://github.com/mathieupelo/sentiment-reddit.git',
    'type': 'data',  # data fetcher -> ORE
    # Set working directory to /app (where code is copied in Dockerfile)
    # This also sets PYTHONPATH=/app automatically to ensure Reddit module can be found
    'workdir': '/app',
    # Command will be set dynamically in execute_quest_reddit_task
    'command': ['python', 'main.py'],
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
    'sentiment-reddit',
    default_args=default_args,
    description='Fetch Reddit posts for QUEST Core Gaming (QUEST) universe (id 491) - previous 2 days',
    schedule_interval='0 2 * * *',  # Daily at 2 AM EST (7 AM UTC)
    start_date=days_ago(1),
    catchup=False,
    tags=['repos', 'data', 'reddit', 'quest'],
)


def execute_quest_reddit_task(**context):
    """
    Wrapper function to calculate previous 2 days and set command arguments.
    Processes yesterday and the day before yesterday for QUEST Core Gaming (QUEST) universe (id 491).
    """
    # Calculate previous 2 days: yesterday and day before yesterday
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    day_before_yesterday = today - timedelta(days=2)
    
    # Start date is day before yesterday, end date is yesterday (2 days total)
    start_date = day_before_yesterday.strftime('%Y-%m-%d')
    end_date = yesterday.strftime('%Y-%m-%d')
    
    # Update the command with date range and universe filter
    # Universe name: "QUEST Core Gaming (QUEST)" with id 491
    repo_config = REPO_CONFIG.copy()
    repo_config['command'] = [
        'python', 'main.py',
        '--start-date', start_date,
        '--end-date', end_date,
        '--universe', 'QUEST Core Gaming'
    ]
    
    logger = logging.getLogger(__name__)
    logger.info(f"Processing QUEST Core Gaming universe (id 491) for date range: {start_date} to {end_date}")
    
    # Execute the repo task with updated config
    return execute_repo_task(repo_config=repo_config, **context)


# Create the task
execute_task = PythonOperator(
    task_id='execute_repo',
    python_callable=execute_quest_reddit_task,
    dag=dag,
)


"""
Airflow DAG for alpha-crucible-signals-news repository.

Fetches data from ORE database, calculates signals, and stores in main database.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from repo_utils import execute_repo_task

# Repository configuration
REPO_CONFIG = {
    'name': 'alpha-crucible-signals-news',
    'url': 'https://github.com/mathieupelo/alpha-crucible-signals-news.git',
    'type': 'signals',  # ORE -> main DB
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
    'alpha-crucible-signals-news',
    default_args=default_args,
    description='Calculate signals from ORE data and store in main database',
    schedule_interval='0 3 * * *',  # Daily at 3 AM EST (8 AM UTC) - runs after data-news
    start_date=days_ago(1),
    catchup=False,
    tags=['repos', 'signals', 'news'],
)

# Create the task
execute_task = PythonOperator(
    task_id='execute_repo',
    python_callable=execute_repo_task,
    op_kwargs={'repo_config': REPO_CONFIG},
    dag=dag,
)


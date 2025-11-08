"""
Airflow DAG for alpha-crucible-data-news repository.

Fetches news data and stores it in ORE database.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from repo_utils import execute_repo_task

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
    schedule_interval='0 2 * * *',  # Daily at 2 AM EST (7 AM UTC) - TODO: Configure per repo
    start_date=days_ago(1),
    catchup=False,
    tags=['repos', 'data', 'news'],
)

# Create the task
execute_task = PythonOperator(
    task_id='execute_repo',
    python_callable=execute_repo_task,
    op_kwargs={'repo_config': REPO_CONFIG},
    dag=dag,
)


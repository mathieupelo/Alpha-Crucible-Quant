"""
Airflow DAG for sentiment-reddit repository.

Fetches Reddit posts for companies and stores them in ORE database.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from repo_utils import execute_repo_task

# Repository configuration
REPO_CONFIG = {
    'name': 'sentiment-reddit',
    'url': 'https://github.com/mathieupelo/sentiment-reddit.git',
    'type': 'data',  # data fetcher -> ORE
    # Set working directory to /app (where code is copied in Dockerfile)
    # This also sets PYTHONPATH=/app automatically to ensure Reddit module can be found
    'workdir': '/app',
    # Custom command to run fetch_company_posts.py with --days 1
    'command': ['python', '-m', 'Reddit.src.database.fetch_company_posts', '--days', '1'],
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
    description='Fetch Reddit posts for companies and store in ORE database',
    schedule_interval='0 23 * * *',  # Daily at 11 PM EST (4 AM UTC next day)
    start_date=days_ago(1),
    catchup=False,
    tags=['repos', 'data', 'reddit'],
)

# Create the task
execute_task = PythonOperator(
    task_id='execute_repo',
    python_callable=execute_repo_task,
    op_kwargs={'repo_config': REPO_CONFIG},
    dag=dag,
)


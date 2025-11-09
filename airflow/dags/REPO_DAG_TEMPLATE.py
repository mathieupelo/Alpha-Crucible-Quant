"""
Template for creating a new repository DAG.

Copy this file and modify it for each new repository.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from repo_utils import execute_repo_task

# Repository configuration
REPO_CONFIG = {
    'name': 'your-repo-name',  # Must match GitHub repo name
    'url': 'https://github.com/mathieupelo/your-repo-name.git',
    'type': 'data',  # 'data' for data fetchers, 'signals' for signal calculators
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
    'your-repo-name',  # DAG ID - should match repo name
    default_args=default_args,
    description='Description of what this repo does',
    schedule_interval='0 2 * * *',  # Cron expression: Daily at 2 AM EST (7 AM UTC)
    # Examples:
    # '0 2 * * *' - Daily at 2 AM EST
    # '0 */6 * * *' - Every 6 hours
    # '0 2 * * 1' - Every Monday at 2 AM EST
    start_date=days_ago(1),
    catchup=False,
    tags=['repos', 'data'],  # Adjust tags as needed
)

# Create the task
execute_task = PythonOperator(
    task_id='execute_repo',
    python_callable=execute_repo_task,
    op_kwargs={'repo_config': REPO_CONFIG},
    dag=dag,
)


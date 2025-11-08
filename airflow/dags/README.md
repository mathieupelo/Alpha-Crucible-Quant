# Airflow DAGs for Repository Execution

This directory contains individual DAG files for each repository that needs to be executed by Airflow.

## Overview

Each repository gets its own independent DAG, allowing you to:
- Set different schedules per repository
- Pause/unpause repositories independently
- Monitor each repository's execution history separately
- Trigger manual runs for specific repositories

## Current Repositories

- **`alpha-crucible-data-news`**: Fetches news data and stores in ORE database
  - Schedule: Daily at 2 AM EST
  - File: `alpha_crucible_data_news_dag.py`

- **`alpha-crucible-signals-news`**: Calculates signals from ORE data and stores in main database
  - Schedule: Daily at 3 AM EST
  - File: `alpha_crucible_signals_news_dag.py`

## Adding More Repositories

To add a new repository DAG, follow these steps:

### Step 1: Copy the Template

Copy `REPO_DAG_TEMPLATE.py` to a new file named `{repo_name}_dag.py`:

```bash
cp airflow/dags/REPO_DAG_TEMPLATE.py airflow/dags/your_repo_name_dag.py
```

**Example:**
```bash
cp airflow/dags/REPO_DAG_TEMPLATE.py airflow/dags/alpha_crucible_data_reddit_dag.py
```

### Step 2: Update the Configuration

Open the new DAG file and update the `REPO_CONFIG` dictionary:

```python
REPO_CONFIG = {
    'name': 'your-repo-name',  # Must match GitHub repo name exactly
    'url': 'https://github.com/mathieupelo/your-repo-name.git',
    'type': 'data',  # 'data' for data fetchers, 'signals' for signal calculators
}
```

**Important**: The `name` field must match your GitHub repository name exactly.

### Step 3: Set Your Desired Schedule

Update the `schedule_interval` in the DAG definition:

```python
dag = DAG(
    'your-repo-name',  # DAG ID - should match repo name
    # ... other config ...
    schedule_interval='0 2 * * *',  # Update this cron expression
    # ...
)
```

#### Schedule Examples

- `'0 2 * * *'` - Daily at 2 AM EST (7 AM UTC)
- `'0 3 * * *'` - Daily at 3 AM EST (8 AM UTC)
- `'0 */6 * * *'` - Every 6 hours
- `'0 2 * * 1'` - Every Monday at 2 AM EST
- `'0 0,12 * * *'` - Twice daily at midnight and noon EST
- `'0 2 1 * *'` - First day of every month at 2 AM EST

**Note**: Airflow uses UTC time. EST is UTC-5, so adjust accordingly:
- 2 AM EST = 7 AM UTC
- 3 AM EST = 8 AM UTC

### Step 4: Update DAG Metadata

Update the DAG name, description, and tags:

```python
dag = DAG(
    'your-repo-name',  # DAG ID - must match repo name
    default_args=default_args,
    description='Brief description of what this repo does',
    schedule_interval='0 2 * * *',
    start_date=days_ago(1),
    catchup=False,
    tags=['repos', 'data', 'your-tag'],  # Add relevant tags
)
```

### Step 5: Verify and Deploy

1. **Save the file** - The DAG file should be saved in `airflow/dags/`
2. **Wait for Airflow to pick it up** - Airflow scans for DAGs every 30-60 seconds
3. **Refresh the Airflow UI** - The new DAG should appear automatically
4. **Verify the DAG** - Check that:
   - DAG name matches your repo name
   - Schedule is correct
   - DAG is not paused (toggle it ON if needed)

## File Structure

```
airflow/dags/
├── README.md                          # This file
├── repo_utils.py                      # Shared utilities (don't modify)
├── REPO_DAG_TEMPLATE.py               # Template for new DAGs
├── alpha_crucible_data_news_dag.py    # Data news repository DAG
└── alpha_crucible_signals_news_dag.py # Signals news repository DAG
```

## DAG Naming Convention

- **DAG ID**: Should match the repository name exactly (e.g., `alpha-crucible-data-news`)
- **File name**: Use snake_case (e.g., `alpha_crucible_data_news_dag.py`)
- **Task ID**: Always `execute_repo` (standardized across all DAGs)

This ensures:
- Easy identification in the Airflow UI
- Consistent naming across the system
- Clear mapping between repos and DAGs

## Troubleshooting

### DAG Not Appearing in UI

1. Check that the file is saved in `airflow/dags/` directory
2. Verify there are no syntax errors (check Airflow logs)
3. Wait 1-2 minutes for Airflow to scan for new DAGs
4. Refresh the Airflow UI page
5. Check scheduler logs: `docker-compose -f docker-compose.airflow.yml logs scheduler`

### DAG Has Errors

1. Check the DAG in Airflow UI - it will show error details
2. Verify Python syntax is correct
3. Ensure `repo_utils.py` is in the same directory
4. Check that repository name matches GitHub exactly
5. Verify the repository URL is correct and accessible

### Repository Execution Fails

1. Check task logs in Airflow UI
2. Verify repository exists on GitHub
3. Ensure Docker can build the repository's Dockerfile
4. Check that environment variables are set in `.env` file
5. Verify database credentials are correct

## Best Practices

1. **Test First**: Create the DAG and trigger a manual run before enabling the schedule
2. **Use Descriptive Tags**: Add relevant tags to make DAGs easier to filter
3. **Set Appropriate Schedules**: Consider dependencies between repos (e.g., signals repos should run after data repos)
4. **Monitor Logs**: Regularly check execution logs to ensure repos are running successfully
5. **Version Control**: Commit DAG files to git so changes are tracked

## Example: Adding a New Data Repository

Here's a complete example for adding `alpha-crucible-data-reddit`:

```python
# File: airflow/dags/alpha_crucible_data_reddit_dag.py

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from repo_utils import execute_repo_task

REPO_CONFIG = {
    'name': 'alpha-crucible-data-reddit',
    'url': 'https://github.com/mathieupelo/alpha-crucible-data-reddit.git',
    'type': 'data',
}

default_args = {
    'owner': 'alpha-crucible',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'alpha-crucible-data-reddit',
    default_args=default_args,
    description='Fetch Reddit data and store in ORE database',
    schedule_interval='0 2 * * *',  # Daily at 2 AM EST
    start_date=days_ago(1),
    catchup=False,
    tags=['repos', 'data', 'reddit'],
)

execute_task = PythonOperator(
    task_id='execute_repo',
    python_callable=execute_repo_task,
    op_kwargs={'repo_config': REPO_CONFIG},
    dag=dag,
)
```

After saving this file, the DAG will appear in Airflow UI within 1-2 minutes.

## Need Help?

- Check the Airflow UI for DAG status and logs
- Review `repo_utils.py` to understand how repositories are executed
- See `REPO_DAG_TEMPLATE.py` for a complete template with comments

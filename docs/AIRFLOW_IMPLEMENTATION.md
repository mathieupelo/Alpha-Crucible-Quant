# Airflow Implementation Summary

This document summarizes the Airflow implementation for scheduling external repository executions.

## What Was Implemented

### 1. Skeleton Repository Structures

Created skeleton structures for two example repositories:

- **`repos_skeleton/alpha-crucible-data-reddit/`**: Data fetcher (Reddit → ORE DB)
- **`repos_skeleton/alpha-crucible-signals-yfinance-news/`**: Signal calculator (ORE DB → Main DB)

Each skeleton includes:
- `Dockerfile`: Container definition
- `requirements.txt`: Python dependencies
- `main.py`: Main execution script (skeleton with exit codes)
- `.env.example`: Environment variable template (note: actual .env files are gitignored)
- `README.md`: Documentation

### 2. Airflow Docker Setup

- **`docker-compose.airflow.yml`**: Separate Docker Compose file for Airflow services
  - PostgreSQL for Airflow metadata
  - Redis (for future scaling)
  - Airflow webserver (UI on port 8080)
  - Airflow scheduler
  - Airflow initialization service

- **`airflow/Dockerfile`**: Custom Airflow image with:
  - Git support
  - Docker CLI (to build/run repo containers)
  - Python packages (psycopg2, docker)

### 3. Airflow DAG

- **`airflow/dags/repo_executor_dag.py`**: Main DAG that:
  - Clones/updates repositories from GitHub
  - Builds Docker images for each repo
  - Runs containers with environment variables
  - Executes repos in parallel
  - Tracks success/failure via exit codes

**Schedule**: Daily at 2 AM EST (7 AM UTC)

### 4. Configuration Files

- **`.env_template`**: Updated with ORE database credentials
- **`airflow/.gitignore`**: Ignores logs and repos directory
- **`airflow/config/airflow.cfg`**: Placeholder config file

### 5. Utility Scripts

- **`scripts/airflow/setup_airflow.bat`**: One-time Airflow setup
- **`scripts/airflow/start_airflow.bat`**: Start Airflow services
- **`scripts/airflow/stop_airflow.bat`**: Stop Airflow services
- **`scripts/setup/create_github_repos.py`**: Script to create GitHub repos (requires token with repo permissions)

### 6. Documentation

- **`docs/AIRFLOW_SETUP.md`**: Comprehensive setup and usage guide
- **`docs/AIRFLOW_IMPLEMENTATION.md`**: This summary document

## Next Steps

### 1. Create GitHub Repositories

**Option A: Manual Creation**
1. Go to GitHub and create:
   - `alpha-crucible-data-reddit`
   - `alpha-crucible-signals-yfinance-news`
2. Clone them locally
3. Copy files from `repos_skeleton/` to each repo
4. Commit and push

**Option B: Use Script (requires token with repo permissions)**
1. Update GitHub token in `scripts/setup/create_github_repos.py` if needed
2. Run: `python scripts/setup/create_github_repos.py`
3. Clone repos and push skeleton files

### 2. Configure Environment

1. Copy `.env_template` to `.env`
2. Fill in ORE database credentials:
   ```bash
   ORE_DATABASE_URL=postgresql://...
   ORE_DB_HOST=...
   ORE_DB_PASSWORD=...
   # etc.
   ```

### 3. Setup Airflow

```bash
# Windows
scripts\airflow\setup_airflow.bat
scripts\airflow\start_airflow.bat

# Linux/Mac
mkdir -p airflow/{logs,plugins,repos,config}
export AIRFLOW_UID=50000
docker-compose -f docker-compose.airflow.yml up airflow-init
docker-compose -f docker-compose.airflow.yml up -d
```

### 4. Access Airflow UI

- URL: http://localhost:8080
- Username: `airflow`
- Password: `airflow` (change in production!)

### 5. Implement Repository Logic

For each skeleton repository:

1. **Data Repos** (`alpha-crucible-data-reddit`):
   - Implement API fetching logic
   - Connect to ORE database
   - Insert raw data

2. **Signal Repos** (`alpha-crucible-signals-yfinance-news`):
   - Connect to ORE database
   - Fetch data
   - Calculate signals
   - Connect to main database
   - Insert signal scores

### 6. Test Execution

1. In Airflow UI, find `repo_executor` DAG
2. Toggle DAG to "On" (unpause)
3. Trigger a manual run or wait for scheduled time
4. Monitor execution in UI

## Architecture

```
┌─────────────────────────────────────────┐
│         Airflow Scheduler               │
│  (Daily at 2 AM EST)                    │
└───────────────┬─────────────────────────┘
                │
                ├─── Clone/Update Repos
                ├─── Build Docker Images
                └─── Run Containers (Parallel)
                     │
        ┌────────────┴────────────┐
        │                         │
   ┌────▼─────┐            ┌──────▼──────┐
   │ Data     │            │ Signal      │
   │ Repos    │            │ Repos       │
   └────┬─────┘            └──────┬──────┘
        │                         │
        │                         │
   ┌────▼──────────┐      ┌───────▼────────┐
   │ ORE Database │      │ Main Database  │
   │ (Raw Data)    │      │ (Signals)      │
   └───────────────┘      └────────────────┘
```

## Repository Configuration

To add more repositories, edit `airflow/dags/repo_executor_dag.py`:

```python
REPOS_CONFIG = [
    {
        'name': 'alpha-crucible-data-reddit',
        'url': 'https://github.com/mathieupelo/alpha-crucible-data-reddit.git',
        'type': 'data',
    },
    {
        'name': 'alpha-crucible-signals-yfinance-news',
        'url': 'https://github.com/mathieupelo/alpha-crucible-signals-yfinance-news.git',
        'type': 'signals',
    },
    # Add more repos here
]
```

## Important Notes

1. **Docker Socket**: Airflow containers mount `/var/run/docker.sock` to access host Docker. This allows building/running repo containers.

2. **Exit Codes**: Repositories must exit with:
   - `0`: Success
   - Non-zero: Failure (will be retried)

3. **Environment Variables**: All database credentials are passed to repo containers via environment variables.

4. **Parallel Execution**: All repos run in parallel (no dependencies). If you need dependencies, modify the DAG.

5. **Windows Docker**: On Windows, Docker socket path might be different. Adjust in `docker-compose.airflow.yml` if needed.

## Troubleshooting

### Port Conflicts
If port 8080 is already in use, change it in `docker-compose.airflow.yml`:
```yaml
ports:
  - "8081:8080"  # Use 8081 instead
```

### Docker Socket Issues
On Windows with WSL2, Docker socket path is typically `/var/run/docker.sock`. On native Windows, it might be different.

### Repository Access
Ensure repositories are accessible (public or with proper credentials configured).

## Future Enhancements

1. **Error Notifications**: Add email/Slack notifications on failures
2. **Dependencies**: Add task dependencies between repos if needed
3. **Retry Logic**: Customize retry behavior per repository
4. **Monitoring**: Add Prometheus/Grafana for metrics
5. **AWS Migration**: Prepare for AWS deployment (ECS, EKS, etc.)


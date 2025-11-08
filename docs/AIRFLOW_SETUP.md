# Airflow Setup Guide

This guide explains how to set up and use Apache Airflow for scheduling external repository executions.

## Overview

Airflow is used to schedule and execute external repositories that:
1. **Fetch data** from APIs (Reddit, YouTube, etc.) and store in ORE database
2. **Calculate signals** from ORE data and store in main database

## Prerequisites

- Docker and Docker Compose installed
- Git installed
- `.env` file configured with database credentials

## Quick Start

### 1. Setup Airflow (One-time)

```bash
# Windows
scripts\airflow\setup_airflow.bat

# Linux/Mac
mkdir -p airflow/{logs,plugins,repos,config}
export AIRFLOW_UID=50000
docker-compose -f docker-compose.airflow.yml up airflow-init
```

### 2. Start Airflow

```bash
# Windows
scripts\airflow\start_airflow.bat

# Linux/Mac
docker-compose -f docker-compose.airflow.yml up -d
```

### 3. Access Airflow UI

- URL: http://localhost:8080
- Username: `airflow`
- Password: `airflow`

**Note:** Change the default password in production!

## Configuration

### Environment Variables

Ensure your `.env` file includes:

```bash
# Main Database (for signal storage)
DATABASE_URL=postgresql://...
DB_HOST=...
DB_PORT=5432
DB_USER=...
DB_PASSWORD=...
DB_NAME=...

# ORE Database (for alternative data storage)
ORE_DATABASE_URL=postgresql://...
ORE_DB_HOST=...
ORE_DB_PORT=5432
ORE_DB_USER=...
ORE_DB_PASSWORD=...
ORE_DB_NAME=...
```

### Repository Configuration

Edit `airflow/dags/repo_executor_dag.py` to add/modify repositories:

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

## How It Works

### DAG Execution Flow

1. **Clone/Update Repos**: Each repository is cloned or updated from GitHub
2. **Build Docker Image**: Docker image is built for each repository
3. **Run Container**: Container runs with environment variables injected
4. **Monitor Execution**: Airflow tracks success/failure via exit codes

### Schedule

- **Frequency**: Daily at 2 AM EST (7 AM UTC)
- **Timezone**: America/New_York (EST)
- **Parallel Execution**: All repos run in parallel (no dependencies)

### Exit Codes

- `0`: Success
- Non-zero: Failure (will be retried once)

## Repository Structure

Each repository should have:

- `Dockerfile`: Container definition
- `requirements.txt`: Python dependencies
- `main.py`: Main execution script (must exit with 0 on success)
- `.env.example`: Environment variable template
- `README.md`: Documentation

## Monitoring

### View DAG Runs

1. Open Airflow UI: http://localhost:8080
2. Navigate to "DAGs" tab
3. Find `repo_executor` DAG
4. Click on the DAG to view runs

### View Logs

1. Click on a task instance
2. Click "Log" button
3. View detailed execution logs

### Check Repository Status

Each repository task shows:
- ✅ Green: Success
- ❌ Red: Failure
- ⏸️ Yellow: Running/Retrying

## Troubleshooting

### Airflow Won't Start

1. Check Docker is running: `docker ps`
2. Check ports are available: `netstat -an | findstr 8080`
3. View logs: `docker-compose -f docker-compose.airflow.yml logs`

### Repository Execution Fails

1. Check repository exists and is accessible
2. Verify Docker can build the image
3. Check environment variables are set correctly
4. View task logs in Airflow UI

### Database Connection Issues

1. Verify database credentials in `.env`
2. Check network connectivity from Airflow container
3. Ensure databases are accessible (not blocked by firewall)

## Adding New Repositories

1. Create the repository on GitHub
2. Add repository config to `airflow/dags/repo_executor_dag.py`
3. Restart Airflow scheduler: `docker-compose -f docker-compose.airflow.yml restart scheduler`

## Production Considerations

### Security

- Change default Airflow password
- Use secrets management for database credentials
- Restrict Airflow UI access
- Use private repositories

### Scaling

- Consider using CeleryExecutor for distributed execution
- Use Kubernetes for production deployments
- Monitor resource usage

### Monitoring

- Set up alerts for failed DAG runs
- Monitor database connections
- Track execution times

## Architecture

```
┌─────────────────┐
│  Airflow        │
│  Scheduler      │
└────────┬────────┘
         │
         ├─── Clone/Update Repos
         ├─── Build Docker Images
         └─── Run Containers
              │
              ├─── Data Repos ──┐
              │                 │
              └─── Signal Repos ─┼──┐
                                │  │
                    ┌───────────┘  │
                    │              │
              ┌─────▼─────┐   ┌────▼────┐
              │ ORE DB    │   │ Main DB │
              │ (Raw Data)│   │(Signals)│
              └───────────┘   └─────────┘
```

## Next Steps

1. Create your repositories using the skeleton templates in `repos_skeleton/`
2. Push repositories to GitHub
3. Update `REPOS_CONFIG` in the DAG
4. Test execution manually in Airflow UI
5. Monitor first scheduled run


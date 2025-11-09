# Repository Skeletons

This directory contains skeleton structures for external repositories that will be executed by Airflow.

## Repositories

### Data Repositories (API → ORE Database)

- **`alpha-crucible-data-reddit`**: Fetches Reddit data and stores in ORE database

### Signal Repositories (ORE Database → Main Database)

- **`alpha-crucible-signals-yfinance-news`**: Fetches data from ORE, calculates signals, stores in main database

## Structure

Each repository skeleton includes:

- `Dockerfile`: Container definition
- `requirements.txt`: Python dependencies
- `main.py`: Main execution script (must exit with 0 on success, non-zero on failure)
- `.env.example`: Environment variable template
- `README.md`: Repository-specific documentation

## Setup Instructions

1. Create the repository on GitHub
2. Clone it locally
3. Copy files from the skeleton directory to the cloned repo
4. Update `.env.example` with actual values (create `.env` file locally)
5. Implement the actual logic in `main.py`
6. Commit and push to GitHub

## Environment Variables

### Data Repositories (need ORE DB only)

- `ORE_DATABASE_URL`
- `ORE_DB_HOST`
- `ORE_DB_PORT`
- `ORE_DB_USER`
- `ORE_DB_PASSWORD`
- `ORE_DB_NAME`

### Signal Repositories (need both ORE and Main DB)

- All ORE variables above, plus:
- `DATABASE_URL`
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

## Exit Codes

- `0`: Success (Airflow will mark task as successful)
- Non-zero: Failure (Airflow will mark task as failed and retry)

## Testing Locally

```bash
# Build Docker image
docker build -t repo-name .

# Run with environment variables
docker run --env-file .env repo-name
```

## Notes

- The `.env.example` files are templates - actual `.env` files should be gitignored
- Each repository should be self-contained and runnable via Docker
- Logging should go to stdout/stderr (Airflow will capture it)


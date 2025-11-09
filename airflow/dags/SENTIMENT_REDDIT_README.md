# Sentiment Reddit DAG

This DAG runs the `sentiment-reddit` repository to fetch Reddit posts for companies and store them in the ORE database.

## Schedule

- **Schedule**: Daily at 11 PM EST (4 AM UTC next day)
- **Cron Expression**: `0 23 * * *`

## What It Does

1. Clones/updates the `sentiment-reddit` repository from GitHub
2. Builds a Docker image from the repository
3. Runs `fetch_company_posts.py` with `--days 1` parameter
4. Fetches Reddit posts for the last 1 day for configured companies
5. Stores posts in the ORE database (`reddit_posts` table)

## Configuration

### Repository Configuration

The DAG is configured in `sentiment_reddit_dag.py`:

```python
REPO_CONFIG = {
    'name': 'sentiment-reddit',
    'url': 'https://github.com/mathieupelo/sentiment-reddit.git',
    'type': 'data',
    'command': ['python', '-m', 'Reddit.src.database.fetch_company_posts', '--days', '1'],
}
```

### Environment Variables Required

The following environment variables must be set in your `.env` file:

- `DATABASE_ORE_URL`: PostgreSQL connection string for ORE database
- `REDDIT_CLIENT_ID`: Reddit API client ID
- `REDDIT_CLIENT_SECRET`: Reddit API client secret
- `REDDIT_USER_AGENT`: Reddit API user agent (format: `your-app-name/1.0 by your-username`)

These are automatically passed to the Docker container when it runs.

## Script Parameters

The script runs with:
- `--days 1`: Fetch posts from the last 1 day
- Default `--per-day-cap`: 200 posts per company per day (default from script)
- Default companies: Uses companies defined in `fetch_company_posts.py` COMPANIES dictionary

## Dockerfile Handling

The repository has `Dockerfile.txt` instead of `Dockerfile`. The build process automatically detects and uses `Dockerfile.txt` if `Dockerfile` doesn't exist.

## Viewing Results

### In Airflow UI

1. Go to http://localhost:8081
2. Find the `sentiment-reddit` DAG
3. Click on a run to see logs and execution details

### In Database

Query the `reddit_posts` table in your ORE database:

```sql
SELECT * FROM reddit_posts 
ORDER BY collected_at DESC 
LIMIT 100;
```

## Troubleshooting

### DAG Not Appearing

- Check that the file is in `airflow/dags/` directory
- Restart Airflow scheduler
- Check for syntax errors in Airflow logs

### Build Failures

- Verify the repository is accessible: https://github.com/mathieupelo/sentiment-reddit
- Check that `Dockerfile.txt` exists in the repo
- Review build logs in Airflow task logs

### Environment Variable Errors

- Verify all Reddit credentials are in `.env` file
- Check that `.env` is loaded by docker-compose
- Restart Airflow after adding environment variables

### Script Execution Errors

- Check Reddit API credentials are valid
- Verify database connection string is correct
- Review script output in Airflow task logs

## Modifying the Schedule

To change the schedule, edit `schedule_interval` in `sentiment_reddit_dag.py`:

```python
schedule_interval='0 23 * * *',  # 11 PM EST daily
```

Common schedules:
- `'0 23 * * *'` - Daily at 11 PM EST
- `'0 22 * * *'` - Daily at 10 PM EST
- `'0 23 * * 1'` - Every Monday at 11 PM EST

## Modifying Script Parameters

To change script parameters, edit the `command` in `REPO_CONFIG`:

```python
'command': ['python', '-m', 'Reddit.src.database.fetch_company_posts', '--days', '7', '--per-day-cap', '100'],
```

Available parameters (from the script):
- `--days N`: Number of days to look back (default: 7)
- `--per-day-cap N`: Maximum posts per company per day (default: 200)
- `--companies company1 company2`: Specific companies to fetch (default: all in COMPANIES dict)
- `--dry-run`: Preview what would be inserted without writing to database


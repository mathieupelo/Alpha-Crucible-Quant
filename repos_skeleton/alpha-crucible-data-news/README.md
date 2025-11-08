# Alpha Crucible Data - News

Fetches news data and stores it in the ORE database.

## Overview

This repository is responsible for:
1. Fetching data from news APIs (yfinance, newsapi, etc.)
2. Transforming and cleaning the data
3. Storing the data in the ORE database

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and fill in your credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python main.py`

## Docker

Build and run with Docker:

```bash
docker build -t alpha-crucible-data-news .
docker run --env-file .env alpha-crucible-data-news
```

## Environment Variables

See `.env.example` for required environment variables.

## Exit Codes

- `0`: Success
- `1`: Failure

## Development

This is a skeleton repository. Implement your news data fetching logic in `main.py`.


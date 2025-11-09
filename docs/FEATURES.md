# Features Documentation

This document covers key features and their implementation details.

## Universe Management

The universe management system allows users to create, manage, and validate universes of tickers for quantitative trading strategies.

### Key Features
- Create and manage universes of tickers
- Add/remove tickers from universes
- Validate ticker symbols using real-time data from yfinance
- User-friendly interface with confirmation dialogs and error handling

### API Endpoints
- `GET /api/universes` - Get all universes
- `POST /api/universes` - Create new universe
- `PUT /api/universes/{id}` - Update universe
- `DELETE /api/universes/{id}` - Delete universe
- `GET /api/universes/{id}/tickers` - Get universe tickers
- `PUT /api/universes/{id}/tickers` - Update all tickers
- `POST /api/tickers/validate` - Validate ticker symbols

### Usage
```bash
# Create universe via API
curl -X POST "http://localhost:8000/api/universes" \
  -H "Content-Type: application/json" \
  -d '{"name": "S&P 500 Tech", "description": "Technology stocks"}'

# Validate tickers
curl -X POST "http://localhost:8000/api/tickers/validate" \
  -H "Content-Type: application/json" \
  -d '["AAPL", "MSFT", "GOOGL"]'
```

For detailed documentation, see the API documentation at `/api/docs`.

## Portfolio Storage

The system stores comprehensive portfolio information including:
- Daily portfolio and benchmark values with returns
- Individual stock weights for each rebalancing date
- Complete backtest performance metrics
- Historical signal calculations and combinations

### Database Tables
- `portfolio_values`: Daily portfolio and benchmark values
- `portfolio_positions`: Individual position weights
- `backtests`: Backtest run configurations
- `backtest_nav`: Daily NAV data for backtests

### API Endpoints
- `GET /api/portfolios/{portfolio_id}` - Get portfolio details
- `GET /api/portfolios/{portfolio_id}/positions` - Get positions
- `GET /api/backtests/{run_id}/portfolios` - Get backtest portfolios
- `GET /api/backtests/{run_id}/nav` - Get NAV data

Portfolio data is automatically stored when running backtests and can be accessed via the API or web interface.

## Forward Fill Signals

When running backtests, there may be dates where signal scores are not available. The forward-fill functionality ensures that the system uses the latest available signal scores from previous dates when current scores are missing.

### Configuration
```python
from src.backtest import BacktestConfig

config = BacktestConfig(
    forward_fill_signals=True  # Enable forward fill (default: True)
)
```

### Benefits
- Ensures continuous portfolio rebalancing even with sparse signal data
- Maintains strategy consistency by using the last known signal values
- Reduces gaps in backtest results due to missing data

The system logs when forward fill is being used, helping track when forward-filled data vs. current data is used.

## Equal Weight Benchmark

The system supports using an equal-weight portfolio of all stocks in the universe as the benchmark for comparison, providing a more direct comparison than a broad market index like SPY.

### Configuration
```python
from src.backtest import BacktestConfig

config = BacktestConfig(
    use_equal_weight_benchmark=True,  # Enable equal-weight benchmark
    benchmark_ticker='SPY'  # Still used for fallback or display
)
```

### Benefits
- Direct comparison against the same universe of stocks
- Eliminates sector bias and market cap bias
- Shows pure alpha from stock selection and timing

The equal-weight benchmark rebalances daily to maintain equal weights (1/N for each stock).

## Dynamic Signal Columns

The Portfolio Details Signal Scores tab dynamically displays the actual signals used for each portfolio, rather than hardcoded columns.

### Features
- Dynamic column generation based on available signals
- Sorted display for consistency
- Proper handling of missing data
- Clear error messages and loading states

The system automatically detects available signals from the database and generates appropriate table columns.

## Rate Limiting

The ticker validation system includes rate limiting improvements to handle Yahoo Finance API limitations.

### Features
- Retry logic with exponential backoff (up to 3 attempts)
- Reduced concurrency (2 tickers per batch)
- Inter-batch delays (2-3 seconds between batches)
- Better error handling for HTTP 429 errors

### Configuration
```python
TickerValidationService(
    timeout=15,      # Request timeout in seconds
    max_retries=3,   # Number of retry attempts
    base_delay=2.0   # Base delay between retries
)
```

## News Feed

The system includes a news feed feature that fetches news articles for tickers in a universe and provides sentiment analysis.

### Setup

1. **Restart Backend Server** (required to load news routes):
   ```bash
   # If using Docker
   docker-compose restart backend
   
   # If running manually
   # Stop and restart the backend server
   ```

2. **Install Optional Dependencies** (for FinBERT sentiment analysis):
   ```bash
   cd backend
   pip install transformers torch
   ```
   Note: The news feed works without these dependencies using keyword-based sentiment analysis.

3. **Verify Route:**
   ```bash
   curl -X GET "http://localhost:8000/api/news/universe/Your-Universe-Name"
   ```

### API Endpoint
- `GET /api/news/universe/{universe_name}` - Get news for universe tickers

### Features
- Fetches news from Yahoo Finance
- Sentiment analysis (keyword-based or FinBERT)
- Displays articles with timestamps and sentiment scores

## Nginx Configuration

The system uses two nginx configuration files:

1. **Root `nginx.conf`**: Reverse proxy for Docker Compose setup
   - Routes `/api/` requests to backend container
   - Routes all other requests to frontend container
   - Provides rate limiting, security headers, and gzip compression

2. **Frontend `frontend/nginx.conf`**: Serves built React app
   - Used when frontend container runs standalone
   - Handles client-side routing with `try_files`
   - Serves static assets with caching

Both configurations are automatically set up and don't require manual changes.

## Additional Resources

For more detailed information:
- [API Documentation](API.md) - Complete API reference
- [Architecture](ARCHITECTURE.md) - System design
- [Usage Guide](USAGE.md) - Usage examples and patterns


# Portfolio Data Storage

This document explains how the portfolio data storage system works in the Alpha Crucible Quant system.

## Overview

The Alpha Crucible Quant system stores comprehensive portfolio information in the database, including:
- **Portfolio Values**: Daily portfolio and benchmark values with returns
- **Portfolio Weights**: Individual stock weights for each rebalancing date
- **Backtest Results**: Complete backtest performance metrics
- **Signal Scores**: Historical signal calculations and combinations
- **Portfolio Configurations**: Portfolio optimization parameters and constraints

## Database Schema

### Portfolio Values Table (`portfolio_values`)

Stores daily portfolio and benchmark values:

| Column | Type | Description |
|--------|------|-------------|
| `portfolio_value_id` | VARCHAR(100) | Unique identifier for each record |
| `backtest_id` | VARCHAR(100) | Links to backtest results |
| `date` | DATE | Date of the portfolio value |
| `portfolio_value` | DECIMAL(15,2) | Total portfolio value |
| `benchmark_value` | DECIMAL(15,2) | Benchmark (SPY) value |
| `portfolio_return` | DECIMAL(10,6) | Daily portfolio return |
| `benchmark_return` | DECIMAL(10,6) | Daily benchmark return |
| `created_at` | TIMESTAMP | Record creation timestamp |

### Portfolio Weights Table (`portfolio_weights`)

Stores individual stock weights for each rebalancing:

| Column | Type | Description |
|--------|------|-------------|
| `portfolio_weight_id` | VARCHAR(100) | Unique identifier for each record |
| `backtest_id` | VARCHAR(100) | Links to backtest results |
| `date` | DATE | Date of the rebalancing |
| `ticker` | VARCHAR(20) | Stock ticker symbol |
| `weight` | DECIMAL(10,6) | Weight of the stock in portfolio |
| `created_at` | TIMESTAMP | Record creation timestamp |

### Backtest Results Table (`backtest_results`)

Stores comprehensive backtest performance metrics:

| Column | Type | Description |
|--------|------|-------------|
| `backtest_id` | VARCHAR(100) | Primary key |
| `start_date` | DATE | Backtest start date |
| `end_date` | DATE | Backtest end date |
| `tickers` | TEXT | Comma-separated list of tickers |
| `signals` | TEXT | Comma-separated list of signals |
| `total_return` | DECIMAL(10,6) | Total return |
| `annualized_return` | DECIMAL(10,6) | Annualized return |
| `sharpe_ratio` | DECIMAL(10,6) | Sharpe ratio |
| `max_drawdown` | DECIMAL(10,6) | Maximum drawdown |
| `volatility` | DECIMAL(10,6) | Volatility |
| `alpha` | DECIMAL(10,6) | Alpha vs benchmark |
| `information_ratio` | DECIMAL(10,6) | Information ratio |
| `execution_time_seconds` | DECIMAL(10,2) | Execution time |
| `created_at` | TIMESTAMP | Record creation timestamp |

### Signal Scores Table (`signal_scores`)

Stores individual signal calculations:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT | Primary key |
| `ticker` | VARCHAR(20) | Stock ticker symbol |
| `signal_id` | VARCHAR(50) | Signal identifier |
| `date` | DATE | Date of calculation |
| `score` | DECIMAL(10,6) | Signal score (-1 to 1) |
| `created_at` | TIMESTAMP | Record creation timestamp |

## Usage

### 1. Setup Database

First, ensure the database schema is up to date:

```bash
python scripts/setup_database.py
```

This will create the new `portfolio_values` and `portfolio_weights` tables.

### 2. Run Backtest

Run a backtest as usual. The system will automatically store portfolio data:

```bash
python scripts/run_backtest.py
```

The backtest will now store:
- Portfolio values for each trading day
- Stock weights for each rebalancing date

### 3. Query Portfolio Data

Use the query script to analyze stored portfolio data:

```bash
python scripts/query_portfolio_data.py
```

This script will:
- Show recent backtest results
- Display portfolio values over time
- Show portfolio weights for each rebalancing
- Create pivot tables for analysis

### 4. Test Storage Functionality

Test the portfolio storage system:

```bash
python tests/test_portfolio_storage.py
```

## API Usage

### REST API Endpoints

The system provides REST API endpoints for accessing portfolio data:

#### Get Portfolio Data
```http
GET /api/portfolios/{portfolio_id}
```

#### Get Portfolio Positions
```http
GET /api/portfolios/{portfolio_id}/positions
```

#### Get Backtest Portfolios
```http
GET /api/backtests/{run_id}/portfolios
```

#### Get Backtest NAV Data
```http
GET /api/backtests/{run_id}/nav?start_date=2024-01-01&end_date=2024-01-31
```

### Python API Client

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api"

# Get portfolio details
portfolio_id = 1
response = requests.get(f"{BASE_URL}/portfolios/{portfolio_id}")
portfolio = response.json()

# Get portfolio positions
response = requests.get(f"{BASE_URL}/portfolios/{portfolio_id}/positions")
positions = response.json()

# Get backtest NAV data
backtest_id = "backtest_123"
response = requests.get(f"{BASE_URL}/backtests/{backtest_id}/nav")
nav_data = response.json()
```

### Database Manager Methods

#### Store Portfolio Data

```python
from database import DatabaseManager, PortfolioValue, PortfolioWeight

db_manager = DatabaseManager()

# Store portfolio values
portfolio_values = [
    PortfolioValue(
        portfolio_value_id="unique_id",
        backtest_id="backtest_123",
        date=date.today(),
        portfolio_value=10000.0,
        benchmark_value=10000.0,
        portfolio_return=0.01,
        benchmark_return=0.005
    )
]
db_manager.store_portfolio_values(portfolio_values)

# Store portfolio weights
portfolio_weights = [
    PortfolioWeight(
        portfolio_weight_id="unique_id",
        backtest_id="backtest_123",
        date=date.today(),
        ticker="AAPL",
        weight=0.3
    )
]
db_manager.store_portfolio_weights(portfolio_weights)
```

#### Query Portfolio Data

```python
# Get portfolio values for a specific backtest
values = db_manager.get_portfolio_values(backtest_id="backtest_123")

# Get portfolio weights for specific tickers
weights = db_manager.get_portfolio_weights(
    backtest_id="backtest_123",
    tickers=["AAPL", "MSFT"]
)

# Get weights as pivot table (date x ticker)
weights_pivot = db_manager.get_portfolio_weights_pivot("backtest_123")
```

## Data Analysis Examples

### Portfolio Performance Analysis

```python
# Get portfolio values
values = db_manager.get_portfolio_values(backtest_id="backtest_123")

# Calculate total returns
first_value = values.iloc[0]['portfolio_value']
last_value = values.iloc[-1]['portfolio_value']
total_return = (last_value / first_value) - 1

print(f"Total Portfolio Return: {total_return:.2%}")
```

### Weight Evolution Analysis

```python
# Get weights pivot table
weights_pivot = db_manager.get_portfolio_weights_pivot("backtest_123")

# Analyze weight changes for a specific ticker
aapl_weights = weights_pivot['AAPL'].dropna()
print(f"AAPL weight range: {aapl_weights.min():.2%} to {aapl_weights.max():.2%}")
```

### Portfolio Concentration Analysis

```python
# Get all weights for a specific date
weights = db_manager.get_portfolio_weights(backtest_id="backtest_123")
latest_date = weights['date'].max()
latest_weights = weights[weights['date'] == latest_date]

# Calculate concentration metrics
top_5_weight = latest_weights.nlargest(5, 'weight')['weight'].sum()
print(f"Top 5 concentration: {top_5_weight:.2%}")
```

## Web Application Integration

### Frontend Components

The web application provides interactive components for portfolio analysis:

#### Portfolio Detail Component
- **Portfolio Overview**: Display portfolio composition and key metrics
- **Position Analysis**: Show individual stock positions and weights
- **Performance Charts**: Visualize portfolio performance over time
- **Risk Metrics**: Display risk analysis and concentration metrics

#### Dashboard Integration
- **Portfolio Summary**: Quick overview of all portfolios
- **Performance Comparison**: Compare different portfolio strategies
- **Historical Analysis**: Track portfolio evolution over time

### Real-time Data Updates

The system supports real-time data updates through the API:
- **Automatic Refresh**: Frontend automatically refreshes data
- **Live Metrics**: Real-time performance calculations
- **Interactive Charts**: Dynamic visualization of portfolio data

## Benefits

1. **Detailed Tracking**: Every portfolio value and weight is stored for analysis
2. **Historical Analysis**: Can analyze portfolio evolution over time
3. **Performance Attribution**: Understand which stocks contributed to performance
4. **Risk Analysis**: Analyze concentration, turnover, and other risk metrics
5. **Backtesting**: Compare different strategies and their portfolio compositions
6. **Web Interface**: Interactive web-based portfolio analysis and visualization
7. **API Access**: Programmatic access to all portfolio data
8. **Real-time Updates**: Live data updates and performance monitoring

## Notes

- Portfolio data is automatically stored when running backtests
- Data is linked to backtest results via `backtest_id`
- Foreign key constraints ensure data integrity
- Indexes are optimized for common query patterns
- Data can be queried efficiently for large datasets

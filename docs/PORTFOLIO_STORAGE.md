# Portfolio Data Storage

This document explains how the portfolio data storage system works in the Quant Project.

## Overview

The system now stores detailed portfolio information in the database, including:
- **Portfolio Values**: Daily portfolio and benchmark values with returns
- **Portfolio Weights**: Individual stock weights for each rebalancing date

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

## Benefits

1. **Detailed Tracking**: Every portfolio value and weight is stored for analysis
2. **Historical Analysis**: Can analyze portfolio evolution over time
3. **Performance Attribution**: Understand which stocks contributed to performance
4. **Risk Analysis**: Analyze concentration, turnover, and other risk metrics
5. **Backtesting**: Compare different strategies and their portfolio compositions

## Notes

- Portfolio data is automatically stored when running backtests
- Data is linked to backtest results via `backtest_id`
- Foreign key constraints ensure data integrity
- Indexes are optimized for common query patterns
- Data can be queried efficiently for large datasets

# Quant Project - Unified Quantitative Investment System

A unified quantitative investment system that combines signal generation, portfolio optimization, and backtesting in a single repository.

## Architecture Overview

This system replaces the previous Signal Forge multi-repository architecture with a simplified, unified approach:

### Key Components

1. **Signal System** (`src/signals/`): Calculate investment signals from alternative data
2. **Portfolio Solver** (`src/solver/`): Optimize portfolio weights using CVXOPT
3. **Backtesting Engine** (`src/backtest/`): Run historical performance analysis
4. **Database Layer** (`src/database/`): Simplified MySQL database for signal scores and results
5. **Utilities** (`src/utils/`): Common utilities and data fetching

### Key Changes from Signal Forge

- **Unified Repository**: All components in one place
- **Local Database**: MySQL hosted on your machine (127.0.0.1:3306)
- **Real-time Prices**: yfinance integration instead of stored stock prices
- **DataFrame Communication**: All database operations use pandas DataFrames
- **No Airflow**: Manual execution with simple scripts
- **Simplified Schema**: Only essential data stored in database

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

3. **Setup Database**:
   ```bash
   python scripts/setup_database.py
   ```
   
   This will create the database schema and automatically seed a default universe named "NA Gaming Starter (5)" with 5 tickers (EA, TTWO, RBLX, MSFT, NVDA) if no universes exist.

4. **Run Tests**:
   ```bash
   pytest tests/
   ```

## Bootstrap Database

If you need to reset the database or ensure the default universe exists, you can run the bootstrap script:

```bash
python scripts/bootstrap_database.py
```

This script will:
- Check if any universes exist in the database
- If no universes exist, create the default "NA Gaming Starter (5)" universe with 5 tickers
- If universes already exist, validate their ticker counts and skip creation
- Provide detailed logging of the process

The script is idempotent and safe to run multiple times.

## Usage

### Calculate Signals
```python
from src.signals import SignalCalculator
from src.database import DatabaseManager

# Calculate signals for a date range
calculator = SignalCalculator()
signals = calculator.calculate_signals(['AAPL', 'MSFT'], '2024-01-01', '2024-12-31')

# Store in database
db = DatabaseManager()
db.store_signal_scores(signals)
```

### Run Backtest
```python
from src.backtest import BacktestEngine

engine = BacktestEngine()
result = engine.run_backtest(
    tickers=['AAPL', 'MSFT', 'GOOGL'],
    signals=['RSI', 'SMA'],
    start_date='2024-01-01',
    end_date='2024-12-31'
)
```

## Database Schema

The simplified database contains only essential tables:

- `signal_scores`: Signal scores by ticker, signal, and date
- `portfolios`: Portfolio configurations and metadata
- `backtest_results`: Backtest performance metrics
- `signal_definitions`: Signal metadata and parameters

## Testing

Comprehensive unit tests cover:
- Signal calculation edge cases
- Database operations
- Portfolio optimization
- Backtesting scenarios
- Error handling for missing data

Run tests with:
```bash
pytest tests/ -v --cov=src
```

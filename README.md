# Alpha-Crucible - Quantitative Investment System

A quantitative investment system focused on portfolio optimization, backtesting, and performance analysis. Signal computation is handled by a separate signals repository.

## Architecture Overview

This system is part of a two-repository architecture:

### Key Components

1. **Signal Reader** (`src/signals/`): Read computed signals from signal_forge.signal_raw
2. **Portfolio Solver** (`src/solver/`): Optimize portfolio weights using CVXOPT
3. **Backtesting Engine** (`src/backtest/`): Run historical performance analysis
4. **Database Layer** (`src/database/`): MySQL database for portfolios, backtests, and results
5. **Web Application** (`frontend/`, `backend/`): User interface and API
6. **Utilities** (`src/utils/`): Common utilities and data fetching

### Repository Separation

- **Alpha-Crucible** (this repo): Portfolio optimization, backtesting, and web application
- **Signals Repository** (separate): Signal computation and data ingestion
- **Integration**: Alpha-crucible reads from `signal_forge.signal_raw` table

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

### Read Signals
```python
from src.signals import SignalReader
from datetime import date, timedelta

# Initialize signal reader
reader = SignalReader()

# Get signals for a date range
end_date = date.today()
start_date = end_date - timedelta(days=30)

signals_df = reader.get_signals(
    tickers=['AAPL', 'MSFT'],
    signal_names=['SENTIMENT_YT'],
    start_date=start_date,
    end_date=end_date
)

# Get pivoted signals for portfolio optimization
pivot_df = reader.get_signal_pivot(
    tickers=['AAPL', 'MSFT'],
    signal_names=['SENTIMENT_YT'],
    start_date=start_date,
    end_date=end_date
)
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

The database contains the following tables:

- `signal_raw`: Raw signal scores (read from signals repository)
- `portfolios`: Portfolio configurations and metadata
- `portfolio_positions`: Individual position weights
- `backtests`: Backtest run configurations
- `backtest_nav`: Daily NAV data for backtests
- `universes`: Ticker universe definitions
- `universe_tickers`: Ticker membership in universes
- `scores_combined`: Combined signal scores

## Integration with Signals Repository

This repository depends on the signals repository for signal data:

1. **Signals Repository** computes signals and writes to `signal_forge.signal_raw`
2. **Alpha-Crucible** reads from `signal_forge.signal_raw` for portfolio optimization
3. **No Direct Signal Computation**: Alpha-crucible does not compute signals directly

## Testing

Comprehensive unit tests cover:
- Signal reading from database
- Portfolio optimization
- Backtesting scenarios
- Database operations
- Error handling for missing data

Run tests with:
```bash
pytest tests/ -v --cov=src
```

# CLI Scripts

Command-line interface scripts for managing universes and running backtests.

## Scripts

### `create_universe.py`

Create a new universe.

**Command-line usage:**
```bash
python scripts/cli/create_universe.py --name "My Universe" --description "Description here"
```

**Interactive usage:**
```bash
python scripts/cli/create_universe.py --interactive
# or
python scripts/cli/create_universe.py -i
```

### `modify_universe.py`

Add tickers to an existing universe. Validates tickers before adding them. Fails if any ticker is invalid.

**Command-line usage:**
```bash
python scripts/cli/modify_universe.py --universe-id 1 --tickers "AAPL,MSFT,GOOGL"
```

**Interactive usage:**
```bash
python scripts/cli/modify_universe.py --interactive
# or
python scripts/cli/modify_universe.py -i
```

### `run_backtest.py`

Run a backtest for a universe.

**Command-line usage:**
```bash
python scripts/cli/run_backtest.py \
  --universe-id 1 \
  --start-date "2024-01-01" \
  --end-date "2024-12-31" \
  --signals "SENTIMENT_YT,SIGNAL_NAME" \
  --name "My Backtest"
```

**Interactive usage:**
```bash
python scripts/cli/run_backtest.py --interactive
# or
python scripts/cli/run_backtest.py -i
```

## Running Tests

Run all tests:
```bash
pytest tests/
```

Run specific test files:
```bash
pytest tests/test_create_universe.py
pytest tests/test_modify_universe.py
pytest tests/test_run_backtest.py
```

Run tests with verbose output:
```bash
pytest tests/ -v
```

Skip slow tests:
```bash
pytest tests/ -m "not slow"
```

## Notes

- All scripts require a database connection
- Test universes are automatically created and cleaned up during tests
- Test universes use the naming pattern `__TEST_UNIVERSE_*__` to avoid conflicts


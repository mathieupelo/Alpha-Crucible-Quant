# Test Scripts

This directory contains **manual test scripts** for debugging and verification purposes.

## Difference from `tests/` Directory

- **`scripts/test/`**: Manual test scripts that can be run standalone for debugging
- **`tests/`**: Proper pytest test suite with fixtures and structured testing

## Manual Test Scripts

### Backtest Tests

- **`test_backtest_execution.py`** - Tests backtest execution and data storage
- **`test_backtest_full_flow.py`** - Tests the complete backtest flow
- **`test_complete_backtest.py`** - Complete end-to-end backtest test

### Integration Tests

- **`test_company_integration.py`** - Tests company-based integration (company_uid resolution, universe companies, signals)
- **`test_varrock_schema.py`** - Tests Varrock schema implementation

## Usage

Run these scripts directly:

```bash
# From repo root
python scripts/test/test_backtest_execution.py
python scripts/test/test_company_integration.py
```

## Other Test Scripts

- **`test_db_connection.bat`** - Windows batch script to test database connection
- **`test_imports.py`** - Tests that all imports work correctly
- **`test_openai_key.py`** - Tests OpenAI API key configuration
- **`verify_connectivity.bat`** - Windows batch script to verify connectivity


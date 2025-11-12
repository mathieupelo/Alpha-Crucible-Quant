# API Tests Documentation

## Overview

This directory contains comprehensive tests for all FastAPI backend endpoints. The tests use a real database connection but clean up all test data after each test to ensure no lasting effects.

## Test Structure

### Files Created

1. **`conftest.py`** - Shared pytest fixtures and configuration
   - `authenticated_client` - Test client with valid API key
   - `unauthenticated_client` - Test client without auth (for testing auth failures)
   - `test_universe` - Fixture that creates a test universe with tickers
   - `mock_yfinance` - Mock for yfinance library
   - `mock_openai` - Mock for OpenAI client
   - `cleanup_test_data` - Auto-cleanup fixture that removes test data after each test

2. **`test_api_universes.py`** - Tests for universe management endpoints
   - Authentication tests
   - CRUD operations (create, read, update, delete)
   - Company management (add, remove, update companies)
   - Ticker validation

3. **`test_api_backtests.py`** - Tests for backtest endpoints
   - Authentication tests
   - Backtest creation, retrieval, deletion
   - Backtest metrics, portfolios, signals, scores
   - Name checking

4. **`test_api_portfolios.py`** - Tests for portfolio endpoints
   - Authentication tests
   - Portfolio retrieval
   - Positions, signals, scores endpoints

5. **`test_api_signals.py`** - Tests for signal endpoints
   - Authentication tests
   - Signal retrieval with various filters
   - Score retrieval
   - Signal types listing

6. **`test_api_nav.py`** - Tests for NAV endpoints
   - Authentication tests
   - NAV data retrieval

7. **`test_api_market.py`** - Tests for market data endpoints
   - Authentication tests
   - Market data retrieval (with mocked yfinance)
   - Live prices
   - Intraday data
   - Normalized data

8. **`test_api_tickers.py`** - Tests for ticker management endpoints
   - Authentication tests
   - Ticker info fetching (with mocked yfinance)
   - Ticker creation

9. **`test_api_news.py`** - Tests for news endpoints
   - Authentication tests
   - News retrieval
   - News analysis with GPT (with mocked OpenAI)

## How Tests Work

### Authentication Testing

All endpoints require API key authentication. Tests verify:
- Unauthenticated requests are rejected (403 Forbidden)
- Invalid API keys are rejected (403 Forbidden)
- Valid API keys work correctly

### Database Cleanup

The `cleanup_test_data` fixture (autouse=True) automatically cleans up after each test:
- Deletes all test universes (names starting with `__TEST_`)
- Deletes all test backtests (names starting with `__TEST_`)
- Handles foreign key constraints by deleting backtests before universes

### Mocking External Services

- **yfinance**: Mocked in market and ticker tests to avoid external API calls
- **OpenAI**: Mocked in news analysis tests to avoid API costs

### Test Data

Tests use tickers that exist in the Varrock schema:
- AAPL, MSFT, CMCSA, DIS, EA (replacing GOOGL, AMZN, TSLA which don't exist)

## Running Tests

```bash
# Run all API tests
pytest tests/test_api/ -v

# Run specific test file
pytest tests/test_api/test_api_universes.py -v

# Run specific test class
pytest tests/test_api/test_api_universes.py::TestUniverseCRUD -v

# Run with coverage
pytest tests/test_api/ --cov=backend --cov-report=html
```

## Test Coverage

The tests cover:
- ✅ All CRUD operations
- ✅ Authentication and authorization
- ✅ Input validation
- ✅ Error handling (404, 400, 500)
- ✅ Edge cases (empty results, pagination)
- ✅ Database cleanup (no lasting effects)

## Notes

- Tests use a real database connection (not mocked)
- All test data is cleaned up automatically
- Tests are designed to be idempotent (can run multiple times)
- External services (yfinance, OpenAI) are mocked for speed and isolation


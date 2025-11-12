"""
Pytest configuration and fixtures for API tests.

Provides common test fixtures for FastAPI endpoint testing.
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))

from main import app
from services.database_service import DatabaseService

# Test API key for authentication
TEST_API_KEY = "test-api-key-123"


@pytest.fixture(scope="session")
def test_api_key():
    """Test API key for authentication."""
    return TEST_API_KEY


@pytest.fixture(scope="session")
def client(test_api_key):
    """Create a test client."""
    # Create test client - authentication will be handled by headers
    test_client = TestClient(app)
    yield test_client


@pytest.fixture
def authenticated_client(test_api_key):
    """Create an authenticated test client."""
    # Mock the API_KEY in main module
    with patch('main.API_KEY', test_api_key):
        test_client = TestClient(app)
        # Set default headers for all requests
        test_client.headers = {
            "Authorization": f"Bearer {test_api_key}",
            "Content-Type": "application/json"
        }
        yield test_client


@pytest.fixture
def unauthenticated_client(test_api_key):
    """Create an unauthenticated test client (for auth testing)."""
    # Use real API_KEY but don't provide auth header
    with patch('main.API_KEY', test_api_key):
        test_client = TestClient(app)
        # Explicitly remove any default headers
        test_client.headers = {}
        yield test_client


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    
    # Cleanup happens after test
    db_service = DatabaseService()
    if db_service.ensure_connection():
        # Clean up test backtests (those with test names) - delete before universes
        try:
            backtests = db_service.get_all_backtests(page=1, size=100)
            if backtests and 'backtests' in backtests:
                for backtest in backtests['backtests']:
                    if backtest.get('name', '').startswith('__TEST_'):
                        try:
                            db_service.delete_backtest(backtest['run_id'])
                        except Exception:
                            pass
        except Exception:
            pass
        
        # Clean up test universes (those starting with __TEST_) - after backtests
        try:
            universes = db_service.get_all_universes()
            for universe in universes:
                if universe['name'].startswith('__TEST_'):
                    try:
                        # Try to delete associated backtests first
                        backtests = db_service.get_all_backtests(page=1, size=100)
                        if backtests and 'backtests' in backtests:
                            for backtest in backtests['backtests']:
                                if backtest.get('universe_id') == universe['id']:
                                    try:
                                        db_service.delete_backtest(backtest['run_id'])
                                    except Exception:
                                        pass
                        db_service.delete_universe(universe['id'])
                    except Exception:
                        pass
        except Exception:
            pass


@pytest.fixture
def test_universe():
    """Create a test universe with tickers for testing."""
    db_service = DatabaseService()
    if not db_service.ensure_connection():
        pytest.skip("Database not available")
    
    # Create test universe
    universe_name = f"__TEST_UNIVERSE_API_{os.getpid()}"
    universe = db_service.create_universe(name=universe_name)
    universe_id = universe['id']
    
    # Add test tickers (use tickers that exist in Varrock schema)
    test_tickers = ['AAPL', 'MSFT', 'CMCSA', 'DIS', 'EA']
    for ticker in test_tickers:
        try:
            db_service.add_universe_company(universe_id, ticker)
        except Exception:
            # If ticker fails, continue with others
            pass
    
    yield universe
    
    # Cleanup
    try:
        db_service.delete_universe(universe_id)
    except Exception:
        pass


@pytest.fixture
def mock_yfinance():
    """Mock yfinance for market data tests."""
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker = MagicMock()
        mock_ticker.info = {
            'currentPrice': 150.0,
            'regularMarketPrice': 150.0,
            'previousClose': 148.0,
            'longName': 'Test Company',
            'shortName': 'TEST',
            'sector': 'Technology',
            'industry': 'Software',
            'marketCap': 1000000000,
            'currency': 'USD',
            'exchange': 'NASDAQ',
            'country': 'United States'
        }
        mock_ticker.history.return_value = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        yield mock_ticker_class


@pytest.fixture
def mock_openai():
    """Mock OpenAI client for news analysis tests."""
    with patch('openai.OpenAI') as mock_openai_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test analysis response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        yield mock_client


"""
Pytest configuration and fixtures for the Quant Project system.

Provides common test fixtures and configuration.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch
import tempfile
import os


@pytest.fixture
def sample_price_data():
    """Create sample price data for testing using real market data."""
    try:
        # Try to get real market data first
        from data import RealTimeDataFetcher
        fetcher = RealTimeDataFetcher()
        
        # Get real data for AAPL
        real_data = fetcher.get_price_history('AAPL', date(2023, 12, 1), date(2024, 1, 31))
        
        if real_data is not None and not real_data.empty:
            return real_data
    except Exception as e:
        print(f"Could not fetch real data: {e}")
    
    # Fallback to mock data if real data is not available
    dates = pd.date_range(start='2023-12-01', end='2024-01-31', freq='D')
    np.random.seed(42)
    
    # Generate realistic price data
    base_price = 100.0
    returns = np.random.randn(len(dates)) * 0.02  # 2% daily volatility
    prices = base_price * np.exp(np.cumsum(returns))
    
    return pd.DataFrame({
        'Open': prices * (1 + np.random.randn(len(dates)) * 0.005),
        'High': prices * (1 + np.abs(np.random.randn(len(dates)) * 0.01)),
        'Low': prices * (1 - np.abs(np.random.randn(len(dates)) * 0.01)),
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates.date)


@pytest.fixture
def sample_tickers():
    """Create sample ticker list."""
    return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']


@pytest.fixture
def sample_signals():
    """Create sample signal list."""
    return ['SENTIMENT']


@pytest.fixture
def sample_date_range():
    """Create sample date range."""
    return date(2024, 1, 1), date(2024, 1, 31)


@pytest.fixture
def sample_signal_scores():
    """Create sample signal scores."""
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    signals = ['SENTIMENT']
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    
    data = []
    for ticker in tickers:
        for signal in signals:
            for date in dates:
                data.append({
                    'ticker': ticker,
                    'signal_id': signal,
                    'date': date.date(),
                    'score': np.random.uniform(-1, 1),
                    'created_at': datetime.now()
                })
    
    return pd.DataFrame(data)


@pytest.fixture
def mock_database_manager():
    """Create mock database manager."""
    mock_db = Mock()
    mock_db.connect.return_value = True
    mock_db.is_connected.return_value = True
    mock_db.execute_query.return_value = pd.DataFrame()
    mock_db.execute_insert.return_value = 1
    mock_db.execute_many.return_value = 1
    return mock_db


@pytest.fixture
def mock_price_fetcher():
    """Create mock price fetcher with real data when possible."""
    try:
        # Try to use real data fetcher
        from data import RealTimeDataFetcher
        fetcher = RealTimeDataFetcher()
        
        # Test if we can get real data
        test_data = fetcher.get_price_history('AAPL', date(2024, 1, 1), date(2024, 1, 5))
        if test_data is not None and not test_data.empty:
            # Use real data fetcher
            return fetcher
    except Exception as e:
        print(f"Could not use real data fetcher: {e}")
    
    # Fallback to mock fetcher
    mock_fetcher = Mock()
    mock_fetcher.get_price.return_value = 100.0
    mock_fetcher.get_prices.return_value = {'AAPL': 100.0, 'MSFT': 200.0}
    mock_fetcher.get_price_history.return_value = pd.DataFrame({
        'Close': [100, 101, 102, 103, 104]
    }, index=pd.date_range('2024-01-01', periods=5, freq='D').date)
    mock_fetcher.get_price_matrix.return_value = pd.DataFrame({
        'AAPL': [100, 101, 102, 103, 104],
        'MSFT': [200, 201, 202, 203, 204]
    }, index=pd.date_range('2024-01-01', periods=5, freq='D').date)
    return mock_fetcher


@pytest.fixture
def temp_database():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def sample_portfolio():
    """Create sample portfolio for testing."""
    from src.solver.models import Portfolio, SolverConfig
    
    portfolio = Portfolio(
        portfolio_id='test-portfolio',
        creation_date=date(2024, 1, 15)
    )
    
    portfolio.add_position('AAPL', 0.1, 0.5)
    portfolio.add_position('MSFT', 0.2, 0.3)
    portfolio.add_position('GOOGL', 0.05, 0.4)
    
    return portfolio


@pytest.fixture
def sample_backtest_result():
    """Create sample backtest result for testing."""
    from src.backtest.models import BacktestResult
    
    result = BacktestResult(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        tickers=['AAPL', 'MSFT', 'GOOGL'],
        signals=['SENTIMENT'],
        total_return=0.15,
        annualized_return=0.12,
        volatility=0.18,
        sharpe_ratio=1.2,
        max_drawdown=-0.08,
        alpha=0.05,
        information_ratio=0.8
    )
    
    # Add mock time series data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)
    returns = pd.Series(np.random.randn(len(dates)) * 0.01, index=dates)
    result.returns = returns
    result.benchmark_returns = returns * 0.8  # Slightly lower returns
    
    return result


@pytest.fixture
def sample_solver_config():
    """Create sample solver configuration."""
    from src.solver.config import SolverConfig
    
    return SolverConfig(
        risk_aversion=0.5,
        max_weight=0.1,
        min_weight=0.0,
        long_only=True,
        transaction_costs=0.001
    )


@pytest.fixture
def sample_backtest_config():
    """Create sample backtest configuration."""
    from src.backtest.config import BacktestConfig
    
    return BacktestConfig(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        initial_capital=10000.0,
        rebalancing_frequency='monthly',
        evaluation_period='monthly',
        transaction_costs=0.001,
        max_weight=0.1,
        risk_aversion=0.5,
        benchmark_ticker='SPY'
    )


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Set environment variables for testing
    os.environ['DB_HOST'] = '127.0.0.1'
    os.environ['DB_PORT'] = '3306'
    os.environ['DB_USER'] = 'test_user'
    os.environ['DB_PASSWORD'] = 'test_password'
    os.environ['DB_NAME'] = 'test_database'
    os.environ['YFINANCE_TIMEOUT'] = '5'
    os.environ['YFINANCE_RETRIES'] = '1'
    
    yield
    
    # Cleanup after each test
    pass


@pytest.fixture
def mock_yfinance():
    """Mock yfinance for testing."""
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame({
            'Close': [100, 101, 102, 103, 104],
            'Open': [99, 100, 101, 102, 103],
            'High': [101, 102, 103, 104, 105],
            'Low': [98, 99, 100, 101, 102],
            'Volume': [1000000] * 5
        }, index=pd.date_range('2024-01-01', periods=5, freq='D'))
        mock_ticker_class.return_value = mock_ticker
        yield mock_ticker_class


@pytest.fixture
def mock_mysql_connector():
    """Mock mysql.connector for testing."""
    with patch('mysql.connector.connect') as mock_connect:
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_conn.cursor.return_value = Mock()
        mock_connect.return_value = mock_conn
        yield mock_connect


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add unit marker to all tests by default
        if not any(marker.name in ['slow', 'integration'] for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)

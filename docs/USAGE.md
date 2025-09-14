# Alpha Crucible Quant Usage Guide

## Quick Start

### 1. Web Application Setup (Recommended)

```bash
# Clone or navigate to the project directory
cd "Alpha-Crucible-Quant"

# Setup environment
cp env.example .env
# Edit .env with your database credentials

# Start all services with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### 2. Development Setup

```bash
# Install Python dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Install Node.js dependencies
cd frontend
npm install
cd ..

# Setup database
python scripts/setup_database.py

# Start backend (in one terminal)
cd backend
python main.py

# Start frontend (in another terminal)
cd frontend
npm run dev
```

### 3. Run Tests

```bash
# Run all tests
python tests/test_runner.py

# Run specific test modules
pytest tests/test_signals.py -v
pytest tests/test_database.py -v
pytest tests/test_utils.py -v
```

### 4. Calculate Signals

```bash
# Calculate signals for a set of tickers
python scripts/calculate_signals.py
```

### 5. Run Backtest

```bash
# Run a complete backtest
python scripts/run_backtest.py
```

## Web Application Usage

### Dashboard Overview
The web application provides an intuitive dashboard for monitoring and analyzing your quantitative strategies:

1. **Performance Metrics**: View key performance indicators at a glance
2. **Backtest History**: Browse and analyze historical backtest results
3. **Interactive Charts**: Explore performance data with interactive visualizations
4. **Portfolio Analysis**: Dive deep into portfolio compositions and allocations

### Using the API
The REST API provides programmatic access to all system functionality:

```python
import requests

# Get all backtests
response = requests.get("http://localhost:8000/api/backtests")
backtests = response.json()

# Get specific backtest details
backtest_id = "your_backtest_id"
response = requests.get(f"http://localhost:8000/api/backtests/{backtest_id}")
backtest = response.json()

# Get backtest NAV data
response = requests.get(f"http://localhost:8000/api/backtests/{backtest_id}/nav")
nav_data = response.json()
```

### API Documentation
Access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Detailed Usage

### Signal Calculation

#### Basic Signal Calculation

```python
from src.signals import SignalCalculator
from src.database import DatabaseManager
from src.utils import PriceFetcher

# Initialize components
price_fetcher = PriceFetcher()
database_manager = DatabaseManager()
calculator = SignalCalculator(database_manager)

# Calculate signals
tickers = ['AAPL', 'MSFT', 'GOOGL']
signals = ['RSI', 'SMA', 'MACD']
start_date = date(2024, 1, 1)
end_date = date(2024, 12, 31)

signal_scores = calculator.calculate_signals(
    tickers=tickers,
    signals=signals,
    start_date=start_date,
    end_date=end_date,
    store_in_db=True
)

print(f"Calculated {len(signal_scores)} signal scores")
```

#### Custom Signal Parameters

```python
from src.signals import RSISignal, SMASignal

# Create custom signal instances
rsi_signal = RSISignal(period=21)  # 21-day RSI
sma_signal = SMASignal(short_period=20, long_period=50)  # 20/50 SMA

# Use in calculator
calculator.registry.register_signal(rsi_signal)
calculator.registry.register_signal(sma_signal)
```

#### Signal Combination

```python
# Combine multiple signals
signal_weights = {
    'RSI': 0.4,
    'SMA': 0.4,
    'MACD': 0.2
}

combined_scores = calculator.combine_signals(signal_scores, signal_weights)
print(combined_scores.head())
```

### Portfolio Optimization

#### Basic Portfolio Optimization

```python
from src.solver import PortfolioSolver, SolverConfig

# Create solver configuration
config = SolverConfig(
    risk_aversion=0.5,
    max_weight=0.1,
    min_weight=0.0,
    long_only=True
)

# Initialize solver
solver = PortfolioSolver(config)

# Optimize portfolio
alpha_scores = {'AAPL': 0.5, 'MSFT': 0.3, 'GOOGL': 0.2}
price_history = price_fetcher.get_price_matrix(['AAPL', 'MSFT', 'GOOGL'], start_date, end_date)
target_date = date(2024, 6, 15)

portfolio = solver.solve_portfolio(alpha_scores, price_history, target_date)

if portfolio:
    print(f"Portfolio created with {len(portfolio.get_active_positions())} positions")
    print("Top positions:")
    for ticker, position in portfolio.get_top_positions(5):
        print(f"  {ticker}: {position.weight:.2%}")
```

#### Advanced Portfolio Configuration

```python
# Advanced solver configuration
config = SolverConfig(
    risk_aversion=0.7,  # Higher risk aversion
    max_weight=0.15,    # Higher max weight
    min_weight=0.01,    # Minimum weight threshold
    long_only=False,    # Allow short selling
    transaction_costs=0.002,  # 0.2% transaction costs
    max_turnover=0.5    # 50% max turnover
)

solver = PortfolioSolver(config)
```

### Backtesting

#### Basic Backtest

```python
from src.backtest import BacktestEngine, BacktestConfig

# Create backtest configuration
config = BacktestConfig(
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    initial_capital=10000.0,
    rebalancing_frequency='monthly',
    transaction_costs=0.001,
    max_weight=0.1,
    risk_aversion=0.5,
    benchmark_ticker='SPY'
)

# Initialize backtest engine
engine = BacktestEngine(price_fetcher, calculator, database_manager)

# Run backtest
result = engine.run_backtest(
    tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
    signals=['RSI', 'SMA', 'MACD'],
    config=config,
    signal_weights={'RSI': 0.4, 'SMA': 0.4, 'MACD': 0.2}
)

# Display results
print("Backtest Results:")
print(f"Total Return: {result.total_return:.2%}")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
print(f"Max Drawdown: {result.max_drawdown:.2%}")
print(f"Alpha: {result.alpha:.2%}")
```

#### Advanced Backtest Configuration

```python
# Advanced backtest configuration
config = BacktestConfig(
    start_date=date(2023, 1, 1),
    end_date=date(2024, 12, 31),
    initial_capital=100000.0,
    rebalancing_frequency='weekly',  # Weekly rebalancing
    evaluation_period='daily',       # Daily evaluation
    transaction_costs=0.002,         # 0.2% transaction costs
    max_weight=0.15,                 # 15% max weight
    min_weight=0.01,                 # 1% min weight
    risk_aversion=0.6,               # Higher risk aversion
    benchmark_ticker='QQQ',          # Different benchmark
    min_lookback_days=252,           # 1 year lookback
    max_lookback_days=756            # 3 years max lookback
)
```

### Database Operations

#### Storing Data

```python
from src.database import DatabaseManager, SignalScore, Portfolio, BacktestResult

# Initialize database manager
db = DatabaseManager()

# Store signal scores
scores = [
    SignalScore('AAPL', 'RSI', date(2024, 1, 15), 0.5),
    SignalScore('MSFT', 'RSI', date(2024, 1, 15), 0.3)
]
db.store_signal_scores(scores)

# Store portfolio
portfolio = Portfolio()
portfolio.add_position('AAPL', 0.1, 0.5)
db.store_portfolio(portfolio)

# Store backtest result
result = BacktestResult(
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    total_return=0.15,
    sharpe_ratio=1.2
)
db.store_backtest_result(result)
```

#### Retrieving Data

```python
# Get signal scores
signal_scores = db.get_signal_scores(
    tickers=['AAPL', 'MSFT'],
    signals=['RSI', 'SMA'],
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31)
)

# Get signal scores as pivot table
pivot_scores = db.get_signal_scores_dataframe(
    tickers=['AAPL', 'MSFT'],
    signals=['RSI', 'SMA'],
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31)
)

# Get portfolios
portfolios = db.get_portfolios(
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31)
)

# Get backtest results
results = db.get_backtest_results(
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31)
)
```

### Price Data Fetching

#### Basic Price Fetching

```python
from src.utils import PriceFetcher

# Initialize price fetcher
fetcher = PriceFetcher()

# Get single price
price = fetcher.get_price('AAPL', date(2024, 1, 15))
print(f"AAPL price on 2024-01-15: ${price}")

# Get multiple prices
prices = fetcher.get_prices(['AAPL', 'MSFT', 'GOOGL'], date(2024, 1, 15))
print(prices)

# Get price history
history = fetcher.get_price_history('AAPL', date(2024, 1, 1), date(2024, 1, 31))
print(history.head())

# Get price matrix
matrix = fetcher.get_price_matrix(['AAPL', 'MSFT'], date(2024, 1, 1), date(2024, 1, 31))
print(matrix.head())
```

#### Advanced Price Fetching

```python
# Price fetcher with fallback
from src.utils.price_fetcher import PriceFetcherWithFallback

fetcher = PriceFetcherWithFallback()

# Get price with fallback to previous days
price = fetcher.get_price('AAPL', date(2024, 1, 15), fallback_days=5)

# Get trading days
trading_days = fetcher.get_trading_days(date(2024, 1, 1), date(2024, 1, 31))
print(f"Found {len(trading_days)} trading days")

# Cache management
fetcher.clear_cache()
cache_info = fetcher.get_cache_info()
print(f"Cache size: {cache_info['cache_size']}")
```

### Date Utilities

```python
from src.utils import DateUtils

# Get trading days
trading_days = DateUtils.get_trading_days(date(2024, 1, 1), date(2024, 1, 31))

# Get next/previous trading day
next_day = DateUtils.get_next_trading_day(date(2024, 1, 15))
prev_day = DateUtils.get_previous_trading_day(date(2024, 1, 15))

# Month operations
month_end = DateUtils.get_month_end(date(2024, 1, 15))
month_start = DateUtils.get_month_start(date(2024, 1, 15))

# Quarter operations
quarter_end = DateUtils.get_quarter_end(date(2024, 1, 15))
quarter_start = DateUtils.get_quarter_start(date(2024, 1, 15))

# Add months
new_date = DateUtils.add_months(date(2024, 1, 15), 3)

# Date parsing
parsed_date = DateUtils.parse_date('2024-01-15')
formatted_date = DateUtils.format_date(date(2024, 1, 15), '%Y/%m/%d')
```

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and start
docker-compose up --build -d
```

### Individual Services

```bash
# Start only database
docker-compose up mysql -d

# Start backend with database
docker-compose up mysql backend -d

# Start frontend with backend
docker-compose up mysql backend frontend -d
```

### Environment Configuration

Create a `.env` file with the following variables:

```bash
# Database Configuration
DB_HOST=mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=signal_forge

# yfinance Configuration
YFINANCE_TIMEOUT=10
YFINANCE_RETRIES=3

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/alpha_crucible.log
```

### Database Setup

```bash
# Run database setup script
python scripts/setup_database.py

# This will:
# 1. Create the database if it doesn't exist
# 2. Create all required tables
# 3. Insert default signal definitions

# Or with Docker
docker-compose exec backend python scripts/setup_database.py
```

## Error Handling

### Common Errors and Solutions

#### Database Connection Errors

```python
# Check database connection
db = DatabaseManager()
if not db.connect():
    print("Database connection failed")
    print("Check your .env file and MySQL server status")
```

#### Price Data Errors

```python
# Handle missing price data
fetcher = PriceFetcher()
price = fetcher.get_price('INVALID_TICKER', date(2024, 1, 15))
if price is None:
    print("No price data available")
```

#### Signal Calculation Errors

```python
# Handle insufficient data
calculator = SignalCalculator()
result = calculator.calculate_signal_for_ticker('AAPL', 'RSI', date(2024, 1, 15))
if result is None:
    print("Signal calculation failed - insufficient data")
```

## Performance Optimization

### Caching

```python
# Enable price caching
fetcher = PriceFetcher()
# Prices are automatically cached

# Clear cache when needed
fetcher.clear_cache()

# Check cache status
cache_info = fetcher.get_cache_info()
print(f"Cache size: {cache_info['cache_size']}")
```

### Batch Operations

```python
# Batch signal calculation
calculator.calculate_signals(tickers, signals, start_date, end_date)

# Batch price fetching
fetcher.get_price_matrix(tickers, start_date, end_date)

# Batch database operations
db.store_signal_scores(scores_list)
```

### Memory Management

```python
# Use context managers for database connections
with DatabaseManager() as db:
    # Database operations
    pass

# Clear large DataFrames when done
del large_dataframe
```

## Best Practices

### 1. Data Validation

```python
# Always validate inputs
if not tickers or not signals:
    raise ValueError("Tickers and signals must be provided")

# Check date ranges
if start_date >= end_date:
    raise ValueError("Start date must be before end date")
```

### 2. Error Handling

```python
try:
    result = calculator.calculate_signals(tickers, signals, start_date, end_date)
except Exception as e:
    logger.error(f"Signal calculation failed: {e}")
    # Handle error appropriately
```

### 3. Logging

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.info("Starting signal calculation")
logger.warning("Insufficient data for some tickers")
logger.error("Database connection failed")
```

### 4. Testing

```python
# Write unit tests for your custom signals
def test_custom_signal():
    signal = CustomSignal()
    result = signal.calculate(price_data, 'AAPL', target_date)
    assert -1 <= result <= 1
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check MySQL server is running
   - Verify credentials in `.env` file
   - Ensure database exists

2. **No Price Data Available**
   - Check internet connection
   - Verify ticker symbols are correct
   - Check date ranges are valid

3. **Signal Calculation Errors**
   - Ensure sufficient price history
   - Check signal parameters
   - Verify date ranges

4. **Memory Issues**
   - Use smaller date ranges
   - Clear caches regularly
   - Process data in batches

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debug mode for price fetcher
fetcher = PriceFetcher()
# Debug information will be logged
```

## Support

For issues and questions:

1. Check the test files for examples
2. Review the architecture documentation
3. Check the logs for error messages
4. Verify your configuration

The system is designed to be robust and provide clear error messages to help with troubleshooting.

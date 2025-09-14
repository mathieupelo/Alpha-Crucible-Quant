# Equal-Weight Benchmark

This document explains the equal-weight benchmark functionality in the Alpha Crucible Quant system.

## Overview

The system now supports using an equal-weight portfolio of all stocks in the universe as the benchmark for comparison. This provides a more direct comparison of your strategy against a simple equal-weight allocation of the same stocks, rather than comparing against a broad market index like SPY.

## How It Works

### Traditional Benchmark (SPY)
- Uses a single ticker (e.g., SPY) as the benchmark
- Compares strategy performance against the S&P 500 ETF
- May not be directly comparable if your strategy focuses on specific sectors or stocks

### Equal-Weight Benchmark (New)
- Creates a portfolio with equal weights across all stocks in your universe
- Each stock gets a weight of 1/N (where N is the number of stocks)
- Rebalances daily to maintain equal weights
- Provides a direct apples-to-apples comparison

## Configuration

### Enable Equal-Weight Benchmark

```python
from backtest import BacktestConfig

config = BacktestConfig(
    start_date=date(2023, 1, 1),
    end_date=date(2023, 12, 31),
    use_equal_weight_benchmark=True,  # Enable equal-weight benchmark
    benchmark_ticker='SPY'  # Still used for fallback or display
)
```

### Use Traditional Benchmark

```python
config = BacktestConfig(
    start_date=date(2023, 1, 1),
    end_date=date(2023, 12, 31),
    use_equal_weight_benchmark=False,  # Use traditional benchmark
    benchmark_ticker='SPY'  # The actual benchmark ticker
)
```

## Implementation Details

### Equal-Weight Return Calculation

The equal-weight benchmark return is calculated as:

```
Equal-weight return = (1/N) * Σ(stock_return_i)
```

Where:
- N = number of stocks in the universe
- stock_return_i = daily return of stock i

### Daily Rebalancing

The equal-weight benchmark rebalances daily to maintain equal weights:
- Each stock gets weight = 1/N
- No transaction costs applied to benchmark
- Assumes perfect rebalancing capability

### Example Calculation

For a universe of 4 stocks (AAPL, MSFT, GOOGL, AMZN):

```
Day 1: AAPL=2%, MSFT=1%, GOOGL=-1%, AMZN=3%
Equal-weight return = (2% + 1% - 1% + 3%) / 4 = 1.25%

Day 2: AAPL=-1%, MSFT=2%, GOOGL=1%, AMZN=0%
Equal-weight return = (-1% + 2% + 1% + 0%) / 4 = 0.5%
```

## Benefits

### 1. Direct Comparison
- Compares your strategy against the same universe of stocks
- Eliminates sector bias and market cap bias
- Shows pure alpha from stock selection and timing

### 2. Fair Benchmark
- Equal-weight portfolio is a reasonable passive strategy
- Many investors use equal-weight allocations
- Provides a realistic comparison point

### 3. Strategy Evaluation
- Shows if your strategy adds value beyond simple equal weighting
- Helps identify if complexity is justified
- Useful for strategy optimization

## Use Cases

### Sector-Specific Strategies
```python
# Technology stocks strategy
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA']
config = BacktestConfig(use_equal_weight_benchmark=True)
```

### Small Cap Strategies
```python
# Small cap stocks strategy
tickers = ['SMALL_CAP_1', 'SMALL_CAP_2', 'SMALL_CAP_3']
config = BacktestConfig(use_equal_weight_benchmark=True)
```

### International Strategies
```python
# International stocks strategy
tickers = ['INTL_1', 'INTL_2', 'INTL_3', 'INTL_4']
config = BacktestConfig(use_equal_weight_benchmark=True)
```

## Performance Metrics

### Alpha and Beta
- **Alpha**: Excess return over equal-weight benchmark
- **Beta**: Sensitivity to equal-weight benchmark movements
- **Information Ratio**: Risk-adjusted excess return

### Example Results
```
Strategy Performance:
  Total Return: 15.2%
  Equal-weight Benchmark: 12.8%
  Outperformance: 2.4%
  Alpha: 2.1%
  Beta: 0.95
  Information Ratio: 0.85
```

## Comparison with SPY

### When to Use Equal-Weight Benchmark
- Your strategy focuses on specific sectors
- You want to isolate stock selection alpha
- Your universe is different from S&P 500
- You want a fair comparison against passive allocation

### When to Use SPY Benchmark
- Your strategy is market-wide
- You want to compare against broad market
- You're evaluating market timing strategies
- You want to show absolute market performance

## Testing

### Test Script
Use the provided test script to compare both benchmarks:

```bash
python tests/test_equal_weight_benchmark.py
```

This script will:
- Run the same strategy against both benchmarks
- Show performance differences
- Verify equal-weight calculation accuracy
- Display comparative metrics

### Manual Verification
```python
# Verify equal-weight calculation
import pandas as pd
import numpy as np

# Get price data
price_data = price_fetcher.get_price_matrix(tickers, start_date, end_date)

# Calculate returns
returns = price_data.pct_change().dropna()

# Calculate equal-weight returns
equal_weight_returns = returns.mean(axis=1)

# Calculate cumulative return
equal_weight_cumulative = (1 + equal_weight_returns).cumprod()
total_return = equal_weight_cumulative.iloc[-1] - 1

print(f"Equal-weight total return: {total_return:.2%}")
```

## Configuration Examples

### Basic Equal-Weight Benchmark
```python
config = BacktestConfig(
    start_date=date(2023, 1, 1),
    end_date=date(2023, 12, 31),
    use_equal_weight_benchmark=True
)
```

### Custom Benchmark Settings
```python
config = BacktestConfig(
    start_date=date(2023, 1, 1),
    end_date=date(2023, 12, 31),
    use_equal_weight_benchmark=True,
    benchmark_ticker='SPY',  # Used for fallback or display
    initial_capital=100000.0,
    rebalancing_frequency='monthly'
)
```

### Switching Between Benchmarks
```python
# Equal-weight benchmark
config_equal = BacktestConfig(use_equal_weight_benchmark=True)

# SPY benchmark
config_spy = BacktestConfig(
    use_equal_weight_benchmark=False,
    benchmark_ticker='SPY'
)

# Custom benchmark
config_custom = BacktestConfig(
    use_equal_weight_benchmark=False,
    benchmark_ticker='QQQ'  # NASDAQ 100
)
```

## Web Application Integration

### API Endpoints

The equal-weight benchmark functionality is accessible through the REST API:

```http
# Get backtest with equal-weight benchmark
GET /api/backtests/{run_id}?use_equal_weight_benchmark=true

# Get backtest metrics including equal-weight comparison
GET /api/backtests/{run_id}/metrics
```

### Frontend Visualization

The web application provides comprehensive visualization of equal-weight benchmark comparisons:

#### Performance Charts
- **Cumulative Returns**: Side-by-side comparison of strategy vs equal-weight
- **Rolling Performance**: Rolling window performance analysis
- **Drawdown Analysis**: Drawdown comparison between strategies

#### Benchmark Selection
- **Interactive Toggle**: Switch between SPY and equal-weight benchmarks
- **Real-time Updates**: Live updates when changing benchmark settings
- **Performance Metrics**: Dynamic calculation of alpha, beta, and other metrics

### Dashboard Integration

The dashboard displays equal-weight benchmark information:
- **Benchmark Type Indicator**: Shows which benchmark is being used
- **Performance Comparison**: Quick comparison of strategy vs benchmark
- **Risk-Adjusted Metrics**: Sharpe ratio, information ratio, and other metrics

## Best Practices

1. **Use Equal-Weight for Stock Selection**: When evaluating stock picking strategies
2. **Use SPY for Market Timing**: When evaluating market timing strategies
3. **Compare Both**: Run backtests with both benchmarks to get full picture
4. **Document Choice**: Clearly document which benchmark you're using and why
5. **Consider Universe**: Ensure your benchmark matches your investment universe
6. **Web Interface**: Use the web application to easily switch between benchmarks
7. **API Integration**: Leverage API endpoints for programmatic benchmark analysis

## Limitations

1. **No Transaction Costs**: Equal-weight benchmark assumes perfect rebalancing
2. **Daily Rebalancing**: May not reflect realistic implementation
3. **Universe Dependency**: Performance depends on stock selection
4. **No Cash Management**: Assumes 100% invested at all times

## Future Enhancements

Potential improvements to the equal-weight benchmark:

1. **Transaction Costs**: Add transaction costs to benchmark
2. **Rebalancing Frequency**: Allow different rebalancing frequencies
3. **Cash Management**: Include cash allocation options
4. **Sector Weights**: Support sector-neutral equal weighting
5. **Market Cap Weights**: Support market cap weighted benchmarks

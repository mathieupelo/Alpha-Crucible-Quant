# Forward Fill Signal Scores

This document explains the forward-fill functionality for signal scores in the Alpha Crucible Quant system.

## Overview

When running backtests, there may be dates where signal scores are not available for specific tickers or signals. The forward-fill functionality ensures that the system uses the latest available signal scores from previous dates when current scores are missing.

## How It Works

### Without Forward Fill (Default Behavior)
- If no signal score is available for a specific date, the system returns `None` for that date
- This can cause portfolio rebalancing to fail on dates with missing data
- Results in gaps in the backtest timeline

### With Forward Fill (New Behavior)
- When signal scores are missing for a date, the system uses the most recent available scores
- Ensures continuous portfolio rebalancing even with sparse signal data
- Maintains strategy consistency by using the last known signal values

## Configuration

### BacktestConfig Parameter

```python
from backtest import BacktestConfig

config = BacktestConfig(
    start_date=date(2023, 1, 1),
    end_date=date(2023, 12, 31),
    forward_fill_signals=True  # Enable forward fill (default: True)
)
```

### Database Manager Parameter

```python
from database import DatabaseManager

db_manager = DatabaseManager()

# Get signal scores with forward fill
signal_scores = db_manager.get_signal_scores_dataframe(
    tickers=['AAPL', 'MSFT'],
    signals=['RSI', 'SMA'],
    start_date=date(2023, 1, 1),
    end_date=date(2023, 12, 31),
    forward_fill=True  # Enable forward fill
)
```

### Signal Calculator Parameter

```python
from signals import SignalCalculator

signal_calculator = SignalCalculator(db_manager)

# Get signal scores with forward fill
signal_scores = signal_calculator.get_signal_scores_pivot(
    tickers=['AAPL', 'MSFT'],
    signals=['RSI', 'SMA'],
    start_date=date(2023, 1, 1),
    end_date=date(2023, 12, 31),
    forward_fill=True  # Enable forward fill
)
```

## Implementation Details

### Database Level
- The `get_signal_scores_dataframe` method applies forward fill using pandas `ffill()`
- Forward fill is applied after creating the pivot table
- Only affects missing values, not existing data

### Backtest Engine Level
- The `_rebalance_portfolio` method checks for missing signal scores
- If scores are missing for a specific date, it finds the latest available date
- Uses the signal scores from the latest available date
- Logs when forward fill is being used

### Example Behavior

Consider the following signal score data:

```
Date       AAPL-RSI  AAPL-SMA  MSFT-RSI  MSFT-SMA
2023-01-01    0.5      0.3      0.7      0.4
2023-01-02    NaN      NaN      NaN      NaN
2023-01-03    NaN      NaN      NaN      NaN
2023-01-04    0.6      0.4      0.8      0.5
2023-01-05    NaN      NaN      NaN      NaN
```

**Without Forward Fill:**
```
Date       AAPL-RSI  AAPL-SMA  MSFT-RSI  MSFT-SMA
2023-01-01    0.5      0.3      0.7      0.4
2023-01-02    NaN      NaN      NaN      NaN
2023-01-03    NaN      NaN      NaN      NaN
2023-01-04    0.6      0.4      0.8      0.5
2023-01-05    NaN      NaN      NaN      NaN
```

**With Forward Fill:**
```
Date       AAPL-RSI  AAPL-SMA  MSFT-RSI  MSFT-SMA
2023-01-01    0.5      0.3      0.7      0.4
2023-01-02    0.5      0.3      0.7      0.4  # Forward filled
2023-01-03    0.5      0.3      0.7      0.4  # Forward filled
2023-01-04    0.6      0.4      0.8      0.5
2023-01-05    0.6      0.4      0.8      0.5  # Forward filled
```

## Benefits

1. **Continuous Trading**: Ensures portfolio rebalancing continues even with missing signal data
2. **Strategy Consistency**: Uses the last known signal values, maintaining strategy logic
3. **Reduced Gaps**: Minimizes gaps in backtest results due to missing data
4. **Realistic Simulation**: Mimics real-world trading where you use the latest available information
5. **Web Application Support**: Seamlessly integrates with the web interface for real-time analysis
6. **API Integration**: Works with REST API endpoints for programmatic access

## Use Cases

### Sparse Signal Data
- When signal calculations are expensive and only run periodically
- When some tickers have less frequent signal updates
- When data sources have irregular update schedules

### Historical Backtesting
- When historical signal data has gaps
- When backtesting over periods with limited data availability
- When combining multiple signal sources with different update frequencies

### Production Trading
- When signal updates are delayed
- When network issues cause temporary data unavailability
- When maintaining trading continuity is critical

## Testing

### Test Script
Use the provided test script to verify forward-fill functionality:

```bash
python tests/test_forward_fill.py
```

This script will:
- Compare signal scores with and without forward fill
- Show the reduction in missing values
- Demonstrate the forward-fill behavior
- Test both database and signal calculator levels

### Manual Testing
```python
# Test with missing data
import pandas as pd
from datetime import date

# Create test data with gaps
data = {
    'date': [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 4)],
    'ticker': ['AAPL', 'AAPL', 'AAPL'],
    'signal_id': ['RSI', 'RSI', 'RSI'],
    'score': [0.5, None, 0.6]
}

df = pd.DataFrame(data)
pivot = df.pivot_table(index='date', columns=['ticker', 'signal_id'], values='score')

# Without forward fill
print("Without forward fill:")
print(pivot)

# With forward fill
pivot_ff = pivot.ffill()
print("\nWith forward fill:")
print(pivot_ff)
```

## Configuration Options

### Enable/Disable Forward Fill
```python
# Enable forward fill (default)
config = BacktestConfig(forward_fill_signals=True)

# Disable forward fill
config = BacktestConfig(forward_fill_signals=False)
```

### Per-Query Control
```python
# Enable for specific query
signal_scores = db_manager.get_signal_scores_dataframe(
    tickers, signals, start_date, end_date, forward_fill=True
)

# Disable for specific query
signal_scores = db_manager.get_signal_scores_dataframe(
    tickers, signals, start_date, end_date, forward_fill=False
)
```

## Logging

The system logs when forward fill is being used:

```
INFO: No signal scores for 2023-01-02, using latest available from 2023-01-01
```

This helps track when the system is using forward-filled data vs. current data.

## Web Application Integration

### API Endpoints

The forward-fill functionality is accessible through the REST API:

```http
# Get signal scores with forward fill
GET /api/signals?tickers=AAPL,MSFT&signal_names=RSI,SMA&start_date=2024-01-01&end_date=2024-01-31

# Get backtest signals with forward fill
GET /api/backtests/{run_id}/signals?start_date=2024-01-01&end_date=2024-01-31
```

### Frontend Visualization

The web application provides visual indicators for forward-filled data:
- **Data Quality Indicators**: Show when forward fill is being used
- **Timeline Visualization**: Display data availability and gaps
- **Signal Charts**: Highlight forward-filled values in performance charts

### Real-time Monitoring

The system logs forward-fill usage for monitoring:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Forward fill applied for AAPL-RSI on 2024-01-15, using data from 2024-01-12",
  "ticker": "AAPL",
  "signal": "RSI",
  "target_date": "2024-01-15",
  "source_date": "2024-01-12"
}
```

## Best Practices

1. **Enable by Default**: Use forward fill for most backtesting scenarios
2. **Monitor Logs**: Check logs to see when forward fill is being used
3. **Data Quality**: Ensure signal data quality to minimize forward fill usage
4. **Testing**: Test both with and without forward fill to understand the impact
5. **Documentation**: Document when and why forward fill is used in your strategies
6. **Web Interface**: Use the web application to monitor forward-fill usage
7. **API Monitoring**: Monitor API responses for forward-fill indicators

## Limitations

1. **Stale Data**: Forward-filled values may become stale over time
2. **Signal Lag**: May not reflect the most current market conditions
3. **Strategy Drift**: Extended use of forward-filled data may cause strategy drift
4. **Performance Impact**: Minimal performance impact from forward fill operations

## Future Enhancements

Potential improvements to the forward-fill system:

1. **Maximum Age**: Limit how old forward-filled data can be
2. **Decay Functions**: Apply decay to forward-filled values over time
3. **Alternative Fill Methods**: Support for interpolation or other fill methods
4. **Signal Quality Metrics**: Track the age and quality of forward-filled data

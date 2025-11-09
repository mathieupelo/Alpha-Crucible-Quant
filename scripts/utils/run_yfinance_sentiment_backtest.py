#!/usr/bin/env python3
"""
Run a backtest on the yfinance sentiment signal for a specific universe.

This script:
1. Queries the database for processed dates for SENTIMENT_YFINANCE_NEWS signal
2. Determines the date range from the processed dates
3. Runs a backtest using those dates
4. Displays the results
"""

import sys
import os
from pathlib import Path
from datetime import date
import pandas as pd

# Add project root and src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from src.backtest.engine import BacktestEngine
from src.backtest.config import BacktestConfig
from src.signals.reader import SignalReader
from src.database.manager import DatabaseManager

def get_processed_dates(database_manager: DatabaseManager, universe_id: int, signal_name: str):
    """
    Query the database to find all processed dates for a signal in a universe.
    
    Args:
        database_manager: DatabaseManager instance
        universe_id: Universe ID to query
        signal_name: Signal name to query (e.g., 'SENTIMENT_YFINANCE_NEWS')
        
    Returns:
        tuple: (min_date, max_date, tickers, date_count_dict)
    """
    print(f"\n{'='*60}")
    print(f"Querying processed dates for signal: {signal_name}")
    print(f"Universe ID: {universe_id}")
    print(f"{'='*60}\n")
    
    # Get universe information
    universe = database_manager.get_universe_by_id(universe_id)
    if not universe:
        raise ValueError(f"Universe with ID {universe_id} not found")
    
    print(f"Universe: {universe.name}")
    print(f"Description: {universe.description}\n")
    
    # Get tickers from universe
    tickers_df = database_manager.get_universe_tickers(universe_id)
    if tickers_df.empty:
        raise ValueError(f"Universe {universe_id} has no tickers")
    
    tickers = tickers_df['ticker'].tolist()
    print(f"Found {len(tickers)} tickers in universe:")
    print(f"  {', '.join(tickers)}\n")
    
    # Query signal_raw table for processed dates
    # Get all signal records for these tickers and this signal
    signals_df = database_manager.get_signals_raw(
        tickers=tickers,
        signal_names=[signal_name],
        start_date=None,
        end_date=None
    )
    
    if signals_df.empty:
        raise ValueError(
            f"No signal data found for signal '{signal_name}' in universe {universe_id}. "
            f"Please ensure signals have been processed for this universe."
        )
    
    print(f"Found {len(signals_df)} signal records\n")
    
    # Get unique dates
    unique_dates = sorted(signals_df['asof_date'].unique())
    min_date = unique_dates[0]
    max_date = unique_dates[-1]
    
    # Count records per date
    date_counts = signals_df.groupby('asof_date').size().to_dict()
    
    print(f"Date Range: {min_date} to {max_date}")
    print(f"Total unique dates: {len(unique_dates)}")
    print(f"\nSignal records per date:")
    for d in unique_dates[:10]:  # Show first 10 dates
        count = date_counts.get(d, 0)
        ticker_count = len(signals_df[signals_df['asof_date'] == d]['ticker'].unique())
        print(f"  {d}: {count} records ({ticker_count} tickers)")
    if len(unique_dates) > 10:
        print(f"  ... and {len(unique_dates) - 10} more dates")
    
    # Check coverage per ticker
    print(f"\nSignal coverage per ticker:")
    ticker_coverage = signals_df.groupby('ticker')['asof_date'].agg(['min', 'max', 'count'])
    for ticker in tickers:
        if ticker in ticker_coverage.index:
            row = ticker_coverage.loc[ticker]
            print(f"  {ticker}: {row['count']} records ({row['min']} to {row['max']})")
        else:
            print(f"  {ticker}: No signal data")
    
    return min_date, max_date, tickers, date_counts

def run_backtest(tickers: list, signal_name: str, start_date: date, end_date: date, 
                 universe_id: int, database_manager: DatabaseManager):
    """
    Run a backtest for the given parameters.
    
    Args:
        tickers: List of ticker symbols
        signal_name: Signal name to use
        start_date: Start date for backtest
        end_date: End date for backtest
        universe_id: Universe ID
        database_manager: DatabaseManager instance
        
    Returns:
        BacktestResult object
    """
    print(f"\n{'='*60}")
    print("Running Backtest")
    print(f"{'='*60}\n")
    
    # Backtest configuration
    config = BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        universe_id=universe_id,
        name=f"YFinance Sentiment Backtest - Universe {universe_id}",
        initial_capital=10000.0,
        rebalancing_frequency='daily',
        evaluation_period='daily',
        transaction_costs=0.001,
        max_weight=0.4,
        min_weight=0.0,
        risk_aversion=1.0,
        benchmark_ticker='SPY',
        use_equal_weight_benchmark=True,
        signal_weights={signal_name: 1.0},
        signal_combination_method='weighted',
        forward_fill_signals=True
    )
    
    print(f"Backtest Configuration:")
    print(f"  Universe ID: {universe_id}")
    print(f"  Tickers: {len(tickers)} tickers")
    print(f"  Signal: {signal_name}")
    print(f"  Date Range: {start_date} to {end_date}")
    print(f"  Initial Capital: ${config.initial_capital:,.2f}")
    print(f"  Rebalancing: {config.rebalancing_frequency}")
    print(f"  Forward Fill Signals: {config.forward_fill_signals}")
    print(f"  Benchmark: Equal-weight portfolio")
    print()
    
    # Initialize components
    from src.utils.price_fetcher import PriceFetcher
    price_fetcher = PriceFetcher()
    signal_reader = SignalReader(database_manager)
    backtest_engine = BacktestEngine(
        price_fetcher=price_fetcher,
        signal_reader=signal_reader,
        database_manager=database_manager
    )
    
    # Run backtest
    print("Executing backtest...")
    result = backtest_engine.run_backtest(
        tickers=tickers,
        signals=[signal_name],
        config=config
    )
    
    return result

def display_results(result):
    """Display backtest results in a formatted way."""
    print(f"\n{'='*60}")
    print("BACKTEST RESULTS")
    print(f"{'='*60}\n")
    
    print(f"Backtest ID: {result.backtest_id}")
    print(f"Period: {result.start_date} to {result.end_date}")
    print(f"Execution time: {result.execution_time_seconds:.1f} seconds")
    print()
    
    print("PERFORMANCE METRICS:")
    print(f"  Total Return: {result.total_return:.2%}")
    print(f"  Annualized Return: {result.annualized_return:.2%}")
    print(f"  Volatility: {result.volatility:.2%}")
    print(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print(f"  Max Drawdown: {result.max_drawdown:.2%}")
    print(f"  Win Rate: {result.win_rate:.2%}")
    print()
    
    print("RISK METRICS:")
    print(f"  Alpha: {result.alpha:.2%}")
    print(f"  Beta: {result.beta:.2f}")
    print(f"  Information Ratio: {result.information_ratio:.2f}")
    print(f"  Tracking Error: {result.tracking_error:.2%}")
    print()
    
    print("PORTFOLIO METRICS:")
    print(f"  Number of Rebalances: {result.num_rebalances}")
    print(f"  Average Turnover: {result.avg_turnover:.2%}")
    print(f"  Average Positions: {result.avg_num_positions:.1f}")
    print(f"  Max Concentration: {result.max_concentration:.2%}")
    print()
    
    # Show top positions from last rebalance
    if result.weights_history.empty:
        print("⚠ No portfolio weights history available")
    else:
        last_weights = result.weights_history.iloc[-1]
        top_positions = last_weights[last_weights > 0].sort_values(ascending=False)
        
        if len(top_positions) > 0:
            print("TOP POSITIONS (Last Rebalance):")
            for ticker, weight in top_positions.head(10).items():
                print(f"  {ticker}: {weight:.2%}")
        else:
            print("⚠ No positions in last rebalance")
        print()
    
    # Show performance comparison
    if result.portfolio_values.empty or result.benchmark_values.empty:
        print("⚠ No portfolio or benchmark values available")
    else:
        final_portfolio_value = result.portfolio_values.iloc[-1]
        final_benchmark_value = result.benchmark_values.iloc[-1]
        
        print("FINAL VALUES:")
        print(f"  Strategy Portfolio: ${final_portfolio_value:,.2f}")
        print(f"  Equal-weight Benchmark: ${final_benchmark_value:,.2f}")
        print(f"  Outperformance: ${final_portfolio_value - final_benchmark_value:,.2f}")
        print()
    
    if hasattr(result, 'error_message') and result.error_message:
        print(f"⚠ WARNING: {result.error_message}")
        print()

def main():
    """Main function to run the backtest."""
    # Configuration
    UNIVERSE_ID = 14
    SIGNAL_NAME = 'SENTIMENT_YFINANCE_NEWS'
    
    print("="*60)
    print("YFinance Sentiment Signal Backtest")
    print("="*60)
    print(f"Universe ID: {UNIVERSE_ID}")
    print(f"Signal: {SIGNAL_NAME}")
    print("="*60)
    
    # Initialize database
    database_manager = DatabaseManager()
    if not database_manager.connect():
        print("❌ Failed to connect to database.")
        print("Please check your database connection settings.")
        return 1
    
    try:
        # Step 1: Query processed dates
        min_date, max_date, tickers, date_counts = get_processed_dates(
            database_manager, UNIVERSE_ID, SIGNAL_NAME
        )
        
        # Step 2: Run backtest
        result = run_backtest(
            tickers=tickers,
            signal_name=SIGNAL_NAME,
            start_date=min_date,
            end_date=max_date,
            universe_id=UNIVERSE_ID,
            database_manager=database_manager
        )
        
        # Step 3: Display results
        display_results(result)
        
        print("✅ Backtest completed successfully!")
        print(f"\nBacktest ID: {result.backtest_id}")
        print("You can view detailed results in the database or via the API.")
        
        return 0
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        database_manager.disconnect()

if __name__ == "__main__":
    sys.exit(main())


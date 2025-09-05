#!/usr/bin/env python3
"""
Example script to run a backtest using the Quant Project system.

This script demonstrates how to use the unified system to run a backtest.
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from backtest import BacktestEngine, BacktestConfig
from signals import SignalCalculator
from database import DatabaseManager
from utils import PriceFetcher
from data import RealTimeDataFetcher, DataValidator


def main():
    """Run a sample backtest with real market data."""
    print("Alpha Crucible Quant - Real-Time Backtest Example")
    print("=" * 60)
    
    # Initialize real-time data fetcher and validator
    data_fetcher = RealTimeDataFetcher()
    data_validator = DataValidator()
    
    # Configuration
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
    signals = ['RSI', 'SMA', 'MACD']
    signal_weights = {'RSI': 0.33, 'SMA': 0.33, 'MACD': 0.34}
    
    # Date range (matching signal calculation)
    start_date = date(2023, 9, 5)
    end_date = date(2024, 12, 31)  # More recent end date for real data
    
    print(f"Using real market data for {len(tickers)} tickers")
    print(f"Date range: {start_date} to {end_date}")
    
    # Validate tickers
    print("\nValidating tickers...")
    valid_tickers = []
    for ticker in tickers:
        if data_fetcher.validate_ticker(ticker):
            valid_tickers.append(ticker)
            print(f"✓ {ticker} - Valid")
        else:
            print(f"✗ {ticker} - Invalid or unavailable")
    
    if not valid_tickers:
        print("No valid tickers found. Exiting.")
        return
    
    tickers = valid_tickers
    print(f"Using {len(tickers)} valid tickers: {', '.join(tickers)}")
    
    # Check market status
    print("\nChecking market status...")
    market_status = data_fetcher.get_market_status()
    for exchange, is_open in market_status.items():
        status = "Open" if is_open else "Closed"
        print(f"{exchange}: {status}")
    
    # Backtest configuration
    config = BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        initial_capital=10000.0,
        rebalancing_frequency='monthly',
        evaluation_period='monthly',
        transaction_costs=0.001,
        max_weight=0.3,
        risk_aversion=0.0,
        benchmark_ticker='SPY',
        use_equal_weight_benchmark=True,  # Use equal-weight portfolio of all stocks as benchmark
        signal_weights=signal_weights,
        forward_fill_signals=True  # Use latest available signal scores when missing
    )
    
    print(f"\nBacktest Configuration:")
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Signals: {', '.join(signals)}")
    print(f"Signal weights: {signal_weights}")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Initial capital: ${config.initial_capital:,.2f}")
    print(f"Rebalancing: {config.rebalancing_frequency}")
    print(f"Forward fill signals: {config.forward_fill_signals}")
    print(f"Benchmark: {'Equal-weight portfolio' if config.use_equal_weight_benchmark else config.benchmark_ticker}")
    print()
    
    try:
        # Initialize components
        print("Initializing components...")
        price_fetcher = PriceFetcher()  # This now uses the enhanced real-time fetcher
        database_manager = DatabaseManager()
        signal_calculator = SignalCalculator(price_fetcher, database_manager)
        backtest_engine = BacktestEngine(price_fetcher, signal_calculator, database_manager)
        
        # Test data fetching and validation
        print("Testing data fetching and validation...")
        test_data = data_fetcher.get_price_history('AAPL', start_date, start_date + timedelta(days=30))
        if test_data is not None and not test_data.empty:
            print(f"✓ Successfully fetched {len(test_data)} days of real market data")
            
            # Validate the data
            validation_result = data_validator.validate_price_data(test_data)
            if validation_result['is_valid']:
                print("✓ Data validation passed")
            else:
                print("⚠ Data validation warnings:")
                for warning in validation_result['warnings']:
                    print(f"  - {warning}")
        else:
            print("⚠ Warning: Could not fetch real market data, using fallback")
        
        # Run backtest
        print("Running backtest...")
        result = backtest_engine.run_backtest(
            tickers=tickers,
            signals=signals,
            config=config
        )
        
        # Display results
        print("\n" + "=" * 50)
        print("BACKTEST RESULTS")
        print("=" * 50)
        
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
        if not result.weights_history.empty:
            last_weights = result.weights_history.iloc[-1]
            top_positions = last_weights[last_weights > 0].sort_values(ascending=False)
            
            print("TOP POSITIONS (Last Rebalance):")
            for ticker, weight in top_positions.head(10).items():
                print(f"  {ticker}: {weight:.2%}")
            print()
        
        # Show performance comparison
        if not result.portfolio_values.empty and not result.benchmark_values.empty:
            final_portfolio_value = result.portfolio_values.iloc[-1]
            final_benchmark_value = result.benchmark_values.iloc[-1]
            
            print("FINAL VALUES:")
            print(f"  Strategy Portfolio: ${final_portfolio_value:,.2f}")
            benchmark_name = "Equal-weight portfolio" if config.use_equal_weight_benchmark else f"Benchmark ({config.benchmark_ticker})"
            print(f"  {benchmark_name}: ${final_benchmark_value:,.2f}")
            print(f"  Outperformance: ${final_portfolio_value - final_benchmark_value:,.2f}")
            print()
        
        print("Backtest completed successfully!")
        
        # Show portfolio data storage information
        print("\nPortfolio Data Storage:")
        print("-" * 25)
        print(f"Portfolio values and weights have been stored in the database")
        print(f"Backtest ID: {result.backtest_id}")
        print(f"Use the query_portfolio_data.py script to analyze the stored data")
        
        # Create and display plots
        print("\nGenerating performance plots...")
        try:
            figures = backtest_engine.create_plots(show_plots=True)
            print(f"Generated {len(figures)} plots")
        except Exception as e:
            print(f"Error generating plots: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"Error running backtest: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

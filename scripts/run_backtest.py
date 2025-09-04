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


def main():
    """Run a sample backtest."""
    print("Quant Project - Backtest Example")
    print("=" * 50)
    
    # Configuration
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
    signals = ['RSI', 'SMA', 'MACD']
    signal_weights = {'RSI': 0.4, 'SMA': 0.4, 'MACD': 0.2}
    
    # Date range (last 2 years)
    end_date = date.today()
    start_date = end_date - timedelta(days=730)
    
    # Backtest configuration
    config = BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        initial_capital=10000.0,
        rebalancing_frequency='monthly',
        evaluation_period='monthly',
        transaction_costs=0.001,
        max_weight=0.15,
        risk_aversion=0.5,
        benchmark_ticker='SPY',
        signal_weights=signal_weights
    )
    
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Signals: {', '.join(signals)}")
    print(f"Signal weights: {signal_weights}")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Initial capital: ${config.initial_capital:,.2f}")
    print(f"Rebalancing: {config.rebalancing_frequency}")
    print()
    
    try:
        # Initialize components
        print("Initializing components...")
        price_fetcher = PriceFetcher()
        database_manager = DatabaseManager()
        signal_calculator = SignalCalculator(price_fetcher, database_manager)
        backtest_engine = BacktestEngine(price_fetcher, signal_calculator, database_manager)
        
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
            print(f"  Benchmark (SPY): ${final_benchmark_value:,.2f}")
            print(f"  Outperformance: ${final_portfolio_value - final_benchmark_value:,.2f}")
            print()
        
        print("Backtest completed successfully!")
        
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

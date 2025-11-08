#!/usr/bin/env python3
"""
CLI script to run a backtest.

This script allows running backtests from the command line or interactively.
"""

import sys
import os
from pathlib import Path
from datetime import date, datetime
import argparse

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from services.database_service import DatabaseService
from src.backtest.engine import BacktestEngine
from src.backtest.config import BacktestConfig


def run_backtest_cli(
    universe_id: int,
    start_date: str,
    end_date: str,
    signals: list,
    name: str = None,
    initial_capital: float = 10000.0,
    rebalancing_frequency: str = 'monthly',
    **kwargs
):
    """Run a backtest with the given parameters."""
    # Initialize services
    db_service = DatabaseService()
    
    if not db_service.ensure_connection():
        raise RuntimeError("Failed to connect to database")
    
    # Validate universe exists
    universe = db_service.get_universe_by_id(universe_id)
    if universe is None:
        raise ValueError(f"Universe with ID {universe_id} not found")
    
    # Get universe tickers
    tickers_data = db_service.get_universe_tickers(universe_id)
    if not tickers_data:
        raise ValueError(f"Universe '{universe['name']}' has no tickers")
    
    tickers = [t['ticker'] for t in tickers_data]
    
    if len(tickers) < 5:
        raise ValueError(f"Universe must have at least 5 tickers. Current count: {len(tickers)}")
    
    # Parse dates
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Create backtest configuration
    config = BacktestConfig(
        start_date=start,
        end_date=end,
        universe_id=universe_id,
        name=name,
        initial_capital=initial_capital,
        rebalancing_frequency=rebalancing_frequency,
        evaluation_period=rebalancing_frequency,
        transaction_costs=kwargs.get('transaction_costs', 0.001),
        max_weight=kwargs.get('max_weight', 0.1),
        min_weight=kwargs.get('min_weight', 0.0),
        risk_aversion=kwargs.get('risk_aversion', 0.5),
        benchmark_ticker=kwargs.get('benchmark_ticker', 'SPY'),
        use_equal_weight_benchmark=kwargs.get('use_equal_weight_benchmark', True),
        min_lookback_days=kwargs.get('min_lookback_days', 252),
        max_lookback_days=kwargs.get('max_lookback_days', 756),
        signal_weights=kwargs.get('signal_weights'),
        signal_combination_method=kwargs.get('signal_combination_method', 'weighted'),
        forward_fill_signals=kwargs.get('forward_fill_signals', True)
    )
    
    # Convert signal names to uppercase
    signals_upper = [s.upper() for s in signals]
    
    # Run backtest
    print(f"Running backtest for universe '{universe['name']}'...")
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Signals: {', '.join(signals_upper)}")
    print(f"Date range: {start_date} to {end_date}")
    
    engine = BacktestEngine()
    result = engine.run_backtest(
        tickers=tickers,
        signals=signals_upper,
        config=config
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("BACKTEST RESULTS")
    print("=" * 60)
    print(f"Backtest ID: {result.backtest_id}")
    print(f"Total Return: {result.total_return:.2%}")
    print(f"Annualized Return: {result.annualized_return:.2%}")
    print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print(f"Max Drawdown: {result.max_drawdown:.2%}")
    
    return result


def interactive_mode():
    """Run in interactive mode."""
    db_service = DatabaseService()
    
    if not db_service.ensure_connection():
        print("❌ Failed to connect to database")
        return 1
    
    # List universes
    print("\nAvailable universes:")
    universes = db_service.get_all_universes()
    if not universes:
        print("  No universes found. Create one first using create_universe.py")
        return 1
    
    for universe in universes:
        print(f"  ID {universe['id']}: {universe['name']} ({universe.get('ticker_count', 0)} tickers)")
    
    # Get universe ID
    try:
        universe_id = int(input("\nEnter universe ID: "))
    except ValueError:
        print("❌ Invalid universe ID")
        return 1
    
    # Get date range
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")
    
    # Get signals
    signals_input = input("Enter signals (comma-separated): ")
    signals = [s.strip() for s in signals_input.split(',')]
    
    # Get optional name
    name = input("Enter backtest name (optional, press Enter to skip): ").strip()
    if not name:
        name = None
    
    try:
        result = run_backtest_cli(
            universe_id=universe_id,
            start_date=start_date,
            end_date=end_date,
            signals=signals,
            name=name
        )
        print("\n✅ Backtest completed successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run a backtest')
    parser.add_argument('--universe-id', type=int, help='Universe ID')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--signals', type=str, help='Comma-separated list of signals')
    parser.add_argument('--name', type=str, help='Backtest name')
    parser.add_argument('--initial-capital', type=float, default=10000.0, help='Initial capital')
    parser.add_argument('--rebalancing-frequency', type=str, default='monthly',
                       choices=['daily', 'weekly', 'monthly', 'quarterly'],
                       help='Rebalancing frequency')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    if args.interactive or not all([args.universe_id, args.start_date, args.end_date, args.signals]):
        return interactive_mode()
    
    try:
        signals = [s.strip() for s in args.signals.split(',')]
        result = run_backtest_cli(
            universe_id=args.universe_id,
            start_date=args.start_date,
            end_date=args.end_date,
            signals=signals,
            name=args.name,
            initial_capital=args.initial_capital,
            rebalancing_frequency=args.rebalancing_frequency
        )
        print("\n✅ Backtest completed successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


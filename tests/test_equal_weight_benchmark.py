#!/usr/bin/env python3
"""
Test script to demonstrate equal-weight benchmark functionality.

This script shows how the system compares strategy performance against
an equal-weight portfolio of all stocks in the universe.
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from backtest import BacktestEngine, BacktestConfig
from signals import SignalCalculator
from database import DatabaseManager
from utils import PriceFetcher


def test_equal_weight_benchmark():
    """Test equal-weight benchmark functionality."""
    print("Equal-Weight Benchmark Test")
    print("=" * 30)
    
    try:
        # Test parameters
        tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
        signals = ['RSI', 'SMA']
        signal_weights = {'RSI': 0.5, 'SMA': 0.5}
        
        # Date range (last 6 months)
        end_date = date.today()
        start_date = end_date - timedelta(days=180)
        
        print(f"Tickers: {', '.join(tickers)}")
        print(f"Signals: {', '.join(signals)}")
        print(f"Date range: {start_date} to {end_date}")
        print()
        
        # Initialize components
        print("Initializing components...")
        price_fetcher = PriceFetcher()
        database_manager = DatabaseManager()
        signal_calculator = SignalCalculator(database_manager)
        backtest_engine = BacktestEngine(price_fetcher, signal_calculator, database_manager)
        
        # Test 1: Equal-weight benchmark
        print("1. Testing with Equal-Weight Benchmark:")
        print("-" * 40)
        
        config_equal_weight = BacktestConfig(
            start_date=start_date,
            end_date=end_date,
            initial_capital=10000.0,
            rebalancing_frequency='monthly',
            transaction_costs=0.001,
            max_weight=0.3,
            risk_aversion=0.5,
            use_equal_weight_benchmark=True,  # Use equal-weight benchmark
            signal_weights=signal_weights,
            forward_fill_signals=True
        )
        
        print(f"Benchmark type: Equal-weight portfolio")
        print("Running backtest...")
        
        result_equal_weight = backtest_engine.run_backtest(
            tickers=tickers,
            signals=signals,
            config=config_equal_weight
        )
        
        print(f"Strategy return: {result_equal_weight.total_return:.2%}")
        print(f"Equal-weight benchmark return: {result_equal_weight.benchmark_values.iloc[-1] / config_equal_weight.initial_capital - 1:.2%}")
        print(f"Outperformance: {result_equal_weight.total_return - (result_equal_weight.benchmark_values.iloc[-1] / config_equal_weight.initial_capital - 1):.2%}")
        print()
        
        # Test 2: Traditional SPY benchmark
        print("2. Testing with Traditional SPY Benchmark:")
        print("-" * 42)
        
        config_spy = BacktestConfig(
            start_date=start_date,
            end_date=end_date,
            initial_capital=10000.0,
            rebalancing_frequency='monthly',
            transaction_costs=0.001,
            max_weight=0.3,
            risk_aversion=0.5,
            use_equal_weight_benchmark=False,  # Use SPY benchmark
            benchmark_ticker='SPY',
            signal_weights=signal_weights,
            forward_fill_signals=True
        )
        
        print(f"Benchmark type: SPY")
        print("Running backtest...")
        
        result_spy = backtest_engine.run_backtest(
            tickers=tickers,
            signals=signals,
            config=config_spy
        )
        
        print(f"Strategy return: {result_spy.total_return:.2%}")
        print(f"SPY benchmark return: {result_spy.benchmark_values.iloc[-1] / config_spy.initial_capital - 1:.2%}")
        print(f"Outperformance: {result_spy.total_return - (result_spy.benchmark_values.iloc[-1] / config_spy.initial_capital - 1):.2%}")
        print()
        
        # Test 3: Comparison
        print("3. Benchmark Comparison:")
        print("-" * 25)
        
        equal_weight_return = result_equal_weight.benchmark_values.iloc[-1] / config_equal_weight.initial_capital - 1
        spy_return = result_spy.benchmark_values.iloc[-1] / config_spy.initial_capital - 1
        
        print(f"Strategy performance: {result_equal_weight.total_return:.2%}")
        print(f"Equal-weight benchmark: {equal_weight_return:.2%}")
        print(f"SPY benchmark: {spy_return:.2%}")
        print()
        
        print("Strategy vs Equal-weight:")
        print(f"  Outperformance: {result_equal_weight.total_return - equal_weight_return:.2%}")
        print(f"  Alpha: {result_equal_weight.alpha:.2%}")
        print(f"  Beta: {result_equal_weight.beta:.2f}")
        print()
        
        print("Strategy vs SPY:")
        print(f"  Outperformance: {result_spy.total_return - spy_return:.2%}")
        print(f"  Alpha: {result_spy.alpha:.2%}")
        print(f"  Beta: {result_spy.beta:.2f}")
        print()
        
        # Test 4: Equal-weight calculation verification
        print("4. Equal-Weight Calculation Verification:")
        print("-" * 45)
        
        # Get price data for verification
        price_data = price_fetcher.get_price_matrix(tickers, start_date, end_date)
        
        if not price_data.empty:
            # Calculate equal-weight returns manually
            returns = price_data.pct_change().dropna()
            equal_weight_returns = returns.mean(axis=1)
            equal_weight_cumulative = (1 + equal_weight_returns).cumprod()
            manual_equal_weight_return = equal_weight_cumulative.iloc[-1] - 1
            
            print(f"Manual equal-weight calculation: {manual_equal_weight_return:.2%}")
            print(f"System equal-weight calculation: {equal_weight_return:.2%}")
            print(f"Difference: {abs(manual_equal_weight_return - equal_weight_return):.4%}")
            
            if abs(manual_equal_weight_return - equal_weight_return) < 0.01:  # Within 1%
                print("✅ Equal-weight calculation is correct!")
            else:
                print("⚠️  Equal-weight calculation may have issues")
        else:
            print("Could not verify equal-weight calculation (no price data)")
        
        print("\nEqual-weight benchmark test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error testing equal-weight benchmark: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    success = test_equal_weight_benchmark()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

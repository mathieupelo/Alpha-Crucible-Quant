#!/usr/bin/env python3
"""
Test script to demonstrate forward-fill functionality for signal scores.

This script shows how the system handles missing signal scores by using
the latest available scores from previous dates.
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import DatabaseManager
from signals import SignalCalculator
from utils import PriceFetcher


def test_forward_fill():
    """Test forward-fill functionality for signal scores."""
    print("Testing Forward-Fill Functionality")
    print("=" * 40)
    
    try:
        # Initialize components
        print("Initializing components...")
        price_fetcher = PriceFetcher()
        db_manager = DatabaseManager()
        signal_calculator = SignalCalculator(db_manager)
        
        if not db_manager.connect():
            print("Failed to connect to database")
            return False
        
        # Test parameters
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        signals = ['RSI', 'SMA']
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        print(f"Testing with tickers: {tickers}")
        print(f"Signals: {signals}")
        print(f"Date range: {start_date} to {end_date}")
        
        # Test 1: Get signal scores without forward fill
        print("\n1. Testing WITHOUT forward fill:")
        print("-" * 35)
        
        signal_scores_no_ff = signal_calculator.get_signal_scores_pivot(
            tickers, signals, start_date, end_date, forward_fill=False
        )
        
        if not signal_scores_no_ff.empty:
            print(f"Signal scores shape: {signal_scores_no_ff.shape}")
            print("Sample data (first 5 rows):")
            print(signal_scores_no_ff.head().round(4))
            
            # Count missing values
            missing_count = signal_scores_no_ff.isna().sum().sum()
            total_values = signal_scores_no_ff.size
            print(f"\nMissing values: {missing_count}/{total_values} ({missing_count/total_values*100:.1f}%)")
        else:
            print("No signal scores found without forward fill")
        
        # Test 2: Get signal scores with forward fill
        print("\n2. Testing WITH forward fill:")
        print("-" * 32)
        
        signal_scores_with_ff = signal_calculator.get_signal_scores_pivot(
            tickers, signals, start_date, end_date, forward_fill=True
        )
        
        if not signal_scores_with_ff.empty:
            print(f"Signal scores shape: {signal_scores_with_ff.shape}")
            print("Sample data (first 5 rows):")
            print(signal_scores_with_ff.head().round(4))
            
            # Count missing values
            missing_count = signal_scores_with_ff.isna().sum().sum()
            total_values = signal_scores_with_ff.size
            print(f"\nMissing values: {missing_count}/{total_values} ({missing_count/total_values*100:.1f}%)")
        else:
            print("No signal scores found with forward fill")
        
        # Test 3: Compare the two approaches
        print("\n3. Comparison:")
        print("-" * 15)
        
        if not signal_scores_no_ff.empty and not signal_scores_with_ff.empty:
            # Check if forward fill reduced missing values
            missing_no_ff = signal_scores_no_ff.isna().sum().sum()
            missing_with_ff = signal_scores_with_ff.isna().sum().sum()
            
            print(f"Missing values without forward fill: {missing_no_ff}")
            print(f"Missing values with forward fill: {missing_with_ff}")
            
            if missing_with_ff < missing_no_ff:
                print(f"✅ Forward fill reduced missing values by {missing_no_ff - missing_with_ff}")
            elif missing_with_ff == missing_no_ff:
                print("ℹ️  Forward fill had no effect (no missing values to fill)")
            else:
                print("⚠️  Unexpected: forward fill increased missing values")
        
        # Test 4: Demonstrate forward fill behavior
        print("\n4. Forward Fill Behavior:")
        print("-" * 25)
        
        if not signal_scores_with_ff.empty:
            # Show how forward fill works for a specific ticker-signal combination
            for ticker in tickers[:2]:  # Show first 2 tickers
                for signal in signals:
                    column = (ticker, signal)
                    if column in signal_scores_with_ff.columns:
                        series = signal_scores_with_ff[column].dropna()
                        if len(series) > 0:
                            print(f"{ticker}-{signal}:")
                            print(f"  First value: {series.iloc[0]:.4f} on {series.index[0]}")
                            print(f"  Last value: {series.iloc[-1]:.4f} on {series.index[-1]}")
                            print(f"  Total non-null values: {len(series)}")
                            break
        
        # Test 5: Test database manager directly
        print("\n5. Testing Database Manager Directly:")
        print("-" * 40)
        
        # Test without forward fill
        df_no_ff = db_manager.get_signal_scores_dataframe(
            tickers, signals, start_date, end_date, forward_fill=False
        )
        
        # Test with forward fill
        df_with_ff = db_manager.get_signal_scores_dataframe(
            tickers, signals, start_date, end_date, forward_fill=True
        )
        
        print(f"Database query without forward fill: {df_no_ff.shape}")
        print(f"Database query with forward fill: {df_with_ff.shape}")
        
        if not df_no_ff.empty and not df_with_ff.empty:
            missing_no_ff = df_no_ff.isna().sum().sum()
            missing_with_ff = df_with_ff.isna().sum().sum()
            print(f"Missing values - No FF: {missing_no_ff}, With FF: {missing_with_ff}")
        
        db_manager.disconnect()
        print("\nForward-fill test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error testing forward fill: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    success = test_forward_fill()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

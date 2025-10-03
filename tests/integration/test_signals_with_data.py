#!/usr/bin/env python3
"""
Test script for signals with data reading.

This script tests that signals can be read from the database
and combined without requiring signal calculation.
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from signals import SignalReader


def test_individual_signals():
    """Test individual signals with data reading."""
    print("Testing Individual Signals with Data Reading")
    print("=" * 50)
    
    # Initialize signal reader
    from unittest.mock import Mock
    database_manager = Mock()
    signal_reader = SignalReader(database_manager)
    
    # Test tickers and dates
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    test_date = date(2024, 1, 31)  # Use a date we know has data
    
    print(f"Testing signals for date: {test_date}")
    print(f"Tickers: {', '.join(tickers)}")
    print()
    
    # Mock signal data
    mock_signal_data = pd.DataFrame([
        {'ticker': 'AAPL', 'signal_id': 'SENTIMENT', 'asof_date': test_date, 'value': 0.5},
        {'ticker': 'MSFT', 'signal_id': 'SENTIMENT', 'asof_date': test_date, 'value': 0.3},
        {'ticker': 'GOOGL', 'signal_id': 'SENTIMENT', 'asof_date': test_date, 'value': 0.7},
    ])
    database_manager.get_signals.return_value = mock_signal_data
    
    # Test reading signals
    print("1. Testing Signal Reading:")
    
    for ticker in tickers:
        try:
            signal_value = signal_reader.read_signal_for_ticker(ticker, 'SENTIMENT', test_date)
            if signal_value is not None and not np.isnan(signal_value):
                print(f"  {ticker}: {signal_value:.4f}")
            else:
                print(f"  {ticker}: No data available")
        except Exception as e:
            print(f"  {ticker}: Error - {e}")
    print()


def test_signal_reader():
    """Test signal reader with data reading."""
    print("Testing Signal Reader with Data Reading")
    print("=" * 50)
    
    # Initialize signal reader
    from unittest.mock import Mock
    database_manager = Mock()
    signal_reader = SignalReader(database_manager)
    
    # Test parameters
    tickers = ['AAPL', 'MSFT']
    signals = ['SENTIMENT']
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Signals: {', '.join(signals)}")
    print(f"Date range: {start_date} to {end_date}")
    print()
    
    # Mock signal data
    mock_signal_data = pd.DataFrame([
        {'ticker': 'AAPL', 'signal_id': 'SENTIMENT', 'asof_date': date(2024, 1, 15), 'value': 0.5},
        {'ticker': 'AAPL', 'signal_id': 'SENTIMENT', 'asof_date': date(2024, 1, 31), 'value': 0.6},
        {'ticker': 'MSFT', 'signal_id': 'SENTIMENT', 'asof_date': date(2024, 1, 15), 'value': 0.3},
        {'ticker': 'MSFT', 'signal_id': 'SENTIMENT', 'asof_date': date(2024, 1, 31), 'value': 0.4},
    ])
    database_manager.get_signals.return_value = mock_signal_data
    
    try:
        # Read signals
        print("Reading signals...")
        signal_df = signal_reader.read_signals(
            tickers=tickers,
            signals=signals,
            start_date=start_date,
            end_date=end_date
        )
        
        if not signal_df.empty:
            print(f"✓ Successfully read {len(signal_df)} signal values")
            print()
            
            # Show sample results
            print("Sample Results:")
            print("-" * 30)
            
            # Group by ticker and signal
            for ticker in tickers:
                print(f"\n{ticker}:")
                ticker_data = signal_df[signal_df['ticker'] == ticker]
                
                for signal in signals:
                    signal_data = ticker_data[ticker_data['signal_id'] == signal]
                    if not signal_data.empty:
                        # Get the latest value
                        latest = signal_data.iloc[-1]
                        print(f"  {signal}: {latest['value']:.4f} (on {latest['asof_date']})")
                    else:
                        print(f"  {signal}: No data")
            
            # Show summary statistics
            print(f"\nSummary Statistics:")
            print(f"  Total signals read: {len(signal_df)}")
            print(f"  Unique tickers: {signal_df['ticker'].nunique()}")
            print(f"  Unique signals: {signal_df['signal_id'].nunique()}")
            print(f"  Date range: {signal_df['asof_date'].min()} to {signal_df['asof_date'].max()}")
            
            # Check for NaN values
            nan_count = signal_df['value'].isna().sum()
            if nan_count > 0:
                print(f"  ⚠ Warning: {nan_count} NaN values found")
            else:
                print(f"  ✓ No NaN values found")
                
        else:
            print("❌ No signals read")
            
    except Exception as e:
        print(f"❌ Error reading signals: {e}")
        import traceback
        traceback.print_exc()


def test_signal_combination():
    """Test signal combination functionality."""
    print("\nTesting Signal Combination")
    print("=" * 30)
    
    # Initialize signal reader
    from unittest.mock import Mock
    database_manager = Mock()
    signal_reader = SignalReader(database_manager)
    
    # Test parameters
    tickers = ['AAPL', 'MSFT']
    signals = ['SENTIMENT']
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    # Mock signal data
    mock_signal_data = pd.DataFrame([
        {'ticker': 'AAPL', 'signal_id': 'SENTIMENT', 'asof_date': date(2024, 1, 15), 'value': 0.5},
        {'ticker': 'AAPL', 'signal_id': 'SENTIMENT', 'asof_date': date(2024, 1, 31), 'value': 0.6},
        {'ticker': 'MSFT', 'signal_id': 'SENTIMENT', 'asof_date': date(2024, 1, 15), 'value': 0.3},
        {'ticker': 'MSFT', 'signal_id': 'SENTIMENT', 'asof_date': date(2024, 1, 31), 'value': 0.4},
    ])
    database_manager.get_signals.return_value = mock_signal_data
    
    try:
        # Read and combine signals
        print("Reading and combining signal scores...")
        combined_df = signal_reader.combine_signals_to_scores(
            tickers=tickers,
            signal_names=signals,
            start_date=start_date,
            end_date=end_date,
            method='equal_weight'
        )
        
        if not combined_df.empty:
            print(f"✓ Successfully combined {len(combined_df)} signal scores")
            print()
            
            # Show sample results
            print("Sample Combined Scores:")
            print("-" * 25)
            
            for ticker in tickers:
                ticker_scores = combined_df[combined_df['ticker'] == ticker]
                if not ticker_scores.empty:
                    latest_score = ticker_scores.iloc[-1]
                    print(f"  {ticker}: {latest_score['score']:.4f} (on {latest_score['asof_date']})")
                else:
                    print(f"  {ticker}: No combined scores")
                    
        else:
            print("❌ No combined scores calculated")
            
    except Exception as e:
        print(f"❌ Error combining signals: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main test function."""
    print("Alpha Crucible Quant - Signal Data Reading Test")
    print("=" * 60)
    print()
    
    try:
        # Test individual signals
        test_individual_signals()
        
        # Test signal reader
        test_signal_reader()
        
        # Test signal combination
        test_signal_combination()
        
        print("\n🎉 All signal tests completed!")
        return 0
        
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

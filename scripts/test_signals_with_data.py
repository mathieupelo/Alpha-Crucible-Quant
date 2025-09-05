#!/usr/bin/env python3
"""
Test script for signals with automatic data fetching.

This script tests that signals can now automatically fetch price data
and calculate signal values without requiring pre-fetched data.
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data import RealTimeDataFetcher
from signals import SignalCalculator
from signals.sentiment import SentimentSignal


def test_individual_signals():
    """Test individual signals with automatic data fetching."""
    print("Testing Individual Signals with Data Fetching")
    print("=" * 50)
    
    # Initialize data fetcher
    data_fetcher = RealTimeDataFetcher()
    
    # Test tickers and dates
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    test_date = date(2024, 1, 31)  # Use a date we know has data
    
    print(f"Testing signals for date: {test_date}")
    print(f"Tickers: {', '.join(tickers)}")
    print()
    
    # Test Sentiment signal
    print("1. Testing Sentiment Signal:")
    sentiment_signal = SentimentSignal(seed=42, price_fetcher=data_fetcher)
    
    for ticker in tickers:
        try:
            signal_value = sentiment_signal.calculate_with_data_fetch(ticker, test_date)
            if not np.isnan(signal_value):
                print(f"  {ticker}: {signal_value:.4f}")
            else:
                print(f"  {ticker}: No data available")
        except Exception as e:
            print(f"  {ticker}: Error - {e}")
    print()


def test_signal_calculator():
    """Test signal calculator with automatic data fetching."""
    print("Testing Signal Calculator with Data Fetching")
    print("=" * 50)
    
    # Initialize signal calculator
    data_fetcher = RealTimeDataFetcher()
    signal_calculator = SignalCalculator(price_fetcher=data_fetcher)
    
    # Test parameters
    tickers = ['AAPL', 'MSFT']
    signals = ['SENTIMENT']
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Signals: {', '.join(signals)}")
    print(f"Date range: {start_date} to {end_date}")
    print()
    
    try:
        # Calculate signals
        print("Calculating signals...")
        signal_df = signal_calculator.calculate_signals(
            tickers=tickers,
            signals=signals,
            start_date=start_date,
            end_date=end_date,
            store_in_db=False  # Don't store in database for testing
        )
        
        if not signal_df.empty:
            print(f"✓ Successfully calculated {len(signal_df)} signal values")
            print()
            
            # Show sample results
            print("Sample Results:")
            print("-" * 30)
            
            # Group by ticker and signal
            for ticker in tickers:
                print(f"\n{ticker}:")
                ticker_data = signal_df[signal_df['ticker'] == ticker]
                
                for signal in signals:
                    signal_data = ticker_data[ticker_data['signal_name'] == signal]
                    if not signal_data.empty:
                        # Get the latest value
                        latest = signal_data.iloc[-1]
                        print(f"  {signal}: {latest['value']:.4f} (on {latest['asof_date']})")
                    else:
                        print(f"  {signal}: No data")
            
            # Show summary statistics
            print(f"\nSummary Statistics:")
            print(f"  Total signals calculated: {len(signal_df)}")
            print(f"  Unique tickers: {signal_df['ticker'].nunique()}")
            print(f"  Unique signals: {signal_df['signal_name'].nunique()}")
            print(f"  Date range: {signal_df['asof_date'].min()} to {signal_df['asof_date'].max()}")
            
            # Check for NaN values
            nan_count = signal_df['value'].isna().sum()
            if nan_count > 0:
                print(f"  ⚠ Warning: {nan_count} NaN values found")
            else:
                print(f"  ✓ No NaN values found")
                
        else:
            print("❌ No signals calculated")
            
    except Exception as e:
        print(f"❌ Error calculating signals: {e}")
        import traceback
        traceback.print_exc()


def test_signal_combination():
    """Test signal combination functionality."""
    print("\nTesting Signal Combination")
    print("=" * 30)
    
    # Initialize signal calculator
    data_fetcher = RealTimeDataFetcher()
    signal_calculator = SignalCalculator(price_fetcher=data_fetcher)
    
    # Test parameters
    tickers = ['AAPL', 'MSFT']
    signals = ['SENTIMENT']
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    try:
        # Calculate combined scores
        print("Calculating combined signal scores...")
        combined_df = signal_calculator.combine_signals_to_scores(
            tickers=tickers,
            signal_names=signals,
            start_date=start_date,
            end_date=end_date,
            method='equal_weight',
            store_in_db=False
        )
        
        if not combined_df.empty:
            print(f"✓ Successfully calculated {len(combined_df)} combined scores")
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
        print(f"❌ Error calculating combined scores: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main test function."""
    print("Alpha Crucible Quant - Signal Data Fetching Test")
    print("=" * 60)
    print()
    
    try:
        # Test individual signals
        test_individual_signals()
        
        # Test signal calculator
        test_signal_calculator()
        
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

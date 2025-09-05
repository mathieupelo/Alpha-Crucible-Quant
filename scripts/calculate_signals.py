#!/usr/bin/env python3
"""
Example script to calculate signals using the Quant Project system.

This script demonstrates how to calculate signals for a set of tickers.
For SENTIMENT signals, no real price data is needed.
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from signals import SignalCalculator
from database import DatabaseManager


def main():
    """Calculate signals for a set of tickers."""
    print("Quant Project - Signal Calculation Example")
    print("=" * 50)
    
    # Configuration (match backtest tickers)
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
    signals = ['SENTIMENT']
    
    # Date range (last 2 years to match backtest)
    end_date = date.today()
    start_date = end_date - timedelta(days=730)
    
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Signals: {', '.join(signals)}")
    print(f"Date range: {start_date} to {end_date}")
    print()
    
    try:
        # Initialize components (no price fetcher needed for SENTIMENT signals)
        print("Initializing components...")
        database_manager = DatabaseManager()
        signal_calculator = SignalCalculator(price_fetcher=None, database_manager=database_manager)
        
        # Calculate raw signals
        print("Calculating raw signals...")
        raw_signals = signal_calculator.calculate_signals(
            tickers=tickers,
            signals=signals,
            start_date=start_date,
            end_date=end_date,
            store_in_db=True
        )
        
        if raw_signals.empty:
            print("No raw signals calculated!")
            return 1
        
        print(f"Calculated {len(raw_signals)} raw signals")
        print()
        
        # Display sample results
        print("SAMPLE RAW SIGNALS:")
        print("-" * 50)
        
        # Group by ticker and show recent signals
        for ticker in tickers:
            ticker_signals = raw_signals[raw_signals['ticker'] == ticker]
            if not ticker_signals.empty:
                print(f"\n{ticker}:")
                recent_signals = ticker_signals.sort_values('asof_date').tail(3)
                for _, row in recent_signals.iterrows():
                    print(f"  {row['asof_date']}: {row['signal_name']} = {row['value']:.3f}")
        
        print()
        
        # Show signal statistics
        print("SIGNAL STATISTICS:")
        print("-" * 50)
        
        for signal in signals:
            signal_data = raw_signals[raw_signals['signal_name'] == signal]
            if not signal_data.empty:
                values = signal_data['value']
                print(f"\n{signal}:")
                print(f"  Count: {len(values)}")
                print(f"  Mean: {values.mean():.3f}")
                print(f"  Std: {values.std():.3f}")
                print(f"  Min: {values.min():.3f}")
                print(f"  Max: {values.max():.3f}")
        
        print()
        
        # Combine signals into scores
        print("COMBINING SIGNALS INTO SCORES...")
        combined_scores = signal_calculator.combine_signals_to_scores(
            tickers=tickers,
            signal_names=signals,
            start_date=start_date,
            end_date=end_date,
            method='equal_weight',
            store_in_db=True
        )
        
        if not combined_scores.empty:
            print(f"Combined {len(combined_scores)} scores")
            
            # Show sample combined scores
            print("\nSAMPLE COMBINED SCORES:")
            print("-" * 50)
            for ticker in tickers:
                ticker_scores = combined_scores[combined_scores['ticker'] == ticker]
                if not ticker_scores.empty:
                    print(f"\n{ticker}:")
                    recent_scores = ticker_scores.sort_values('asof_date').tail(3)
                    for _, row in recent_scores.iterrows():
                        print(f"  {row['asof_date']}: score = {row['score']:.3f}")
        else:
            print("No combined scores calculated")
        
        print()
        print("Signal calculation completed successfully!")
        
    except Exception as e:
        print(f"Error calculating signals: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

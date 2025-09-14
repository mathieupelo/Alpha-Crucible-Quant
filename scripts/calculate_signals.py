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
    
    # Initialize database manager first
    database_manager = DatabaseManager()
    if not database_manager.connect():
        print("Error: Failed to connect to database")
        return 1
    
    # Get tickers from universe (default universe ID 1)
    try:
        universe_tickers_df = database_manager.get_universe_tickers(1)  # Default universe
        if universe_tickers_df.empty:
            print("Error: No tickers found in universe 1. Please run setup_database.py first.")
            return 1
        
        tickers = universe_tickers_df['ticker'].tolist()
        print(f"Retrieved {len(tickers)} tickers from universe 1: {', '.join(tickers)}")
    except Exception as e:
        print(f"Error retrieving tickers from database: {e}")
        print("Falling back to hardcoded tickers...")
        tickers = ['EA', 'TTWO', 'RBLX', 'MSFT', 'SONY', 'NTES', 'WBD', 'NCBDY', 'GDEV', 'OTGLF']
        tickers = ['EA', 'TTWO', 'NTES']
    
    signals = ['SENTIMENT', 'SENTIMENT_YT']
    tickers = ['EA', 'TTWO', 'NTES']
    
    # Date range (last 2 years to match backtest)
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    #start_date = date(2020, 1, 1)
    
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Signals: {', '.join(signals)}")
    print(f"Date range: {start_date} to {end_date}")
    print()
    
    try:
        # Initialize signal calculator (database_manager already initialized)
        print("Initializing signal calculator...")
        signal_calculator = SignalCalculator(database_manager=database_manager)
        
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
        print("Signal calculation completed successfully!")
        print("Note: Signal combination will be handled during portfolio creation.")
        
    except Exception as e:
        print(f"Error calculating signals: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

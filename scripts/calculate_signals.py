#!/usr/bin/env python3
"""
Example script to calculate signals using the Quant Project system.

This script demonstrates how to calculate signals for a set of tickers.
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from signals import SignalCalculator
from database import DatabaseManager
from utils import PriceFetcher


def main():
    """Calculate signals for a set of tickers."""
    print("Quant Project - Signal Calculation Example")
    print("=" * 50)
    
    # Configuration (match backtest tickers)
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
    signals = ['RSI', 'SMA', 'MACD']
    
    # Date range (last 2 years to match backtest)
    end_date = date.today()
    start_date = end_date - timedelta(days=730)
    
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Signals: {', '.join(signals)}")
    print(f"Date range: {start_date} to {end_date}")
    print()
    
    try:
        # Initialize components
        print("Initializing components...")
        price_fetcher = PriceFetcher()
        database_manager = DatabaseManager()
        signal_calculator = SignalCalculator(price_fetcher, database_manager)
        
        # Calculate signals
        print("Calculating signals...")
        signal_scores = signal_calculator.calculate_signals(
            tickers=tickers,
            signals=signals,
            start_date=start_date,
            end_date=end_date,
            store_in_db=True
        )
        
        if signal_scores.empty:
            print("No signal scores calculated!")
            return 1
        
        print(f"Calculated {len(signal_scores)} signal scores")
        print()
        
        # Display sample results
        print("SAMPLE SIGNAL SCORES:")
        print("-" * 50)
        
        # Group by ticker and show recent scores
        for ticker in tickers:
            ticker_scores = signal_scores[signal_scores['ticker'] == ticker]
            if not ticker_scores.empty:
                print(f"\n{ticker}:")
                recent_scores = ticker_scores.sort_values('date').tail(3)
                for _, row in recent_scores.iterrows():
                    print(f"  {row['date']}: {row['signal_id']} = {row['score']:.3f}")
        
        print()
        
        # Show signal statistics
        print("SIGNAL STATISTICS:")
        print("-" * 50)
        
        for signal in signals:
            signal_data = signal_scores[signal_scores['signal_id'] == signal]
            if not signal_data.empty:
                scores = signal_data['score']
                print(f"\n{signal}:")
                print(f"  Count: {len(scores)}")
                print(f"  Mean: {scores.mean():.3f}")
                print(f"  Std: {scores.std():.3f}")
                print(f"  Min: {scores.min():.3f}")
                print(f"  Max: {scores.max():.3f}")
        
        print()
        
        # Show missing signals
        print("CHECKING FOR MISSING SIGNALS...")
        missing_signals = signal_calculator.get_missing_signals(
            tickers, signals, start_date, end_date
        )
        
        if missing_signals:
            print(f"Found {len(missing_signals)} missing signal calculations")
            print("Calculating missing signals...")
            
            missing_scores = signal_calculator.calculate_missing_signals(
                tickers, signals, start_date, end_date
            )
            
            if not missing_scores.empty:
                print(f"Calculated {len(missing_scores)} missing signal scores")
            else:
                print("No missing signals could be calculated")
        else:
            print("No missing signals found")
        
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

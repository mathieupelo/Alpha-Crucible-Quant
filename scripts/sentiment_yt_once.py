#!/usr/bin/env python3
"""
Simple script to test YouTube sentiment signal calculation for one ticker and one date.
This is a dev-only script for quick testing of sentiment_yt.py changes.
"""

import sys
import os
from pathlib import Path
from datetime import date
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from signals.sentiment_yt import SentimentSignalYT


def main():
    """Test YouTube sentiment calculation for one ticker and date."""
    print("YouTube Sentiment Signal Test")
    print("=" * 40)
    
    # Test parameters
    ticker = "TTWO"  # Take-Two Interactive (has GTA VI trailer)
    target_date = date(2024, 1, 15)  # Test date
    
    print(f"Ticker: {ticker}")
    print(f"Target Date: {target_date}")
    print()
    
    try:
        # Initialize the YouTube sentiment signal
        print("Initializing YouTube sentiment signal...")
        signal = SentimentSignalYT(seed=42)  # Use seed for reproducible results
        
        print("Calculating sentiment...")
        print("-" * 20)
        
        # Calculate the sentiment signal (price_data is ignored for sentiment signals)
        sentiment_value = signal.calculate(
            price_data=None,  # Sentiment signals don't use price data
            ticker=ticker,
            target_date=target_date
        )
        
        print(f"\nResult:")
        print(f"Sentiment Value: {sentiment_value}")
        print(f"Type: {type(sentiment_value)}")
        
        if pd.isna(sentiment_value):
            print("Note: Result is NaN (no data available or error occurred)")
        else:
            print(f"Interpretation: {'Positive' if sentiment_value > 0 else 'Negative' if sentiment_value < 0 else 'Neutral'} sentiment")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

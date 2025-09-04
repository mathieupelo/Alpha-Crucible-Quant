#!/usr/bin/env python3
"""
Demo script showing forward-fill functionality for signal scores.

This script demonstrates how the system handles missing signal scores
by using the latest available scores from previous dates.
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def demo_forward_fill():
    """Demonstrate forward-fill functionality with sample data."""
    print("Forward-Fill Signal Scores Demo")
    print("=" * 35)
    
    # Create sample signal score data with gaps
    print("1. Creating sample signal score data with gaps...")
    
    dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    signals = ['RSI', 'SMA']
    
    # Create data with intentional gaps
    data = []
    for dt in dates:
        for ticker in tickers:
            for signal in signals:
                # Create gaps on weekends and some random days
                if dt.weekday() < 5 and np.random.random() > 0.3:  # 70% chance of data
                    score = np.random.random()  # Random score between 0 and 1
                    data.append({
                        'date': dt.date(),
                        'ticker': ticker,
                        'signal_id': signal,
                        'score': score
                    })
    
    df = pd.DataFrame(data)
    print(f"Created {len(df)} signal score records")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Tickers: {sorted(df['ticker'].unique())}")
    print(f"Signals: {sorted(df['signal_id'].unique())}")
    
    # Create pivot table
    print("\n2. Creating pivot table...")
    pivot_df = df.pivot_table(
        index='date',
        columns=['ticker', 'signal_id'],
        values='score',
        aggfunc='first'
    )
    
    print(f"Pivot table shape: {pivot_df.shape}")
    print("Sample data (first 5 rows):")
    print(pivot_df.head().round(4))
    
    # Show missing values
    print("\n3. Analyzing missing values...")
    missing_count = pivot_df.isna().sum().sum()
    total_values = pivot_df.size
    missing_pct = missing_count / total_values * 100
    
    print(f"Missing values: {missing_count}/{total_values} ({missing_pct:.1f}%)")
    
    # Show missing values by date
    missing_by_date = pivot_df.isna().sum(axis=1)
    print("\nMissing values by date:")
    for dt, missing in missing_by_date.items():
        if missing > 0:
            print(f"  {dt}: {missing} missing values")
    
    # Apply forward fill
    print("\n4. Applying forward fill...")
    pivot_df_ff = pivot_df.ffill()
    
    # Show results after forward fill
    missing_count_ff = pivot_df_ff.isna().sum().sum()
    missing_pct_ff = missing_count_ff / total_values * 100
    
    print(f"Missing values after forward fill: {missing_count_ff}/{total_values} ({missing_pct_ff:.1f}%)")
    print(f"Reduction in missing values: {missing_count - missing_count_ff}")
    
    # Show sample data after forward fill
    print("\nSample data after forward fill (first 5 rows):")
    print(pivot_df_ff.head().round(4))
    
    # Demonstrate forward fill behavior for a specific ticker-signal
    print("\n5. Forward fill behavior example:")
    print("-" * 35)
    
    # Pick a ticker-signal combination with gaps
    for ticker in tickers:
        for signal in signals:
            column = (ticker, signal)
            if column in pivot_df.columns:
                series_orig = pivot_df[column]
                series_ff = pivot_df_ff[column]
                
                # Check if this series has gaps
                if series_orig.isna().any():
                    print(f"\n{ticker}-{signal}:")
                    print("Original data:")
                    for dt, value in series_orig.items():
                        if pd.isna(value):
                            print(f"  {dt}: NaN")
                        else:
                            print(f"  {dt}: {value:.4f}")
                    
                    print("After forward fill:")
                    for dt, value in series_ff.items():
                        if pd.isna(value):
                            print(f"  {dt}: NaN")
                        else:
                            print(f"  {dt}: {value:.4f}")
                    break
        else:
            continue
        break
    
    # Show how this would work in backtesting
    print("\n6. Backtesting scenario:")
    print("-" * 25)
    
    # Simulate a rebalancing date with missing data
    rebalancing_date = date(2023, 1, 5)  # A date that might have missing data
    
    print(f"Rebalancing on {rebalancing_date}:")
    
    if rebalancing_date in pivot_df.index:
        # Check original data
        orig_data = pivot_df.loc[rebalancing_date]
        missing_orig = orig_data.isna().sum()
        
        # Check forward-filled data
        ff_data = pivot_df_ff.loc[rebalancing_date]
        missing_ff = ff_data.isna().sum()
        
        print(f"  Missing signal scores (original): {missing_orig}")
        print(f"  Missing signal scores (forward-filled): {missing_ff}")
        
        if missing_orig > 0 and missing_ff < missing_orig:
            print(f"  ✅ Forward fill would enable rebalancing (reduced missing from {missing_orig} to {missing_ff})")
        elif missing_orig == 0:
            print(f"  ℹ️  No missing data on this date")
        else:
            print(f"  ⚠️  Still {missing_ff} missing values after forward fill")
    
    print("\n7. Summary:")
    print("-" * 10)
    print(f"• Original data had {missing_count} missing values ({missing_pct:.1f}%)")
    print(f"• After forward fill: {missing_count_ff} missing values ({missing_pct_ff:.1f}%)")
    print(f"• Forward fill reduced missing values by {missing_count - missing_count_ff}")
    print(f"• This enables more continuous portfolio rebalancing")
    print(f"• Strategy can continue using the latest available signal scores")
    
    return True


def main():
    """Main demo function."""
    try:
        success = demo_forward_fill()
        if success:
            print("\n✅ Forward-fill demo completed successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Error in forward-fill demo: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

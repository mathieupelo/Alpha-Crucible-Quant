#!/usr/bin/env python3
"""
Test Portfolio Signals

Simple test script to verify the dynamic signal columns work correctly.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.database_service import DatabaseService

def test_portfolio_signals():
    """Test portfolio signals with dynamic columns."""
    print("Testing portfolio signals with dynamic columns...")
    
    try:
        # Initialize database service
        db_service = DatabaseService()
        
        # Get all portfolios to test with
        portfolios = db_service.get_all_backtests()
        print(f"Found {len(portfolios.get('backtests', []))} backtests")
        
        # Test with the first portfolio if available
        if portfolios.get('backtests'):
            first_backtest = portfolios['backtests'][0]
            print(f"Testing with backtest: {first_backtest['run_id']}")
            
            # Get portfolios for this backtest
            portfolios_data = db_service.get_backtest_portfolios(first_backtest['run_id'])
            print(f"Found {len(portfolios_data)} portfolios")
            
            if portfolios_data:
                first_portfolio = portfolios_data[0]
                print(f"Testing with portfolio ID: {first_portfolio['id']}")
                
                # Get signal data
                signals = db_service.get_portfolio_signals(first_portfolio['id'])
                print(f"Found {len(signals)} signal entries")
                
                if signals:
                    print("\nSignal data structure:")
                    print(f"First entry keys: {list(signals[0].keys())}")
                    
                    if 'available_signals' in signals[0]:
                        print(f"Available signals: {signals[0]['available_signals']}")
                    
                    # Show sample data
                    print("\nSample signal data:")
                    for i, signal in enumerate(signals[:3]):  # Show first 3 entries
                        print(f"  {i+1}. {signal['ticker']}: {signal}")
                else:
                    print("No signal data found for this portfolio")
            else:
                print("No portfolios found for this backtest")
        else:
            print("No backtests found to test with")
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db_service.close()
        except:
            pass

if __name__ == "__main__":
    success = test_portfolio_signals()
    if not success:
        sys.exit(1)

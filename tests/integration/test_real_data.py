#!/usr/bin/env python3
"""
Test script for real-time data integration.

This script tests the real-time data fetching capabilities and validates
that the system can successfully fetch and process real market data.
"""

import sys
import os
from pathlib import Path
from datetime import date, timedelta
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from data import RealTimeDataFetcher, DataValidator
from utils import PriceFetcher


def test_real_data_fetching():
    """Test real-time data fetching capabilities."""
    print("Alpha Crucible Quant - Real-Time Data Test")
    print("=" * 50)
    
    # Initialize components
    data_fetcher = RealTimeDataFetcher()
    data_validator = DataValidator()
    price_fetcher = PriceFetcher()
    
    # Test tickers
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    test_date = date(2024, 1, 15)
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    print(f"Testing with tickers: {', '.join(test_tickers)}")
    print(f"Test date: {test_date}")
    print(f"Date range: {start_date} to {end_date}")
    print()
    
    # Test 1: Ticker validation
    print("1. Testing ticker validation...")
    for ticker in test_tickers:
        is_valid = data_fetcher.validate_ticker(ticker)
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"  {ticker}: {status}")
    print()
    
    # Test 2: Single price fetching
    print("2. Testing single price fetching...")
    for ticker in test_tickers[:3]:  # Test first 3 tickers
        price = data_fetcher.get_price(ticker, test_date)
        if price is not None:
            print(f"  {ticker} on {test_date}: ${price:.2f}")
        else:
            print(f"  {ticker} on {test_date}: No data available")
    print()
    
    # Test 3: Multiple prices fetching
    print("3. Testing multiple prices fetching...")
    prices = data_fetcher.get_prices(test_tickers, test_date)
    for ticker, price in prices.items():
        if price is not None:
            print(f"  {ticker}: ${price:.2f}")
        else:
            print(f"  {ticker}: No data available")
    print()
    
    # Test 4: Price history fetching
    print("4. Testing price history fetching...")
    for ticker in test_tickers[:2]:  # Test first 2 tickers
        history = data_fetcher.get_price_history(ticker, start_date, end_date)
        if history is not None and not history.empty:
            print(f"  {ticker}: {len(history)} days of data")
            print(f"    Date range: {history.index.min()} to {history.index.max()}")
            print(f"    Price range: ${history['Close'].min():.2f} to ${history['Close'].max():.2f}")
        else:
            print(f"  {ticker}: No data available")
    print()
    
    # Test 5: Price matrix fetching
    print("5. Testing price matrix fetching...")
    price_matrix = data_fetcher.get_price_matrix(test_tickers, start_date, end_date)
    if price_matrix is not None and not price_matrix.empty:
        print(f"  Price matrix: {price_matrix.shape[0]} days x {price_matrix.shape[1]} tickers")
        print(f"  Date range: {price_matrix.index.min()} to {price_matrix.index.max()}")
        print(f"  Tickers: {', '.join(price_matrix.columns)}")
    else:
        print("  Price matrix: No data available")
    print()
    
    # Test 6: Market status
    print("6. Testing market status...")
    market_status = data_fetcher.get_market_status()
    for exchange, is_open in market_status.items():
        status = "Open" if is_open else "Closed"
        print(f"  {exchange}: {status}")
    print()
    
    # Test 7: Trading calendar
    print("7. Testing trading calendar...")
    calendar = data_fetcher.get_trading_calendar(start_date, end_date)
    if not calendar.empty:
        trading_days = calendar[calendar['is_trading_day']]
        print(f"  Trading days: {len(trading_days)} out of {len(calendar)} total days")
        print(f"  Weekends: {calendar['is_weekend'].sum()}")
        print(f"  Holidays: {calendar['is_holiday'].sum()}")
    else:
        print("  Trading calendar: No data available")
    print()
    
    # Test 8: Data validation
    print("8. Testing data validation...")
    if price_matrix is not None and not price_matrix.empty:
        # Convert to OHLC format for validation
        ohlc_data = pd.DataFrame({
            'Open': price_matrix.iloc[:, 0],
            'High': price_matrix.iloc[:, 0] * 1.01,
            'Low': price_matrix.iloc[:, 0] * 0.99,
            'Close': price_matrix.iloc[:, 0],
            'Volume': 1000000
        })
        
        validation_result = data_validator.validate_price_data(ohlc_data)
        print(f"  Data validation: {'✓ Passed' if validation_result['is_valid'] else '✗ Failed'}")
        
        if validation_result['warnings']:
            print("  Warnings:")
            for warning in validation_result['warnings']:
                print(f"    - {warning}")
        
        if validation_result['errors']:
            print("  Errors:")
            for error in validation_result['errors']:
                print(f"    - {error}")
    else:
        print("  Data validation: Skipped (no data available)")
    print()
    
    # Test 9: Cache information
    print("9. Testing cache information...")
    cache_info = data_fetcher.get_cache_info()
    print(f"  Cache size: {cache_info['cache_size']} items")
    print(f"  Sample keys: {cache_info['cache_keys']}")
    print()
    
    # Test 10: Backward compatibility with PriceFetcher
    print("10. Testing backward compatibility...")
    for ticker in test_tickers[:2]:
        price1 = data_fetcher.get_price(ticker, test_date)
        price2 = price_fetcher.get_price(ticker, test_date)
        
        if price1 is not None and price2 is not None:
            diff = abs(price1 - price2)
            status = "✓ Match" if diff < 0.01 else f"✗ Different (diff: ${diff:.2f})"
            print(f"  {ticker}: {status}")
        else:
            print(f"  {ticker}: One or both prices unavailable")
    print()
    
    print("Real-time data testing completed!")
    return True


def test_data_quality():
    """Test data quality and validation."""
    print("\nData Quality Test")
    print("=" * 30)
    
    data_fetcher = RealTimeDataFetcher()
    data_validator = DataValidator()
    
    # Test with a known good ticker
    ticker = 'AAPL'
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    print(f"Testing data quality for {ticker}...")
    
    # Fetch data
    data = data_fetcher.get_price_history(ticker, start_date, end_date)
    
    if data is None or data.empty:
        print("No data available for quality testing")
        return False
    
    print(f"Fetched {len(data)} days of data")
    
    # Validate data
    validation_result = data_validator.validate_price_data(data)
    
    print(f"Validation result: {'✓ Valid' if validation_result['is_valid'] else '✗ Invalid'}")
    
    if validation_result['statistics']:
        stats = validation_result['statistics']
        print(f"Statistics:")
        print(f"  Rows: {stats.get('num_rows', 'N/A')}")
        print(f"  Columns: {stats.get('num_columns', 'N/A')}")
        print(f"  Date range: {stats.get('date_range', 'N/A')}")
        
        if 'close_stats' in stats:
            close_stats = stats['close_stats']
            print(f"  Close price stats:")
            print(f"    Min: ${close_stats.get('min', 0):.2f}")
            print(f"    Max: ${close_stats.get('max', 0):.2f}")
            print(f"    Mean: ${close_stats.get('mean', 0):.2f}")
            print(f"    Std: ${close_stats.get('std', 0):.2f}")
    
    if validation_result['warnings']:
        print("Warnings:")
        for warning in validation_result['warnings']:
            print(f"  - {warning}")
    
    if validation_result['errors']:
        print("Errors:")
        for error in validation_result['errors']:
            print(f"  - {error}")
    
    return validation_result['is_valid']


def main():
    """Main test function."""
    try:
        # Test real data fetching
        success1 = test_real_data_fetching()
        
        # Test data quality
        success2 = test_data_quality()
        
        if success1 and success2:
            print("\n🎉 All tests passed! Real-time data integration is working correctly.")
            return 0
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

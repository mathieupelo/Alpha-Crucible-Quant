#!/usr/bin/env python3
"""
Test Ticker Validation

Simple test script to verify ticker validation works with rate limiting.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.ticker_validation_service import TickerValidationService

def test_ticker_validation():
    """Test ticker validation with a few sample tickers."""
    print("Testing ticker validation with rate limiting...")
    
    # Initialize validator with conservative settings
    validator = TickerValidationService(
        timeout=15,
        max_retries=3,
        base_delay=2.0
    )
    
    # Test with a few common tickers
    test_tickers = ["AAPL", "MSFT", "GOOGL", "INVALID_TICKER"]
    
    print(f"Validating tickers: {test_tickers}")
    print("This may take a moment due to rate limiting...")
    
    try:
        results = validator.validate_tickers_batch(test_tickers, batch_size=1)
        
        print("\nValidation Results:")
        print("-" * 50)
        for result in results:
            status = "✅ VALID" if result['is_valid'] else "❌ INVALID"
            print(f"{result['ticker']}: {status}")
            if result['is_valid']:
                print(f"  Company: {result['company_name']}")
            else:
                print(f"  Error: {result['error_message']}")
            print()
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error during validation: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_ticker_validation()
    if not success:
        sys.exit(1)

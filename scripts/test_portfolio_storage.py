#!/usr/bin/env python3
"""
Test script to verify portfolio data storage functionality.

This script tests the new portfolio storage features without running a full backtest.
"""

import sys
import os
from pathlib import Path
from datetime import date, datetime, timedelta
import uuid

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import DatabaseManager, PortfolioValue, PortfolioWeight


def test_portfolio_storage():
    """Test portfolio data storage functionality."""
    print("Testing Portfolio Data Storage")
    print("=" * 40)
    
    try:
        # Initialize database manager
        print("Connecting to database...")
        db_manager = DatabaseManager()
        
        if not db_manager.connect():
            print("Failed to connect to database")
            return False
        
        # Create test data
        test_backtest_id = f"test_{uuid.uuid4().hex[:8]}"
        test_date = date.today()
        
        print(f"Creating test data with backtest ID: {test_backtest_id}")
        
        # Test portfolio values
        portfolio_values = [
            PortfolioValue(
                portfolio_value_id=str(uuid.uuid4()),
                backtest_id=test_backtest_id,
                date=test_date,
                portfolio_value=10000.0,
                benchmark_value=10000.0,
                portfolio_return=0.0,
                benchmark_return=0.0,
                created_at=datetime.now()
            ),
            PortfolioValue(
                portfolio_value_id=str(uuid.uuid4()),
                backtest_id=test_backtest_id,
                date=test_date + timedelta(days=1),
                portfolio_value=10100.0,
                benchmark_value=10050.0,
                portfolio_return=0.01,
                benchmark_return=0.005,
                created_at=datetime.now()
            )
        ]
        
        # Test portfolio weights
        portfolio_weights = [
            PortfolioWeight(
                portfolio_weight_id=str(uuid.uuid4()),
                backtest_id=test_backtest_id,
                date=test_date,
                ticker="AAPL",
                weight=0.3,
                created_at=datetime.now()
            ),
            PortfolioWeight(
                portfolio_weight_id=str(uuid.uuid4()),
                backtest_id=test_backtest_id,
                date=test_date,
                ticker="MSFT",
                weight=0.4,
                created_at=datetime.now()
            ),
            PortfolioWeight(
                portfolio_weight_id=str(uuid.uuid4()),
                backtest_id=test_backtest_id,
                date=test_date,
                ticker="GOOGL",
                weight=0.3,
                created_at=datetime.now()
            )
        ]
        
        # Store test data
        print("Storing portfolio values...")
        values_stored = db_manager.store_portfolio_values(portfolio_values)
        print(f"Stored {values_stored} portfolio value records")
        
        print("Storing portfolio weights...")
        weights_stored = db_manager.store_portfolio_weights(portfolio_weights)
        print(f"Stored {weights_stored} portfolio weight records")
        
        # Retrieve and verify data
        print("\nRetrieving stored data...")
        
        # Get portfolio values
        retrieved_values = db_manager.get_portfolio_values(backtest_id=test_backtest_id)
        print(f"Retrieved {len(retrieved_values)} portfolio value records")
        
        if not retrieved_values.empty:
            print("Portfolio Values:")
            for _, value in retrieved_values.iterrows():
                print(f"  {value['date']}: Portfolio=${value['portfolio_value']:,.2f}, "
                      f"Benchmark=${value['benchmark_value']:,.2f}")
        
        # Get portfolio weights
        retrieved_weights = db_manager.get_portfolio_weights(backtest_id=test_backtest_id)
        print(f"Retrieved {len(retrieved_weights)} portfolio weight records")
        
        if not retrieved_weights.empty:
            print("Portfolio Weights:")
            for _, weight in retrieved_weights.iterrows():
                print(f"  {weight['date']} {weight['ticker']}: {weight['weight']:.2%}")
        
        # Test pivot table
        print("\nTesting pivot table...")
        weights_pivot = db_manager.get_portfolio_weights_pivot(test_backtest_id)
        print(f"Pivot table shape: {weights_pivot.shape}")
        if not weights_pivot.empty:
            print("Pivot table:")
            print(weights_pivot.round(4))
        
        # Clean up test data
        print(f"\nCleaning up test data...")
        db_manager.execute_query(f"DELETE FROM portfolio_values WHERE backtest_id = '{test_backtest_id}'")
        db_manager.execute_query(f"DELETE FROM portfolio_weights WHERE backtest_id = '{test_backtest_id}'")
        print("Test data cleaned up")
        
        db_manager.disconnect()
        print("\nPortfolio storage test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error testing portfolio storage: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    success = test_portfolio_storage()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

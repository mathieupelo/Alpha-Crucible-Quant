#!/usr/bin/env python3
"""
Test script to create a backtest with a name to verify it gets stored correctly.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import date, datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import DatabaseManager
from database.models import Backtest

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_create_backtest_with_name():
    """Test creating a backtest with a name."""
    try:
        db_manager = DatabaseManager()
        if not db_manager.connect():
            logger.error("Failed to connect to database")
            return False
        
        # Create a test backtest with a name
        test_backtest = Backtest(
            run_id=f"test_backtest_{int(datetime.now().timestamp())}",
            name="Test Backtest with Name",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            frequency="monthly",
            universe_id=1,  # Assuming universe 1 exists
            universe={'tickers': ['AAPL', 'MSFT'], 'signals': ['RSI', 'SMA']},
            benchmark="SPY",
            params={
                'initial_capital': 10000,
                'risk_aversion': 0.5,
                'max_weight': 0.1,
                'min_weight': 0.0,
                'transaction_costs': 0.001
            },
            created_at=datetime.now()
        )
        
        # Store the backtest
        backtest_id = db_manager.store_backtest(test_backtest)
        logger.info(f"Stored backtest with ID: {backtest_id}")
        
        # Retrieve the backtest to verify the name was stored
        retrieved_backtest = db_manager.get_backtest_by_run_id(test_backtest.run_id)
        if retrieved_backtest:
            logger.info(f"Retrieved backtest:")
            logger.info(f"  Run ID: {retrieved_backtest.run_id}")
            logger.info(f"  Name: {retrieved_backtest.name}")
            logger.info(f"  Start Date: {retrieved_backtest.start_date}")
            logger.info(f"  End Date: {retrieved_backtest.end_date}")
            
            if retrieved_backtest.name == test_backtest.name:
                logger.info("SUCCESS: Name was stored and retrieved correctly!")
                return True
            else:
                logger.error(f"FAILED: Name mismatch. Expected '{test_backtest.name}', got '{retrieved_backtest.name}'")
                return False
        else:
            logger.error("FAILED: Could not retrieve the backtest")
            return False
            
    except Exception as e:
        logger.error(f"Error testing backtest creation: {e}")
        return False
    finally:
        if 'db_manager' in locals():
            db_manager.disconnect()


def main():
    """Main test function."""
    logger.info("Testing backtest creation with name...")
    
    if test_create_backtest_with_name():
        logger.info("Test completed successfully!")
        return True
    else:
        logger.error("Test failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

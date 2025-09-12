#!/usr/bin/env python3
"""
Test script to simulate what the frontend receives from the backend API.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import DatabaseManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_frontend_response():
    """Test what the frontend would receive from the backend."""
    try:
        db_manager = DatabaseManager()
        if not db_manager.connect():
            logger.error("Failed to connect to database")
            return False
        
        # Get backtests using the same method as the backend
        backtests_df = db_manager.get_backtests()
        
        if backtests_df.empty:
            logger.info("No backtests found")
            return True
        
        logger.info(f"Found {len(backtests_df)} backtests")
        logger.info("Columns in DataFrame:")
        for col in backtests_df.columns:
            logger.info(f"  {col}")
        
        # Convert to list of dictionaries (same as backend)
        backtests = backtests_df.to_dict('records')
        
        logger.info(f"\nFirst 3 backtests as dictionaries:")
        for i, backtest in enumerate(backtests[:3]):
            print(f"Backtest {i+1}:")
            for key, value in backtest.items():
                print(f"  {key}: {value} (type: {type(value).__name__})")
            print("  ---")
        
        # Check if name field exists and has values
        names = [bt.get('name') for bt in backtests]
        non_null_names = [name for name in names if name is not None]
        
        logger.info(f"\nName field analysis:")
        logger.info(f"  Total backtests: {len(backtests)}")
        logger.info(f"  Names with values: {len(non_null_names)}")
        logger.info(f"  Names that are None: {len(names) - len(non_null_names)}")
        
        if non_null_names:
            logger.info(f"  Sample names: {non_null_names[:3]}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing frontend response: {e}")
        return False
    finally:
        if 'db_manager' in locals():
            db_manager.disconnect()


def main():
    """Main test function."""
    logger.info("Testing what frontend receives from backend...")
    
    if test_frontend_response():
        logger.info("Test completed successfully!")
        return True
    else:
        logger.error("Test failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

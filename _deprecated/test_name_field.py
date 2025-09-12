#!/usr/bin/env python3
"""
Simple test to check the name field in backtests.
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


def test_name_field():
    """Test the name field in backtests."""
    try:
        db_manager = DatabaseManager()
        if not db_manager.connect():
            logger.error("Failed to connect to database")
            return False
        
        # Get backtests using the same method as the backend
        backtests_df = db_manager.get_backtests()
        
        if backtests_df.empty:
            print("No backtests found")
            return True
        
        print(f"Found {len(backtests_df)} backtests")
        
        # Check name column specifically
        if 'name' in backtests_df.columns:
            print("Name column exists in DataFrame")
            names = backtests_df['name'].tolist()
            print(f"Name values: {names[:5]}")  # First 5 names
            
            # Count non-null names
            non_null_count = backtests_df['name'].notna().sum()
            print(f"Non-null names: {non_null_count}")
            print(f"Null names: {len(backtests_df) - non_null_count}")
        else:
            print("Name column does NOT exist in DataFrame")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'db_manager' in locals():
            db_manager.disconnect()


if __name__ == "__main__":
    test_name_field()

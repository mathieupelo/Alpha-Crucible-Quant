#!/usr/bin/env python3
"""
Test script to check if backtest names are being stored and retrieved correctly.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_backtest_names():
    """Test if backtest names are stored and retrieved correctly."""
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = int(os.getenv('DB_PORT', '3306'))
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    database = os.getenv('DB_NAME', 'signal_forge')
    
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Check table structure
        cursor.execute("""
            DESCRIBE backtests
        """)
        
        columns = cursor.fetchall()
        logger.info("Backtests table structure:")
        for column in columns:
            logger.info(f"  {column['Field']}: {column['Type']} {column['Null']} {column['Key']}")
        
        # Check if name column exists
        name_column_exists = any(col['Field'] == 'name' for col in columns)
        logger.info(f"Name column exists: {name_column_exists}")
        
        # Get recent backtests
        cursor.execute("""
            SELECT run_id, name, start_date, end_date, created_at 
            FROM backtests 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        backtests = cursor.fetchall()
        logger.info(f"Found {len(backtests)} backtests:")
        for backtest in backtests:
            logger.info(f"  Run ID: {backtest['run_id']}")
            logger.info(f"  Name: {backtest['name']}")
            logger.info(f"  Date Range: {backtest['start_date']} to {backtest['end_date']}")
            logger.info(f"  Created: {backtest['created_at']}")
            logger.info("  ---")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        logger.error(f"Error testing backtest names: {e}")
        return False


def main():
    """Main test function."""
    logger.info("Testing backtest name storage and retrieval...")
    
    if test_backtest_names():
        logger.info("Test completed successfully!")
        return True
    else:
        logger.error("Test failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

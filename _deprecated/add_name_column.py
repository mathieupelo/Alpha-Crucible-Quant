#!/usr/bin/env python3
"""
Database migration script to add name column to backtests table.
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


def add_name_column():
    """Add name column to backtests table."""
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
        
        cursor = connection.cursor()
        
        # Check if name column already exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'backtests' 
            AND COLUMN_NAME = 'name'
        """, (database,))
        
        if cursor.fetchone():
            logger.info("Name column already exists in backtests table")
            return True
        
        # Add name column
        cursor.execute("""
            ALTER TABLE backtests 
            ADD COLUMN name VARCHAR(255) NULL 
            AFTER run_id
        """)
        
        logger.info("Successfully added name column to backtests table")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        logger.error(f"Error adding name column: {e}")
        return False


def main():
    """Main migration function."""
    logger.info("Starting migration to add name column to backtests table...")
    
    if add_name_column():
        logger.info("Migration completed successfully!")
        return True
    else:
        logger.error("Migration failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

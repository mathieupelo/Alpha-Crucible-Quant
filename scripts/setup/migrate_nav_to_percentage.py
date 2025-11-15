#!/usr/bin/env python3
"""
Migration script to add return_pct column to backtest_nav table.

This migration:
1. Adds return_pct column (percentage change, e.g., 0.15 = 15% gain, -0.10 = 10% loss)
2. Adds benchmark_return_pct column (percentage change for benchmark)
3. Migrates existing data to calculate return_pct from nav values
4. Keeps nav column for backward compatibility
5. Initial capital is retrieved from backtests.params, not stored in backtest_nav
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_nav_table():
    """Migrate backtest_nav table to support percentage-based returns."""
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
        
        # Check if columns already exist
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'backtest_nav' 
            AND COLUMN_NAME IN ('return_pct', 'benchmark_return_pct')
        """, (database,))
        
        existing_columns = {row[0] for row in cursor.fetchall()}
        
        # Add return_pct column if it doesn't exist
        if 'return_pct' not in existing_columns:
            logger.info("Adding return_pct column to backtest_nav table...")
            cursor.execute("""
                ALTER TABLE backtest_nav 
                ADD COLUMN return_pct FLOAT DEFAULT NULL
            """)
            logger.info("Added return_pct column")
        else:
            logger.info("return_pct column already exists")
        
        # Add benchmark_return_pct column if it doesn't exist
        if 'benchmark_return_pct' not in existing_columns:
            logger.info("Adding benchmark_return_pct column to backtest_nav table...")
            cursor.execute("""
                ALTER TABLE backtest_nav 
                ADD COLUMN benchmark_return_pct FLOAT DEFAULT NULL
            """)
            logger.info("Added benchmark_return_pct column")
        else:
            logger.info("benchmark_return_pct column already exists")
        
        # Migrate existing data: calculate return_pct from nav values
        # For each run_id, get the first nav value as baseline and calculate percentage change
        logger.info("Migrating existing NAV data to percentage format...")
        
        # Get all unique run_ids
        cursor.execute("SELECT DISTINCT run_id FROM backtest_nav")
        run_ids = [row[0] for row in cursor.fetchall()]
        
        migrated_count = 0
        for run_id in run_ids:
            # Get the first NAV value for this run_id (sorted by date) - this is the baseline
            cursor.execute("""
                SELECT date, nav, benchmark_nav 
                FROM backtest_nav 
                WHERE run_id = %s 
                ORDER BY date ASC 
                LIMIT 1
            """, (run_id,))
            
            first_row = cursor.fetchone()
            if not first_row:
                continue
            
            first_date, first_nav, first_benchmark_nav = first_row
            
            # Use first nav as baseline (default to 10000 if nav is 0 or negative)
            baseline_nav = first_nav if first_nav > 0 else 10000.0
            baseline_benchmark_nav = first_benchmark_nav if first_benchmark_nav and first_benchmark_nav > 0 else baseline_nav
            
            # Get all NAV records for this run_id
            cursor.execute("""
                SELECT date, nav, benchmark_nav 
                FROM backtest_nav 
                WHERE run_id = %s 
                ORDER BY date ASC
            """, (run_id,))
            
            nav_records = cursor.fetchall()
            
            # Update each record with return_pct (percentage change)
            for date, nav, benchmark_nav in nav_records:
                # Calculate return_pct as percentage change: (nav - baseline) / baseline
                # e.g., if baseline=10000 and nav=11500, return_pct = (11500-10000)/10000 = 0.15 (15% gain)
                return_pct = (nav - baseline_nav) / baseline_nav if baseline_nav > 0 else 0.0
                
                # Calculate benchmark_return_pct if benchmark_nav exists
                benchmark_return_pct = None
                if benchmark_nav and benchmark_nav > 0 and baseline_benchmark_nav > 0:
                    benchmark_return_pct = (benchmark_nav - baseline_benchmark_nav) / baseline_benchmark_nav
                
                # Update the record
                cursor.execute("""
                    UPDATE backtest_nav 
                    SET return_pct = %s, 
                        benchmark_return_pct = %s
                    WHERE run_id = %s AND date = %s
                """, (return_pct, benchmark_return_pct, run_id, date))
                
                migrated_count += 1
        
        logger.info(f"Migrated {migrated_count} NAV records to percentage format")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info("Migration completed successfully!")
        return True
        
    except Error as e:
        logger.error(f"Error during migration: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting NAV percentage migration...")
    success = migrate_nav_table()
    sys.exit(0 if success else 1)


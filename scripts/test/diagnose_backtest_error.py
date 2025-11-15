#!/usr/bin/env python3
"""
Diagnostic script to help identify backtest errors.

Run this script to check common issues that might cause backtest failures.
"""

import sys
import logging
from pathlib import Path

# Add src and backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))

from src.database import DatabaseManager
from services.database_service import DatabaseService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_database_connection():
    """Check if database connection works."""
    logger.info("=" * 60)
    logger.info("Checking database connection...")
    logger.info("=" * 60)
    
    try:
        db_manager = DatabaseManager()
        if db_manager.connect():
            logger.info("✅ Database connection successful")
            db_manager.disconnect()
            return True
        else:
            logger.error("❌ Failed to connect to database")
            return False
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        return False


def check_nav_columns():
    """Check if NAV columns exist."""
    logger.info("=" * 60)
    logger.info("Checking NAV table columns...")
    logger.info("=" * 60)
    
    try:
        db_manager = DatabaseManager()
        if not db_manager.connect():
            logger.error("❌ Cannot check columns - database not connected")
            return False
        
        cursor = db_manager._connection.cursor()
        try:
            # Check for return_pct column
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                AND table_name = 'backtest_nav' 
                AND column_name = 'return_pct'
            """)
            has_return_pct = cursor.fetchone()[0] > 0
            
            # Check for benchmark_return_pct column
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                AND table_name = 'backtest_nav' 
                AND column_name = 'benchmark_return_pct'
            """)
            has_benchmark_return_pct = cursor.fetchone()[0] > 0
            
            cursor.close()
            
            if has_return_pct:
                logger.info("✅ return_pct column exists")
            else:
                logger.warning("⚠️  return_pct column does NOT exist")
            
            if has_benchmark_return_pct:
                logger.info("✅ benchmark_return_pct column exists")
            else:
                logger.warning("⚠️  benchmark_return_pct column does NOT exist")
            
            if has_return_pct and has_benchmark_return_pct:
                logger.info("✅ All required columns exist - code will use new schema")
                return True
            else:
                logger.info("⚠️  Some columns missing - code will use backward compatible mode")
                return True  # Still OK, just using old schema
        
        except Exception as e:
            logger.error(f"❌ Error checking columns: {e}")
            cursor.close()
            return False
        finally:
            db_manager.disconnect()
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def check_column_detection_method():
    """Test the column detection method."""
    logger.info("=" * 60)
    logger.info("Testing column detection method...")
    logger.info("=" * 60)
    
    try:
        db_manager = DatabaseManager()
        if not db_manager.connect():
            logger.error("❌ Cannot test - database not connected")
            return False
        
        # Import the mixin to test the method
        from src.database.backtest_operations import BacktestOperationsMixin
        
        # The DatabaseManager already includes this mixin, so we can use it directly
        has_columns = db_manager._check_nav_columns_exist()
        
        if has_columns:
            logger.info("✅ Column detection method reports: columns EXIST")
        else:
            logger.info("⚠️  Column detection method reports: columns DO NOT EXIST")
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing column detection: {e}", exc_info=True)
        return False


def check_backtest_table_structure():
    """Check the structure of backtest_nav table."""
    logger.info("=" * 60)
    logger.info("Checking backtest_nav table structure...")
    logger.info("=" * 60)
    
    try:
        db_manager = DatabaseManager()
        if not db_manager.connect():
            logger.error("❌ Cannot check - database not connected")
            return False
        
        cursor = db_manager._connection.cursor()
        try:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                AND table_name = 'backtest_nav'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            logger.info(f"Found {len(columns)} columns in backtest_nav table:")
            for col_name, data_type, is_nullable in columns:
                nullable = "NULL" if is_nullable == 'YES' else "NOT NULL"
                logger.info(f"  - {col_name}: {data_type} ({nullable})")
            
            cursor.close()
            db_manager.disconnect()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking table structure: {e}")
            cursor.close()
            db_manager.disconnect()
            return False
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def main():
    """Run all diagnostic checks."""
    logger.info("Starting backtest error diagnostics...")
    logger.info("")
    
    results = []
    
    results.append(("Database Connection", check_database_connection()))
    logger.info("")
    
    results.append(("NAV Columns", check_nav_columns()))
    logger.info("")
    
    results.append(("Column Detection Method", check_column_detection_method()))
    logger.info("")
    
    results.append(("Table Structure", check_backtest_table_structure()))
    logger.info("")
    
    # Summary
    logger.info("=" * 60)
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info("=" * 60)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{name}: {status}")
    
    logger.info("")
    logger.info("If all checks passed, please share:")
    logger.info("1. The exact error message you're seeing")
    logger.info("2. Where the error appears (frontend, backend logs, terminal)")
    logger.info("3. Any stack trace or error details")


if __name__ == "__main__":
    main()


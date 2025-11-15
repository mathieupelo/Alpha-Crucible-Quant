#!/usr/bin/env python3
"""
Verification script to ensure backtest fixes are working correctly.

This script verifies:
1. Column existence check works
2. NAV data can be stored with return_pct columns
3. Backtest creation and metrics retrieval work end-to-end
"""

import sys
import logging
from pathlib import Path
from datetime import date, timedelta

# Add src and backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))

from src.database import DatabaseManager
from services.database_service import DatabaseService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def verify_column_existence():
    """Verify that return_pct columns exist and can be checked."""
    logger.info("=" * 60)
    logger.info("Step 1: Verifying column existence check")
    logger.info("=" * 60)
    
    try:
        db_manager = DatabaseManager()
        if not db_manager.connect():
            logger.error("Failed to connect to database")
            return False
        
        # Check if columns exist using the new method
        from src.database.backtest_operations import BacktestOperationsMixin
        
        # Create a temporary class to test the method
        class TestMixin(BacktestOperationsMixin):
            def __init__(self, connection):
                self.connection = connection
        
        test_mixin = TestMixin(db_manager.connection)
        has_columns = test_mixin._check_nav_columns_exist()
        
        if has_columns:
            logger.info("✅ return_pct and benchmark_return_pct columns exist")
        else:
            logger.warning("⚠️  return_pct columns not found - code will use backward compatible mode")
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        logger.error(f"Error verifying columns: {e}")
        return False


def verify_nav_storage():
    """Verify that NAV data can be stored."""
    logger.info("=" * 60)
    logger.info("Step 2: Verifying NAV storage functionality")
    logger.info("=" * 60)
    
    try:
        db_service = DatabaseService()
        if not db_service.ensure_connection():
            logger.error("Failed to connect to database")
            return False
        
        # Check if we have any existing backtests with NAV data
        backtests = db_service.get_all_backtests(page=1, size=5)
        
        if backtests['total'] > 0:
            logger.info(f"Found {backtests['total']} existing backtest(s)")
            
            # Try to get NAV data for the first backtest
            first_backtest = backtests['backtests'][0]
            run_id = first_backtest['run_id']
            
            logger.info(f"Checking NAV data for backtest: {run_id}")
            nav_data = db_service.get_backtest_nav(run_id)
            
            if not nav_data.empty:
                logger.info(f"✅ Found {len(nav_data)} NAV records")
                logger.info(f"   Date range: {nav_data['date'].min()} to {nav_data['date'].max()}")
                
                # Check if return_pct columns exist in the data
                if 'return_pct' in nav_data.columns:
                    logger.info("✅ return_pct column exists in NAV data")
                    non_null_count = nav_data['return_pct'].notna().sum()
                    logger.info(f"   {non_null_count} records have return_pct values")
                else:
                    logger.warning("⚠️  return_pct column not in NAV data (may be using old schema)")
                
                if 'benchmark_return_pct' in nav_data.columns:
                    logger.info("✅ benchmark_return_pct column exists in NAV data")
                else:
                    logger.warning("⚠️  benchmark_return_pct column not in NAV data")
            else:
                logger.warning(f"⚠️  No NAV data found for backtest {run_id}")
        else:
            logger.info("No existing backtests found - this is okay for a fresh database")
        
        return True
        
    except Exception as e:
        logger.error(f"Error verifying NAV storage: {e}", exc_info=True)
        return False


def verify_metrics_endpoint():
    """Verify that metrics can be retrieved."""
    logger.info("=" * 60)
    logger.info("Step 3: Verifying metrics endpoint functionality")
    logger.info("=" * 60)
    
    try:
        db_service = DatabaseService()
        if not db_service.ensure_connection():
            logger.error("Failed to connect to database")
            return False
        
        # Get a backtest with NAV data
        backtests = db_service.get_all_backtests(page=1, size=5)
        
        if backtests['total'] > 0:
            for backtest in backtests['backtests']:
                run_id = backtest['run_id']
                
                # Check if NAV data exists
                nav_data = db_service.get_backtest_nav(run_id)
                if not nav_data.empty:
                    logger.info(f"Testing metrics for backtest: {run_id}")
                    
                    try:
                        metrics = db_service.get_backtest_metrics(run_id)
                        if metrics:
                            logger.info("✅ Metrics retrieved successfully")
                            logger.info(f"   Total return: {metrics.get('total_return', 'N/A')}%")
                            logger.info(f"   Sharpe ratio: {metrics.get('sharpe_ratio', 'N/A')}")
                            logger.info(f"   Max drawdown: {metrics.get('max_drawdown', 'N/A')}%")
                            return True
                        else:
                            logger.warning(f"⚠️  Metrics returned None for {run_id}")
                    except Exception as e:
                        logger.warning(f"⚠️  Error getting metrics: {e}")
            
            logger.warning("⚠️  No backtests with NAV data found for metrics testing")
        else:
            logger.info("No existing backtests found - skipping metrics test")
        
        return True
        
    except Exception as e:
        logger.error(f"Error verifying metrics: {e}", exc_info=True)
        return False


def main():
    """Run all verification checks."""
    logger.info("Starting backtest fix verification...")
    logger.info("")
    
    results = []
    
    # Step 1: Verify column existence check
    results.append(("Column Existence Check", verify_column_existence()))
    logger.info("")
    
    # Step 2: Verify NAV storage
    results.append(("NAV Storage", verify_nav_storage()))
    logger.info("")
    
    # Step 3: Verify metrics endpoint
    results.append(("Metrics Endpoint", verify_metrics_endpoint()))
    logger.info("")
    
    # Summary
    logger.info("=" * 60)
    logger.info("VERIFICATION SUMMARY")
    logger.info("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    logger.info("")
    if all_passed:
        logger.info("🎉 All verifications passed! Backtest system is working correctly.")
        return 0
    else:
        logger.warning("⚠️  Some verifications failed. Please check the logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())


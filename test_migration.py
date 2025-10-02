#!/usr/bin/env python3
"""
Test script to verify the migration between signals repo and alpha-crucible.

This script tests that:
1. Signals repo can write to signal_forge.signal_raw
2. Alpha-crucible can read from signal_forge.signal_raw
"""

import sys
import os
from datetime import date, datetime, timedelta
from pathlib import Path

# Add src to path for alpha-crucible
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Add signals_repo to path
sys.path.insert(0, str(Path(__file__).parent / 'signals_repo' / 'src'))

def test_signals_repo_write():
    """Test that signals repo can write to signal_forge.signal_raw."""
    print("Testing signals repo write capability...")
    
    try:
        from database import SignalDatabaseManager, SignalRaw
        
        # Initialize database manager
        db_manager = SignalDatabaseManager()
        
        if not db_manager.connect():
            print("❌ Failed to connect to signal_forge database")
            return False
        
        # Create test signal data
        test_signals = [
            SignalRaw(
                asof_date=date.today(),
                ticker='TEST',
                signal_name='TEST_SIGNAL',
                value=0.5,
                metadata={'test': True},
                created_at=datetime.now()
            )
        ]
        
        # Write to database
        stored_count = db_manager.store_signals_raw(test_signals)
        
        if stored_count > 0:
            print(f"✅ Successfully wrote {stored_count} signals to signal_forge.signal_raw")
            return True
        else:
            print("❌ Failed to write signals to database")
            return False
            
    except Exception as e:
        print(f"❌ Error testing signals repo write: {e}")
        return False
    finally:
        if 'db_manager' in locals():
            db_manager.disconnect()

def test_alpha_crucible_read():
    """Test that alpha-crucible can read from signal_forge.signal_raw."""
    print("Testing alpha-crucible read capability...")
    
    try:
        from signals import SignalReader
        
        # Initialize signal reader
        reader = SignalReader()
        
        # Read test signals
        signals_df = reader.get_signals(
            tickers=['TEST'],
            signal_names=['TEST_SIGNAL'],
            start_date=date.today(),
            end_date=date.today()
        )
        
        if not signals_df.empty:
            print(f"✅ Successfully read {len(signals_df)} signals from signal_forge.signal_raw")
            print(f"   Sample data: {signals_df.iloc[0].to_dict()}")
            return True
        else:
            print("❌ No signals found in database")
            return False
            
    except Exception as e:
        print(f"❌ Error testing alpha-crucible read: {e}")
        return False

def test_signal_pivot():
    """Test signal pivoting functionality."""
    print("Testing signal pivot functionality...")
    
    try:
        from signals import SignalReader
        
        reader = SignalReader()
        
        # Get pivoted signals
        pivot_df = reader.get_signal_pivot(
            tickers=['TEST'],
            signal_names=['TEST_SIGNAL'],
            start_date=date.today(),
            end_date=date.today()
        )
        
        if not pivot_df.empty:
            print(f"✅ Successfully created pivot table with shape: {pivot_df.shape}")
            return True
        else:
            print("❌ Failed to create pivot table")
            return False
            
    except Exception as e:
        print(f"❌ Error testing signal pivot: {e}")
        return False

def cleanup_test_data():
    """Clean up test data from database."""
    print("Cleaning up test data...")
    
    try:
        from database import DatabaseManager
        
        db_manager = DatabaseManager()
        
        if not db_manager.connect():
            print("❌ Failed to connect to database for cleanup")
            return False
        
        # Delete test data
        query = "DELETE FROM signal_raw WHERE ticker = 'TEST' AND signal_name = 'TEST_SIGNAL'"
        affected_rows = db_manager.execute_insert(query)
        
        print(f"✅ Cleaned up {affected_rows} test records")
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False
    finally:
        if 'db_manager' in locals():
            db_manager.disconnect()

def main():
    """Run all migration tests."""
    print("=" * 60)
    print("MIGRATION TEST: Signals Repo ↔ Alpha-Crucible")
    print("=" * 60)
    
    # Test signals repo write
    write_success = test_signals_repo_write()
    
    # Test alpha-crucible read
    read_success = test_alpha_crucible_read()
    
    # Test signal pivot
    pivot_success = test_signal_pivot()
    
    # Cleanup
    cleanup_success = cleanup_test_data()
    
    # Summary
    print("\n" + "=" * 60)
    print("MIGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Signals Repo Write: {'✅ PASS' if write_success else '❌ FAIL'}")
    print(f"Alpha-Crucible Read: {'✅ PASS' if read_success else '❌ FAIL'}")
    print(f"Signal Pivot: {'✅ PASS' if pivot_success else '❌ FAIL'}")
    print(f"Cleanup: {'✅ PASS' if cleanup_success else '❌ FAIL'}")
    
    overall_success = write_success and read_success and pivot_success
    
    if overall_success:
        print("\n🎉 MIGRATION SUCCESSFUL!")
        print("   Signals repo can write to signal_forge.signal_raw")
        print("   Alpha-crucible can read from signal_forge.signal_raw")
        print("   The two repositories are properly decoupled")
    else:
        print("\n❌ MIGRATION FAILED!")
        print("   Please check the errors above and fix the issues")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Verify that test signals were cleaned up from the database."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))

from services.database_service import DatabaseService

# Test signal names that should be cleaned up
TEST_SIGNAL_NAMES = [
    'SIGNAL_A',
    'SIGNAL_B',
    'SIGNAL_C',
    'TEST_SIGNAL_NULL',
    'TEST_SIGNAL_PORTFOLIO',
    'TEST_SIGNAL_MISSING',
    'TEST_SIGNAL_FULL'
]

def main():
    """Check if any test signals remain in the database."""
    db_service = DatabaseService()
    if not db_service.ensure_connection():
        print("Failed to connect to database")
        return
    
    db_manager = db_service.db_manager
    
    print("Checking for leftover test signals...")
    print("=" * 60)
    
    found_signals = []
    for signal_name in TEST_SIGNAL_NAMES:
        try:
            signal = db_manager.get_signal_by_name(signal_name)
            if signal:
                # Check if there are any signal_raw records
                count_result = db_manager.execute_query(
                    "SELECT COUNT(*) as count FROM signal_raw WHERE signal_id = %s",
                    (signal.id,)
                )
                count = count_result.iloc[0]['count'] if not count_result.empty else 0
                found_signals.append({
                    'name': signal_name,
                    'id': signal.id,
                    'raw_count': count
                })
        except Exception as e:
            # Signal doesn't exist, which is good
            pass
    
    if found_signals:
        print(f"⚠️  Found {len(found_signals)} test signals still in database:")
        for sig in found_signals:
            print(f"  - {sig['name']} (ID: {sig['id']}, {sig['raw_count']} raw records)")
        print("\nCleanup may have failed. These should be deleted.")
    else:
        print("✓ All test signals have been cleaned up successfully!")
        print("  No test signals found in database.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()


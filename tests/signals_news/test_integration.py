#!/usr/bin/env python3
"""
Integration tests for database connections and Varrock schema integration.
"""

import os
import sys
from pathlib import Path
from datetime import date
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / 'Alpha-Crucible-Quant' / '.env'
if env_path.exists():
    load_dotenv(env_path, override=True)
else:
    load_dotenv()

from main import (
    get_main_db_connection,
    get_ore_db_connection,
    get_all_tickers_with_company_uid,
    get_all_tickers,
    resolve_ticker_to_company_uid,
    is_signal_processed,
    insert_signal,
)

from test_cleanup import TestDataCleanup


def test_database_connections():
    """Test that database connections work."""
    print("Testing database connections...")
    
    main_conn = None
    ore_conn = None
    
    try:
        main_conn = get_main_db_connection()
        assert main_conn is not None, "Main database connection failed"
        print("  ✓ Main database connection successful")
        
        ore_conn = get_ore_db_connection()
        assert ore_conn is not None, "ORE database connection failed"
        print("  ✓ ORE database connection successful")
        
        return True
    except Exception as e:
        print(f"  ✗ Database connection failed: {e}")
        return False
    finally:
        if main_conn:
            main_conn.close()
        if ore_conn:
            ore_conn.close()


def test_ticker_fetching():
    """Test fetching tickers from varrock.tickers."""
    print("\nTesting ticker fetching...")
    
    main_conn = None
    
    try:
        main_conn = get_main_db_connection()
        
        # Test get_all_tickers
        tickers = get_all_tickers(main_conn)
        assert isinstance(tickers, set), "get_all_tickers should return a set"
        assert len(tickers) > 0, "Should find at least one ticker"
        print(f"  ✓ Found {len(tickers)} tickers using get_all_tickers()")
        
        # Test get_all_tickers_with_company_uid
        ticker_map = get_all_tickers_with_company_uid(main_conn)
        assert isinstance(ticker_map, dict), "get_all_tickers_with_company_uid should return a dict"
        assert len(ticker_map) > 0, "Should find at least one ticker with company_uid"
        print(f"  ✓ Found {len(ticker_map)} tickers with company_uid")
        
        # Verify all tickers have company_uid
        tickers_with_uid = [t for t, uid in ticker_map.items() if uid is not None]
        print(f"  ✓ {len(tickers_with_uid)}/{len(ticker_map)} tickers have company_uid")
        
        return True
    except Exception as e:
        print(f"  ✗ Ticker fetching failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if main_conn:
            main_conn.close()


def test_company_uid_resolution():
    """Test resolving tickers to company_uid."""
    print("\nTesting company_uid resolution...")
    
    main_conn = None
    
    try:
        main_conn = get_main_db_connection()
        
        # Get a sample ticker
        ticker_map = get_all_tickers_with_company_uid(main_conn)
        if not ticker_map:
            print("  ⚠ No tickers found to test resolution")
            return True
        
        test_ticker = list(ticker_map.keys())[0]
        expected_uid = ticker_map[test_ticker]
        
        # Test resolution
        resolved_uid = resolve_ticker_to_company_uid(main_conn, test_ticker)
        
        if expected_uid:
            assert resolved_uid == expected_uid, \
                f"Expected {expected_uid}, got {resolved_uid}"
            print(f"  ✓ Resolved {test_ticker} -> {resolved_uid}")
        else:
            print(f"  ⚠ {test_ticker} has no company_uid (expected)")
        
        # Test a few more tickers
        resolved_count = 0
        for ticker in list(ticker_map.keys())[:5]:
            uid = resolve_ticker_to_company_uid(main_conn, ticker)
            if uid:
                resolved_count += 1
        
        print(f"  ✓ Resolved {resolved_count}/5 sample tickers to company_uid")
        
        return True
    except Exception as e:
        print(f"  ✗ Company UID resolution failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if main_conn:
            main_conn.close()


def test_signal_raw_schema():
    """Test that signal_raw table has expected columns."""
    print("\nTesting signal_raw schema...")
    
    main_conn = None
    
    try:
        main_conn = get_main_db_connection()
        
        with main_conn.cursor() as cursor:
            # Check if company_uid column exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'signal_raw' 
                    AND column_name = 'company_uid'
                )
            """)
            has_company_uid = cursor.fetchone()[0]
            
            if has_company_uid:
                print("  ✓ signal_raw.company_uid column exists")
            else:
                print("  ⚠ signal_raw.company_uid column does not exist (will insert without it)")
            
            # Check if signal_id column exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'signal_raw' 
                    AND column_name = 'signal_id'
                )
            """)
            has_signal_id = cursor.fetchone()[0]
            
            if has_signal_id:
                print("  ✓ signal_raw.signal_id column exists")
            else:
                print("  ⚠ signal_raw.signal_id column does not exist")
            
            # Check required columns
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'signal_raw'
                AND column_name IN ('asof_date', 'ticker', 'signal_name', 'value')
            """)
            required_cols = {row[0] for row in cursor.fetchall()}
            expected_cols = {'asof_date', 'ticker', 'signal_name', 'value'}
            
            assert expected_cols.issubset(required_cols), \
                f"Missing required columns: {expected_cols - required_cols}"
            print("  ✓ All required columns exist")
        
        return True
    except Exception as e:
        print(f"  ✗ Schema check failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if main_conn:
            main_conn.close()


def test_signal_insertion_and_cleanup():
    """Test inserting a signal and then cleaning it up."""
    print("\nTesting signal insertion and cleanup...")
    
    main_conn = None
    cleanup = TestDataCleanup()
    
    # Use a test ticker and date that won't conflict with real data
    test_ticker = "TEST_CLEANUP"
    test_date = date(2099, 12, 31)  # Far future date
    test_signal_name = "SENTIMENT_YFINANCE_NEWS"
    
    try:
        main_conn = get_main_db_connection()
        
        # Verify signal doesn't exist before insertion
        processed_before = is_signal_processed(main_conn, test_ticker, test_date, test_signal_name)
        assert not processed_before, f"Signal already exists for {test_ticker}/{test_date}"
        
        # Insert test signal
        insert_signal(
            main_conn,
            ticker=test_ticker,
            target_date=test_date,
            signal_name=test_signal_name,
            value=0.5,
            metadata={'test': True, 'cleanup_test': True}
        )
        cleanup.track_signal(test_ticker, test_date, test_signal_name)
        print(f"  ✓ Inserted test signal for {test_ticker} on {test_date}")
        
        # Verify signal exists after insertion
        processed_after = is_signal_processed(main_conn, test_ticker, test_date, test_signal_name)
        assert processed_after, f"Signal not found after insertion for {test_ticker}/{test_date}"
        print(f"  ✓ Verified signal exists after insertion")
        
        return True
    except Exception as e:
        print(f"  ✗ Signal insertion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Always clean up, even if test fails
        if main_conn:
            cleanup.cleanup_signals(main_conn)
            print(f"  ✓ Cleaned up test signal")
            main_conn.close()


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("Integration Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("Database Connections", test_database_connections()))
    results.append(("Ticker Fetching", test_ticker_fetching()))
    results.append(("Company UID Resolution", test_company_uid_resolution()))
    results.append(("Signal Raw Schema", test_signal_raw_schema()))
    results.append(("Signal Insertion and Cleanup", test_signal_insertion_and_cleanup()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("All integration tests passed! ✓")
    else:
        print("Some integration tests failed! ✗")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


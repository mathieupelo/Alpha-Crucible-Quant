#!/usr/bin/env python3
"""
CLI script to modify a universe by adding tickers.

This script validates tickers before adding them to a universe.
If any ticker is invalid, the operation fails.
"""

import sys
import os
from pathlib import Path
import argparse

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))

from services.database_service import DatabaseService
from services.ticker_validation_service import TickerValidationService
from security.input_validation import validate_ticker


def modify_universe_cli(universe_id: int, tickers: list):
    """Add tickers to a universe after validating them."""
    db_service = DatabaseService()
    ticker_validator = TickerValidationService(
        timeout=15,
        max_retries=3,
        base_delay=2.0
    )
    
    if not db_service.ensure_connection():
        raise RuntimeError("Failed to connect to database")
    
    # Validate universe exists
    universe = db_service.get_universe_by_id(universe_id)
    if universe is None:
        raise ValueError(f"Universe with ID {universe_id} not found")
    
    # Validate and sanitize ticker list
    print(f"Validating {len(tickers)} ticker(s)...")
    validated_tickers = []
    for ticker in tickers:
        try:
            # validate_ticker may raise HTTPException, convert to ValueError for CLI
            from fastapi import HTTPException
            try:
                validated_ticker = validate_ticker(ticker)
                if validated_ticker not in validated_tickers:  # Remove duplicates
                    validated_tickers.append(validated_ticker)
            except HTTPException as e:
                raise ValueError(f"Invalid ticker format: {ticker} - {e.detail}")
        except ValueError:
            raise  # Re-raise ValueError as-is
        except Exception as e:
            raise ValueError(f"Invalid ticker format: {ticker} - {str(e)}")
    
    if not validated_tickers:
        raise ValueError("No valid tickers provided")
    
    if len(validated_tickers) > 50:
        raise ValueError("Too many tickers (max 50)")
    
    # Validate tickers with external service
    print("Checking ticker validity with market data...")
    validation_results = ticker_validator.validate_tickers_batch(validated_tickers, batch_size=2)
    
    # Check for invalid tickers
    invalid_tickers = [r for r in validation_results if not r['is_valid']]
    if invalid_tickers:
        invalid_list = ', '.join([r['ticker'] for r in invalid_tickers])
        error_messages = [f"{r['ticker']}: {r.get('error_message', 'Unknown error')}" 
                         for r in invalid_tickers]
        raise ValueError(f"Invalid tickers found:\n" + "\n".join(error_messages))
    
    # All tickers are valid, add them to the universe
    print(f"All tickers are valid. Adding {len(validated_tickers)} ticker(s) to universe '{universe['name']}'...")
    
    added_tickers = []
    for ticker in validated_tickers:
        try:
            ticker_data = db_service.add_universe_ticker(universe_id, ticker)
            added_tickers.append(ticker_data)
            print(f"  ✅ Added {ticker}")
        except Exception as e:
            # If ticker already exists, that's okay
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print(f"  ⚠️  {ticker} already exists in universe")
            else:
                raise
    
    # Get updated universe info
    updated_universe = db_service.get_universe_by_id(universe_id)
    tickers_data = db_service.get_universe_tickers(universe_id)
    
    print(f"\n✅ Successfully modified universe '{updated_universe['name']}'")
    print(f"   Total tickers: {len(tickers_data)}")
    
    return {
        'universe': updated_universe,
        'added_tickers': added_tickers,
        'total_tickers': len(tickers_data)
    }


def interactive_mode():
    """Run in interactive mode."""
    db_service = DatabaseService()
    
    if not db_service.ensure_connection():
        print("❌ Failed to connect to database")
        return 1
    
    # List universes
    print("\nAvailable universes:")
    universes = db_service.get_all_universes()
    if not universes:
        print("  No universes found. Create one first using create_universe.py")
        return 1
    
    for universe in universes:
        print(f"  ID {universe['id']}: {universe['name']} ({universe.get('ticker_count', 0)} tickers)")
    
    # Get universe ID
    try:
        universe_id = int(input("\nEnter universe ID: "))
    except ValueError:
        print("❌ Invalid universe ID")
        return 1
    
    # Get tickers
    tickers_input = input("Enter tickers to add (comma-separated): ")
    tickers = [t.strip() for t in tickers_input.split(',') if t.strip()]
    
    if not tickers:
        print("❌ No tickers provided")
        return 1
    
    try:
        result = modify_universe_cli(universe_id=universe_id, tickers=tickers)
        print("\n✅ Universe modified successfully!")
        return 0
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Modify a universe by adding tickers')
    parser.add_argument('--universe-id', type=int, help='Universe ID')
    parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers to add')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    if args.interactive or not all([args.universe_id, args.tickers]):
        return interactive_mode()
    
    try:
        tickers = [t.strip() for t in args.tickers.split(',') if t.strip()]
        result = modify_universe_cli(universe_id=args.universe_id, tickers=tickers)
        print("\n✅ Universe modified successfully!")
        return 0
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


#!/usr/bin/env python3
"""
CLI script to create a new universe.

This script allows creating universes from the command line or interactively.
"""

import sys
import os
from pathlib import Path
import argparse

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))

from services.database_service import DatabaseService


def create_universe_cli(name: str, description: str = None):
    """Create a new universe."""
    db_service = DatabaseService()
    
    if not db_service.ensure_connection():
        raise RuntimeError("Failed to connect to database")
    
    # Create universe
    universe = db_service.create_universe(name=name, description=description)
    
    print(f"✅ Created universe:")
    print(f"   ID: {universe['id']}")
    print(f"   Name: {universe['name']}")
    if universe.get('description'):
        print(f"   Description: {universe['description']}")
    print(f"   Ticker count: {universe.get('ticker_count', 0)}")
    
    return universe


def interactive_mode():
    """Run in interactive mode."""
    db_service = DatabaseService()
    
    if not db_service.ensure_connection():
        print("❌ Failed to connect to database")
        return 1
    
    # Get universe name
    name = input("Enter universe name: ").strip()
    if not name:
        print("❌ Universe name cannot be empty")
        return 1
    
    # Get description (optional)
    description = input("Enter description (optional, press Enter to skip): ").strip()
    if not description:
        description = None
    
    try:
        universe = create_universe_cli(name=name, description=description)
        print("\n✅ Universe created successfully!")
        return 0
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Create a new universe')
    parser.add_argument('--name', type=str, help='Universe name')
    parser.add_argument('--description', type=str, help='Universe description')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    if args.interactive or not args.name:
        return interactive_mode()
    
    try:
        universe = create_universe_cli(name=args.name, description=args.description)
        print("\n✅ Universe created successfully!")
        return 0
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


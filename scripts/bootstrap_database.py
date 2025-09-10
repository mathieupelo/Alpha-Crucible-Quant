#!/usr/bin/env python3
"""
Database Bootstrap Script for Alpha Crucible Quant

This script initializes the database with a default universe if none exists.
It's designed to be idempotent and safe to run multiple times.

Usage:
    python scripts/bootstrap_database.py
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import DatabaseManager
from database.models import Universe, UniverseTicker

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default universe configuration
DEFAULT_UNIVERSE = {
    'name': 'NA Gaming Starter (5)',
    'description': 'Starter universe for demo/testing: five liquid NA gaming-related tickers.',
    'tickers': ['EA', 'TTWO', 'RBLX', 'MSFT', 'NVDA']
}

MINIMUM_TICKER_COUNT = 5


def check_database_connection(db_manager: DatabaseManager) -> bool:
    """Check if database connection is working."""
    try:
        if not db_manager.connect():
            logger.error("Failed to connect to database")
            return False
        logger.info("Database connection established")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def check_universes_exist(db_manager: DatabaseManager) -> bool:
    """Check if any universes exist in the database."""
    try:
        universes_df = db_manager.get_universes()
        return not universes_df.empty
    except Exception as e:
        logger.error(f"Error checking existing universes: {e}")
        return False


def create_default_universe(db_manager: DatabaseManager) -> bool:
    """Create the default universe with its tickers."""
    try:
        logger.info(f"Creating default universe: {DEFAULT_UNIVERSE['name']}")
        
        # Create universe
        universe = Universe(
            name=DEFAULT_UNIVERSE['name'],
            description=DEFAULT_UNIVERSE['description'],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        universe_id = db_manager.store_universe(universe)
        logger.info(f"Created universe with ID: {universe_id}")
        
        # Create universe tickers
        universe_tickers = []
        for ticker in DEFAULT_UNIVERSE['tickers']:
            universe_ticker = UniverseTicker(
                universe_id=universe_id,
                ticker=ticker,
                added_at=datetime.now()
            )
            universe_tickers.append(universe_ticker)
        
        # Store all tickers
        stored_count = db_manager.store_universe_tickers(universe_tickers)
        logger.info(f"Added {stored_count} tickers to universe")
        
        # Verify the universe was created correctly
        created_universe = db_manager.get_universe_by_id(universe_id)
        if created_universe:
            tickers_df = db_manager.get_universe_tickers(universe_id)
            logger.info(f"Verification: Universe '{created_universe.name}' has {len(tickers_df)} tickers")
            return True
        else:
            logger.error("Failed to verify universe creation")
            return False
            
    except Exception as e:
        logger.error(f"Error creating default universe: {e}")
        return False


def validate_universe_ticker_count(db_manager: DatabaseManager, universe_id: int) -> bool:
    """Validate that a universe has at least the minimum number of tickers."""
    try:
        tickers_df = db_manager.get_universe_tickers(universe_id)
        ticker_count = len(tickers_df)
        
        if ticker_count < MINIMUM_TICKER_COUNT:
            logger.warning(f"Universe {universe_id} has only {ticker_count} tickers (minimum: {MINIMUM_TICKER_COUNT})")
            return False
        
        logger.info(f"Universe {universe_id} has {ticker_count} tickers (✓ meets minimum requirement)")
        return True
        
    except Exception as e:
        logger.error(f"Error validating universe ticker count: {e}")
        return False


def main():
    """Main bootstrap function."""
    logger.info("Starting database bootstrap process")
    logger.info("=" * 50)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Check database connection
    if not check_database_connection(db_manager):
        logger.error("Bootstrap failed: Database connection error")
        sys.exit(1)
    
    # Check if universes already exist
    if check_universes_exist(db_manager):
        logger.info("Universes already exist in database")
        
        # Get all universes and validate their ticker counts
        universes_df = db_manager.get_universes()
        logger.info(f"Found {len(universes_df)} existing universes")
        
        for _, universe_row in universes_df.iterrows():
            universe_id = universe_row['id']
            universe_name = universe_row['name']
            logger.info(f"Validating universe: {universe_name} (ID: {universe_id})")
            validate_universe_ticker_count(db_manager, universe_id)
        
        logger.info("Bootstrap completed: No new universe created (universes already exist)")
        return
    
    # Create default universe
    logger.info("No universes found, creating default universe")
    if create_default_universe(db_manager):
        logger.info("Bootstrap completed successfully: Default universe created")
    else:
        logger.error("Bootstrap failed: Could not create default universe")
        sys.exit(1)


if __name__ == "__main__":
    main()

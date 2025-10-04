#!/usr/bin/env python3
"""
Database setup script for PostgreSQL (Supabase).

Creates the database and tables with the simplified schema.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all required tables."""
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = int(os.getenv('DB_PORT', '5432'))
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', '')
    database = os.getenv('DB_NAME', 'postgres')
    
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            sslmode='require'
        )
        
        cursor = connection.cursor()
        
        # Signal raw table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signal_raw (
                id SERIAL PRIMARY KEY,
                asof_date DATE NOT NULL,
                ticker VARCHAR(20) NOT NULL,
                signal_name VARCHAR(100) NOT NULL,
                value FLOAT NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(asof_date, ticker, signal_name)
            )
        """)
        logger.info("Created signal_raw table")
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signal_raw_asof_date ON signal_raw(asof_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signal_raw_ticker ON signal_raw(ticker)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signal_raw_signal_name ON signal_raw(signal_name)")
        
        # Scores combined table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores_combined (
                id SERIAL PRIMARY KEY,
                asof_date DATE NOT NULL,
                ticker VARCHAR(20) NOT NULL,
                score FLOAT NOT NULL,
                method VARCHAR(100) NOT NULL,
                params JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(asof_date, ticker, method)
            )
        """)
        logger.info("Created scores_combined table")
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_combined_asof_date ON scores_combined(asof_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_combined_ticker ON scores_combined(ticker)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_combined_method ON scores_combined(method)")
        
        # Universes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS universes (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Created universes table")
        
        # Universe tickers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS universe_tickers (
                id SERIAL PRIMARY KEY,
                universe_id INTEGER NOT NULL REFERENCES universes(id) ON DELETE CASCADE,
                ticker VARCHAR(50) NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(universe_id, ticker)
            )
        """)
        logger.info("Created universe_tickers table")
        
        # Backtests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtests (
                id SERIAL PRIMARY KEY,
                run_id VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(255),
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly', 'quarterly')),
                universe_id INTEGER NOT NULL REFERENCES universes(id),
                universe JSONB,
                benchmark VARCHAR(20),
                params JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Created backtests table")
        
        # Portfolios table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id SERIAL PRIMARY KEY,
                run_id VARCHAR(100) NOT NULL REFERENCES backtests(run_id) ON DELETE CASCADE,
                universe_id INTEGER NOT NULL REFERENCES universes(id),
                asof_date DATE NOT NULL,
                method VARCHAR(100) NOT NULL,
                params JSONB,
                cash FLOAT DEFAULT 0.0,
                total_value FLOAT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(run_id, asof_date)
            )
        """)
        logger.info("Created portfolios table")
        
        # Portfolio positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_positions (
                id SERIAL PRIMARY KEY,
                portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
                ticker VARCHAR(20) NOT NULL,
                weight FLOAT NOT NULL,
                price_used FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(portfolio_id, ticker)
            )
        """)
        logger.info("Created portfolio_positions table")
        
        # Backtest NAV table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtest_nav (
                id SERIAL PRIMARY KEY,
                run_id VARCHAR(100) NOT NULL REFERENCES backtests(run_id) ON DELETE CASCADE,
                date DATE NOT NULL,
                nav FLOAT NOT NULL,
                benchmark_nav FLOAT,
                pnl FLOAT,
                UNIQUE(run_id, date)
            )
        """)
        logger.info("Created backtest_nav table")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False


def bootstrap_default_universe():
    """Bootstrap the default universe if none exists."""
    try:
        # Add src to path for imports
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
        
        from database import DatabaseManager
        from database.models import Universe, UniverseTicker
        from datetime import datetime
        
        db_manager = DatabaseManager()
        if not db_manager.connect():
            logger.error("Failed to connect to database for bootstrap")
            return False
        
        # Check if universes exist
        universes_df = db_manager.get_universes()
        if not universes_df.empty:
            logger.info("Universes already exist, skipping bootstrap")
            return True
        
        # Create default universe
        logger.info("No universes found, creating default universe...")
        
        universe = Universe(
            name='GameCore-12 (GC-12)',
            description='A curated 12-stock universe spanning the video-game value chain—pure-play developers, platforms, and media giants with meaningful gaming exposure—built for signal research on trailers, sentiment, and engagement.',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        universe_id = db_manager.store_universe(universe)
        logger.info(f"Created default universe with ID: {universe_id}")
        
        # Add default tickers
        default_tickers = ['OTGLF', 'SNAL', 'GRVY', 'GDEV', 'NCBDY', 'RBLX', 'WBD', 'NTES', 'TTWO', 'MSFT', 'EA', 'SONY']

        universe_tickers = []
        for ticker in default_tickers:
            universe_ticker = UniverseTicker(
                universe_id=universe_id,
                ticker=ticker,
                added_at=datetime.now()
            )
            universe_tickers.append(universe_ticker)
        
        stored_count = db_manager.store_universe_tickers(universe_tickers)
        logger.info(f"Added {stored_count} tickers to default universe")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during bootstrap: {e}")
        return False


def main():
    """Main setup function."""
    logger.info("Starting PostgreSQL database setup...")
    
    # Create tables
    if not create_tables():
        logger.error("Failed to create tables")
        return False
    
    # Bootstrap default universe
    if not bootstrap_default_universe():
        logger.warning("Failed to bootstrap default universe, but database setup completed")
    
    logger.info("PostgreSQL database setup completed successfully!")
    logger.info("Created tables: signals_raw, scores_combined, backtests, portfolios, portfolio_positions, backtest_nav, universes, universe_tickers")
    logger.info("Default universe 'GameCore-12 (GC-12)' created with 12 tickers")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

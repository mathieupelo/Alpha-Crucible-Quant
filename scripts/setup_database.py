#!/usr/bin/env python3
"""
Database setup script for the Quant Project system.

Creates the database and tables with the simplified schema.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database():
    """Create the database if it doesn't exist."""
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = int(os.getenv('DB_PORT', '3306'))
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    database = os.getenv('DB_NAME', 'signal_forge')
    
    try:
        # Connect without specifying database
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        
        cursor = connection.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        logger.info(f"Database '{database}' created or already exists")
        
        # Use the database
        cursor.execute(f"USE {database}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        logger.error(f"Error creating database: {e}")
        return False


def create_tables():
    """Create all required tables."""
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
        
        # Signals raw table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals_raw (
                id INT AUTO_INCREMENT PRIMARY KEY,
                asof_date DATE NOT NULL,
                ticker VARCHAR(20) NOT NULL,
                signal_name VARCHAR(100) NOT NULL,
                value FLOAT NOT NULL,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_signal_raw (asof_date, ticker, signal_name),
                INDEX idx_asof_date (asof_date),
                INDEX idx_ticker (ticker),
                INDEX idx_signal_name (signal_name),
                INDEX idx_date_ticker (asof_date, ticker)
            )
        """)
        logger.info("Created signals_raw table")
        
        # Scores combined table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores_combined (
                id INT AUTO_INCREMENT PRIMARY KEY,
                asof_date DATE NOT NULL,
                ticker VARCHAR(20) NOT NULL,
                score FLOAT NOT NULL,
                method VARCHAR(100) NOT NULL,
                params JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_score_combined (asof_date, ticker, method),
                INDEX idx_asof_date (asof_date),
                INDEX idx_ticker (ticker),
                INDEX idx_method (method),
                INDEX idx_date_ticker (asof_date, ticker)
            )
        """)
        logger.info("Created scores_combined table")
        
        # Universes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS universes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_name (name)
            )
        """)
        logger.info("Created universes table")
        
        # Universe tickers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS universe_tickers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                universe_id INT NOT NULL,
                ticker VARCHAR(50) NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_universe_ticker (universe_id, ticker),
                INDEX idx_universe_id (universe_id),
                INDEX idx_ticker (ticker),
                FOREIGN KEY (universe_id) REFERENCES universes(id) ON DELETE CASCADE
            )
        """)
        logger.info("Created universe_tickers table")
        
        # Backtests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                run_id VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(255),
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                frequency ENUM('daily', 'weekly', 'monthly', 'quarterly') NOT NULL,
                universe_id INT NOT NULL,
                universe JSON,
                benchmark VARCHAR(20),
                params JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_run_id (run_id),
                INDEX idx_name (name),
                INDEX idx_start_date (start_date),
                INDEX idx_end_date (end_date),
                INDEX idx_created_at (created_at),
                INDEX idx_universe_id (universe_id),
                FOREIGN KEY (universe_id) REFERENCES universes(id) ON DELETE RESTRICT
            )
        """)
        logger.info("Created backtests table")
        
        # Portfolios table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                run_id VARCHAR(100) NOT NULL,
                universe_id INT NOT NULL,
                asof_date DATE NOT NULL,
                method VARCHAR(100) NOT NULL,
                params JSON,
                cash FLOAT DEFAULT 0.0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_portfolio (run_id, asof_date),
                INDEX idx_run_id (run_id),
                INDEX idx_universe_id (universe_id),
                INDEX idx_asof_date (asof_date),
                INDEX idx_method (method),
                FOREIGN KEY (run_id) REFERENCES backtests(run_id) ON DELETE CASCADE,
                FOREIGN KEY (universe_id) REFERENCES universes(id) ON DELETE RESTRICT
            )
        """)
        logger.info("Created portfolios table")
        
        # Portfolio positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_positions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                portfolio_id INT NOT NULL,
                ticker VARCHAR(20) NOT NULL,
                weight FLOAT NOT NULL,
                price_used FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_portfolio_position (portfolio_id, ticker),
                INDEX idx_portfolio_id (portfolio_id),
                INDEX idx_ticker (ticker),
                FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
            )
        """)
        logger.info("Created portfolio_positions table")
        
        # Backtest NAV table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtest_nav (
                id INT AUTO_INCREMENT PRIMARY KEY,
                run_id VARCHAR(100) NOT NULL,
                date DATE NOT NULL,
                nav FLOAT NOT NULL,
                benchmark_nav FLOAT,
                pnl FLOAT,
                UNIQUE KEY unique_backtest_nav (run_id, date),
                INDEX idx_run_id (run_id),
                INDEX idx_date (date),
                FOREIGN KEY (run_id) REFERENCES backtests(run_id) ON DELETE CASCADE
            )
        """)
        logger.info("Created backtest_nav table")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
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
        #default_tickers = ['EA', 'TTWO', 'RBLX', 'MSFT', 'NVDA']
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
    logger.info("Starting database setup...")
    
    # Create database
    if not create_database():
        logger.error("Failed to create database")
        return False
    
    # Create tables (including universe tables)
    if not create_tables():
        logger.error("Failed to create tables")
        return False
    
    # Bootstrap default universe
    if not bootstrap_default_universe():
        logger.warning("Failed to bootstrap default universe, but database setup completed")
    
    logger.info("Database setup completed successfully!")
    logger.info("Created tables: signals_raw, scores_combined, backtests, portfolios, portfolio_positions, backtest_nav, universes, universe_tickers")
    logger.info("Default universe 'NA Gaming Starter (5)' created with 5 tickers")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

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
        
        # Backtests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                run_id VARCHAR(100) UNIQUE NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                frequency ENUM('daily', 'weekly', 'monthly', 'quarterly') NOT NULL,
                universe JSON,
                benchmark VARCHAR(20),
                params JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_run_id (run_id),
                INDEX idx_start_date (start_date),
                INDEX idx_end_date (end_date),
                INDEX idx_created_at (created_at)
            )
        """)
        logger.info("Created backtests table")
        
        # Portfolios table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                run_id VARCHAR(100) NOT NULL,
                asof_date DATE NOT NULL,
                method VARCHAR(100) NOT NULL,
                params JSON,
                cash FLOAT DEFAULT 0.0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_portfolio (run_id, asof_date),
                INDEX idx_run_id (run_id),
                INDEX idx_asof_date (asof_date),
                INDEX idx_method (method),
                FOREIGN KEY (run_id) REFERENCES backtests(run_id) ON DELETE CASCADE
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




def main():
    """Main setup function."""
    logger.info("Starting database setup...")
    
    # Create database
    if not create_database():
        logger.error("Failed to create database")
        return False
    
    # Create tables
    if not create_tables():
        logger.error("Failed to create tables")
        return False
    
    logger.info("Database setup completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

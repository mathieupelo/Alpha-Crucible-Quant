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
    database = os.getenv('DB_NAME', 'quant_project')
    
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
    database = os.getenv('DB_NAME', 'quant_project')
    
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        
        # Signal definitions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signal_definitions (
                signal_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                parameters TEXT,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        logger.info("Created signal_definitions table")
        
        # Signal scores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signal_scores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticker VARCHAR(20) NOT NULL,
                signal_id VARCHAR(50) NOT NULL,
                date DATE NOT NULL,
                score DECIMAL(10, 6) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_signal_score (ticker, signal_id, date),
                INDEX idx_ticker_date (ticker, date),
                INDEX idx_signal_date (signal_id, date),
                INDEX idx_date (date)
            )
        """)
        logger.info("Created signal_scores table")
        
        # Portfolios table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                portfolio_id VARCHAR(100) PRIMARY KEY,
                creation_date DATE NOT NULL,
                weights TEXT NOT NULL,
                signal_weights TEXT NOT NULL,
                risk_aversion DECIMAL(10, 6) NOT NULL,
                max_weight DECIMAL(10, 6) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_creation_date (creation_date)
            )
        """)
        logger.info("Created portfolios table")
        
        # Backtest results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtest_results (
                backtest_id VARCHAR(100) PRIMARY KEY,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                tickers TEXT NOT NULL,
                signals TEXT NOT NULL,
                total_return DECIMAL(10, 6) NOT NULL,
                annualized_return DECIMAL(10, 6) NOT NULL,
                sharpe_ratio DECIMAL(10, 6) NOT NULL,
                max_drawdown DECIMAL(10, 6) NOT NULL,
                volatility DECIMAL(10, 6) NOT NULL,
                alpha DECIMAL(10, 6) NOT NULL,
                information_ratio DECIMAL(10, 6) NOT NULL,
                execution_time_seconds DECIMAL(10, 3) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_start_date (start_date),
                INDEX idx_end_date (end_date),
                INDEX idx_created_at (created_at)
            )
        """)
        logger.info("Created backtest_results table")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        logger.error(f"Error creating tables: {e}")
        return False


def insert_default_signal_definitions():
    """Insert default signal definitions."""
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = int(os.getenv('DB_PORT', '3306'))
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    database = os.getenv('DB_NAME', 'quant_project')
    
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        
        # Default signal definitions
        signals = [
            ('RSI', 'Relative Strength Index', '{"period": 14}'),
            ('SMA', 'Simple Moving Average', '{"short_period": 50, "long_period": 200}'),
            ('MACD', 'Moving Average Convergence Divergence', '{"fast_period": 12, "slow_period": 26, "signal_period": 9}'),
        ]
        
        for signal_id, name, parameters in signals:
            cursor.execute("""
                INSERT IGNORE INTO signal_definitions (signal_id, name, parameters, enabled)
                VALUES (%s, %s, %s, %s)
            """, (signal_id, name, parameters, True))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info("Inserted default signal definitions")
        return True
        
    except Error as e:
        logger.error(f"Error inserting signal definitions: {e}")
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
    
    # Insert default signal definitions
    if not insert_default_signal_definitions():
        logger.error("Failed to insert signal definitions")
        return False
    
    logger.info("Database setup completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

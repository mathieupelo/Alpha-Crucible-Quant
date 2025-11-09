#!/usr/bin/env python3
"""
Database setup script for the Varrock schema in Supabase PostgreSQL.

Creates the varrock schema and all required tables for company and ticker management.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_connection():
    """Get database connection to Supabase PostgreSQL."""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Ensure sslmode=require for Supabase
        url_lower = database_url.lower()
        has_query = '?' in database_url
        has_ssl = 'sslmode=' in url_lower
        if not has_ssl:
            separator = '&' if has_query else '?'
            database_url = f"{database_url}{separator}sslmode=require"
        return psycopg2.connect(database_url)
    else:
        # Fallback to individual connection parameters
        host = os.getenv('DB_HOST', '127.0.0.1')
        port = int(os.getenv('DB_PORT', '5432'))
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', '')
        database = os.getenv('DB_NAME', 'postgres')
        
        return psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            sslmode='require'
        )


def create_varrock_schema():
    """Create the varrock schema and all tables."""
    connection = None
    try:
        connection = get_connection()
        connection.autocommit = False
        cursor = connection.cursor()
        
        # Create schema
        cursor.execute("CREATE SCHEMA IF NOT EXISTS varrock;")
        logger.info("Created varrock schema")
        
        # Create companies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS varrock.companies (
                company_uid VARCHAR(36) PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Created varrock.companies table")
        
        # Create company_info table (one-to-one with companies)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS varrock.company_info (
                company_info_uid VARCHAR(36) PRIMARY KEY,
                company_uid VARCHAR(36) NOT NULL UNIQUE,
                name VARCHAR(255),
                full_name VARCHAR(500),
                short_name VARCHAR(255),
                country VARCHAR(100),
                continent VARCHAR(50),
                hq_address TEXT,
                city VARCHAR(100),
                state VARCHAR(100),
                zip_code VARCHAR(20),
                phone VARCHAR(50),
                website VARCHAR(500),
                sector VARCHAR(100),
                industry VARCHAR(200),
                industry_key VARCHAR(100),
                industry_disp VARCHAR(200),
                sector_key VARCHAR(100),
                sector_disp VARCHAR(200),
                market_cap BIGINT,
                currency VARCHAR(10),
                exchange VARCHAR(50),
                exchange_timezone VARCHAR(50),
                description TEXT,
                long_business_summary TEXT,
                employees INT,
                founded_year INT,
                data_source VARCHAR(50) DEFAULT 'yfinance',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_uid) REFERENCES varrock.companies(company_uid) ON DELETE CASCADE,
                CONSTRAINT unique_company_info UNIQUE (company_uid)
            )
        """)
        logger.info("Created varrock.company_info table")
        
        # Create tickers table (one-to-many with companies)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS varrock.tickers (
                ticker_uid VARCHAR(36) PRIMARY KEY,
                company_uid VARCHAR(36) NOT NULL,
                ticker VARCHAR(50) NOT NULL,
                market VARCHAR(50),
                exchange VARCHAR(50),
                currency VARCHAR(10),
                is_in_yfinance BOOLEAN DEFAULT FALSE,
                is_main_ticker BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                ticker_type VARCHAR(50),
                yfinance_symbol VARCHAR(50),
                data_quality_score DECIMAL(3,2),
                first_seen_date DATE,
                last_verified_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_uid) REFERENCES varrock.companies(company_uid) ON DELETE CASCADE,
                CONSTRAINT unique_ticker_market UNIQUE (ticker, market)
            )
        """)
        logger.info("Created varrock.tickers table")
        
        # Create company_info_history table (for versioning)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS varrock.company_info_history (
                history_id SERIAL PRIMARY KEY,
                company_info_uid VARCHAR(36) NOT NULL,
                company_uid VARCHAR(36) NOT NULL,
                name VARCHAR(255),
                full_name VARCHAR(500),
                short_name VARCHAR(255),
                country VARCHAR(100),
                continent VARCHAR(50),
                hq_address TEXT,
                city VARCHAR(100),
                state VARCHAR(100),
                zip_code VARCHAR(20),
                phone VARCHAR(50),
                website VARCHAR(500),
                sector VARCHAR(100),
                industry VARCHAR(200),
                industry_key VARCHAR(100),
                industry_disp VARCHAR(200),
                sector_key VARCHAR(100),
                sector_disp VARCHAR(200),
                market_cap BIGINT,
                currency VARCHAR(10),
                exchange VARCHAR(50),
                exchange_timezone VARCHAR(50),
                description TEXT,
                long_business_summary TEXT,
                employees INT,
                founded_year INT,
                data_source VARCHAR(50),
                version_number INT DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_uid) REFERENCES varrock.companies(company_uid) ON DELETE CASCADE
            )
        """)
        logger.info("Created varrock.company_info_history table")
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_company_info_company_uid 
            ON varrock.company_info(company_uid)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_company_info_country 
            ON varrock.company_info(country)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_company_info_sector 
            ON varrock.company_info(sector)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_company_info_exchange 
            ON varrock.company_info(exchange)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickers_company_uid 
            ON varrock.tickers(company_uid)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickers_ticker 
            ON varrock.tickers(ticker)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickers_market 
            ON varrock.tickers(market)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickers_is_main_ticker 
            ON varrock.tickers(is_main_ticker)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickers_is_active 
            ON varrock.tickers(is_active)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickers_is_in_yfinance 
            ON varrock.tickers(is_in_yfinance)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_company_info_history_company_uid 
            ON varrock.company_info_history(company_uid)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_company_info_history_created_at 
            ON varrock.company_info_history(created_at)
        """)
        
        # Create partial unique index to ensure only one main ticker per company
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_one_main_ticker_per_company 
            ON varrock.tickers(company_uid) 
            WHERE is_main_ticker = TRUE
        """)
        logger.info("Created indexes")
        
        # Create trigger to update updated_at timestamp
        cursor.execute("""
            CREATE OR REPLACE FUNCTION varrock.update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_companies_updated_at ON varrock.companies;
            CREATE TRIGGER update_companies_updated_at
            BEFORE UPDATE ON varrock.companies
            FOR EACH ROW
            EXECUTE FUNCTION varrock.update_updated_at_column();
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_tickers_updated_at ON varrock.tickers;
            CREATE TRIGGER update_tickers_updated_at
            BEFORE UPDATE ON varrock.tickers
            FOR EACH ROW
            EXECUTE FUNCTION varrock.update_updated_at_column();
        """)
        logger.info("Created update triggers")
        
        connection.commit()
        logger.info("Varrock schema setup completed successfully!")
        
        return True
        
    except Error as e:
        if connection:
            connection.rollback()
        logger.error(f"Error creating varrock schema: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()


def main():
    """Main setup function."""
    logger.info("Starting Varrock schema setup...")
    
    if not create_varrock_schema():
        logger.error("Failed to create varrock schema")
        sys.exit(1)
    
    logger.info("Varrock schema setup completed successfully!")
    logger.info("Created tables: companies, company_info, tickers, company_info_history")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


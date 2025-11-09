#!/usr/bin/env python3
"""
Migration script to populate company_uid values in signal_raw, scores_combined, and portfolio_positions.

This script:
1. For each table, gets all distinct tickers
2. Resolves each ticker to company_uid via varrock.tickers table
3. Updates records with company_uid
4. Logs any tickers that don't exist in Varrock
5. Handles NULL tickers gracefully
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Optional

# Add project root and src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
        host = os.getenv('DB_HOST')
        port = int(os.getenv('DB_PORT', '5432'))
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        database = os.getenv('DB_NAME')
        
        if not all([host, user, password, database]):
            raise ValueError(
                "Database connection requires either DATABASE_URL environment variable or "
                "all of: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME. "
                "Please set DATABASE_URL or configure connection parameters."
            )
        
        return psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            sslmode='require'
        )


def build_ticker_to_company_map(connection) -> Dict[str, str]:
    """Build a mapping of ticker -> company_uid from varrock.tickers."""
    cursor = connection.cursor()
    try:
        query = """
            SELECT DISTINCT t.ticker, t.company_uid
            FROM varrock.tickers t
            WHERE t.ticker IS NOT NULL
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        ticker_map = {}
        for ticker, company_uid in results:
            ticker_upper = str(ticker).strip().upper()
            ticker_map[ticker_upper] = str(company_uid)
        
        logger.info(f"Built ticker-to-company map with {len(ticker_map)} entries")
        return ticker_map
    finally:
        cursor.close()


def migrate_table(connection, table_name: str, ticker_column: str, ticker_map: Dict[str, str]) -> tuple:
    """
    Migrate a single table by populating company_uid from ticker.
    
    Returns: (success_count, failed_count, missing_tickers)
    """
    cursor = connection.cursor()
    success_count = 0
    failed_count = 0
    missing_tickers = set()
    
    try:
        # Get all distinct tickers from the table
        query = f"""
            SELECT DISTINCT {ticker_column}
            FROM {table_name}
            WHERE {ticker_column} IS NOT NULL
            AND company_uid IS NULL
        """
        cursor.execute(query)
        tickers = [row[0] for row in cursor.fetchall()]
        
        if not tickers:
            logger.info(f"No records to migrate in {table_name}")
            return (0, 0, set())
        
        logger.info(f"Found {len(tickers)} distinct tickers to migrate in {table_name}")
        
        # Update records in batches
        for ticker in tickers:
            ticker_upper = str(ticker).strip().upper()
            company_uid = ticker_map.get(ticker_upper)
            
            if not company_uid:
                missing_tickers.add(ticker_upper)
                failed_count += 1
                continue
            
            # Update all records with this ticker
            update_query = f"""
                UPDATE {table_name}
                SET company_uid = %s
                WHERE {ticker_column} = %s
                AND company_uid IS NULL
            """
            cursor.execute(update_query, (company_uid, ticker))
            rows_updated = cursor.rowcount
            success_count += rows_updated
        
        connection.commit()
        logger.info(f"Migrated {table_name}: {success_count} records updated, {failed_count} tickers not found")
        
        return (success_count, failed_count, missing_tickers)
        
    except Error as e:
        connection.rollback()
        logger.error(f"Error migrating {table_name}: {e}")
        raise
    finally:
        cursor.close()


def migrate_all_tables():
    """Migrate all tables to use company_uid."""
    connection = None
    try:
        connection = get_connection()
        connection.autocommit = False
        
        # Build ticker to company_uid mapping
        logger.info("Building ticker-to-company mapping...")
        ticker_map = build_ticker_to_company_map(connection)
        
        if not ticker_map:
            logger.warning("No tickers found in varrock.tickers. Please ensure Varrock schema is populated.")
            return False
        
        all_missing_tickers = set()
        total_success = 0
        total_failed = 0
        
        # Migrate signal_raw
        logger.info("Migrating signal_raw table...")
        success, failed, missing = migrate_table(connection, 'signal_raw', 'ticker', ticker_map)
        total_success += success
        total_failed += failed
        all_missing_tickers.update(missing)
        
        # Migrate scores_combined
        logger.info("Migrating scores_combined table...")
        success, failed, missing = migrate_table(connection, 'scores_combined', 'ticker', ticker_map)
        total_success += success
        total_failed += failed
        all_missing_tickers.update(missing)
        
        # Migrate portfolio_positions
        logger.info("Migrating portfolio_positions table...")
        success, failed, missing = migrate_table(connection, 'portfolio_positions', 'ticker', ticker_map)
        total_success += success
        total_failed += failed
        all_missing_tickers.update(missing)
        
        # Report results
        logger.info("=" * 60)
        logger.info("Migration Summary:")
        logger.info(f"  Total records updated: {total_success}")
        logger.info(f"  Total tickers not found: {total_failed}")
        if all_missing_tickers:
            logger.warning(f"  Missing tickers: {sorted(all_missing_tickers)}")
            logger.warning("  These tickers need to be added to Varrock schema first")
        logger.info("=" * 60)
        
        return True
        
    except Error as e:
        if connection:
            connection.rollback()
        logger.error(f"Error during migration: {e}")
        return False
    finally:
        if connection:
            connection.close()


def main():
    """Main migration function."""
    logger.info("Starting migration to populate company_uid values...")
    
    if not migrate_all_tables():
        logger.error("Migration failed")
        sys.exit(1)
    
    logger.info("Migration completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


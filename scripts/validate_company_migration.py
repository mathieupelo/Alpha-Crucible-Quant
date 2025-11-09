#!/usr/bin/env python3
"""
Validation script to verify company_uid migration.

This script checks:
1. All signal_raw records have company_uid populated
2. All scores_combined records have company_uid populated
3. All portfolio_positions records have company_uid populated
4. All company_uids reference valid companies in varrock.companies
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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


def validate_table(connection, table_name: str, ticker_column: str) -> dict:
    """Validate company_uid migration for a specific table."""
    cursor = connection.cursor()
    results = {
        'table': table_name,
        'total_records': 0,
        'records_with_company_uid': 0,
        'records_without_company_uid': 0,
        'records_with_invalid_company_uid': 0,
        'missing_tickers': []
    }
    
    try:
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        results['total_records'] = cursor.fetchone()[0]
        
        # Get count with company_uid
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE company_uid IS NOT NULL")
        results['records_with_company_uid'] = cursor.fetchone()[0]
        
        # Get count without company_uid
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE company_uid IS NULL")
        results['records_without_company_uid'] = cursor.fetchone()[0]
        
        # Get records with invalid company_uid (not in varrock.companies)
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM {table_name} sr
            WHERE sr.company_uid IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM varrock.companies c 
                WHERE c.company_uid = sr.company_uid
            )
        """)
        results['records_with_invalid_company_uid'] = cursor.fetchone()[0]
        
        # Get tickers that don't have company_uid
        if results['records_without_company_uid'] > 0:
            cursor.execute(f"""
                SELECT DISTINCT {ticker_column}
                FROM {table_name}
                WHERE company_uid IS NULL
                AND {ticker_column} IS NOT NULL
                LIMIT 20
            """)
            results['missing_tickers'] = [row[0] for row in cursor.fetchall()]
        
        return results
        
    except Error as e:
        logger.error(f"Error validating {table_name}: {e}")
        raise
    finally:
        cursor.close()


def main():
    """Main validation function."""
    connection = None
    try:
        connection = get_connection()
        
        logger.info("=" * 60)
        logger.info("Company UID Migration Validation")
        logger.info("=" * 60)
        
        all_valid = True
        
        # Validate signal_raw
        logger.info("\nValidating signal_raw table...")
        signal_results = validate_table(connection, 'signal_raw', 'ticker')
        logger.info(f"  Total records: {signal_results['total_records']}")
        logger.info(f"  With company_uid: {signal_results['records_with_company_uid']}")
        logger.info(f"  Without company_uid: {signal_results['records_without_company_uid']}")
        logger.info(f"  Invalid company_uid: {signal_results['records_with_invalid_company_uid']}")
        if signal_results['missing_tickers']:
            logger.warning(f"  Missing tickers (sample): {signal_results['missing_tickers']}")
        if signal_results['records_without_company_uid'] > 0 or signal_results['records_with_invalid_company_uid'] > 0:
            all_valid = False
        
        # Validate scores_combined
        logger.info("\nValidating scores_combined table...")
        scores_results = validate_table(connection, 'scores_combined', 'ticker')
        logger.info(f"  Total records: {scores_results['total_records']}")
        logger.info(f"  With company_uid: {scores_results['records_with_company_uid']}")
        logger.info(f"  Without company_uid: {scores_results['records_without_company_uid']}")
        logger.info(f"  Invalid company_uid: {scores_results['records_with_invalid_company_uid']}")
        if scores_results['missing_tickers']:
            logger.warning(f"  Missing tickers (sample): {scores_results['missing_tickers']}")
        if scores_results['records_without_company_uid'] > 0 or scores_results['records_with_invalid_company_uid'] > 0:
            all_valid = False
        
        # Validate portfolio_positions
        logger.info("\nValidating portfolio_positions table...")
        positions_results = validate_table(connection, 'portfolio_positions', 'ticker')
        logger.info(f"  Total records: {positions_results['total_records']}")
        logger.info(f"  With company_uid: {positions_results['records_with_company_uid']}")
        logger.info(f"  Without company_uid: {positions_results['records_without_company_uid']}")
        logger.info(f"  Invalid company_uid: {positions_results['records_with_invalid_company_uid']}")
        if positions_results['missing_tickers']:
            logger.warning(f"  Missing tickers (sample): {positions_results['missing_tickers']}")
        if positions_results['records_without_company_uid'] > 0 or positions_results['records_with_invalid_company_uid'] > 0:
            all_valid = False
        
        # Summary
        logger.info("\n" + "=" * 60)
        if all_valid:
            logger.info("✅ Migration validation PASSED - All records have valid company_uid")
        else:
            logger.warning("⚠️  Migration validation FAILED - Some records need attention")
            logger.info("Run migrate_to_company_uid.py to populate missing company_uid values")
        logger.info("=" * 60)
        
        return all_valid
        
    except Error as e:
        logger.error(f"Error during validation: {e}")
        return False
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


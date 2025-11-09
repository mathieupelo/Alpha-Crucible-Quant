"""
Populate company_uid values in signal_raw, scores_combined, and portfolio_positions tables.

This script resolves tickers to company_uid using the Varrock schema and updates
all NULL company_uid values in the affected tables.
"""

import os
import sys
import logging
import psycopg2
from psycopg2 import Error
from psycopg2.extras import execute_batch
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
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


def resolve_ticker_to_company_uid(cursor, ticker: str) -> Optional[str]:
    """
    Resolve a ticker symbol to company_uid via varrock.tickers.
    
    Args:
        cursor: Database cursor
        ticker: Ticker symbol to resolve
        
    Returns:
        company_uid if found, None if not found
    """
    query = """
    SELECT company_uid 
    FROM varrock.tickers 
    WHERE ticker = %s 
    LIMIT 1
    """
    cursor.execute(query, (ticker.strip().upper(),))
    result = cursor.fetchone()
    
    if result:
        return str(result[0])
    return None


def populate_signal_raw_company_uid(connection) -> int:
    """Populate company_uid in signal_raw table."""
    cursor = connection.cursor()
    updated_count = 0
    
    try:
        # Get all rows with NULL company_uid
        logger.info("Fetching signal_raw rows with NULL company_uid...")
        cursor.execute("""
            SELECT DISTINCT ticker 
            FROM signal_raw 
            WHERE company_uid IS NULL
        """)
        tickers = [row[0] for row in cursor.fetchall()]
        
        if not tickers:
            logger.info("No signal_raw rows need updating")
            return 0
        
        logger.info(f"Found {len(tickers)} unique tickers to resolve in signal_raw")
        
        # Build ticker to company_uid mapping
        ticker_to_company_uid: Dict[str, str] = {}
        unresolved_tickers = []
        
        for ticker in tickers:
            company_uid = resolve_ticker_to_company_uid(cursor, ticker)
            if company_uid:
                ticker_to_company_uid[ticker] = company_uid
            else:
                unresolved_tickers.append(ticker)
        
        logger.info(f"Resolved {len(ticker_to_company_uid)} tickers to company_uid")
        if unresolved_tickers:
            logger.warning(f"Could not resolve {len(unresolved_tickers)} tickers: {unresolved_tickers[:10]}...")
        
        # Update rows in batches
        if ticker_to_company_uid:
            update_query = """
            UPDATE signal_raw 
            SET company_uid = %s 
            WHERE ticker = %s AND company_uid IS NULL
            """
            
            # Update each ticker separately to get accurate counts
            total_updated = 0
            for ticker, company_uid in ticker_to_company_uid.items():
                cursor.execute(update_query, (company_uid, ticker))
                total_updated += cursor.rowcount
            
            connection.commit()
            updated_count = total_updated
            
            logger.info(f"Updated {updated_count:,} rows in signal_raw")
        
        return updated_count
        
    except Error as e:
        logger.error(f"Error populating signal_raw.company_uid: {e}")
        connection.rollback()
        return 0
    finally:
        cursor.close()


def populate_scores_combined_company_uid(connection) -> int:
    """Populate company_uid in scores_combined table."""
    cursor = connection.cursor()
    updated_count = 0
    
    try:
        # Get all rows with NULL company_uid
        logger.info("Fetching scores_combined rows with NULL company_uid...")
        cursor.execute("""
            SELECT DISTINCT ticker 
            FROM scores_combined 
            WHERE company_uid IS NULL
        """)
        tickers = [row[0] for row in cursor.fetchall()]
        
        if not tickers:
            logger.info("No scores_combined rows need updating")
            return 0
        
        logger.info(f"Found {len(tickers)} unique tickers to resolve in scores_combined")
        
        # Build ticker to company_uid mapping
        ticker_to_company_uid: Dict[str, str] = {}
        unresolved_tickers = []
        
        for ticker in tickers:
            company_uid = resolve_ticker_to_company_uid(cursor, ticker)
            if company_uid:
                ticker_to_company_uid[ticker] = company_uid
            else:
                unresolved_tickers.append(ticker)
        
        logger.info(f"Resolved {len(ticker_to_company_uid)} tickers to company_uid")
        if unresolved_tickers:
            logger.warning(f"Could not resolve {len(unresolved_tickers)} tickers: {unresolved_tickers[:10]}...")
        
        # Update rows in batches
        if ticker_to_company_uid:
            update_query = """
            UPDATE scores_combined 
            SET company_uid = %s 
            WHERE ticker = %s AND company_uid IS NULL
            """
            
            # Update each ticker separately to get accurate counts
            total_updated = 0
            for ticker, company_uid in ticker_to_company_uid.items():
                cursor.execute(update_query, (company_uid, ticker))
                total_updated += cursor.rowcount
            
            connection.commit()
            updated_count = total_updated
            
            logger.info(f"Updated {updated_count:,} rows in scores_combined")
        
        return updated_count
        
    except Error as e:
        logger.error(f"Error populating scores_combined.company_uid: {e}")
        connection.rollback()
        return 0
    finally:
        cursor.close()


def populate_portfolio_positions_company_uid(connection) -> int:
    """Populate company_uid in portfolio_positions table."""
    cursor = connection.cursor()
    updated_count = 0
    
    try:
        # Get all rows with NULL company_uid
        logger.info("Fetching portfolio_positions rows with NULL company_uid...")
        cursor.execute("""
            SELECT DISTINCT ticker 
            FROM portfolio_positions 
            WHERE company_uid IS NULL
        """)
        tickers = [row[0] for row in cursor.fetchall()]
        
        if not tickers:
            logger.info("No portfolio_positions rows need updating")
            return 0
        
        logger.info(f"Found {len(tickers)} unique tickers to resolve in portfolio_positions")
        
        # Build ticker to company_uid mapping
        ticker_to_company_uid: Dict[str, str] = {}
        unresolved_tickers = []
        
        for ticker in tickers:
            company_uid = resolve_ticker_to_company_uid(cursor, ticker)
            if company_uid:
                ticker_to_company_uid[ticker] = company_uid
            else:
                unresolved_tickers.append(ticker)
        
        logger.info(f"Resolved {len(ticker_to_company_uid)} tickers to company_uid")
        if unresolved_tickers:
            logger.warning(f"Could not resolve {len(unresolved_tickers)} tickers: {unresolved_tickers[:10]}...")
        
        # Update rows in batches
        if ticker_to_company_uid:
            update_query = """
            UPDATE portfolio_positions 
            SET company_uid = %s 
            WHERE ticker = %s AND company_uid IS NULL
            """
            
            # Update each ticker separately to get accurate counts
            total_updated = 0
            for ticker, company_uid in ticker_to_company_uid.items():
                cursor.execute(update_query, (company_uid, ticker))
                total_updated += cursor.rowcount
            
            connection.commit()
            updated_count = total_updated
            
            logger.info(f"Updated {updated_count:,} rows in portfolio_positions")
        
        return updated_count
        
    except Error as e:
        logger.error(f"Error populating portfolio_positions.company_uid: {e}")
        connection.rollback()
        return 0
    finally:
        cursor.close()


def get_null_counts(connection) -> Dict[str, int]:
    """Get counts of NULL company_uid values in each table."""
    cursor = connection.cursor()
    counts = {}
    
    try:
        # Check signal_raw
        cursor.execute("SELECT COUNT(*) FROM signal_raw WHERE company_uid IS NULL")
        counts['signal_raw'] = cursor.fetchone()[0]
        
        # Check scores_combined
        cursor.execute("SELECT COUNT(*) FROM scores_combined WHERE company_uid IS NULL")
        counts['scores_combined'] = cursor.fetchone()[0]
        
        # Check portfolio_positions
        cursor.execute("SELECT COUNT(*) FROM portfolio_positions WHERE company_uid IS NULL")
        counts['portfolio_positions'] = cursor.fetchone()[0]
        
    except Error as e:
        logger.error(f"Error getting NULL counts: {e}")
    finally:
        cursor.close()
    
    return counts


def main():
    """Main migration function."""
    connection = None
    
    try:
        logger.info("=" * 60)
        logger.info("Populate company_uid Values Migration")
        logger.info("=" * 60)
        
        # Check if Varrock schema exists
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'varrock')")
        varrock_exists = cursor.fetchone()[0]
        cursor.close()
        
        if not varrock_exists:
            logger.error("Varrock schema does not exist. Please run setup_varrock_schema.py first.")
            return False
        
        # Set autocommit to False for transaction control
        if connection.autocommit:
            connection.autocommit = False
        
        # Check if company_uid columns exist
        cursor = connection.cursor()
        tables_to_check = ['signal_raw', 'scores_combined', 'portfolio_positions']
        for table in tables_to_check:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s 
                AND column_name = 'company_uid'
            """, (table,))
            if cursor.fetchone() is None:
                logger.error(f"Column company_uid does not exist in {table}. Please run migrate_add_company_uid_columns.py first.")
                cursor.close()
                return False
        cursor.close()
        
        # Get initial NULL counts
        logger.info("\nChecking current NULL company_uid counts...")
        initial_counts = get_null_counts(connection)
        logger.info(f"  signal_raw: {initial_counts['signal_raw']:,} NULL values")
        logger.info(f"  scores_combined: {initial_counts['scores_combined']:,} NULL values")
        logger.info(f"  portfolio_positions: {initial_counts['portfolio_positions']:,} NULL values")
        
        total_null = sum(initial_counts.values())
        if total_null == 0:
            logger.info("\n✅ All company_uid values are already populated!")
            return True
        
        logger.info(f"\nTotal rows to update: {total_null:,}")
        logger.info("\nStarting migration...")
        
        # Populate each table (connection is already set up)
        
        signal_raw_count = populate_signal_raw_company_uid(connection)
        scores_combined_count = populate_scores_combined_company_uid(connection)
        portfolio_positions_count = populate_portfolio_positions_company_uid(connection)
        
        # Get final NULL counts
        logger.info("\nChecking final NULL company_uid counts...")
        final_counts = get_null_counts(connection)
        logger.info(f"  signal_raw: {final_counts['signal_raw']:,} NULL values (updated {signal_raw_count:,})")
        logger.info(f"  scores_combined: {final_counts['scores_combined']:,} NULL values (updated {scores_combined_count:,})")
        logger.info(f"  portfolio_positions: {final_counts['portfolio_positions']:,} NULL values (updated {portfolio_positions_count:,})")
        
        total_updated = signal_raw_count + scores_combined_count + portfolio_positions_count
        total_remaining = sum(final_counts.values())
        
        logger.info("\n" + "=" * 60)
        logger.info("Migration Summary")
        logger.info("=" * 60)
        logger.info(f"Total rows updated: {total_updated:,}")
        logger.info(f"Total rows remaining NULL: {total_remaining:,}")
        
        if total_remaining > 0:
            logger.warning(f"\n⚠️  {total_remaining:,} rows still have NULL company_uid.")
            logger.warning("These tickers may not exist in the Varrock schema.")
            logger.warning("You may need to add these tickers to a universe first.")
        else:
            logger.info("\n✅ All company_uid values have been populated!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during migration: {e}", exc_info=True)
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            connection.close()
            logger.info("\nDatabase connection closed.")


if __name__ == "__main__":
    logger.info("Starting populate company_uid values migration...")
    if main():
        logger.info("Migration completed successfully.")
    else:
        logger.error("Migration failed.")
        sys.exit(1)


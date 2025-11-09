#!/usr/bin/env python3
"""
Migration script to add company_uid columns to signal_raw, scores_combined, and portfolio_positions tables.

This script:
1. Adds company_uid VARCHAR(36) column to each table
2. Adds foreign key constraints to varrock.companies
3. Creates indexes on company_uid columns
4. Keeps ticker columns for backward compatibility
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


def add_company_uid_columns():
    """Add company_uid columns to required tables."""
    connection = None
    try:
        connection = get_connection()
        connection.autocommit = False
        cursor = connection.cursor()
        
        # Check if varrock schema exists
        cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'varrock')")
        varrock_exists = cursor.fetchone()[0]
        
        if not varrock_exists:
            logger.error("Varrock schema does not exist. Please run setup_varrock_schema.py first.")
            return False
        
        # 1. Add company_uid to signal_raw table
        logger.info("Adding company_uid column to signal_raw table...")
        try:
            cursor.execute("""
                ALTER TABLE signal_raw 
                ADD COLUMN IF NOT EXISTS company_uid VARCHAR(36)
            """)
            logger.info("Added company_uid column to signal_raw")
        except Error as e:
            logger.warning(f"Column may already exist in signal_raw: {e}")
        
        # Add foreign key constraint for signal_raw
        try:
            cursor.execute("""
                ALTER TABLE signal_raw
                DROP CONSTRAINT IF EXISTS fk_signal_raw_company_uid
            """)
            cursor.execute("""
                ALTER TABLE signal_raw
                ADD CONSTRAINT fk_signal_raw_company_uid
                FOREIGN KEY (company_uid) REFERENCES varrock.companies(company_uid) ON DELETE SET NULL
            """)
            logger.info("Added foreign key constraint to signal_raw.company_uid")
        except Error as e:
            logger.warning(f"Foreign key constraint may already exist: {e}")
        
        # Add index for signal_raw
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_signal_raw_company_uid 
            ON signal_raw(company_uid)
        """)
        logger.info("Created index on signal_raw.company_uid")
        
        # 2. Add company_uid to scores_combined table
        logger.info("Adding company_uid column to scores_combined table...")
        try:
            cursor.execute("""
                ALTER TABLE scores_combined 
                ADD COLUMN IF NOT EXISTS company_uid VARCHAR(36)
            """)
            logger.info("Added company_uid column to scores_combined")
        except Error as e:
            logger.warning(f"Column may already exist in scores_combined: {e}")
        
        # Add foreign key constraint for scores_combined
        try:
            cursor.execute("""
                ALTER TABLE scores_combined
                DROP CONSTRAINT IF EXISTS fk_scores_combined_company_uid
            """)
            cursor.execute("""
                ALTER TABLE scores_combined
                ADD CONSTRAINT fk_scores_combined_company_uid
                FOREIGN KEY (company_uid) REFERENCES varrock.companies(company_uid) ON DELETE SET NULL
            """)
            logger.info("Added foreign key constraint to scores_combined.company_uid")
        except Error as e:
            logger.warning(f"Foreign key constraint may already exist: {e}")
        
        # Add index for scores_combined
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scores_combined_company_uid 
            ON scores_combined(company_uid)
        """)
        logger.info("Created index on scores_combined.company_uid")
        
        # 3. Add company_uid to portfolio_positions table
        logger.info("Adding company_uid column to portfolio_positions table...")
        try:
            cursor.execute("""
                ALTER TABLE portfolio_positions 
                ADD COLUMN IF NOT EXISTS company_uid VARCHAR(36)
            """)
            logger.info("Added company_uid column to portfolio_positions")
        except Error as e:
            logger.warning(f"Column may already exist in portfolio_positions: {e}")
        
        # Add foreign key constraint for portfolio_positions
        try:
            cursor.execute("""
                ALTER TABLE portfolio_positions
                DROP CONSTRAINT IF EXISTS fk_portfolio_positions_company_uid
            """)
            cursor.execute("""
                ALTER TABLE portfolio_positions
                ADD CONSTRAINT fk_portfolio_positions_company_uid
                FOREIGN KEY (company_uid) REFERENCES varrock.companies(company_uid) ON DELETE SET NULL
            """)
            logger.info("Added foreign key constraint to portfolio_positions.company_uid")
        except Error as e:
            logger.warning(f"Foreign key constraint may already exist: {e}")
        
        # Add index for portfolio_positions
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_portfolio_positions_company_uid 
            ON portfolio_positions(company_uid)
        """)
        logger.info("Created index on portfolio_positions.company_uid")
        
        connection.commit()
        logger.info("Successfully added company_uid columns to all tables!")
        return True
        
    except Error as e:
        if connection:
            connection.rollback()
        logger.error(f"Error adding company_uid columns: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()


def main():
    """Main migration function."""
    logger.info("Starting migration to add company_uid columns...")
    
    if not add_company_uid_columns():
        logger.error("Failed to add company_uid columns")
        sys.exit(1)
    
    logger.info("Migration completed successfully!")
    logger.info("Next step: Run migrate_to_company_uid.py to populate company_uid values")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


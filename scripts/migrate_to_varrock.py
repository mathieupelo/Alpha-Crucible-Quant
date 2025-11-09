#!/usr/bin/env python3
"""
Migration script to migrate from universe_tickers to universe_companies using Varrock schema.

This script:
1. Creates the universe_companies table
2. For each ticker in universe_tickers:
   - Validates ticker with yfinance
   - Creates company, company_info, and ticker records if they don't exist
   - Determines main ticker (NYSE/NASDAQ priority)
   - Creates universe_companies entry
"""

import os
import sys
import logging
import uuid
from pathlib import Path
from datetime import date, datetime
from typing import Optional, Dict, Any

# Add project root and src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
import yfinance as yf

from database import DatabaseManager
from database.models import Company, CompanyInfo, Ticker, UniverseCompany

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_ticker_with_yfinance(ticker: str) -> tuple:
    """Validate ticker and get yfinance info."""
    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        
        # Check if we can get basic info
        is_valid = 'symbol' in info and info['symbol'] is not None
        
        if is_valid:
            return True, info
        else:
            return False, None
    except Exception as e:
        logger.warning(f"Ticker validation failed for {ticker}: {e}")
        return False, None


def extract_company_info_from_yfinance(info: Dict[str, Any]) -> CompanyInfo:
    """Extract company info from yfinance data."""
    company_info_uid = str(uuid.uuid4())
    company_uid = str(uuid.uuid4())  # Will be set later
    
    return CompanyInfo(
        company_info_uid=company_info_uid,
        company_uid=company_uid,  # Temporary, will be updated
        name=info.get('longName') or info.get('shortName') or info.get('name'),
        full_name=info.get('longName'),
        short_name=info.get('shortName'),
        country=info.get('country'),
        continent=None,  # Not in yfinance
        hq_address=info.get('address1'),
        city=info.get('city'),
        state=info.get('state'),
        zip_code=info.get('zip'),
        phone=info.get('phone'),
        website=info.get('website'),
        sector=info.get('sector'),
        industry=info.get('industry'),
        industry_key=info.get('industryKey'),
        industry_disp=info.get('industryDisp'),
        sector_key=info.get('sectorKey'),
        sector_disp=info.get('sectorDisp'),
        market_cap=info.get('marketCap'),
        currency=info.get('currency'),
        exchange=info.get('exchange'),
        exchange_timezone=info.get('exchangeTimezoneName'),
        description=info.get('longBusinessSummary'),
        long_business_summary=info.get('longBusinessSummary'),
        employees=info.get('fullTimeEmployees'),
        founded_year=info.get('foundedYear'),
        data_source='yfinance',
        last_updated=datetime.now()
    )


def create_universe_companies_table(db_manager: DatabaseManager) -> bool:
    """Create the universe_companies table."""
    try:
        query = """
        CREATE TABLE IF NOT EXISTS universe_companies (
            id SERIAL PRIMARY KEY,
            universe_id INT NOT NULL,
            company_uid VARCHAR(36) NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_universe_company UNIQUE (universe_id, company_uid),
            FOREIGN KEY (universe_id) REFERENCES universes(id) ON DELETE CASCADE,
            FOREIGN KEY (company_uid) REFERENCES varrock.companies(company_uid) ON DELETE CASCADE
        )
        """
        
        db_manager.ensure_connection()
        # Temporarily disable autocommit for table creation
        original_autocommit = db_manager._connection.autocommit
        db_manager._connection.autocommit = False
        cursor = db_manager._connection.cursor()
        try:
            cursor.execute(query)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_universe_companies_universe_id ON universe_companies(universe_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_universe_companies_company_uid ON universe_companies(company_uid)")
            db_manager._connection.commit()
        except Exception as e:
            db_manager._connection.rollback()
            raise
        finally:
            cursor.close()
            db_manager._connection.autocommit = original_autocommit
        
        logger.info("Created universe_companies table")
        return True
    except Exception as e:
        logger.error(f"Error creating universe_companies table: {e}")
        return False


def find_or_create_company_from_ticker(db_manager: DatabaseManager, ticker: str) -> Optional[str]:
    """Find existing company by ticker or create new one."""
    # Check if ticker already exists
    ticker_query = """
    SELECT company_uid FROM varrock.tickers WHERE ticker = %s LIMIT 1
    """
    ticker_df = db_manager.execute_query(ticker_query, (ticker,))
    
    if not ticker_df.empty:
        company_uid = str(ticker_df.iloc[0]['company_uid'])
        logger.info(f"Found existing company {company_uid} for ticker {ticker}")
        return company_uid
    
    # Validate ticker with yfinance
    is_valid, yf_info = validate_ticker_with_yfinance(ticker)
    
    # Create company
    company_uid = db_manager.create_company()
    logger.info(f"Created new company {company_uid} for ticker {ticker}")
    
    # Create ticker record
    ticker_uid = str(uuid.uuid4())
    exchange = yf_info.get('exchange') if yf_info else None
    market = exchange  # Use exchange as market for now
    
    ticker_obj = Ticker(
        ticker_uid=ticker_uid,
        company_uid=company_uid,
        ticker=ticker,
        market=market,
        exchange=exchange,
        currency=yf_info.get('currency') if yf_info else None,
        is_in_yfinance=is_valid,
        is_main_ticker=False,  # Will be determined later
        is_active=True,
        ticker_type=None,
        yfinance_symbol=ticker,
        first_seen_date=date.today(),
        last_verified_date=date.today() if is_valid else None,
        created_at=datetime.now()
    )
    
    db_manager.store_ticker(ticker_obj)
    
    # Create company info if we have yfinance data
    if is_valid and yf_info:
        company_info = extract_company_info_from_yfinance(yf_info)
        company_info.company_uid = company_uid
        db_manager.store_company_info(company_info)
        logger.info(f"Stored company info for {ticker}")
    
    return company_uid


def migrate_universe_tickers(db_manager: DatabaseManager) -> bool:
    """Migrate all universe_tickers to universe_companies."""
    try:
        # Get all universe_tickers
        query = "SELECT DISTINCT universe_id, ticker, added_at FROM universe_tickers ORDER BY universe_id, ticker"
        tickers_df = db_manager.execute_query(query)
        
        if tickers_df.empty:
            logger.info("No universe_tickers found to migrate")
            return True
        
        logger.info(f"Found {len(tickers_df)} universe_ticker records to migrate")
        
        # Track companies per universe for main ticker determination
        universe_companies: Dict[int, list] = {}
        
        for idx, row in tickers_df.iterrows():
            universe_id = int(row['universe_id'])
            ticker = str(row['ticker']).strip().upper()
            added_at = row.get('added_at')
            
            logger.info(f"Processing ticker {ticker} for universe {universe_id}")
            
            # Find or create company
            company_uid = find_or_create_company_from_ticker(db_manager, ticker)
            
            if not company_uid:
                logger.warning(f"Failed to create/find company for ticker {ticker}, skipping")
                continue
            
            # Track company for this universe
            if universe_id not in universe_companies:
                universe_companies[universe_id] = []
            universe_companies[universe_id].append((company_uid, ticker))
            
            # Create universe_companies entry
            universe_company = UniverseCompany(
                universe_id=universe_id,
                company_uid=company_uid,
                added_at=added_at if added_at else datetime.now()
            )
            
            db_manager.store_universe_company(universe_company)
            logger.info(f"Added company {company_uid} to universe {universe_id}")
        
        # Determine main tickers for each company
        logger.info("Determining main tickers...")
        for universe_id, companies in universe_companies.items():
            # Group by company_uid to handle multiple tickers per company
            company_tickers: Dict[str, list] = {}
            for company_uid, ticker in companies:
                if company_uid not in company_tickers:
                    company_tickers[company_uid] = []
                company_tickers[company_uid].append(ticker)
            
            # For each company, determine main ticker
            for company_uid, tickers in company_tickers.items():
                db_manager.determine_main_ticker(company_uid)
                logger.info(f"Determined main ticker for company {company_uid}")
        
        logger.info("Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main migration function."""
    logger.info("Starting migration to Varrock schema...")
    
    db_manager = DatabaseManager()
    
    if not db_manager.connect():
        logger.error("Failed to connect to database")
        sys.exit(1)
    
    try:
        # Create universe_companies table
        if not create_universe_companies_table(db_manager):
            logger.error("Failed to create universe_companies table")
            sys.exit(1)
        
        # Migrate data
        if not migrate_universe_tickers(db_manager):
            logger.error("Migration failed")
            sys.exit(1)
        
        logger.info("Migration completed successfully!")
        logger.info("You can now use universe_companies instead of universe_tickers")
        logger.info("Note: universe_tickers table is kept for rollback purposes")
        
    except Exception as e:
        logger.error(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


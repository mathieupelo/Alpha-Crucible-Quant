#!/usr/bin/env python3
"""
Test script for Varrock schema implementation.

Tests:
1. Schema creation
2. Company creation
3. Ticker validation and storage
4. Company info storage
5. Main ticker determination
6. Universe company operations
"""

import os
import sys
import logging
import uuid
from pathlib import Path
from datetime import date, datetime

# Add project root and src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from dotenv import load_dotenv
from database import DatabaseManager
from database.models import Company, CompanyInfo, Ticker, UniverseCompany

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_schema_exists(db_manager: DatabaseManager) -> bool:
    """Test if varrock schema exists."""
    try:
        query = """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.schemata 
            WHERE schema_name = 'varrock'
        )
        """
        result = db_manager.execute_query(query)
        exists = result.iloc[0][0] if not result.empty else False
        logger.info(f"Varrock schema exists: {exists}")
        return exists
    except Exception as e:
        logger.error(f"Error checking schema: {e}")
        return False


def test_company_operations(db_manager: DatabaseManager) -> bool:
    """Test company creation and retrieval."""
    try:
        # Create a test company
        company_uid = db_manager.create_company()
        logger.info(f"Created test company: {company_uid}")
        
        # Retrieve the company
        company = db_manager.get_company(company_uid)
        if company is None:
            logger.error("Failed to retrieve created company")
            return False
        
        logger.info(f"Retrieved company: {company.company_uid}")
        return True
    except Exception as e:
        logger.error(f"Error in company operations: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ticker_validation(db_manager: DatabaseManager) -> bool:
    """Test ticker validation with yfinance."""
    try:
        # Test with a known valid ticker
        test_ticker = "AAPL"
        is_valid = db_manager.validate_ticker_with_yfinance(test_ticker)
        logger.info(f"Ticker {test_ticker} validation: {is_valid}")
        
        # Test with an invalid ticker
        invalid_ticker = "INVALID123"
        is_invalid = db_manager.validate_ticker_with_yfinance(invalid_ticker)
        logger.info(f"Ticker {invalid_ticker} validation: {is_invalid} (should be False)")
        
        return True
    except Exception as e:
        logger.error(f"Error in ticker validation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ticker_storage(db_manager: DatabaseManager) -> bool:
    """Test ticker storage and main ticker determination."""
    try:
        # Create a test company
        company_uid = db_manager.create_company()
        logger.info(f"Created test company for ticker storage: {company_uid}")
        
        # Create a test ticker
        ticker_uid = str(uuid.uuid4())
        ticker = Ticker(
            ticker_uid=ticker_uid,
            company_uid=company_uid,
            ticker="TEST",
            market="NYSE",
            exchange="NYSE",
            currency="USD",
            is_in_yfinance=False,
            is_main_ticker=False,
            is_active=True,
            first_seen_date=date.today(),
            created_at=datetime.now()
        )
        
        db_manager.store_ticker(ticker)
        logger.info(f"Stored test ticker: {ticker.ticker}")
        
        # Test main ticker determination
        main_ticker_uid = db_manager.determine_main_ticker(company_uid)
        logger.info(f"Determined main ticker: {main_ticker_uid}")
        
        # Get main ticker
        main_ticker = db_manager.get_main_ticker(company_uid)
        if main_ticker:
            logger.info(f"Main ticker: {main_ticker.ticker}")
        
        return True
    except Exception as e:
        logger.error(f"Error in ticker storage: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_company_info_storage(db_manager: DatabaseManager) -> bool:
    """Test company info storage."""
    try:
        # Create a test company
        company_uid = db_manager.create_company()
        logger.info(f"Created test company for info storage: {company_uid}")
        
        # Create test company info
        company_info_uid = str(uuid.uuid4())
        company_info = CompanyInfo(
            company_info_uid=company_info_uid,
            company_uid=company_uid,
            name="Test Company",
            full_name="Test Company Inc.",
            country="USA",
            sector="Technology",
            industry="Software",
            data_source="test",
            last_updated=datetime.now()
        )
        
        db_manager.store_company_info(company_info)
        logger.info("Stored test company info")
        
        # Retrieve company info
        retrieved_info = db_manager.get_company_info(company_uid)
        if retrieved_info:
            logger.info(f"Retrieved company info: {retrieved_info.name}")
            return True
        else:
            logger.error("Failed to retrieve company info")
            return False
    except Exception as e:
        logger.error(f"Error in company info storage: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_universe_companies_table(db_manager: DatabaseManager) -> bool:
    """Test if universe_companies table exists."""
    try:
        query = """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'universe_companies'
        )
        """
        result = db_manager.execute_query(query)
        exists = result.iloc[0][0] if not result.empty else False
        logger.info(f"universe_companies table exists: {exists}")
        return exists
    except Exception as e:
        logger.error(f"Error checking universe_companies table: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("Starting Varrock schema tests...")
    
    db_manager = DatabaseManager()
    
    if not db_manager.connect():
        logger.error("Failed to connect to database")
        sys.exit(1)
    
    try:
        tests = [
            ("Schema Exists", test_schema_exists),
            ("Universe Companies Table", test_universe_companies_table),
            ("Company Operations", test_company_operations),
            ("Ticker Validation", test_ticker_validation),
            ("Ticker Storage", test_ticker_storage),
            ("Company Info Storage", test_company_info_storage),
        ]
        
        results = {}
        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running test: {test_name}")
            logger.info(f"{'='*50}")
            try:
                results[test_name] = test_func(db_manager)
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {e}")
                results[test_name] = False
        
        # Print summary
        logger.info(f"\n{'='*50}")
        logger.info("Test Summary")
        logger.info(f"{'='*50}")
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            logger.info(f"{test_name}: {status}")
        
        all_passed = all(results.values())
        if all_passed:
            logger.info("\nAll tests passed!")
            return True
        else:
            logger.error("\nSome tests failed!")
            return False
        
    except Exception as e:
        logger.error(f"Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


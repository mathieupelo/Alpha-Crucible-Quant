#!/usr/bin/env python3
"""
Test script to verify company-based integration works correctly.

This script tests:
1. Database manager can resolve tickers to company_uid
2. Universe companies operations work
3. Signal operations include company info
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all imports work correctly."""
    logger.info("Testing imports...")
    try:
        from src.database.manager import DatabaseManager
        from src.database.models import SignalRaw, ScoreCombined, PortfolioPosition, UniverseCompany
        from src.database.signal_operations import SignalOperationsMixin
        from src.database.universe_operations import UniverseOperationsMixin
        logger.info("✅ All imports successful")
        return True
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False


def test_database_manager_structure():
    """Test that DatabaseManager has the required methods."""
    logger.info("Testing DatabaseManager structure...")
    try:
        from src.database.manager import DatabaseManager
        
        # Check for required methods
        required_methods = [
            'resolve_ticker_to_company_uid',
            'get_universe_companies',
            'store_universe_company',
            'get_signals_raw',
            'get_scores_combined',
            'get_portfolio_positions'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(DatabaseManager, method):
                missing_methods.append(method)
        
        if missing_methods:
            logger.error(f"❌ Missing methods: {missing_methods}")
            return False
        
        logger.info("✅ DatabaseManager has all required methods")
        return True
    except Exception as e:
        logger.error(f"❌ Structure test failed: {e}")
        return False


def test_models():
    """Test that models have company_uid fields."""
    logger.info("Testing models...")
    try:
        from src.database.models import SignalRaw, ScoreCombined, PortfolioPosition, UniverseCompany
        
        # Check SignalRaw
        import inspect
        sig = inspect.signature(SignalRaw.__init__)
        if 'company_uid' not in sig.parameters:
            logger.error("❌ SignalRaw missing company_uid")
            return False
        
        # Check ScoreCombined
        sig = inspect.signature(ScoreCombined.__init__)
        if 'company_uid' not in sig.parameters:
            logger.error("❌ ScoreCombined missing company_uid")
            return False
        
        # Check PortfolioPosition
        sig = inspect.signature(PortfolioPosition.__init__)
        if 'company_uid' not in sig.parameters:
            logger.error("❌ PortfolioPosition missing company_uid")
            return False
        
        logger.info("✅ All models have company_uid fields")
        return True
    except Exception as e:
        logger.error(f"❌ Model test failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("Company Integration Tests")
    logger.info("=" * 60)
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test database manager structure
    results.append(("DatabaseManager Structure", test_database_manager_structure()))
    
    # Test models
    results.append(("Models", test_models()))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    logger.info("=" * 60)
    if all_passed:
        logger.info("✅ All tests passed!")
    else:
        logger.warning("⚠️  Some tests failed")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

